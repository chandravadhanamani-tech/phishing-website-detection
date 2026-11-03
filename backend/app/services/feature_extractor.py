"""
feature_extractor.py - URL Feature Extraction Service
======================================================
Extracts 30+ features from a URL for phishing detection.

Features are grouped into three categories:
  1. URL-level features  (structural, always available)
  2. Domain-level features  (TLD, subdomain analysis)
  3. Webpage features  (HTML content, only when deep_scan=True)

Safety note:
  - Webpage fetching uses a strict timeout and never executes JavaScript.
  - The URL is treated as untrusted input throughout.
  - All external requests use safe read-only HTTP GET.
"""

import ipaddress
import logging
import re
import socket
import urllib.parse
from dataclasses import dataclass, field, asdict
from typing import Optional, Tuple

import requests
import tldextract
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ── Known URL shortener domains ───────────────────────────────────────────────
SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "buff.ly",
    "adf.ly", "short.link", "tiny.cc", "rb.gy", "cutt.ly", "shorturl.at",
    "bl.ink", "clicky.me", "fc.lc", "soo.gd", "s2r.co", "qps.ru",
}

# ── Suspicious keywords often found in phishing URLs ─────────────────────────
SUSPICIOUS_KEYWORDS = [
    "login", "signin", "sign-in", "bank", "secure", "account", "update",
    "verify", "password", "confirm", "free", "lucky", "service", "bonus",
    "ebay", "paypal", "amazon", "apple", "google", "microsoft", "netflix",
    "support", "alert", "suspend", "urgent", "claim", "winner", "prize",
    "billing", "invoice", "credential", "authenticate", "validation",
]

# ── Suspicious TLDs commonly abused in phishing ───────────────────────────────
SUSPICIOUS_TLDS = {
    "xyz", "top", "tk", "ml", "ga", "cf", "gq", "pw", "cc", "club",
    "work", "party", "gdn", "racing", "date", "faith", "review", "cricket",
    "science", "bid", "stream", "download", "win", "accountant", "loan",
}


@dataclass
class ExtractedFeatures:
    """
    Dataclass holding all 30+ extracted features.
    Default values are None (unset) for webpage features
    that are only available during deep scan.
    """
    # ── URL Structure ──────────────────────────────────────────────────────────
    url_length:         int   = 0
    domain_length:      int   = 0
    path_length:        int   = 0
    dot_count:          int   = 0
    hyphen_count:       int   = 0
    digit_count:        int   = 0
    special_char_count: int   = 0
    slash_count:        int   = 0
    query_param_count:  int   = 0
    fragment_count:     int   = 0
    subdomain_count:    int   = 0

    # ── Boolean URL Flags ─────────────────────────────────────────────────────
    has_at_symbol:    bool = False
    has_ip_address:   bool = False
    has_https:        bool = False
    is_shortened:     bool = False
    has_double_slash: bool = False
    has_redirect:     bool = False
    has_port:         bool = False
    prefix_suffix:    bool = False  # Hyphen used as prefix/suffix in domain

    # ── Keyword & TLD ─────────────────────────────────────────────────────────
    suspicious_keywords: bool = False
    keyword_count:       int  = 0
    suspicious_tld:      bool = False
    tld:                 str  = ""

    # ── Webpage Features (deep scan only) ────────────────────────────────────
    form_count:           Optional[int]   = None
    external_link_ratio:  Optional[float] = None
    has_iframe:           Optional[bool]  = None
    favicon_external:     Optional[bool]  = None
    submit_to_email:      Optional[bool]  = None
    right_click_disabled: Optional[bool]  = None
    popup_window:         Optional[bool]  = None

    def to_dict(self) -> dict:
        """Convert to dictionary. Used for ML model input and DB storage."""
        return asdict(self)

    def to_model_input(self) -> dict:
        """
        Return only the numeric/boolean features used by the ML model.
        Fills None values with 0 for ML inference.
        Excludes 'tld' (string) since ML model uses numeric features.
        """
        d = asdict(self)
        d.pop("tld", None)  # Remove string field
        # Replace None with 0 (safe default for missing webpage features)
        return {k: (0 if v is None else int(v) if isinstance(v, bool) else v)
                for k, v in d.items()}


