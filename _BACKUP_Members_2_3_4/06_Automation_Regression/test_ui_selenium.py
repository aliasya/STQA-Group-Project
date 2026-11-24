"""
Week 6 - Selenium UI automation (BACKUP for Member 3)

End-to-end browser flows for the most important user journeys. Uses a live
server on a throw-away DB (see conftest.live_server) and headless Chrome.
Set HEADLESS=0 to watch it in the live demo:
    HEADLESS=0 pytest _BACKUP_Members_2_3_4/06_Automation_Regression/test_ui_selenium.py -v      (macOS/Linux)
    set HEADLESS=0 && pytest _BACKUP_Members_2_3_4/06_Automation_Regression/test_ui_selenium.py -v (Windows cmd)
"""
import uuid

import pytest

pytestmark = [pytest.mark.ui, pytest.mark.regression]


def _by():
    from selenium.webdriver.common.by import By
    return By


@pytest.fixture(autouse=True)
def fresh_session(browser):
    """Each UI test starts logged out (independent tests)."""
    browser.delete_all_cookies()
    yield


def submit(browser, element):
    """Click something that loads a new page and WAIT until the new page is there
    (avoids flaky tests that read the old page)."""
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    old = browser.find_element(_by().TAG_NAME, "html")
    element.click()
    WebDriverWait(browser, 10).until(EC.staleness_of(old))


def signup(browser, base):
    By = _by()
    user = "ui_" + uuid.uuid4().hex[:8]
    browser.get(f"{base}/register")
    browser.find_element(By.NAME, "username").send_keys(user)
    browser.find_element(By.NAME, "password").send_keys("password123")
    submit(browser, browser.find_element(By.CSS_SELECTOR, "button[type=submit]"))
    return user


def test_UI_001_register_lands_on_task_list(browser, live_server):      # TC-BB-001
    user = signup(browser, live_server)
    assert "My Tasks" in browser.page_source and user in browser.page_source


def test_UI_002_invalid_login_shows_error(browser, live_server):       # TC-BB-013
    By = _by()
    browser.get(f"{live_server}/login")
    browser.find_element(By.NAME, "username").send_keys("nobody_here")
    browser.find_element(By.NAME, "password").send_keys("wrongpass1")
    submit(browser, browser.find_element(By.CSS_SELECTOR, "button[type=submit]"))
    assert browser.find_element(By.CLASS_NAME, "error").text == "Invalid username or password."


def test_UI_003_create_toggle_delete_task(browser, live_server):        # TC-BB-015, 029, 030
    By = _by()
    signup(browser, live_server)
    submit(browser, browser.find_element(By.LINK_TEXT, "+ New Task"))
    browser.find_element(By.NAME, "title").send_keys("Selenium task")
    submit(browser, browser.find_element(By.CSS_SELECTOR, "button[type=submit]"))
    assert "Selenium task" in browser.find_element(By.CLASS_NAME, "task-table").text

    submit(browser, browser.find_element(By.CLASS_NAME, "check-btn"))
    assert "done" in browser.find_element(By.CSS_SELECTOR, "tbody tr").get_attribute("class")

    browser.execute_script("window.confirm = () => true;")   # auto-accept the delete dialog
    submit(browser, browser.find_element(By.CLASS_NAME, "link-btn"))
    assert "No tasks match your filters." in browser.page_source


def test_UI_004_filter_by_status(browser, live_server):                 # TC-BB-026
    By = _by()
    signup(browser, live_server)
    for t in ("Open one", "Closed one"):
        browser.get(f"{live_server}/tasks/new")
        browser.find_element(By.NAME, "title").send_keys(t)
        submit(browser, browser.find_element(By.CSS_SELECTOR, "button[type=submit]"))
    submit(browser, browser.find_elements(By.CLASS_NAME, "check-btn")[0])   # newest first -> "Closed one"
    browser.get(f"{live_server}/?status=open")                              # same URL the status dropdown submits
    table = browser.find_element(By.CLASS_NAME, "task-table").text
    assert "Open one" in table and "Closed one" not in table


def test_UI_005_logged_out_user_redirected(browser, live_server):       # TC-BB-032
    browser.get(f"{live_server}/dashboard")
    assert browser.current_url.endswith("/login")
