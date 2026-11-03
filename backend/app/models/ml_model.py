"""
ml_model.py - ML Model Registry ORM Model
==========================================
Tracks trained ML models and their evaluation metrics.
Only one model should have is_active=True at a time.
"""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from app.database import Base


class MLModel(Base):
    """
    ORM model for the 'ml_models' table.
    
    Each row represents a trained ML model version.
    The active model (is_active=True) is used for live predictions.
    """
    __tablename__ = "ml_models"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    model_name     = Column(String(100), nullable=False)   # e.g., "xgboost", "random_forest"
    version        = Column(String(20), default="1.0.0")
    accuracy       = Column(Float)
    precision_score = Column(Float)   # Named precision_score to avoid Python built-in clash
    recall_score   = Column(Float)
    f1_score       = Column(Float)
    roc_auc        = Column(Float)
    is_active      = Column(Boolean, default=False, nullable=False)
    created_at     = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<MLModel name={self.model_name!r} "
            f"f1={self.f1_score:.4f} active={self.is_active}>"
        )
