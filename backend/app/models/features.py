"""
features.py - URL Features, Risk Factor & SHAP ORM Models
===========================================================
Three related tables:

  url_features      - The 30+ extracted URL characteristics
  risk_factors      - Individual risk signals detected for an analysis
  shap_explanations - Per-feature SHAP contribution values
"""

from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class URLFeatures(Base):
    """
    Stores the 30+ features extracted from a URL during analysis.
    One-to-one relationship with URLAnalysis.
    """
    __tablename__ = "url_features"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id         = Column(Integer, ForeignKey("url_analyses.id"), unique=True, nullable=False)

    # ── URL Structure Features ────────────────────────────────────────────────
    url_length          = Column(Integer)
    domain_length       = Column(Integer)
    path_length         = Column(Integer)
    dot_count           = Column(Integer)
    hyphen_count        = Column(Integer)
    digit_count         = Column(Integer)
    special_char_count  = Column(Integer)
    slash_count         = Column(Integer)
    query_param_count   = Column(Integer)
    fragment_count      = Column(Integer)
    subdomain_count     = Column(Integer)

    # ── Boolean URL Flags ─────────────────────────────────────────────────────
    has_at_symbol       = Column(Boolean)
    has_ip_address      = Column(Boolean)
    has_https           = Column(Boolean)
    is_shortened        = Column(Boolean)
    has_double_slash    = Column(Boolean)
    has_redirect        = Column(Boolean)
    has_port            = Column(Boolean)
    prefix_suffix       = Column(Boolean)   # Hyphen in domain name

    # ── Keyword & TLD Features ────────────────────────────────────────────────
    suspicious_keywords = Column(Boolean)
    keyword_count       = Column(Integer)
    suspicious_tld      = Column(Boolean)
    tld                 = Column(String(20))

    # ── Webpage Features (filled only during deep scan) ───────────────────────
    form_count          = Column(Integer)
    external_link_ratio = Column(Float)
    has_iframe          = Column(Boolean)
    favicon_external    = Column(Boolean)
    submit_to_email     = Column(Boolean)
    right_click_disabled = Column(Boolean)
    popup_window        = Column(Boolean)

    # ── Relationship ──────────────────────────────────────────────────────────
    analysis = relationship("URLAnalysis", back_populates="features")

    def __repr__(self) -> str:
        return f"<URLFeatures analysis_id={self.analysis_id}>"


class RiskFactor(Base):
    """
    Individual risk indicators detected during analysis.
    One URLAnalysis can have multiple RiskFactor rows.
    """
    __tablename__ = "risk_factors"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("url_analyses.id"), nullable=False, index=True)
    factor      = Column(String(200), nullable=False)
    severity    = Column(Enum("Low", "Medium", "High", "Critical"), nullable=False)
    description = Column(Text)

    # ── Relationship ──────────────────────────────────────────────────────────
    analysis = relationship("URLAnalysis", back_populates="risk_factors")

    def __repr__(self) -> str:
        return f"<RiskFactor analysis_id={self.analysis_id} severity={self.severity!r}>"


class SHAPExplanation(Base):
    """
    SHAP (SHapley Additive exPlanations) values for each prediction.
    Stores the top contributing features and their SHAP values.
    """
    __tablename__ = "shap_explanations"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id   = Column(Integer, ForeignKey("url_analyses.id"), nullable=False, index=True)
    feature_name  = Column(String(100), nullable=False)
    shap_value    = Column(Float, nullable=False)    # Positive → phishing, Negative → legitimate
    feature_value = Column(Float)                    # Actual value of the feature
    rank_order    = Column(Integer)                  # 1 = most important

    # ── Relationship ──────────────────────────────────────────────────────────
    analysis = relationship("URLAnalysis", back_populates="shap_explanations")

    def __repr__(self) -> str:
        return f"<SHAP feature={self.feature_name!r} value={self.shap_value:.4f}>"
