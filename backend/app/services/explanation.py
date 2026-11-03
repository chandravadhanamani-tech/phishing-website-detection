"""
explanation.py - Explainable AI (XAI) Service
==============================================
Generates SHAP-based explanations for phishing predictions.

For each prediction, this service explains:
  - Which features contributed most to the decision
  - Whether each feature pushed toward Phishing or Legitimate
  - A human-readable explanation text

SHAP (SHapley Additive exPlanations) is an industry-standard XAI method.
Positive SHAP values → push prediction toward PHISHING
Negative SHAP values → push prediction toward LEGITIMATE

If the SHAP explainer is not yet available (pre-training),
a rule-based fallback explanation is generated instead.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import numpy as np

from app.core.config import get_settings
from app.services.feature_extractor import ExtractedFeatures

logger = logging.getLogger(__name__)
settings = get_settings()

EXPLAINER_FILE = Path(settings.ml_models_dir) / "shap_explainer.pkl"
FEATURE_NAMES_FILE = Path(settings.ml_models_dir) / "feature_names.pkl"


@dataclass
class FeatureContribution:
    """A single feature's contribution to a prediction."""
    feature_name:  str
    shap_value:    float
    feature_value: Optional[float]
    rank_order:    int
    direction:     str   # "phishing" or "legitimate"


@dataclass
class ExplanationResult:
    """Complete SHAP explanation for one prediction."""
    contributions:    List[FeatureContribution] = field(default_factory=list)
    explanation_text: str = ""
    base_value:       float = 0.0
    method:           str = "shap"  # "shap" or "fallback"


