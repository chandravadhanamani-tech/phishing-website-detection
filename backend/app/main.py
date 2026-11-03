"""
main.py - FastAPI Application Entry Point
==========================================
Phishing Website Detection and Risk Analysis System
MCA Final Year Project

This file:
  - Creates the FastAPI application instance
  - Configures CORS middleware
  - Configures logging
  - Registers all API routers
  - Initializes the database on startup
  - Provides health check and root endpoints
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.database import check_db_connection, init_db
from app.routes import admin, analysis, auth, dashboard, model

# ── Logging Configuration ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger   = logging.getLogger(__name__)
settings = get_settings()


# ── Lifespan (Startup / Shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Code before 'yield' runs at startup.
    Code after 'yield' runs at shutdown.
    """
    # ── Startup ───────────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info("=" * 60)

    # Initialize database tables
    try:
        init_db()
        logger.info("✅ Database initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.warning(
            "The app will start, but database operations will fail. "
            "Please check your .env DB settings and MySQL connection."
        )

    logger.info("📡 API Documentation: http://localhost:{settings.backend_port}/docs")
    logger.info(f"🌐 Frontend: {settings.frontend_url}")
    logger.info("=" * 60)

    yield  # App is running

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info(f"🛑 Shutting down {settings.app_name}...")


# ── FastAPI App Instance ───────────────────────────────────────────────────────
app = FastAPI(
    title       = settings.app_name,
    description = (
        "## An Explainable ML-Based Framework for Phishing Website Detection\n\n"
        "**MCA Final Year Project** — Analyzes URLs for phishing using machine learning, "
        "extracts 30+ URL features, computes a transparent risk score (0–100), "
        "and provides SHAP-based explainability.\n\n"
        "### Authentication\n"
        "Use `POST /auth/login` to get a JWT token, then click **Authorize** above "
        "and enter: `Bearer <your_token>`"
    ),
    version     = settings.app_version,
    contact     = {
        "name":  "MCA Final Year Project",
        "email": "admin@phishingshield.local",
    },
    license_info = {"name": "MIT"},
    lifespan    = lifespan,
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)


# ── CORS Middleware ────────────────────────────────────────────────────────────
# Allows the React frontend (localhost:5173) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins     = [settings.frontend_url, "http://localhost:5173"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)


# ── Request Timing Middleware ──────────────────────────────────────────────────
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Adds X-Process-Time header to all responses for performance monitoring."""
    start = time.time()
    response = await call_next(request)
    process_time = (time.time() - start) * 1000
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response


# ── Include Routers ────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(analysis.router)
app.include_router(dashboard.router)
app.include_router(model.router)
app.include_router(admin.router)


# ── Root Endpoint ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    """Root endpoint — returns app info and links to documentation."""
    return {
        "app":         settings.app_name,
        "version":     settings.app_version,
        "description": "Phishing Website Detection & Risk Analysis System",
        "docs":        "/docs",
        "redoc":       "/redoc",
        "health":      "/health",
        "status":      "running",
    }


# ── Health Check Endpoint ──────────────────────────────────────────────────────
@app.get("/health", tags=["Root"])
def health_check():
    """
    Health check endpoint.
    Returns the status of the application and database connection.
    Used for monitoring and deployment verification.
    """
    db_ok = check_db_connection()

    return JSONResponse(
        status_code=200 if db_ok else 503,
        content={
            "status":   "healthy" if db_ok else "degraded",
            "database": "connected" if db_ok else "disconnected",
            "app":      settings.app_name,
            "version":  settings.app_version,
        },
    )
