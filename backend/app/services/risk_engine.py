"""
risk_engine.py - Risk Analysis Engine
======================================
Calculates a transparent, documented risk score (0–100) for a URL.

Methodology:
  Risk Score = (w1 × ML_Probability × 100)
             + (w2 × URL_Risk_Score)
             + (w3 × Domain_Risk_Score)
             + (w4 × Webpage_Risk_Score)

  Weights:
    w1 (ML probability)      = 0.50  (core signal — most reliable)
    w2 (URL risk indicators) = 0.25  (structural URL flags)
    w3 (Domain indicators)   = 0.15  (TLD, domain structure)
    w4 (Webpage indicators)  = 0.10  (HTML content signals)

  The final score is normalized to 0–100 and mapped to a risk level:
    0–20   → Very Low
    21–40  → Low
    41–60  → Medium
    61–80  → High
    81–100 → Critical

IMPORTANT: This risk score is an academic project framework.
It does not guarantee that a URL is malicious or safe.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from app.services.feature_extractor import ExtractedFeatures

logger = logging.getLogger(__name__)

# ── Risk Level Thresholds ─────────────────────────────────────────────────────
RISK_LEVELS = {
    "Very Low": (0, 20),
    "Low":      (21, 40),
    "Medium":   (41, 60),
    "High":     (61, 80),
    "Critical": (81, 100),
}

# ── Component Weights ─────────────────────────────────────────────────────────
WEIGHT_ML       = 0.50
WEIGHT_URL      = 0.25
WEIGHT_DOMAIN   = 0.15
WEIGHT_WEBPAGE  = 0.10


@dataclass
class RiskFactorResult:
    """A single detected risk signal with its severity and description."""
    factor:      str
    severity:    str   # Low / Medium / High / Critical
    description: str
    points:      float = 0.0  # Internal scoring points (0–10)


@dataclass
class RiskAnalysisResult:
    """Complete risk analysis output for a URL."""
    risk_score:       float
    risk_level:       str
    risk_factors:     List[RiskFactorResult] = field(default_factory=list)
    component_scores: dict = field(default_factory=dict)  # Breakdown for transparency


class RiskEngine:
    """
    Computes a weighted risk score from ML probability and URL features.
    
    Usage:
        engine = RiskEngine()
        result = engine.analyze(features, ml_probability=0.87)
        print(result.risk_score)   # e.g., 89.3
        print(result.risk_level)   # e.g., "Critical"
    """

    def analyze(
        self,
        features: ExtractedFeatures,
        ml_probability: float,
        deep_scan_results: Optional[dict] = None,
    ) -> RiskAnalysisResult:
        """
        Calculate the final risk score.
        
        Args:
            features:          Extracted URL features
            ml_probability:    ML model's phishing probability (0.0–1.0)
            deep_scan_results: Dict of webpage features (optional)
        
        Returns:
            RiskAnalysisResult with score, level, and detected risk factors
        """
        all_risk_factors: List[RiskFactorResult] = []

        # ── Component 1: ML Score (50% weight) ───────────────────────────────
        ml_score = ml_probability * 100  # Convert to 0–100 range

        # ── Component 2: URL Risk (25% weight) ───────────────────────────────
        url_score, url_factors = self._calculate_url_risk(features)
        all_risk_factors.extend(url_factors)

        # ── Component 3: Domain Risk (15% weight) ────────────────────────────
        domain_score, domain_factors = self._calculate_domain_risk(features)
        all_risk_factors.extend(domain_factors)

        # ── Component 4: Webpage Risk (10% weight) ───────────────────────────
        webpage_score = 0.0
        if deep_scan_results:
            webpage_score, webpage_factors = self._calculate_webpage_risk(deep_scan_results)
            all_risk_factors.extend(webpage_factors)

        # ── Final Weighted Score ──────────────────────────────────────────────
        weighted_score = (
            (WEIGHT_ML      * ml_score)     +
            (WEIGHT_URL     * url_score)    +
            (WEIGHT_DOMAIN  * domain_score) +
            (WEIGHT_WEBPAGE * webpage_score)
        )

        # Clamp to 0–100
        final_score = max(0.0, min(100.0, weighted_score))
        risk_level  = self._determine_risk_level(final_score)

        logger.debug(
            f"Risk Score: {final_score:.1f} ({risk_level}) | "
            f"ML={ml_score:.1f} URL={url_score:.1f} "
            f"Domain={domain_score:.1f} Web={webpage_score:.1f}"
        )

        return RiskAnalysisResult(
            risk_score   = round(final_score, 2),
            risk_level   = risk_level,
            risk_factors = all_risk_factors,
            component_scores={
                "ml_component":      round(ml_score, 2),
                "url_component":     round(url_score, 2),
                "domain_component":  round(domain_score, 2),
                "webpage_component": round(webpage_score, 2),
                "weights": {
                    "ml": WEIGHT_ML,
                    "url": WEIGHT_URL,
                    "domain": WEIGHT_DOMAIN,
                    "webpage": WEIGHT_WEBPAGE,
                },
            },
        )

    # ── URL Risk ──────────────────────────────────────────────────────────────

    def _calculate_url_risk(
        self, features: ExtractedFeatures
    ) -> Tuple[float, List[RiskFactorResult]]:
        """
        Evaluate URL structural risk indicators.
        Each factor adds points proportional to its danger.
        Max possible = 100.
        """
        factors: List[RiskFactorResult] = []
        total_points = 0.0

        # IP address in URL (very strong signal)
        if features.has_ip_address:
            p = 10.0
            total_points += p
            factors.append(RiskFactorResult(
                factor="IP Address in URL",
                severity="Critical",
                description="The URL uses an IP address instead of a domain name. "
                            "Legitimate websites rarely use raw IP addresses.",
                points=p,
            ))

        # URL shortener
        if features.is_shortened:
            p = 8.0
            total_points += p
            factors.append(RiskFactorResult(
                factor="URL Shortener Detected",
                severity="High",
                description="URL shorteners can hide the true destination of a link. "
                            "Phishing attacks commonly use them to mask malicious URLs.",
                points=p,
            ))

        # @ symbol in URL
        if features.has_at_symbol:
            p = 7.0
            total_points += p
            factors.append(RiskFactorResult(
                factor="@ Symbol in URL",
                severity="High",
                description="The @ symbol in a URL causes browsers to ignore everything "
                            "before it. This is a classic phishing technique.",
                points=p,
            ))

        # Suspicious keywords
        if features.suspicious_keywords:
            p = min(6.0, features.keyword_count * 2.0)
            total_points += p
            factors.append(RiskFactorResult(
                factor=f"Suspicious Keywords ({features.keyword_count} found)",
                severity="Medium" if features.keyword_count < 3 else "High",
                description=f"Found {features.keyword_count} suspicious keyword(s) "
                            f"(e.g., 'login', 'bank', 'secure', 'verify') in the URL. "
                            f"These are commonly used to impersonate legitimate services.",
                points=p,
            ))

        # Very long URL
        if features.url_length > 75:
            p = 3.0 if features.url_length <= 100 else 5.0
            total_points += p
            factors.append(RiskFactorResult(
                factor=f"Unusually Long URL ({features.url_length} chars)",
                severity="Low" if features.url_length <= 100 else "Medium",
                description="Legitimate URLs are typically concise. Very long URLs "
                            "may be obfuscating a malicious destination.",
                points=p,
            ))

        # Multiple subdomains (> 3)
        if features.subdomain_count > 3:
            p = 5.0
            total_points += p
            factors.append(RiskFactorResult(
                factor=f"Excessive Subdomains ({features.subdomain_count})",
                severity="High",
                description="An unusually high number of subdomains can be a sign of "
                            "domain impersonation (e.g., secure.paypal.com.evil.com).",
                points=p,
            ))
        elif features.subdomain_count > 1:
            p = 2.0
            total_points += p

        # No HTTPS
        if not features.has_https:
            p = 5.0
            total_points += p
            factors.append(RiskFactorResult(
                factor="No HTTPS (Insecure Connection)",
                severity="Medium",
                description="The URL uses HTTP instead of HTTPS. "
                            "While not proof of phishing, legitimate sites "
                            "that handle user data should use HTTPS.",
                points=p,
            ))

        # Double slash redirect
        if features.has_double_slash:
            p = 4.0
            total_points += p
            factors.append(RiskFactorResult(
                factor="Double-Slash Redirect Pattern",
                severity="Medium",
                description="A '//' in the URL path can indicate a redirect "
                            "attempt to hide the true destination.",
                points=p,
            ))

        # Prefix/Suffix (hyphen in domain)
        if features.prefix_suffix:
            p = 3.0
            total_points += p
            factors.append(RiskFactorResult(
                factor="Hyphen in Domain Name",
                severity="Low",
                description="Hyphens in domain names are sometimes used to mimic "
                            "legitimate domains (e.g., 'pay-pal.com' vs 'paypal.com').",
                points=p,
            ))

        return min(total_points, 100.0), factors

    # ── Domain Risk ───────────────────────────────────────────────────────────

    def _calculate_domain_risk(
        self, features: ExtractedFeatures
    ) -> Tuple[float, List[RiskFactorResult]]:
        """Evaluate domain-level risk indicators."""
        factors: List[RiskFactorResult] = []
        total_points = 0.0

        # Suspicious TLD
        if features.suspicious_tld:
            p = 8.0
            total_points += p
            factors.append(RiskFactorResult(
                factor=f"Suspicious TLD (.{features.tld})",
                severity="High",
                description=f"The TLD '.{features.tld}' is commonly associated with "
                            f"free/low-cost domain registrations often abused for phishing.",
                points=p,
            ))

        # Non-standard port
        if features.has_port:
            p = 5.0
            total_points += p
            factors.append(RiskFactorResult(
                factor="Non-Standard Port Used",
                severity="Medium",
                description="The URL specifies a non-standard port number. "
                            "Legitimate web services typically use standard ports (80/443).",
                points=p,
            ))

        # Multiple redirects
        if features.has_redirect:
            p = 4.0
            total_points += p
            factors.append(RiskFactorResult(
                factor="URL Redirect Detected",
                severity="Medium",
                description="The URL contains redirect patterns which may hide "
                            "the true destination of the link.",
                points=p,
            ))

        return min(total_points, 100.0), factors

    # ── Webpage Risk ──────────────────────────────────────────────────────────

    def _calculate_webpage_risk(
        self, deep_scan_results: dict
    ) -> Tuple[float, List[RiskFactorResult]]:
        """Evaluate webpage content risk indicators (only when deep scan is enabled)."""
        factors: List[RiskFactorResult] = []
        total_points = 0.0

        if deep_scan_results.get("has_iframe"):
            p = 8.0
            total_points += p
            factors.append(RiskFactorResult(
                factor="Hidden IFrame Detected",
                severity="High",
                description="Hidden iframes are commonly used in phishing pages "
                            "to embed malicious content from another domain.",
                points=p,
            ))

        ext_ratio = deep_scan_results.get("external_link_ratio", 0)
        if ext_ratio and ext_ratio > 0.7:
            p = 6.0
            total_points += p
            factors.append(RiskFactorResult(
                factor=f"High External Link Ratio ({ext_ratio:.0%})",
                severity="Medium",
                description="Most links on this page point to external domains. "
                            "This can indicate a cloned phishing page.",
                points=p,
            ))

        if deep_scan_results.get("submit_to_email"):
            p = 7.0
            total_points += p
            factors.append(RiskFactorResult(
                factor="Form Submits to Email",
                severity="High",
                description="A form on this page submits data via mailto:, "
                            "which can be used to steal form input.",
                points=p,
            ))

        if deep_scan_results.get("right_click_disabled"):
            p = 4.0
            total_points += p
            factors.append(RiskFactorResult(
                factor="Right-Click Disabled",
                severity="Low",
                description="JavaScript is used to disable right-clicking. "
                            "Some phishing pages do this to prevent inspection.",
                points=p,
            ))

        if deep_scan_results.get("popup_window"):
            p = 3.0
            total_points += p
            factors.append(RiskFactorResult(
                factor="Popup Window Script Detected",
                severity="Low",
                description="The page contains JavaScript code to open popup windows.",
                points=p,
            ))

        return min(total_points, 100.0), factors

    # ── Risk Level ────────────────────────────────────────────────────────────

    @staticmethod
    def _determine_risk_level(score: float) -> str:
        """
        Map a numeric score (0–100) to a named risk level.
        
        Thresholds (project-defined, not industry standard):
          0–20   → Very Low
          21–40  → Low
          41–60  → Medium
          61–80  → High
          81–100 → Critical
        """
        if score <= 20:
            return "Very Low"
        elif score <= 40:
            return "Low"
        elif score <= 60:
            return "Medium"
        elif score <= 80:
            return "High"
        else:
            return "Critical"


    @staticmethod
    def get_recommended_action(risk_level: str, prediction: str) -> str:
        """
        Returns a user-friendly recommended action based on risk level.
        
        Note: This is guidance only — not a guarantee of maliciousness.
        """
        actions = {
            "Critical": (
                "⛔ DO NOT proceed. This URL shows multiple critical risk indicators "
                "consistent with phishing attacks. Do not enter any personal information. "
                "Report this URL to your IT security team or use phishtank.com to report it."
            ),
            "High": (
                "🚨 Exercise extreme caution. This URL has high-risk characteristics. "
                "Avoid entering credentials or personal information. "
                "Verify the URL with the organization directly through official channels."
            ),
            "Medium": (
                "⚠️ Proceed with caution. Some suspicious indicators were detected. "
                "Verify the URL is from a trusted source before entering any information. "
                "Check the SSL certificate and domain name carefully."
            ),
            "Low": (
                "🔵 Low risk detected. The URL appears mostly safe but exercise "
                "normal web safety practices. Verify you are on the intended website."
            ),
            "Very Low": (
                "✅ Very low risk. This URL shows characteristics consistent with "
                "legitimate websites. Continue with standard caution."
            ),
        }
        return actions.get(risk_level, "Exercise caution when visiting this URL.")