class FeatureExtractor:
    """
    Extracts phishing-detection features from a URL string.
    
    Usage:
        extractor = FeatureExtractor()
        features = extractor.extract("http://example.com", deep_scan=False)
        print(features.url_length)
    """

    def extract(self, url: str, deep_scan: bool = False) -> ExtractedFeatures:
        """
        Main entry point. Extracts all features from the given URL.
        
        Args:
            url:        The URL to analyze (must start with http:// or https://)
            deep_scan:  If True, also fetches the webpage for content features
        
        Returns:
            ExtractedFeatures dataclass with all values populated.
        """
        features = ExtractedFeatures()

        try:
            parsed    = urllib.parse.urlparse(url)
            extracted = tldextract.extract(url)

            self._extract_url_features(features, url, parsed, extracted)
            self._extract_domain_features(features, extracted)

            if deep_scan:
                self._extract_webpage_features(features, url)

        except Exception as e:
            logger.warning(f"Feature extraction error for {url!r}: {e}")

        return features

    # ── Private: URL-Level Features ───────────────────────────────────────────

    def _extract_url_features(
        self,
        features: ExtractedFeatures,
        url: str,
        parsed: urllib.parse.ParseResult,
        extracted: tldextract.tldextract.ExtractResult,
    ) -> None:
        """Extract structural features from the URL string and parsed components."""

        # Lengths
        features.url_length    = len(url)
        features.domain_length = len(parsed.netloc)
        features.path_length   = len(parsed.path)

        # Character counts
        features.dot_count          = url.count(".")
        features.hyphen_count       = url.count("-")
        features.digit_count        = sum(c.isdigit() for c in url)
        features.special_char_count = sum(
            1 for c in url if c in "@!%^&*()+={}[]|\\;:',<>?~`"
        )
        features.slash_count        = url.count("/")

        # Query & fragment
        query_params = urllib.parse.parse_qs(parsed.query)
        features.query_param_count = len(query_params)
        features.fragment_count    = 1 if parsed.fragment else 0

        # Subdomains: e.g. "mail.google.com" → subdomain="mail" → count=1
        subdomain = extracted.subdomain
        features.subdomain_count = len(subdomain.split(".")) if subdomain else 0

        # Boolean flags
        features.has_at_symbol  = "@" in url
        features.has_https      = parsed.scheme == "https"
        features.has_ip_address = self._detect_ip_address(parsed.hostname or "")
        features.is_shortened   = self._detect_shortener(extracted.domain + "." + extracted.suffix)
        features.has_port       = bool(parsed.port)

        # Double-slash redirect: e.g. "http://legit.com//redirect?to=phishing.com"
        path_and_query = parsed.path + ("?" + parsed.query if parsed.query else "")
        features.has_double_slash = "//" in path_and_query

        # Redirect: multiple URLs detected
        features.has_redirect = url.count("http") > 1

        # Prefix/Suffix: hyphen in registered domain name
        features.prefix_suffix = "-" in (extracted.domain or "")

        # Keywords
        suspicious, count = self._count_suspicious_keywords(url)
        features.suspicious_keywords = suspicious
        features.keyword_count       = count

    # ── Private: Domain-Level Features ───────────────────────────────────────

    def _extract_domain_features(
        self,
        features: ExtractedFeatures,
        extracted: tldextract.tldextract.ExtractResult,
    ) -> None:
        """Extract TLD-based and domain-structure features."""
        tld = extracted.suffix.lower() if extracted.suffix else ""
        features.tld             = tld
        features.suspicious_tld  = self._detect_suspicious_tld(tld)

    # ── Private: Webpage Features (deep scan) ────────────────────────────────

    def _extract_webpage_features(self, features: ExtractedFeatures, url: str) -> None:
        """
        Safely fetch the webpage and extract HTML-based features.
        
        Safety measures:
        - Hard timeout (10 seconds max)
        - Read-only GET request
        - No JavaScript execution (BeautifulSoup parses static HTML only)
        - Treats all content as untrusted
        """
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (compatible; PhishingShield/1.0; "
                    "+https://github.com/phishing-shield)"
                )
            }
            from app.core.config import get_settings
            cfg = get_settings()
            response = requests.get(
                url,
                timeout=cfg.deep_scan_timeout,
                headers=headers,
                allow_redirects=True,
                verify=False,
            )
            soup = BeautifulSoup(response.text, "lxml")
            base_domain = tldextract.extract(url).registered_domain

            # Number of forms
            forms = soup.find_all("form")
            features.form_count = len(forms)

            # External link ratio
            all_links = soup.find_all("a", href=True)
            if all_links:
                external = sum(
                    1 for a in all_links
                    if tldextract.extract(a["href"]).registered_domain not in
                    ("", base_domain)
                )
                features.external_link_ratio = external / len(all_links)
            else:
                features.external_link_ratio = 0.0

            # Iframe presence
            features.has_iframe = bool(soup.find("iframe") or soup.find("frame"))

            # Favicon from different domain
            favicon_tag = soup.find("link", rel=lambda r: r and "icon" in r)
            if favicon_tag and favicon_tag.get("href"):
                fav_domain = tldextract.extract(favicon_tag["href"]).registered_domain
                features.favicon_external = bool(fav_domain and fav_domain != base_domain)
            else:
                features.favicon_external = False

            # Form action submits to email
            features.submit_to_email = any(
                "mailto:" in (f.get("action", "") or "") for f in forms
            )

            # JavaScript checks (static analysis only — never executed)
            page_text = response.text.lower()
            features.right_click_disabled = "contextmenu" in page_text
            features.popup_window = "window.open" in page_text

        except Exception as e:
            logger.warning(f"Deep scan failed for {url!r}: {e}. Skipping webpage features.")
            # Leave webpage features as None (not available)

    # ── Private: Helper Methods ───────────────────────────────────────────────

    @staticmethod
    def _detect_ip_address(hostname: str) -> bool:
        """
        Returns True if the hostname is an IPv4 or IPv6 address.
        e.g., "192.168.1.1" → True, "google.com" → False
        """
        if not hostname:
            return False
        try:
            ipaddress.ip_address(hostname)
            return True
        except ValueError:
            pass
        # Also detect IP in brackets: [192.168.1.1]
        if re.search(r"\[?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\]?", hostname):
            return True
        return False

    @staticmethod
    def _detect_shortener(domain: str) -> bool:
        """
        Returns True if the domain is a known URL shortener service.
        """
        return domain.lower() in SHORTENER_DOMAINS

    @staticmethod
    def _count_suspicious_keywords(url: str) -> Tuple[bool, int]:
        """
        Checks the URL for suspicious phishing-related keywords.
        
        Returns:
            (has_suspicious_keywords: bool, count: int)
        """
        url_lower = url.lower()
        count = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in url_lower)
        return count > 0, count

    @staticmethod
    def _detect_suspicious_tld(tld: str) -> bool:
        """
        Returns True if the TLD is in the known suspicious/abused list.
        """
        return tld.lower() in SUSPICIOUS_TLDS
