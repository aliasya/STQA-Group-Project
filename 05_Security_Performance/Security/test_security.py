"""
Week 5 - Security test cases (Member 1, QA/Test Lead)

Each test asserts the SECURE (expected) behaviour.
  PASS  -> the control works.
  FAIL  -> a security defect; the DEF-ID is in the docstring.

Scope: the local test instance only (temp database). No external targets,
no automated attack tools - this is controlled, course-appropriate testing.

Run:  pytest 05_Security_Performance/Security -v
"""
import pytest

from conftest import register

pytestmark = pytest.mark.security


# --- Spoofing -------------------------------------------------------------
def test_TC_SEC_001_wrong_password_is_rejected_with_generic_message(client, app_module):
    """Login with a wrong password must fail and not reveal whether the username exists."""
    register(app_module.app.test_client(), "victim")
    wrong_pw = client.post("/api/login", json={"username": "victim", "password": "wrongpass1"})
    no_user = client.post("/api/login", json={"username": "nobody", "password": "wrongpass1"})
    assert wrong_pw.status_code == 401 and no_user.status_code == 401
    assert wrong_pw.get_json() == no_user.get_json()  # same message -> no user enumeration


def test_TC_SEC_002_repeated_failed_logins_are_throttled(client, app_module):
    """DEF-006: 20 wrong passwords in a row should trigger lockout / 429. App never throttles."""
    register(app_module.app.test_client(), "victim")
    codes = [client.post("/api/login", json={"username": "victim", "password": f"guess{i:04d}"}).status_code
             for i in range(20)]
    assert 429 in codes or codes[-1] == 423, f"no throttling, codes={set(codes)}"


def test_TC_SEC_003_session_is_invalid_after_logout(auth_client):
    """After logout the old session must not access protected data."""
    auth_client.get("/logout")
    assert auth_client.get("/api/tasks").status_code == 401


def test_TC_SEC_004_duplicate_username_cannot_be_registered(client, app_module):
    """DEF-008: registering an existing username must be refused (identity spoofing risk)."""
    register(app_module.app.test_client(), "alice")
    assert register(client, "alice", "differentpw1").status_code in (400, 409)


# --- Tampering ------------------------------------------------------------
def test_TC_SEC_005_user_cannot_delete_another_users_task(auth_client, second_client):
    """DEF-003 (IDOR): mallory deletes alice's task by guessing its id."""
    tid = auth_client.post("/api/tasks", json={"title": "alice private"}).get_json()["id"]
    second_client.delete(f"/api/tasks/{tid}")
    assert auth_client.get(f"/api/tasks/{tid}").status_code == 200, "alice's task was deleted by another user"


def test_TC_SEC_006_user_cannot_update_another_users_task(auth_client, second_client):
    tid = auth_client.post("/api/tasks", json={"title": "alice private"}).get_json()["id"]
    r = second_client.put(f"/api/tasks/{tid}", json={"title": "hacked"})
    assert r.status_code == 404
    assert auth_client.get(f"/api/tasks/{tid}").get_json()["title"] == "alice private"


def test_TC_SEC_007_search_parameter_is_not_sql_injectable(auth_client, second_client):
    """DEF-001: q is concatenated into SQL. Payload makes mallory see alice's tasks."""
    auth_client.post("/api/tasks", json={"title": "alice salary review"})
    r = second_client.get("/api/tasks", query_string={"q": "%' OR 1=1 OR title LIKE '"})
    titles = [t["title"] for t in (r.get_json() or [])] if r.status_code == 200 else []
    assert "alice salary review" not in titles, "SQL injection leaked another user's task"


def test_TC_SEC_008_single_quote_in_search_does_not_crash(auth_client):
    """DEF-001: a single quote (e.g. searching "Alia's") should be a normal search, not HTTP 500."""
    assert auth_client.get("/api/tasks", query_string={"q": "Alia's"}).status_code == 200


def test_TC_SEC_009_task_title_is_html_escaped(auth_client):
    """DEF-002 (stored XSS): template renders title with |safe."""
    payload = "<script>alert('xss')</script>"
    auth_client.post("/api/tasks", json={"title": payload})
    html = auth_client.get("/").get_data(as_text=True)
    assert payload not in html, "script tag rendered unescaped in task list"


def test_TC_SEC_010_state_changing_forms_have_csrf_token(auth_client):
    """DEF-004: forms that create/delete/toggle tasks carry no CSRF token."""
    auth_client.post("/api/tasks", json={"title": "t"})
    html = auth_client.get("/").get_data(as_text=True) + auth_client.get("/tasks/new").get_data(as_text=True)
    assert "csrf" in html.lower()


# --- Information disclosure ------------------------------------------------
def test_TC_SEC_011_passwords_are_stored_hashed(auth_client, app_module):
    import sqlite3
    row = sqlite3.connect(app_module.DATABASE).execute("SELECT password_hash FROM users").fetchone()
    assert row[0] != "password123" and row[0].startswith(("scrypt:", "pbkdf2:"))


def test_TC_SEC_012_session_cookie_is_httponly(client):
    r = register(client, "cookieuser")
    cookie = r.headers.get("Set-Cookie", "")
    assert "HttpOnly" in cookie


def test_TC_SEC_013_secret_key_not_hardcoded_and_debug_off():
    """DEF-005: SECRET_KEY is a constant in source and app.run(debug=True)."""
    import pathlib
    src = (pathlib.Path(__file__).resolve().parents[2] / "app" / "app.py").read_text()
    assert '"pytodo-pro-dev-secret"' not in src and "debug=True" not in src


def test_TC_SEC_014_errors_do_not_leak_internal_details(auth_client):
    """DEF-009: a malformed due date causes an unhandled exception (HTTP 500)."""
    r = auth_client.post("/api/tasks", json={"title": "x", "due_date": "2026-13-45"})
    assert r.status_code == 400


# --- Denial of service / Elevation ------------------------------------------
def test_TC_SEC_015_oversized_title_is_rejected(auth_client):
    """DEF-007: a 100,000-character title is accepted and stored."""
    r = auth_client.post("/api/tasks", json={"title": "A" * 100_000})
    assert r.status_code in (400, 413)


@pytest.mark.parametrize("path", ["/", "/dashboard", "/tasks/new"])
def test_TC_SEC_016_protected_pages_redirect_when_logged_out(client, path):
    r = client.get(path)
    assert r.status_code == 302 and "/login" in r.headers["Location"]


@pytest.mark.parametrize("method,path", [("get", "/api/tasks"), ("post", "/api/tasks"),
                                         ("get", "/api/dashboard"), ("delete", "/api/tasks/1")])
def test_TC_SEC_017_protected_api_requires_login(client, method, path):
    assert getattr(client, method)(path).status_code == 401
