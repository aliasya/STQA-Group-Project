"""
Week 4 - REST API test suite (BACKUP for Member 3)

Valid requests, invalid/missing data, wrong types, edge conditions,
HTTP status codes and response content, plus UI-vs-API comparisons.
Expected results follow the README spec and normal REST conventions
(400 bad input, 401 not logged in, 404 not found, 201 created).

Run:  pytest _BACKUP_Members_2_3_4/04_Web_API -v
"""
import pytest

from conftest import register

TASK_KEYS = {"id", "title", "description", "category_id", "category", "due_date",
             "done", "urgency", "completed_at", "created_at"}


# ---------------- /api/register, /api/login ---------------------------------
def test_TC_API_001_register_valid(client):
    r = register(client, "api_user")
    assert r.status_code == 201 and r.get_json()["username"] == "api_user" and "id" in r.get_json()


@pytest.mark.parametrize("tc_id, body", [
    ("TC-API-002", {"password": "password123"}),                        # missing username
    ("TC-API-003", {"username": "api_user"}),                           # missing password
    ("TC-API-004", {"username": "ab", "password": "password123"}),      # username too short
    ("TC-API-005", {"username": "api_user", "password": "short"}),      # password too short
    ("TC-API-006", {}),                                                 # empty body
])
def test_register_invalid_returns_400(client, tc_id, body):
    r = client.post("/api/register", json=body)
    assert r.status_code == 400 and "error" in r.get_json()


def test_TC_API_007_register_password_exactly_8(client):
    """DEF-012"""
    assert register(client, "api_user", "abcdefgh").status_code == 201


def test_TC_API_008_register_duplicate_username(client, app_module):
    """DEF-008"""
    register(app_module.app.test_client(), "api_user")
    assert register(client, "api_user", "anotherpw1").status_code in (400, 409)


def test_TC_API_009_login_valid(client, app_module):
    register(app_module.app.test_client(), "api_user")
    r = client.post("/api/login", json={"username": "api_user", "password": "password123"})
    assert r.status_code == 200 and r.get_json()["username"] == "api_user"


def test_TC_API_010_login_wrong_password(client, app_module):
    register(app_module.app.test_client(), "api_user")
    r = client.post("/api/login", json={"username": "api_user", "password": "wrongpass1"})
    assert r.status_code == 401 and r.get_json() == {"error": "invalid credentials"}


def test_TC_API_011_login_non_json_body(client):
    """Malformed request should be 400, not 401 - observation (body ignored, treated as bad creds)."""
    assert client.post("/api/login", data="not json").status_code in (400, 401)


# ---------------- auth on protected endpoints --------------------------------
@pytest.mark.parametrize("method, path", [("get", "/api/tasks"), ("post", "/api/tasks"),
                                          ("get", "/api/tasks/1"), ("put", "/api/tasks/1"),
                                          ("delete", "/api/tasks/1"), ("get", "/api/dashboard")])
def test_TC_API_012_protected_endpoints_require_login(client, method, path):
    r = getattr(client, method)(path)
    assert r.status_code == 401 and r.get_json() == {"error": "authentication required"}


def test_TC_API_013_categories_seeded(client):
    names = [c["name"] for c in client.get("/api/categories").get_json()]
    assert names == ["Personal", "Study", "Urgent", "Work"]


# ---------------- POST /api/tasks ------------------------------------------
def test_TC_API_014_create_task_full(auth_client):
    r = auth_client.post("/api/tasks", json={"title": "Write report", "description": "STQA",
                                             "category_id": 3, "due_date": "2999-01-01"})
    body = r.get_json()
    assert r.status_code == 201
    assert set(body) == TASK_KEYS
    assert body["category"] == "Study" and body["urgency"] == "Upcoming" and body["done"] is False


def test_TC_API_015_create_task_title_only(auth_client):
    r = auth_client.post("/api/tasks", json={"title": "Minimal"})
    assert r.status_code == 201 and r.get_json()["urgency"] == "No due date"


