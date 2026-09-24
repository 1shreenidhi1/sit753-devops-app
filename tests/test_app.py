from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "cpu_usage_percent" in response.json()
