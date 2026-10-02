from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the SIT753 DevOps Task API"}

def test_create_and_read_task():
    # Test Create (POST)
    post_response = client.post("/tasks/", json={"title": "Test DevOps Pipeline"})
    assert post_response.status_code == 200
    task_id = post_response.json()["id"]
    assert post_response.json()["title"] == "Test DevOps Pipeline"

    # Test Read (GET)
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Test DevOps Pipeline"

    # Test Delete (DELETE)
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200