@pytest.mark.parametrize("tc_id, body", [("TC-API-016", {}), ("TC-API-017", {"title": ""}),
                                         ("TC-API-018", {"title": "   "})])
def test_create_task_missing_title_400(auth_client, tc_id, body):
    r = auth_client.post("/api/tasks", json=body)
    assert r.status_code == 400 and r.get_json() == {"error": "title is required"}


def test_TC_API_019_create_task_title_wrong_type(auth_client):
    """DEF-016: integer title -> AttributeError -> HTTP 500."""
    assert auth_client.post("/api/tasks", json={"title": 123}).status_code == 400


def test_TC_API_020_create_task_invalid_date(auth_client):
    """DEF-009: impossible date is stored, then every read of the task crashes."""
    r = auth_client.post("/api/tasks", json={"title": "x", "due_date": "2026-13-45"})
    assert r.status_code == 400
    assert auth_client.get("/api/tasks").status_code == 200, "task list is broken after bad date"


def test_TC_API_021_create_task_unknown_category(auth_client):
    """DEF-019"""
    assert auth_client.post("/api/tasks", json={"title": "x", "category_id": 999}).status_code == 400


# ---------------- GET /api/tasks (list, filters, paging) ---------------------
@pytest.fixture
def seeded(auth_client):
    for i in range(12):
        auth_client.post("/api/tasks", json={"title": f"Task {i:02d}", "category_id": 1 if i % 2 else 3})
    auth_client.put("/api/tasks/1", json={"done": True})
    return auth_client


def test_TC_API_022_list_default_page_size(seeded):
    data = seeded.get("/api/tasks").get_json()
    assert len(data) == 10 and data[0]["title"] == "Task 11"   # newest first


def test_TC_API_023_list_second_page(seeded):
    assert [t["title"] for t in seeded.get("/api/tasks?page=1").get_json()] == ["Task 01", "Task 00"]


def test_TC_API_024_list_filters(seeded):
    assert {t["category"] for t in seeded.get("/api/tasks?category=Work&per_page=50").get_json()} == {"Work"}
    assert [t["id"] for t in seeded.get("/api/tasks?status=done").get_json()] == [1]
    assert [t["title"] for t in seeded.get("/api/tasks?q=Task 05").get_json()] == ["Task 05"]


@pytest.mark.parametrize("tc_id, qs", [("TC-API-025", "per_page=-1"), ("TC-API-026", "per_page=0"),
                                       ("TC-API-027", "page=-1")])
def test_paging_parameters_validated(seeded, tc_id, qs):
    """DEF-020: invalid paging values are silently accepted (per_page=-1 returns ALL rows)."""
    assert seeded.get(f"/api/tasks?{qs}").status_code == 400


def test_TC_API_028_search_with_apostrophe(seeded):
    """DEF-001: 'Alia's' -> SQL syntax error -> 500."""
    assert seeded.get("/api/tasks", query_string={"q": "Alia's"}).status_code == 200


# ---------------- GET/PUT/DELETE /api/tasks/<id> -----------------------------
def test_TC_API_029_get_task(auth_client):
    tid = auth_client.post("/api/tasks", json={"title": "x"}).get_json()["id"]
    assert auth_client.get(f"/api/tasks/{tid}").get_json()["title"] == "x"


def test_TC_API_030_get_missing_task_404(auth_client):
    assert auth_client.get("/api/tasks/9999").status_code == 404


def test_TC_API_031_put_partial_update(auth_client):
    tid = auth_client.post("/api/tasks", json={"title": "x", "description": "keep"}).get_json()["id"]
    body = auth_client.put(f"/api/tasks/{tid}", json={"title": "y"}).get_json()
    assert body["title"] == "y" and body["description"] == "keep"


