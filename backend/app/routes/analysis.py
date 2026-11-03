"""
routes/analysis.py - URL Analysis Endpoints
=============================================
Provides:
  POST   /analysis/predict       - Submit a URL for phishing analysis
  GET    /analysis/history       - Get the current user's analysis history
  GET    /analysis/{id}          - Get a specific analysis result by ID
  DELETE /analysis/{id}          - Delete an analysis record

This is the core workflow of the application:
  URL Input → Feature Extraction → ML Prediction → Risk Scoring → XAI → DB Save
"""

import logging
import csv
import io
import time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.analysis import URLAnalysis
from app.models.features import RiskFactor, SHAPExplanation, URLFeatures
from app.models.user import User
from app.schemas.analysis import (
    AnalysisListItem,
    AnalysisRequest,
    AnalysisResponse,
    FeatureResponse,
    RiskFactorResponse,
    SHAPFeatureResponse,
)
from app.services.explanation import explanation_service
from app.services.feature_extractor import FeatureExtractor
from app.services.prediction import model_loader
from app.services.risk_engine import RiskEngine

logger   = logging.getLogger(__name__)
router   = APIRouter(prefix="/analysis", tags=["URL Analysis"])

# Module-level service instances (instantiated once)
feature_extractor = FeatureExtractor()
risk_engine       = RiskEngine()


