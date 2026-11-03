"""
test_auth_and_api.py - Integration tests for FastAPI endpoints.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import hash_password, verify_password, create_access_token

client = TestClient(app)

def test_password_hashing():
    raw_pass = "Chandra@1234"
    hashed = hash_password(raw_pass)
    assert verify_password(raw_pass, hashed) == True
    assert verify_password("wrongpassword", hashed) == False

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert data["status"] == "running"

def test_jwt_token_generation():
    token = create_access_token({"sub": "test@example.com", "role": "user"})
    assert isinstance(token, str)
    assert len(token) > 20
