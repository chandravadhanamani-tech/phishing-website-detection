"""
schemas/analysis.py - Pydantic Schemas for URL Analysis
========================================================
Defines request/response shapes for:
  - URL analysis (predict endpoint)
  - Analysis history
  - Dashboard statistics
  - Model performance
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator


# ── Request ───────────────────────────────────────────────────────────────────

class AnalysisRequest(BaseModel):
    """Request body for POST /analysis/predict"""
    url: str
    deep_scan: bool = False   # If True, also fetch webpage content

    @field_validator("url")
    @classmethod
    def url_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty.")
        if len(v) > 2048:
            raise ValueError("URL exceeds maximum allowed length of 2048 characters.")
        # Ensure URL starts with http:// or https://
        if not (v.startswith("http://") or v.startswith("https://")):
            v = "http://" + v  # Auto-prepend http:// for convenience
        return v


# ── Feature Response ──────────────────────────────────────────────────────────

class FeatureResponse(BaseModel):
    """All 30+ extracted URL features — returned as part of analysis result."""
    url_length: Optional[int] = None
    domain_length: Optional[int] = None
    path_length: Optional[int] = None
    dot_count: Optional[int] = None
    hyphen_count: Optional[int] = None
    digit_count: Optional[int] = None
    special_char_count: Optional[int] = None
    slash_count: Optional[int] = None
    query_param_count: Optional[int] = None
    fragment_count: Optional[int] = None
    subdomain_count: Optional[int] = None
    has_at_symbol: Optional[bool] = None
    has_ip_address: Optional[bool] = None
    has_https: Optional[bool] = None
    is_shortened: Optional[bool] = None
    has_double_slash: Optional[bool] = None
    has_redirect: Optional[bool] = None
    has_port: Optional[bool] = None
    prefix_suffix: Optional[bool] = None
    suspicious_keywords: Optional[bool] = None
    keyword_count: Optional[int] = None
    suspicious_tld: Optional[bool] = None
    tld: Optional[str] = None
    # Webpage (deep scan only)
    form_count: Optional[int] = None
    external_link_ratio: Optional[float] = None
    has_iframe: Optional[bool] = None
    favicon_external: Optional[bool] = None
    submit_to_email: Optional[bool] = None
    right_click_disabled: Optional[bool] = None
    popup_window: Optional[bool] = None

    model_config = {"from_attributes": True}


# ── Risk & Explanation Responses ─────────────────────────────────────────────

class RiskFactorResponse(BaseModel):
    """A single detected risk signal."""
    factor: str
    severity: str       # Low / Medium / High / Critical
    description: str

    model_config = {"from_attributes": True}


class SHAPFeatureResponse(BaseModel):
    """A single feature's SHAP contribution to the prediction."""
    feature_name: str
    shap_value: float
    feature_value: Optional[float] = None
    rank_order: int
    direction: str  # "phishing" if shap_value > 0, else "legitimate"

    model_config = {"from_attributes": True}


# ── Main Analysis Response ────────────────────────────────────────────────────

class AnalysisResponse(BaseModel):
    """Full result returned after analyzing a URL."""
    id: int
    url: str
    prediction: str           # "PHISHING" or "LEGITIMATE"
    probability: float         # Phishing probability (0.0 – 1.0)
    risk_score: float          # 0 – 100
    risk_level: str            # Very Low / Low / Medium / High / Critical
    risk_factors: List[RiskFactorResponse]
    shap_features: List[SHAPFeatureResponse]
    features: Optional[FeatureResponse] = None
    model_used: Optional[str] = None
    analysis_time_ms: Optional[int] = None
    created_at: datetime
    recommended_action: Optional[str] = None

    model_config = {"from_attributes": True}


class AnalysisListItem(BaseModel):
    """Compact summary used in history list and dashboard tables."""
    id: int
    url: str
    prediction: str
    probability: float
    risk_score: float
    risk_level: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Dashboard & Statistics ────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    """Aggregate statistics for the current user's dashboard."""
    total_analyses: int
    phishing_count: int
    legitimate_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    very_low_count: int


class RiskDistribution(BaseModel):
    """Risk level counts for charting."""
    risk_level: str
    count: int


# ── Model Performance ─────────────────────────────────────────────────────────

class ModelPerformanceResponse(BaseModel):
    """Evaluation metrics for a trained ML model."""
    id: int
    model_name: str
    version: Optional[str] = None
    accuracy: Optional[float] = None
    precision_score: Optional[float] = None
    recall_score: Optional[float] = None
    f1_score: Optional[float] = None
    roc_auc: Optional[float] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class FeatureImportanceItem(BaseModel):
    """A single feature and its global importance score."""
    feature_name: str
    importance: float
    rank: int
