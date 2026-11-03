"""
routes/admin.py - Admin-Only Endpoints
=======================================
All endpoints here require 'admin' role (enforced by get_current_admin_user).

GET  /admin/users               - All registered users
GET  /admin/statistics          - System-wide statistics
GET  /admin/analyses            - All analyses across all users
PUT  /admin/model/{id}/activate - Set a model as the active prediction model
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_admin_user
from app.database import get_db
from app.models.analysis import URLAnalysis
from app.models.ml_model import MLModel
from app.models.user import User
from app.schemas.analysis import AnalysisListItem, DashboardStats, ModelPerformanceResponse
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/users",
    response_model=List[UserResponse],
    summary="List all users (admin only)",
)
def list_users(
    skip:  int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=200),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Returns all registered users. Admin only."""
    users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return [UserResponse.model_validate(u) for u in users]


@router.get(
    "/statistics",
    response_model=DashboardStats,
    summary="System-wide statistics (admin only)",
)
def get_system_statistics(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Returns aggregate statistics across ALL users. Admin only."""
    total      = db.query(func.count(URLAnalysis.id)).scalar() or 0
    phishing   = db.query(func.count(URLAnalysis.id)).filter(URLAnalysis.prediction == "PHISHING").scalar() or 0
    legitimate = db.query(func.count(URLAnalysis.id)).filter(URLAnalysis.prediction == "LEGITIMATE").scalar() or 0
    critical   = db.query(func.count(URLAnalysis.id)).filter(URLAnalysis.risk_level == "Critical").scalar() or 0
    high       = db.query(func.count(URLAnalysis.id)).filter(URLAnalysis.risk_level == "High").scalar() or 0
    medium     = db.query(func.count(URLAnalysis.id)).filter(URLAnalysis.risk_level == "Medium").scalar() or 0
    low        = db.query(func.count(URLAnalysis.id)).filter(URLAnalysis.risk_level == "Low").scalar() or 0
    very_low   = db.query(func.count(URLAnalysis.id)).filter(URLAnalysis.risk_level == "Very Low").scalar() or 0

    return DashboardStats(
        total_analyses   = total,
        phishing_count   = phishing,
        legitimate_count = legitimate,
        critical_count   = critical,
        high_count       = high,
        medium_count     = medium,
        low_count        = low,
        very_low_count   = very_low,
    )


@router.get(
    "/analyses",
    response_model=List[AnalysisListItem],
    summary="List all analyses (admin only)",
)
def list_all_analyses(
    skip:  int = Query(default=0, ge=0),
    limit: int = Query(default=50, le=200),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Returns all URL analyses across all users. Admin only."""
    records = (
        db.query(URLAnalysis)
        .order_by(URLAnalysis.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [AnalysisListItem.model_validate(r) for r in records]


@router.put(
    "/model/{model_id}/activate",
    response_model=ModelPerformanceResponse,
    summary="Activate a trained model (admin only)",
    description="Sets the specified model as active. Deactivates all others.",
)
def activate_model(
    model_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Set a trained model as the active prediction model.
    Deactivates all other models.
    """
    target = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model with ID {model_id} not found.",
        )

    # Deactivate all models first
    db.query(MLModel).update({"is_active": False})

    # Activate the target model
    target.is_active = True
    db.commit()
    db.refresh(target)

    logger.info(f"Admin {admin_user.email} activated model: {target.model_name} (id={model_id})")

    return ModelPerformanceResponse.model_validate(target)