class ExplanationService:
    """
    Generates per-prediction SHAP explanations.
    
    Usage:
        service = ExplanationService()
        result = service.explain(features, prediction="PHISHING", probability=0.87)
    """
    _explainer = None
    _feature_names: list = []
    _loaded: bool = False

    def _load_explainer(self) -> bool:
        """Load the SHAP TreeExplainer from disk. Returns True if successful."""
        import joblib  # Lazy import

        if self._loaded:
            return self._explainer is not None

        self._loaded = True

        if EXPLAINER_FILE.exists():
            try:
                self._explainer = joblib.load(EXPLAINER_FILE)
                logger.info("✅ SHAP explainer loaded.")
            except Exception as e:
                logger.warning(f"Could not load SHAP explainer: {e}")

        if FEATURE_NAMES_FILE.exists():
            try:
                import joblib
                self._feature_names = joblib.load(FEATURE_NAMES_FILE).tolist()
            except Exception:
                pass

        return self._explainer is not None

    def explain(
        self,
        features: ExtractedFeatures,
        prediction: str,
        probability: float,
        top_n: int = 10,
    ) -> ExplanationResult:
        """
        Generate an explanation for a phishing prediction.
        
        Args:
            features:   Extracted URL features
            prediction: "PHISHING" or "LEGITIMATE"
            probability: Phishing probability (0.0–1.0)
            top_n:      Number of top features to include
        
        Returns:
            ExplanationResult with feature contributions and explanation text
        """
        shap_available = self._load_explainer()

        if shap_available:
            return self._shap_explanation(features, prediction, probability, top_n)
        else:
            logger.warning("SHAP explainer not available. Using rule-based fallback.")
            return self._fallback_explanation(features, prediction, probability)

    def _shap_explanation(
        self,
        features: ExtractedFeatures,
        prediction: str,
        probability: float,
        top_n: int,
    ) -> ExplanationResult:
        """Generate SHAP-based explanation using the trained TreeExplainer."""
        try:
            feature_dict = features.to_model_input()

            if self._feature_names:
                feature_vector = [feature_dict.get(f, 0) for f in self._feature_names]
                names = self._feature_names
            else:
                feature_vector = list(feature_dict.values())
                names = list(feature_dict.keys())

            X = np.array(feature_vector).reshape(1, -1)
            shap_values = self._explainer.shap_values(X)

            # For binary classification, shap_values may be a list [legit, phishing]
            if isinstance(shap_values, list):
                sv = shap_values[1][0]  # Phishing class
            else:
                sv = shap_values[0]

            base_value = float(self._explainer.expected_value)
            if isinstance(self._explainer.expected_value, (list, np.ndarray)):
                base_value = float(self._explainer.expected_value[1])

            # Build contribution list
            contributions = []
            for i, (name, sv_val, feat_val) in enumerate(zip(names, sv, feature_vector)):
                contributions.append(FeatureContribution(
                    feature_name  = name,
                    shap_value    = float(sv_val),
                    feature_value = float(feat_val),
                    rank_order    = 0,  # Will be set after sorting
                    direction     = "phishing" if sv_val > 0 else "legitimate",
                ))

            # Sort by absolute SHAP value (most important first)
            contributions.sort(key=lambda c: abs(c.shap_value), reverse=True)
            for rank, c in enumerate(contributions[:top_n]):
                c.rank_order = rank + 1

            top_contributions = contributions[:top_n]
            explanation_text  = self._generate_explanation_text(
                top_contributions, prediction, probability
            )

            return ExplanationResult(
                contributions    = top_contributions,
                explanation_text = explanation_text,
                base_value       = base_value,
                method           = "shap",
            )

        except Exception as e:
            logger.error(f"SHAP explanation failed: {e}. Falling back.")
            return self._fallback_explanation(features, prediction, probability)

    def _fallback_explanation(
        self,
        features: ExtractedFeatures,
        prediction: str,
        probability: float,
    ) -> ExplanationResult:
        """
        Rule-based fallback explanation when SHAP is not available.
        Uses heuristic importance weights derived from domain knowledge.
        
        This is used:
        1. Before ML training is complete
        2. If SHAP calculation fails
        """
        # Heuristic importance weights (domain knowledge)
        HEURISTIC_WEIGHTS = {
            "has_ip_address":      0.95,
            "is_shortened":        0.85,
            "has_at_symbol":       0.80,
            "subdomain_count":     0.70,
            "suspicious_keywords": 0.65,
            "has_https":          -0.60,  # Negative: HTTPS is a good sign
            "url_length":          0.55,
            "suspicious_tld":      0.75,
            "prefix_suffix":       0.45,
            "has_double_slash":    0.50,
            "keyword_count":       0.60,
            "digit_count":         0.30,
            "has_port":            0.40,
            "dot_count":           0.20,
            "hyphen_count":        0.25,
        }

        feature_dict = features.to_model_input()
        contributions = []

        for feat_name, weight in HEURISTIC_WEIGHTS.items():
            feat_val = feature_dict.get(feat_name, 0)
            # Scale SHAP-like value by actual feature value
            if feat_name == "has_https":
                # HTTPS = good signal, invert contribution
                shap_like = weight * (1 - int(bool(feat_val)))
            elif isinstance(feat_val, bool) or feat_val in (0, 1):
                shap_like = weight * int(bool(feat_val))
            else:
                # Numeric: scale by normalized value
                shap_like = weight * min(float(feat_val) / 10.0, 1.0)

            if abs(shap_like) > 0.01:  # Skip near-zero contributions
                contributions.append(FeatureContribution(
                    feature_name  = feat_name,
                    shap_value    = round(shap_like, 4),
                    feature_value = float(feat_val),
                    rank_order    = 0,
                    direction     = "phishing" if shap_like > 0 else "legitimate",
                ))

        # Sort by absolute value
        contributions.sort(key=lambda c: abs(c.shap_value), reverse=True)
        for rank, c in enumerate(contributions[:10]):
            c.rank_order = rank + 1

        top = contributions[:10]
        explanation_text = self._generate_explanation_text(top, prediction, probability)

        return ExplanationResult(
            contributions    = top,
            explanation_text = explanation_text,
            base_value       = 0.0,
            method           = "fallback",
        )

    @staticmethod
    def _generate_explanation_text(
        contributions: List[FeatureContribution],
        prediction: str,
        probability: float,
    ) -> str:
        """
        Generate a human-readable explanation paragraph.
        
        Example output:
          "This URL was classified as PHISHING with 87% confidence.
           The top contributing factors were: IP address in URL (strong phishing signal),
           suspicious keywords detected, and no HTTPS."
        """
        pct = int(probability * 100)

        # Find top phishing and legitimate signals
        phishing_signals = [c for c in contributions if c.direction == "phishing"][:3]
        legit_signals    = [c for c in contributions if c.direction == "legitimate"][:2]

        # Format feature names for readability
        def fmt(name: str) -> str:
            return name.replace("_", " ").replace("has ", "").title()

        if prediction == "PHISHING":
            top_reasons = ", ".join(
                f"**{fmt(c.feature_name)}**" for c in phishing_signals
            ) if phishing_signals else "multiple suspicious URL characteristics"

            text = (
                f"This URL was classified as **PHISHING** with {pct}% probability. "
                f"The model's primary reasons were: {top_reasons}. "
            )
            if legit_signals:
                legit_reasons = ", ".join(fmt(c.feature_name) for c in legit_signals)
                text += (
                    f"Some features suggested legitimacy ({legit_reasons}), "
                    f"but were outweighed by the phishing signals."
                )
        else:
            top_legit = ", ".join(
                f"**{fmt(c.feature_name)}**" for c in legit_signals
            ) if legit_signals else "overall URL structure"

            text = (
                f"This URL was classified as **LEGITIMATE** with {100 - pct}% confidence. "
                f"Positive signals include: {top_legit}. "
            )
            if phishing_signals:
                phishing_reasons = ", ".join(fmt(c.feature_name) for c in phishing_signals)
                text += (
                    f"Some cautionary signals were noted ({phishing_reasons}), "
                    f"but they did not outweigh the legitimate characteristics."
                )

        text += (
            " Note: This explanation is generated by an ML model and "
            "should not be treated as absolute proof of intent."
        )
        return text


# ── Module-level singleton ────────────────────────────────────────────────────
explanation_service = ExplanationService()
