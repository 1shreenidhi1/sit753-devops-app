from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to SIT753 DevOps CRUD API with Real Prometheus Monitoring!"}

def test_create_and_read_task():
    # Test Create (POST)
    post_response = client.post("/tasks/", json={"title": "Test DevOps Pipeline", "description": "HD Incoming"})
    assert post_response.status_code == 200
    data = post_response.json()
    assert data["title"] == "Test DevOps Pipeline"
    assert data["description"] == "HD Incoming"
    assert "id" in data
    
    # Test Read (GET)
    task_id = data["id"]
    get_response = client.get("/tasks/")
    assert get_response.status_code == 200
    assert any(task["id"] == task_id for task in get_response.json())
