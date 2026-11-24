"""
GUI / compatibility evidence capture (Member 1).

Starts PyTodo Pro on a throw-away database, seeds demo data (one task per
urgency label, a long title, a done task), then opens every page in a real
browser and saves screenshots named  <CFG>_<page>.png  into ./screenshots.

Usage (from the repo root):
    python 03_Special_Testing/GUI_Compatibility/capture_gui_evidence.py --browser chrome  --cfg CFG-01
    python 03_Special_Testing/GUI_Compatibility/capture_gui_evidence.py --browser firefox --cfg CFG-02
    python 03_Special_Testing/GUI_Compatibility/capture_gui_evidence.py --browser edge    --cfg CFG-03
    python 03_Special_Testing/GUI_Compatibility/capture_gui_evidence.py --browser chrome  --cfg CFG-04 --mobile
Add --show to watch the browser instead of running headless.

Screenshots are EVIDENCE for the compatibility matrix - you still have to
look at each one and record Pass/Fail against the GUI checklist.
"""
import argparse
import os
import sys
import tempfile
import threading
import time
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "app"))

import app as pytodo  # noqa: E402
from selenium import webdriver  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402


def start_server():
    from werkzeug.serving import make_server
    pytodo.DATABASE = os.path.join(tempfile.mkdtemp(), "gui.db")
    pytodo.init_db()
    srv = make_server("127.0.0.1", 0, pytodo.app, threaded=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_port}"


def seed(base):
    import requests
    s = requests.Session()
    s.post(f"{base}/api/register", json={"username": "gui_tester", "password": "password123"})
    t = date.today()
    for title, due, cat in [
        ("Submit STQA report", (t - timedelta(days=1)).isoformat(), 3),
        ("Group meeting", t.isoformat(), 1),
        ("Revise for quiz", (t + timedelta(days=2)).isoformat(), 3),
        ("Plan holiday", (t + timedelta(days=10)).isoformat(), 2),
        ("No deadline task", None, None),
        ("A very long task title to check wrapping " * 4, (t + timedelta(days=5)).isoformat(), 4),
    ]:
        s.post(f"{base}/api/tasks", json={"title": title, "due_date": due, "category_id": cat})
    done = s.post(f"{base}/api/tasks", json={"title": "Finished task"}).json()["id"]
    s.put(f"{base}/api/tasks/{done}", json={"done": True})


def make_driver(name, headless, mobile):
    if name == "chrome":
        o = webdriver.ChromeOptions()
        if mobile:
            o.add_experimental_option("mobileEmulation", {"deviceName": "Pixel 7"})
    elif name == "edge":
        o = webdriver.EdgeOptions()
    elif name == "firefox":
        o = webdriver.FirefoxOptions()
    else:
        raise SystemExit("browser must be chrome, edge or firefox")
    if headless:
        o.add_argument("--headless=new" if name != "firefox" else "-headless")
    if name != "firefox":
        o.add_argument("--no-sandbox")
    d = {"chrome": webdriver.Chrome, "edge": webdriver.Edge, "firefox": webdriver.Firefox}[name](options=o)
    if not mobile:
        d.set_window_size(1366, 900)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--browser", default="chrome")
    ap.add_argument("--cfg", default="CFG-01")
    ap.add_argument("--mobile", action="store_true")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()

    srv, base = start_server()
    seed(base)
    out = os.path.join(HERE, "screenshots")
    os.makedirs(out, exist_ok=True)
    d = make_driver(a.browser, not a.show, a.mobile)
    print("Browser:", d.capabilities.get("browserName"), d.capabilities.get("browserVersion"))

    def shot(name):
        time.sleep(0.4)
        path = os.path.join(out, f"{a.cfg}_{name}.png")
        d.save_screenshot(path)
        print("saved", os.path.relpath(path, ROOT))

    try:
        d.get(f"{base}/login"); shot("01_login")
        d.find_element(By.NAME, "username").send_keys("gui_tester")
        d.find_element(By.NAME, "password").send_keys("wrongpass1")
        d.find_element(By.CSS_SELECTOR, "button[type=submit]").click(); shot("02_login_error")
        d.get(f"{base}/register"); shot("03_register")
        d.find_element(By.NAME, "username").send_keys("ab")
        d.find_element(By.NAME, "password").send_keys("password123")
        d.find_element(By.CSS_SELECTOR, "button[type=submit]").click(); shot("04_register_error")
        d.get(f"{base}/login")
        d.find_element(By.NAME, "username").send_keys("gui_tester")
        d.find_element(By.NAME, "password").send_keys("password123")
        d.find_element(By.CSS_SELECTOR, "button[type=submit]").click(); shot("05_task_list")
        d.get(f"{base}/?status=open&category=Study"); shot("06_task_list_filtered")
        d.get(f"{base}/?q=zzzz"); shot("07_task_list_empty")
        d.get(f"{base}/tasks/new"); shot("08_new_task_form")
        d.get(f"{base}/tasks/1/edit"); shot("09_edit_task_form")
        d.get(f"{base}/dashboard"); shot("10_dashboard")
    finally:
        d.quit()
        srv.shutdown()


if __name__ == "__main__":
    main()
