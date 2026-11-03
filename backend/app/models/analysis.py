"""
analysis.py - URL Analysis ORM Model
=====================================
Defines the 'url_analyses' table.
Each row represents one URL submission by a user,
with prediction result, probability, and risk assessment.
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class URLAnalysis(Base):
    """
    ORM model for the 'url_analyses' table.
    
    Stores the result of each phishing detection analysis.
    Links to URLFeatures, RiskFactor, and SHAPExplanation via foreign keys.
    """
    __tablename__ = "url_analyses"

    id              = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    url             = Column(Text, nullable=False)
    prediction      = Column(Enum("PHISHING", "LEGITIMATE"), nullable=False)
    probability     = Column(Float, nullable=False)      # Phishing probability: 0.0 – 1.0
    risk_score      = Column(Float, nullable=False)       # Normalized score: 0 – 100
    risk_level      = Column(
        Enum("Very Low", "Low", "Medium", "High", "Critical"),
        nullable=False,
    )
    model_used      = Column(String(50), default="xgboost")
    analysis_time_ms = Column(Integer)                   # Time taken in milliseconds
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # ── Relationships ──────────────────────────────────────────────────────────
    user             = relationship("User", back_populates="analyses")
    features         = relationship("URLFeatures", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    risk_factors     = relationship("RiskFactor", back_populates="analysis", cascade="all, delete-orphan")
    shap_explanations = relationship("SHAPExplanation", back_populates="analysis", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<URLAnalysis id={self.id} url={self.url[:40]!r} prediction={self.prediction!r}>"
