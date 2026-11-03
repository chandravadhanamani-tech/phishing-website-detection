"""
routes/dashboard.py - Dashboard Endpoints
==========================================
Provides aggregate statistics for the current user's dashboard.

GET /dashboard/statistics     - Total counts by prediction and risk level
GET /dashboard/recent         - Last 10 analyses
GET /dashboard/risk-distribution - Counts grouped by risk level (for charting)
"""

import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database import get_db
from app.models.analysis import URLAnalysis
from app.models.user import User
from app.schemas.analysis import AnalysisListItem, DashboardStats, RiskDistribution

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/statistics",
    response_model=DashboardStats,
    summary="Get dashboard statistics",
    description="Returns aggregate counts of analyses for the current user.",
)
def get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Aggregate analysis counts for the current user's dashboard cards."""
    uid = current_user.id

    total = db.query(func.count(URLAnalysis.id)).filter(URLAnalysis.user_id == uid).scalar() or 0
    phishing = db.query(func.count(URLAnalysis.id)).filter(
        URLAnalysis.user_id == uid, URLAnalysis.prediction == "PHISHING"
    ).scalar() or 0
    legitimate = db.query(func.count(URLAnalysis.id)).filter(
        URLAnalysis.user_id == uid, URLAnalysis.prediction == "LEGITIMATE"
    ).scalar() or 0
    critical = db.query(func.count(URLAnalysis.id)).filter(
        URLAnalysis.user_id == uid, URLAnalysis.risk_level == "Critical"
    ).scalar() or 0
    high = db.query(func.count(URLAnalysis.id)).filter(
        URLAnalysis.user_id == uid, URLAnalysis.risk_level == "High"
    ).scalar() or 0
    medium = db.query(func.count(URLAnalysis.id)).filter(
        URLAnalysis.user_id == uid, URLAnalysis.risk_level == "Medium"
    ).scalar() or 0
    low = db.query(func.count(URLAnalysis.id)).filter(
        URLAnalysis.user_id == uid, URLAnalysis.risk_level == "Low"
    ).scalar() or 0
    very_low = db.query(func.count(URLAnalysis.id)).filter(
        URLAnalysis.user_id == uid, URLAnalysis.risk_level == "Very Low"
    ).scalar() or 0

    return DashboardStats(
        total_analyses  = total,
        phishing_count  = phishing,
        legitimate_count = legitimate,
        critical_count  = critical,
        high_count      = high,
        medium_count    = medium,
        low_count       = low,
        very_low_count  = very_low,
    )


@router.get(
    "/recent",
    response_model=List[AnalysisListItem],
    summary="Get recent analyses",
    description="Returns the 10 most recent analyses for the current user.",
)
def get_recent(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns the 10 most recent analysis records for dashboard display."""
    records = (
        db.query(URLAnalysis)
        .filter(URLAnalysis.user_id == current_user.id)
        .order_by(URLAnalysis.created_at.desc())
        .limit(10)
        .all()
    )
    return [AnalysisListItem.model_validate(r) for r in records]


@router.get(
    "/risk-distribution",
    response_model=List[RiskDistribution],
    summary="Get risk level distribution",
    description="Returns counts grouped by risk level for pie/donut charts.",
)
def get_risk_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns risk level counts for the dashboard donut chart."""
    results = (
        db.query(URLAnalysis.risk_level, func.count(URLAnalysis.id).label("count"))
        .filter(URLAnalysis.user_id == current_user.id)
        .group_by(URLAnalysis.risk_level)
        .all()
    )
    return [RiskDistribution(risk_level=r, count=c) for r, c in results]
