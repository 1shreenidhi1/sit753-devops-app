from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to SIT753 DevOps CRUD API with Real Prometheus Monitoring!"}

def test_complete_task_crud():
    # 1. Test Create (POST)
    post_response = client.post("/tasks/", json={"title": "Test DevOps Pipeline", "description": "HD Incoming"})
    assert post_response.status_code == 200
    data = post_response.json()
    assert data["title"] == "Test DevOps Pipeline"
    assert data["description"] == "HD Incoming"
    assert "id" in data
    
    task_id = data["id"]
    
    # 2. Test Read All (GET)
    get_response = client.get("/tasks/")
    assert get_response.status_code == 200
    assert any(task["id"] == task_id for task in get_response.json())

    # 3. Test Update (PUT)
    update_response = client.put(f"/tasks/{task_id}", json={"title": "Updated DevOps Pipeline", "description": "Pipeline Verified"})
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["title"] == "Updated DevOps Pipeline"
    assert updated_data["description"] == "Pipeline Verified"

    # 4. Test Delete (DELETE)
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code in [200, 204]
