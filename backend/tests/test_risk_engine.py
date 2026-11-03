"""
test_risk_engine.py - Unit tests for weighted risk scoring engine.
"""

import pytest
from app.services.feature_extractor import FeatureExtractor
from app.services.risk_engine import RiskEngine

extractor = FeatureExtractor()
risk_engine = RiskEngine()

def test_legitimate_url_risk_score():
    features = extractor.extract("https://example.com")
    result = risk_engine.analyze(features, ml_probability=0.05)
    
    assert result.risk_score < 30.0
    assert result.risk_level in ["Very Low", "Low"]

def test_phishing_url_risk_score():
    features = extractor.extract("http://192.168.1.1/login/paypal-verification@attacker.xyz")
    result = risk_engine.analyze(features, ml_probability=0.92)
    
    assert result.risk_score >= 50.0
    assert result.risk_level in ["Medium", "High", "Critical"]
    assert len(result.risk_factors) >= 2

def test_risk_level_boundaries():
    assert risk_engine._determine_risk_level(85.0) == "Critical"
    assert risk_engine._determine_risk_level(65.0) == "High"
    assert risk_engine._determine_risk_level(45.0) == "Medium"
    assert risk_engine._determine_risk_level(25.0) == "Low"
    assert risk_engine._determine_risk_level(10.0) == "Very Low"
