"""
prediction.py - ML Prediction Service
=======================================
Loads trained ML models from disk and runs phishing detection inference.

Model loading uses a singleton pattern (ModelLoader class):
  - Models are loaded ONCE at startup (lazy loading on first call)
  - Subsequent predictions use the cached loaded model

Before Phase 5 (ML training), model files won't exist yet.
In that case, a clearly labeled STUB result is returned so the
rest of the system can still be tested end-to-end.
"""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

from app.core.config import get_settings
from app.services.feature_extractor import ExtractedFeatures

logger = logging.getLogger(__name__)
settings = get_settings()

# ── Model file paths ──────────────────────────────────────────────────────────
MODELS_DIR = Path(settings.ml_models_dir)

MODEL_FILES = {
    "xgboost":       MODELS_DIR / "xgboost_model.pkl",
    "random_forest": MODELS_DIR / "random_forest_model.pkl",
    "logistic":      MODELS_DIR / "logistic_regression_model.pkl",
    "decision_tree": MODELS_DIR / "decision_tree_model.pkl",
    "svm":           MODELS_DIR / "svm_model.pkl",
}

SCALER_FILE        = MODELS_DIR / "scaler.pkl"
FEATURE_NAMES_FILE = MODELS_DIR / "feature_names.pkl"
METRICS_FILE       = MODELS_DIR / "metrics.json"


@dataclass
class PredictionResult:
    """Result of a single prediction."""
    prediction:  str     # "PHISHING" or "LEGITIMATE"
    probability: float   # Phishing probability (0.0 – 1.0)
    confidence:  float   # Confidence = max(probability, 1 - probability)
    model_name:  str
    is_stub:     bool = False  # True when ML model is not yet trained


class ModelLoader:
    """
    Singleton-pattern model loader.
    Loads the ML model files once at first use and caches them.
    """
    _instance: Optional["ModelLoader"] = None
    _model = None
    _scaler = None
    _feature_names: list = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_models(self) -> bool:
        """
        Load the active ML model, scaler, and feature names from disk.
        Returns True if successful, False if files not found (pre-training).
        """
        import joblib  # Import here to avoid startup overhead if not used

        model_name = settings.active_model
        model_file = MODEL_FILES.get(model_name)

        if not model_file or not model_file.exists():
            logger.warning(
                f"⚠️  ML model file not found: {model_file}. "
                f"The system will return STUB predictions until Phase 5 "
                f"(model training) is complete. Run: python ml/train_models.py"
            )
            return False

        try:
            self._model        = joblib.load(model_file)
            self._scaler       = joblib.load(SCALER_FILE) if SCALER_FILE.exists() else None
            self._feature_names = (
                joblib.load(FEATURE_NAMES_FILE).tolist()
                if FEATURE_NAMES_FILE.exists() else []
            )
            logger.info(f"✅ Loaded ML model: {model_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return False

    def model_available(self) -> bool:
        """Check if a usable model is loaded."""
        return self._model is not None

    def predict(self, features: ExtractedFeatures) -> PredictionResult:
        """
        Run inference on a feature vector.
        
        If the model is not yet available (pre-training), returns a STUB
        result with equal probability and a clear warning.
        
        Args:
            features: Extracted URL features
        
        Returns:
            PredictionResult with prediction, probability, and confidence
        """
        if not self.model_available():
            # Attempt lazy load
            self.load_models()

        if not self.model_available():
            # Still not available — return stub
            logger.warning("Returning STUB prediction: ML model not trained yet.")
            return PredictionResult(
                prediction  = "LEGITIMATE",  # Default to safe
                probability = 0.50,
                confidence  = 0.50,
                model_name  = "stub_model",
                is_stub     = True,
            )

        try:
            # Build feature vector in the correct order
            feature_dict = features.to_model_input()

            if self._feature_names:
                # Use the exact feature order from training
                feature_vector = [feature_dict.get(f, 0) for f in self._feature_names]
            else:
                feature_vector = list(feature_dict.values())

            X = np.array(feature_vector).reshape(1, -1)

            # Apply scaler if available
            if self._scaler is not None:
                X = self._scaler.transform(X)

            # Get probability
            if hasattr(self._model, "predict_proba"):
                proba = self._model.predict_proba(X)[0]
                # proba[1] = phishing class probability (label=1 → phishing)
                phishing_prob = float(proba[1])
            else:
                # For models without predict_proba (e.g., LinearSVC)
                raw = self._model.predict(X)[0]
                phishing_prob = 1.0 if raw == 1 else 0.0

            prediction = "PHISHING" if phishing_prob >= 0.5 else "LEGITIMATE"
            confidence = max(phishing_prob, 1 - phishing_prob)

            return PredictionResult(
                prediction  = prediction,
                probability = round(phishing_prob, 4),
                confidence  = round(confidence, 4),
                model_name  = settings.active_model,
                is_stub     = False,
            )

        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return PredictionResult(
                prediction  = "LEGITIMATE",
                probability = 0.50,
                confidence  = 0.50,
                model_name  = "error_fallback",
                is_stub     = True,
            )

    def get_feature_importance(self) -> list:
        """
        Return global feature importance for the active model.
        Used by GET /model/features endpoint.
        
        Returns:
            List of dicts: [{feature_name, importance, rank}]
        """
        if not self.model_available():
            return []

        try:
            if hasattr(self._model, "feature_importances_"):
                importances = self._model.feature_importances_
                names = self._feature_names or [f"feature_{i}" for i in range(len(importances))]
                ranked = sorted(
                    zip(names, importances),
                    key=lambda x: x[1],
                    reverse=True,
                )
                return [
                    {"feature_name": name, "importance": float(imp), "rank": rank + 1}
                    for rank, (name, imp) in enumerate(ranked)
                ]
            elif hasattr(self._model, "coef_"):
                # Logistic Regression
                importances = abs(self._model.coef_[0])
                names = self._feature_names or [f"feature_{i}" for i in range(len(importances))]
                ranked = sorted(
                    zip(names, importances),
                    key=lambda x: x[1],
                    reverse=True,
                )
                return [
                    {"feature_name": name, "importance": float(imp), "rank": rank + 1}
                    for rank, (name, imp) in enumerate(ranked)
                ]
        except Exception as e:
            logger.error(f"Feature importance error: {e}")

        return []

    def get_metrics(self) -> dict:
        """Load metrics from metrics.json saved during training."""
        if METRICS_FILE.exists():
            try:
                with open(METRICS_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Could not load metrics.json: {e}")
        return {}


# ── Module-level singleton ────────────────────────────────────────────────────
model_loader = ModelLoader()