@router.post(
    "/predict",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze a URL for phishing",
    description=(
        "Submit a URL for phishing detection. "
        "Returns prediction, probability, risk score, risk factors, "
        "and SHAP-based feature explanations."
    ),
)
def predict(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Full phishing detection pipeline:
    
    1. Validate URL
    2. Extract URL features (30+ features)
    3. Run ML inference (XGBoost)
    4. Calculate risk score (0–100) with weighted formula
    5. Generate SHAP explanation
    6. Save everything to database
    7. Return complete result
    """
    start_time = time.time()
    url = request.url

    logger.info(f"Analyzing URL: {url!r} (deep_scan={request.deep_scan}) for user {current_user.id}")

    # ── Step 1: Feature Extraction ────────────────────────────────────────────
    try:
        features = feature_extractor.extract(url, deep_scan=request.deep_scan)
    except Exception as e:
        logger.error(f"Feature extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not extract features from the provided URL: {str(e)}",
        )

    # ── Step 2: ML Prediction ─────────────────────────────────────────────────
    prediction_result = model_loader.predict(features)

    # ── Step 3: Risk Analysis ─────────────────────────────────────────────────
    deep_scan_dict = None
    if request.deep_scan and features.has_iframe is not None:
        deep_scan_dict = {
            "has_iframe":           features.has_iframe,
            "external_link_ratio":  features.external_link_ratio,
            "submit_to_email":      features.submit_to_email,
            "right_click_disabled": features.right_click_disabled,
            "popup_window":         features.popup_window,
        }

    risk_result = risk_engine.analyze(
        features        = features,
        ml_probability  = prediction_result.probability,
        deep_scan_results = deep_scan_dict,
    )

    # ── Step 4: SHAP Explanation ──────────────────────────────────────────────
    explanation = explanation_service.explain(
        features    = features,
        prediction  = prediction_result.prediction,
        probability = prediction_result.probability,
    )

    # ── Step 5: Recommended Action ────────────────────────────────────────────
    recommended_action = risk_engine.get_recommended_action(
        risk_result.risk_level,
        prediction_result.prediction,
    )

    # ── Step 6: Save to Database ──────────────────────────────────────────────
    elapsed_ms = int((time.time() - start_time) * 1000)

    analysis_record = URLAnalysis(
        user_id          = current_user.id,
        url              = url,
        prediction       = prediction_result.prediction,
        probability      = prediction_result.probability,
        risk_score       = risk_result.risk_score,
        risk_level       = risk_result.risk_level,
        model_used       = prediction_result.model_name,
        analysis_time_ms = elapsed_ms,
    )
    db.add(analysis_record)
    db.flush()  # Get the analysis ID before adding related records

    # Save extracted features
    feat_dict = features.to_dict()
    url_features_record = URLFeatures(
        analysis_id           = analysis_record.id,
        url_length            = feat_dict.get("url_length"),
        domain_length         = feat_dict.get("domain_length"),
        path_length           = feat_dict.get("path_length"),
        dot_count             = feat_dict.get("dot_count"),
        hyphen_count          = feat_dict.get("hyphen_count"),
        digit_count           = feat_dict.get("digit_count"),
        special_char_count    = feat_dict.get("special_char_count"),
        slash_count           = feat_dict.get("slash_count"),
        query_param_count     = feat_dict.get("query_param_count"),
        fragment_count        = feat_dict.get("fragment_count"),
        subdomain_count       = feat_dict.get("subdomain_count"),
        has_at_symbol         = feat_dict.get("has_at_symbol"),
        has_ip_address        = feat_dict.get("has_ip_address"),
        has_https             = feat_dict.get("has_https"),
        is_shortened          = feat_dict.get("is_shortened"),
        has_double_slash      = feat_dict.get("has_double_slash"),
        has_redirect          = feat_dict.get("has_redirect"),
        has_port              = feat_dict.get("has_port"),
        prefix_suffix         = feat_dict.get("prefix_suffix"),
        suspicious_keywords   = feat_dict.get("suspicious_keywords"),
        keyword_count         = feat_dict.get("keyword_count"),
        suspicious_tld        = feat_dict.get("suspicious_tld"),
        tld                   = feat_dict.get("tld"),
        form_count            = feat_dict.get("form_count"),
        external_link_ratio   = feat_dict.get("external_link_ratio"),
        has_iframe            = feat_dict.get("has_iframe"),
        favicon_external      = feat_dict.get("favicon_external"),
        submit_to_email       = feat_dict.get("submit_to_email"),
        right_click_disabled  = feat_dict.get("right_click_disabled"),
        popup_window          = feat_dict.get("popup_window"),
    )
    db.add(url_features_record)

    # Save risk factors
    for rf in risk_result.risk_factors:
        db.add(RiskFactor(
            analysis_id = analysis_record.id,
            factor      = rf.factor,
            severity    = rf.severity,
            description = rf.description,
        ))

    # Save SHAP explanations
    for contrib in explanation.contributions:
        db.add(SHAPExplanation(
            analysis_id   = analysis_record.id,
            feature_name  = contrib.feature_name,
            shap_value    = contrib.shap_value,
            feature_value = contrib.feature_value,
            rank_order    = contrib.rank_order,
        ))

    db.commit()
    db.refresh(analysis_record)

    logger.info(
        f"Analysis complete: id={analysis_record.id} "
        f"prediction={prediction_result.prediction} "
        f"risk={risk_result.risk_score:.1f} ({risk_result.risk_level}) "
        f"time={elapsed_ms}ms"
    )

    # ── Step 7: Build Response ────────────────────────────────────────────────
    return AnalysisResponse(
        id               = analysis_record.id,
        url              = url,
        prediction       = prediction_result.prediction,
        probability      = prediction_result.probability,
        risk_score       = risk_result.risk_score,
        risk_level       = risk_result.risk_level,
        risk_factors     = [
            RiskFactorResponse(
                factor      = rf.factor,
                severity    = rf.severity,
                description = rf.description,
            )
            for rf in risk_result.risk_factors
        ],
        shap_features    = [
            SHAPFeatureResponse(
                feature_name  = c.feature_name,
                shap_value    = c.shap_value,
                feature_value = c.feature_value,
                rank_order    = c.rank_order,
                direction     = c.direction,
            )
            for c in explanation.contributions
        ],
        features         = FeatureResponse.model_validate(url_features_record),
        model_used       = prediction_result.model_name,
        analysis_time_ms = elapsed_ms,
        created_at       = analysis_record.created_at,
        recommended_action = recommended_action,
    )


@router.get(
    "/history",
    response_model=List[AnalysisListItem],
    summary="Get analysis history",
    description="Returns the current user's URL analysis history, newest first.",
)
def get_history(
    skip:  int = Query(default=0,  ge=0,   description="Number of records to skip"),
    limit: int = Query(default=20, le=100, description="Max records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns paginated analysis history for the current user."""
    records = (
        db.query(URLAnalysis)
        .filter(URLAnalysis.user_id == current_user.id)
        .order_by(URLAnalysis.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [AnalysisListItem.model_validate(r) for r in records]


@router.get(
    "/{analysis_id}",
    response_model=AnalysisResponse,
    summary="Get a specific analysis result",
)
def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fetch the full result of a specific analysis by ID.
    Users can only access their own analyses (unless admin).
    """
    record = db.query(URLAnalysis).filter(URLAnalysis.id == analysis_id).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {analysis_id} not found.",
        )

    # Authorization: users can only see their own analyses
    if record.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this analysis.",
        )

    recommended_action = risk_engine.get_recommended_action(
        record.risk_level, record.prediction
    )

    return AnalysisResponse(
        id               = record.id,
        url              = record.url,
        prediction       = record.prediction,
        probability      = record.probability,
        risk_score       = record.risk_score,
        risk_level       = record.risk_level,
        risk_factors     = [
            RiskFactorResponse.model_validate(rf)
            for rf in record.risk_factors
        ],
        shap_features    = [
            SHAPFeatureResponse(
                feature_name  = s.feature_name,
                shap_value    = s.shap_value,
                feature_value = s.feature_value,
                rank_order    = s.rank_order,
                direction     = "phishing" if s.shap_value > 0 else "legitimate",
            )
            for s in record.shap_explanations
        ],
        features         = FeatureResponse.model_validate(record.features) if record.features else None,
        model_used       = record.model_used,
        analysis_time_ms = record.analysis_time_ms,
        created_at       = record.created_at,
        recommended_action = recommended_action,
    )


@router.delete(
    "/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an analysis record",
)
def delete_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a specific analysis record. Users can only delete their own."""
    record = db.query(URLAnalysis).filter(URLAnalysis.id == analysis_id).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {analysis_id} not found.",
        )

    if record.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this analysis.",
        )

    db.delete(record)
    db.commit()
    logger.info(f"Analysis {analysis_id} deleted by user {current_user.id}")


@router.post(
    "/predict-batch-file",
    status_code=status.HTTP_200_OK,
    summary="Batch analyze URLs from a CSV or TXT file",
)
async def predict_batch_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Accepts a .csv or .txt file containing URLs (up to 50 URLs max).
    Extracts features and predicts phishing risk for each URL in the file.
    Returns a summary report with counts and individual URL predictions.
    """
    filename = file.filename.lower()
    if not (filename.endswith(".csv") or filename.endswith(".txt")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .csv or .txt files are supported.",
        )
    
    content = (await file.read()).decode("utf-8", errors="ignore")
    urls = []
    
    if filename.endswith(".csv"):
        reader = csv.reader(io.StringIO(content))
        header = None
        url_idx = 0
        for row in reader:
            if not row or not any(row):
                continue
            if header is None:
                lowered_row = [c.strip().lower() for c in row]
                if any(h in lowered_row for h in ["url", "website", "link", "domain"]):
                    header = lowered_row
                    for idx, h in enumerate(header):
                        if h in ["url", "website", "link", "domain"]:
                            url_idx = idx
                            break
                    continue
                else:
                    header = ["url"]
            
            if len(row) > url_idx:
                candidate = row[url_idx].strip()
                if candidate and candidate.lower() not in ["url", "website", "link", "domain"]:
                    urls.append(candidate)
    else:
        for line in content.splitlines():
            trimmed = line.strip()
            if trimmed and not trimmed.startswith("#"):
                urls.append(trimmed)

    urls = urls[:50]
    if not urls:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid URLs found in the uploaded file.",
        )

    results = []
    phishing_count = 0
    legitimate_count = 0
    high_risk_count = 0

    for item_url in urls:
        if not (item_url.startswith("http://") or item_url.startswith("https://")):
            item_url = "http://" + item_url
        
        try:
            features = feature_extractor.extract(item_url, deep_scan=False)
            prediction_result = model_loader.predict(features)
            risk_result = risk_engine.analyze(
                features=features,
                ml_probability=prediction_result.probability,
            )
            
            if prediction_result.prediction == "PHISHING":
                phishing_count += 1
            else:
                legitimate_count += 1
                
            if risk_result.risk_level in ["High", "Critical"]:
                high_risk_count += 1
                
            results.append({
                "url": item_url,
                "prediction": prediction_result.prediction,
                "probability": round(prediction_result.probability, 4),
                "risk_score": round(risk_result.risk_score, 1),
                "risk_level": risk_result.risk_level,
                "model_used": prediction_result.model_name,
            })
        except Exception as err:
            results.append({
                "url": item_url,
                "prediction": "ERROR",
                "probability": 0.0,
                "risk_score": 0.0,
                "risk_level": "Unknown",
                "error": str(err),
            })

    return {
        "filename": file.filename,
        "total_scanned": len(results),
        "phishing_count": phishing_count,
        "legitimate_count": legitimate_count,
        "high_risk_count": high_risk_count,
        "results": results,
    }