def test_TC_API_032_put_mark_done_sets_completed_at(auth_client):
    tid = auth_client.post("/api/tasks", json={"title": "x"}).get_json()["id"]
    body = auth_client.put(f"/api/tasks/{tid}", json={"done": True}).get_json()
    assert body["done"] is True and body["urgency"] == "Done" and body["completed_at"]
    body = auth_client.put(f"/api/tasks/{tid}", json={"done": False}).get_json()
    assert body["done"] is False and body["completed_at"] is None


def test_TC_API_033_put_empty_title_rejected(auth_client):
    """DEF-017: POST rejects empty title but PUT accepts it."""
    tid = auth_client.post("/api/tasks", json={"title": "x"}).get_json()["id"]
    assert auth_client.put(f"/api/tasks/{tid}", json={"title": ""}).status_code == 400


def test_TC_API_034_put_done_as_string_false(auth_client):
    """DEF-017: {"done": "false"} is truthy in Python -> task marked done."""
    tid = auth_client.post("/api/tasks", json={"title": "x"}).get_json()["id"]
    r = auth_client.put(f"/api/tasks/{tid}", json={"done": "false"})
    assert r.status_code == 400 or r.get_json()["done"] is False


def test_TC_API_035_put_missing_task_404(auth_client):
    assert auth_client.put("/api/tasks/9999", json={"title": "y"}).status_code == 404


def test_TC_API_036_delete_own_task(auth_client):
    tid = auth_client.post("/api/tasks", json={"title": "x"}).get_json()["id"]
    assert auth_client.delete(f"/api/tasks/{tid}").get_json() == {"result": "ok"}
    assert auth_client.get(f"/api/tasks/{tid}").status_code == 404


def test_TC_API_037_delete_missing_task_404(auth_client):
    """DEF-018: deleting a non-existent id still returns 200 {"result":"ok"}."""
    assert auth_client.delete("/api/tasks/9999").status_code == 404


def test_TC_API_038_cannot_read_other_users_task(auth_client, second_client):
    tid = auth_client.post("/api/tasks", json={"title": "x"}).get_json()["id"]
    assert second_client.get(f"/api/tasks/{tid}").status_code == 404


def test_TC_API_039_cannot_delete_other_users_task(auth_client, second_client):
    """DEF-003 (IDOR) - GET is scoped to the owner but DELETE is not."""
    tid = auth_client.post("/api/tasks", json={"title": "x"}).get_json()["id"]
    second_client.delete(f"/api/tasks/{tid}")
    assert auth_client.get(f"/api/tasks/{tid}").status_code == 200


# ---------------- /api/dashboard --------------------------------------------
def test_TC_API_040_dashboard_counts(auth_client):
    from datetime import date, timedelta
    d = lambda n: (date.today() + timedelta(days=n)).isoformat()  # noqa: E731
    for n in (-3, 1, 10):
        auth_client.post("/api/tasks", json={"title": f"t{n}", "due_date": d(n)})
    tid = auth_client.post("/api/tasks", json={"title": "done"}).get_json()["id"]
    auth_client.put(f"/api/tasks/{tid}", json={"done": True})
    assert auth_client.get("/api/dashboard").get_json() == {
        "total": 4, "open": 3, "overdue": 1, "due_soon": 1, "completed_this_week": 1}


# ---------------- UI vs API comparison ----------------------------------------
def test_TC_API_041_ui_and_api_apply_same_title_rule(auth_client):
    """Web form accepts a blank title (DEF-014) but the API rejects it -> inconsistent server-side validation."""
    api = auth_client.post("/api/tasks", json={"title": "   "}).status_code
    auth_client.post("/tasks/new", data={"title": "   "})
    ui_created = any(t["title"] == "" for t in auth_client.get("/api/tasks").get_json())
    assert api == 400 and not ui_created


def test_TC_API_042_ui_and_api_same_urgency(auth_client):
    from datetime import date, timedelta
    due = (date.today() + timedelta(days=1)).isoformat()
    body = auth_client.post("/api/tasks", json={"title": "cmp", "due_date": due}).get_json()
    assert body["urgency"] in auth_client.get("/").get_data(as_text=True)
