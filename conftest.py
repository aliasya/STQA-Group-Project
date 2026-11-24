"""
Shared PyTest fixtures for the PyTodo Pro QA repository.

Every test gets a FRESH, EMPTY SQLite database in a temp folder, so tests
never touch the real app/pytodo_pro.db and never depend on each other.
"""
import os
import socket
import sys
import threading

import pytest

ROOT = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(ROOT, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

import app as pytodo  # noqa: E402  (the application under test)

DEFAULT_PASSWORD = "password123"


def register(client, username, password=DEFAULT_PASSWORD):
    """Register through the API; the session cookie keeps the client logged in."""
    return client.post("/api/register", json={"username": username, "password": password})


@pytest.fixture
def app_module(tmp_path, monkeypatch):
    monkeypatch.setattr(pytodo, "DATABASE", str(tmp_path / "test.db"))
    # Behave like the real server: unhandled errors become HTTP 500 responses
    # (instead of being re-raised inside the test), so testers see what users see.
    pytodo.app.config["PROPAGATE_EXCEPTIONS"] = False
    pytodo.init_db()
    return pytodo


@pytest.fixture
def client(app_module):
    """Logged-out test client."""
    return app_module.app.test_client()


@pytest.fixture
def auth_client(app_module):
    """Test client already logged in as 'alice'."""
    c = app_module.app.test_client()
    assert register(c, "alice").status_code == 201
    return c


@pytest.fixture
def second_client(app_module):
    """A second, independent user ('mallory') for access-control tests."""
    c = app_module.app.test_client()
    assert register(c, "mallory").status_code == 201
    return c


# ---------------------------------------------------------------------------
# Live server (for Selenium UI tests and performance scripts)
# ---------------------------------------------------------------------------
def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture(scope="session")
def live_server(tmp_path_factory):
    from werkzeug.serving import make_server

    pytodo.DATABASE = str(tmp_path_factory.mktemp("live") / "live.db")
    pytodo.init_db()
    port = _free_port()
    server = make_server("127.0.0.1", port, pytodo.app, threaded=True)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


@pytest.fixture(scope="session")
def browser():
    """Headless Chrome. Set HEADLESS=0 to watch the browser during the live demo."""
    selenium = pytest.importorskip("selenium")
    from selenium import webdriver

    opts = webdriver.ChromeOptions()
    if os.environ.get("HEADLESS", "1") != "0":
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1366,900")
    try:
        driver = webdriver.Chrome(options=opts)
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"Chrome/WebDriver not available: {exc}")
    yield driver
    driver.quit()
