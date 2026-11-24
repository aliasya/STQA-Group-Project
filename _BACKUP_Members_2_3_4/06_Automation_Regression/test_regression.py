"""
Week 6 - Focused regression suite (BACKUP for Member 3)

Selected from the manual / earlier tests because they are REPEATED after every
change, STABLE (deterministic, no timing), CRITICAL (login, CRUD, access
control, urgency) and have high REGRESSION VALUE. See Automation_Report.md
for the manual-to-automated traceability table.

Known open defects are marked xfail(strict=True) with their DEF-ID:
  * while the defect is open the suite stays GREEN (xfail) - usable in CI;
  * when a developer fixes it, the test XPASSes, strict mode turns that into
    a FAILURE, telling QA to retest and close the defect and remove the marker.

Run:  pytest -m regression -v
"""
from datetime import date, timedelta

import pytest

from conftest import register

pytestmark = pytest.mark.regression
D = lambda n: (date.today() + timedelta(days=n)).isoformat()  # noqa: E731


def known_defect(def_id, reason):
    return pytest.mark.xfail(strict=True, reason=f"{def_id}: {reason}")


# --- Authentication (manual TC-BB-001, 012, 013, 032) ------------------------
def test_REG_001_register_and_login(client, app_module):            # TC-BB-001 / TC-BB-012
    assert register(client, "reg_user").status_code == 201
    c2 = app_module.app.test_client()
    assert c2.post("/api/login", json={"username": "reg_user", "password": "password123"}).status_code == 200


def test_REG_002_wrong_password_rejected(client, app_module):       # TC-BB-013
    register(app_module.app.test_client(), "reg_user")
    assert client.post("/api/login", json={"username": "reg_user", "password": "nopenope1"}).status_code == 401


def test_REG_003_logout_ends_session(auth_client):                  # TC-BB-032
    auth_client.get("/logout")
    assert auth_client.get("/api/tasks").status_code == 401


@known_defect("DEF-012", "password of exactly 8 characters rejected")
def test_REG_004_password_min_length_boundary(client):               # TC-BB-009
    assert register(client, "reg_user", "a" * 8).status_code == 201


@known_defect("DEF-008", "duplicate usernames accepted")
def test_REG_005_duplicate_username_rejected(client, app_module):    # TC-BB-011
    register(app_module.app.test_client(), "reg_user")
    assert register(client, "reg_user").status_code in (400, 409)


# --- Task CRUD (TC-BB-015, 029, 030, 034; TC-API-014, 031, 036) ---------------
def test_REG_006_create_read_update_delete(auth_client):
    tid = auth_client.post("/api/tasks", json={"title": "crud", "category_id": 1}).get_json()["id"]
    assert auth_client.get(f"/api/tasks/{tid}").get_json()["category"] == "Work"
    assert auth_client.put(f"/api/tasks/{tid}", json={"title": "crud2"}).get_json()["title"] == "crud2"
    auth_client.delete(f"/api/tasks/{tid}")
    assert auth_client.get(f"/api/tasks/{tid}").status_code == 404


def test_REG_007_toggle_done_and_reopen(auth_client):
    tid = auth_client.post("/api/tasks", json={"title": "t"}).get_json()["id"]
    auth_client.post(f"/tasks/{tid}/toggle")
    assert auth_client.get(f"/api/tasks/{tid}").get_json()["urgency"] == "Done"
    auth_client.post(f"/tasks/{tid}/toggle")
    assert auth_client.get(f"/api/tasks/{tid}").get_json()["done"] is False


def test_REG_008_blank_title_rejected_by_api(auth_client):           # TC-API-018
    assert auth_client.post("/api/tasks", json={"title": "  "}).status_code == 400


@known_defect("DEF-014", "web form accepts whitespace-only title")
def test_REG_009_blank_title_rejected_by_web_form(auth_client):      # TC-BB-016
    auth_client.post("/tasks/new", data={"title": "   "})
    assert auth_client.get("/api/tasks").get_json() == []


# --- Urgency rules (TC-BB-018..023, TC-WB-001..007) ---------------------------
@pytest.mark.parametrize("offset, label", [(-1, "Overdue"), (1, "Due Soon"), (2, "Due Soon"),
                                           (3, "Upcoming"), (None, "No due date")])
def test_REG_010_urgency_labels(auth_client, offset, label):
    due = None if offset is None else D(offset)
    assert auth_client.post("/api/tasks", json={"title": "u", "due_date": due}).get_json()["urgency"] == label


@known_defect("DEF-013", "task due today labelled Overdue")
def test_REG_011_urgency_due_today(auth_client):                      # TC-BB-019
    assert auth_client.post("/api/tasks", json={"title": "u", "due_date": D(0)}).get_json()["urgency"] == "Due Today"


# --- Filters (TC-BB-024..028) -------------------------------------------------
def test_REG_012_filters(auth_client):
    auth_client.post("/api/tasks", json={"title": "Alpha", "category_id": 3})
    auth_client.post("/api/tasks", json={"title": "Beta", "category_id": 1})
    assert [t["title"] for t in auth_client.get("/api/tasks?category=Study").get_json()] == ["Alpha"]
    assert [t["title"] for t in auth_client.get("/api/tasks?q=bet").get_json()] == ["Beta"]


# --- Access control / security (TC-SEC-005, 007, 009, 016) --------------------
def test_REG_013_cannot_read_or_edit_other_users_task(auth_client, second_client):
    tid = auth_client.post("/api/tasks", json={"title": "mine"}).get_json()["id"]
    assert second_client.get(f"/api/tasks/{tid}").status_code == 404
    assert second_client.put(f"/api/tasks/{tid}", json={"title": "x"}).status_code == 404


@known_defect("DEF-003", "API DELETE not scoped to owner")
def test_REG_014_cannot_delete_other_users_task(auth_client, second_client):
    tid = auth_client.post("/api/tasks", json={"title": "mine"}).get_json()["id"]
    second_client.delete(f"/api/tasks/{tid}")
    assert auth_client.get(f"/api/tasks/{tid}").status_code == 200


@known_defect("DEF-001", "search parameter concatenated into SQL")
def test_REG_015_search_is_injection_safe(auth_client, second_client):
    auth_client.post("/api/tasks", json={"title": "secret"})
    r = second_client.get("/api/tasks", query_string={"q": "%' OR 1=1 OR title LIKE '"})
    assert r.status_code == 200 and r.get_json() == []


@known_defect("DEF-002", "task title rendered with |safe")
def test_REG_016_title_is_escaped(auth_client):
    auth_client.post("/api/tasks", json={"title": "<b>x</b>"})
    assert "<b>x</b>" not in auth_client.get("/").get_data(as_text=True)


@known_defect("DEF-009", "malformed due date causes HTTP 500")
def test_REG_017_invalid_due_date_rejected(auth_client):
    assert auth_client.post("/api/tasks", json={"title": "x", "due_date": "2026-02-30"}).status_code == 400


def test_REG_018_protected_routes_require_login(client):
    assert client.get("/").status_code == 302 and client.get("/api/tasks").status_code == 401


# --- Dashboard (TC-API-040) --------------------------------------------------
def test_REG_019_dashboard_counts(auth_client):
    auth_client.post("/api/tasks", json={"title": "a", "due_date": D(-2)})
    auth_client.post("/api/tasks", json={"title": "b", "due_date": D(1)})
    d = auth_client.get("/api/dashboard").get_json()
    assert (d["total"], d["open"], d["overdue"], d["due_soon"]) == (2, 2, 1, 1)
