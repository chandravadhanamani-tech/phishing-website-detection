"""
test_feature_extractor.py - Unit tests for real-time URL feature extractor.
"""

import pytest
from app.services.feature_extractor import FeatureExtractor, ExtractedFeatures

extractor = FeatureExtractor()

def test_clean_url_extraction():
    url = "https://example.com"
    features = extractor.extract(url, deep_scan=False)
    
    assert isinstance(features, ExtractedFeatures)
    assert features.has_https == True
    assert features.has_ip_address == False
    assert features.is_shortened == False
    assert features.has_at_symbol == False
    assert features.suspicious_keywords == False

def test_suspicious_ip_url_extraction():
    url = "http://192.168.1.1/login/bank/verify"
    features = extractor.extract(url, deep_scan=False)
    
    assert features.has_ip_address == True
    assert features.has_https == False
    assert features.suspicious_keywords == True
    assert features.keyword_count >= 2

def test_shortened_url_extraction():
    url = "http://bit.ly/secure-login-update"
    features = extractor.extract(url, deep_scan=False)
    
    assert features.is_shortened == True
    assert features.suspicious_keywords == True

def test_at_symbol_and_prefix_suffix():
    url = "http://paypal-security.com@attacker-server.net/login"
    features = extractor.extract(url, deep_scan=False)
    
    assert features.has_at_symbol == True
    assert features.prefix_suffix == True
