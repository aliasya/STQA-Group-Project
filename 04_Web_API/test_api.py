"""Reconstructed from the Member 3 testing walkthrough; compare with original local test_api.py."""
import pytest
import app as pytodo


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Isolated test database: does not use the user's normal PyTodo database.
    test_db = tmp_path / "pytodo_test.db"
    monkeypatch.setattr(pytodo, "DATABASE", str(test_db))
    pytodo.app.config["TESTING"] = True
    pytodo.init_db()
    # Do not keep a test-client context open while creating a second client.
    test_client = pytodo.app.test_client()
    yield test_client


def test_unauthorized_task_access(client):
    response = client.get("/api/tasks")
    assert response.status_code == 401
    assert response.get_json() == {"error": "authentication required"}


def test_registration_missing_data(client):
    response = client.post("/api/register", json={})
    assert response.status_code == 400
    assert response.get_json() == {"error": "invalid username"}


def test_valid_registration(client):
    response = client.post("/api/register", json={"username": "automated_user", "password": "Password123"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["username"] == "automated_user"
    assert "id" in data


def test_valid_login(client):
    client.post("/api/register", json={"username": "login_test_user", "password": "Password123"})
    response = client.post("/api/login", json={"username": "login_test_user", "password": "Password123"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["username"] == "login_test_user"
    assert "id" in data


def test_create_task(client):
    client.post("/api/register", json={"username": "task_test_user", "password": "Password123"})
    client.post("/api/login", json={"username": "task_test_user", "password": "Password123"})
    response = client.post("/api/tasks", json={"title": "Automated Test Task", "description": "Testing task creation"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Automated Test Task"
    assert data["description"] == "Testing task creation"
    assert data["done"] is False
    assert "id" in data


def test_get_created_task(client):
    client.post("/api/register", json={"username": "retrieve_test_user", "password": "Password123"})
    client.post("/api/login", json={"username": "retrieve_test_user", "password": "Password123"})
    create_response = client.post("/api/tasks", json={"title": "Retrieve Test Task", "description": "Testing task retrieval"})
    assert create_response.status_code == 201
    task_id = create_response.get_json()["id"]
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == task_id
    assert data["title"] == "Retrieve Test Task"
    assert data["description"] == "Testing task retrieval"
    assert data["done"] is False


def test_update_task(client):
    client.post("/api/register", json={"username": "update_test_user", "password": "Password123"})
    client.post("/api/login", json={"username": "update_test_user", "password": "Password123"})
    create_response = client.post("/api/tasks", json={"title": "Original Task", "description": "Original description"})
    assert create_response.status_code == 201
    task_id = create_response.get_json()["id"]
    response = client.put(f"/api/tasks/{task_id}", json={"title": "Updated Task", "description": "Updated description"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == task_id
    assert data["title"] == "Updated Task"
    assert data["description"] == "Updated description"
    assert data["done"] is False
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 200
    assert get_response.get_json()["title"] == "Updated Task"


def test_complete_task(client):
    client.post("/api/register", json={"username": "complete_test_user", "password": "Password123"})
    client.post("/api/login", json={"username": "complete_test_user", "password": "Password123"})
    create_response = client.post("/api/tasks", json={"title": "Completion Test Task", "description": "Testing task completion"})
    assert create_response.status_code == 201
    task_id = create_response.get_json()["id"]
    response = client.put(f"/api/tasks/{task_id}", json={"done": True})
    assert response.status_code == 200
    data = response.get_json()
    assert data["done"] is True
    assert data["completed_at"] is not None
    assert data["urgency"] == "Done"
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 200
    assert get_response.get_json()["done"] is True


def test_delete_task(client):
    client.post("/api/register", json={"username": "delete_test_user", "password": "Password123"})
    client.post("/api/login", json={"username": "delete_test_user", "password": "Password123"})
    create_response = client.post("/api/tasks", json={"title": "Delete Test Task", "description": "Testing task deletion"})
    assert create_response.status_code == 201
    task_id = create_response.get_json()["id"]
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.get_json() == {"result": "ok"}
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 404
    assert get_response.get_json() == {"error": "not found"}


def test_unauthorized_task_deletion(client):
    client.post("/api/register", json={"username": "security_user_a", "password": "Password123"})
    client.post("/api/login", json={"username": "security_user_a", "password": "Password123"})
    create_response = client.post("/api/tasks", json={"title": "User A Private Task"})
    assert create_response.status_code == 201
    task_id = create_response.get_json()["id"]
    client_b = pytodo.app.test_client()
    client_b.post("/api/register", json={"username": "security_user_b", "password": "Password123"})
    client_b.post("/api/login", json={"username": "security_user_b", "password": "Password123"})
    delete_response = client_b.delete(f"/api/tasks/{task_id}")
    owner_response = client.get(f"/api/tasks/{task_id}")
    # Both assertions describe expected secure behavior (the current app fails).
    assert delete_response.status_code in (403, 404)
    assert owner_response.status_code == 200


def test_password_minimum_boundary(client):
    response = client.post("/api/register", json={"username": "boundary_user", "password": "Pass1234"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["username"] == "boundary_user"


def test_duplicate_username_registration(client):
    first_response = client.post("/api/register", json={"username": "duplicate_user", "password": "Password123"})
    assert first_response.status_code == 201
    second_response = client.post("/api/register", json={"username": "duplicate_user", "password": "AnotherPassword123"})
    assert second_response.status_code in (400, 409)


def test_invalid_login(client):
    register_response = client.post("/api/register", json={"username": "invalid_login_user", "password": "Password123"})
    assert register_response.status_code == 201
    response = client.post("/api/login", json={"username": "invalid_login_user", "password": "WrongPassword123"})
    assert response.status_code == 401
    assert response.get_json() == {"error": "invalid credentials"}


def test_create_task_without_title(client):
    client.post("/api/register", json={"username": "missing_title_user", "password": "Password123"})
    client.post("/api/login", json={"username": "missing_title_user", "password": "Password123"})
    response = client.post("/api/tasks", json={})
    assert response.status_code == 400
    assert response.get_json() == {"error": "title is required"}
