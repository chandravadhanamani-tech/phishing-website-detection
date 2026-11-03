"""
routes/model.py - ML Model Performance Endpoints
=================================================
Provides:
  GET /model/performance  - All trained model metrics from DB
  GET /model/features     - Global feature importance from active model
  GET /model/active       - Currently active model information
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.ml_model import MLModel
from app.models.user import User
from app.schemas.analysis import FeatureImportanceItem, ModelPerformanceResponse
from app.services.prediction import model_loader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/model", tags=["ML Model"])


@router.get(
    "/performance",
    response_model=List[ModelPerformanceResponse],
    summary="Get ML model performance metrics",
    description=(
        "Returns accuracy, precision, recall, F1-score, and ROC-AUC "
        "for all trained models stored in the database."
    ),
)
def get_model_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns evaluation metrics for all trained models.
    
    These metrics are populated automatically when train_models.py is run
    and the results are inserted into the ml_models table.
    
    If no models are in the database yet, returns an empty list
    (run ml/train_models.py first).
    """
    models = db.query(MLModel).order_by(MLModel.f1_score.desc().nullslast()).all()
    return [ModelPerformanceResponse.model_validate(m) for m in models]


@router.get(
    "/features",
    response_model=List[FeatureImportanceItem],
    summary="Get global feature importance",
    description=(
        "Returns the top features and their importance scores "
        "from the currently active ML model."
    ),
)
def get_feature_importance(
    current_user: User = Depends(get_current_user),
):
    """
    Returns global feature importance from the active model.
    
    For XGBoost/Random Forest: uses model.feature_importances_
    For Logistic Regression: uses abs(model.coef_)
    
    Returns empty list if model is not yet trained.
    """
    importance_data = model_loader.get_feature_importance()

    if not importance_data:
        return []

    return [
        FeatureImportanceItem(
            feature_name = item["feature_name"],
            importance   = item["importance"],
            rank         = item["rank"],
        )
        for item in importance_data
    ]


@router.get(
    "/active",
    response_model=ModelPerformanceResponse,
    summary="Get active model information",
    description="Returns details of the currently active model used for predictions.",
)
def get_active_model(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns information about the currently active prediction model."""
    active = db.query(MLModel).filter(MLModel.is_active == True).first()

    if not active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No active model found in the database. "
                "Please run 'python ml/train_models.py' to train and register models."
            ),
        )

    return ModelPerformanceResponse.model_validate(active)
