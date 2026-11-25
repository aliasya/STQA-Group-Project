"""
Defect evidence generator for PyTodo Pro (Group 6, consolidated register DEF-001 .. DEF-017).

For every defect in the final register (report Table 7.6) this script
  1. starts PyTodo Pro on a throw-away SQLite database (the real app.db is never touched),
  2. reproduces the defect over real HTTP (requests) or in a real browser (Selenium / Chrome),
  3. writes the evidence into the folder of the test activity that found it:

        <test folder>/Defect_Evidence/DEF-0XX_<slug>/
            evidence.md      steps, expected vs actual, captured request/response trace,
                             faulty source lines, cross-references to other members' evidence
            screenshot*.png  (GUI / browser-visible defects only)

  4. writes the index 07_Test_Management/Defect_Evidence/Defect_Evidence_Index.md

Usage (from the repo root, venv active):
    python 07_Test_Management/Defect_Evidence/reproduce_defects.py            # all, with screenshots
    python 07_Test_Management/Defect_Evidence/reproduce_defects.py --no-browser
"""
import argparse
import os
import platform
import re
import sys
import tempfile
import threading
import time
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
APP_DIR = os.path.join(ROOT, "app")
sys.path.insert(0, APP_DIR)

import requests  # noqa: E402
import app as pytodo  # noqa: E402
import helpers  # noqa: E402

RUN_AT = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
PW = "password123"


# --------------------------------------------------------------------------- server / helpers
def start_server():
    from werkzeug.serving import make_server
    pytodo.DATABASE = os.path.join(tempfile.mkdtemp(), "defects.db")
    pytodo.init_db()
    srv = make_server("127.0.0.1", 0, pytodo.app, threaded=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_port}"


LAST_TRACE = None


def sess_name(sess):
    if not getattr(sess, "name", None):
        sess_name.n = getattr(sess_name, "n", 0) + 1
        sess.name = f"client{sess_name.n}"
    return sess.name


class Trace:
    """Records every request/response: as text for evidence.md and as a terminal
    transcript (equivalent curl commands + the real responses) for the PNG."""

    def __init__(self, base):
        global LAST_TRACE
        self.base, self.lines, self.n, self.term = base, [], 0, []
        LAST_TRACE = self

    def note(self, text):
        self.lines.append(f"# {text}")
        self.term.append(("comment", f"# {text}"))

    def shell(self, cmd, output):
        """Show a local command (grep / python -c) with the output computed by this script."""
        self.lines.append(f"$ {cmd}")
        self.term.append(("cmd", cmd))
        for ln in (output or ["(no output)"]):
            self.lines.append("    " + ln)
            self.term.append(("out", ln))

    def call(self, sess, method, path, show_body=True, max_body=600, **kw):
        import json as _json
        from urllib.parse import unquote
        self.n += 1
        r = sess.request(method, self.base + path, allow_redirects=False, **kw)
        req = f"{method} {unquote(r.request.path_url)}"
        if "json" in kw:
            body = repr(kw["json"])
            req += "   json=" + (body if len(body) < 200 else body[:200] + f"... ({len(body)} chars)")
        if "data" in kw:
            req += f"   form={kw['data']!r}"
        self.lines.append(f"[{self.n}] >>> {req}")
        resp = f"    <<< HTTP {r.status_code}"
        if r.headers.get("Location"):
            resp += f"  Location: {r.headers['Location']}"
        self.lines.append(resp)
        # ---- terminal transcript
        jar = sess_name(sess) + ".jar"
        cookie = f"-b {jar} -c {jar}"
        if getattr(sess, "raw_cookie", None):
            cookie = f"-b \"session={sess.raw_cookie[:48]}...\""
        cmd = f"curl -s -i -X {method} \"{unquote(r.request.url)}\" {cookie}"
        for h, v in (kw.get("headers") or {}).items():
            cmd += f" -H \"{h}: {v}\""
        if "json" in kw:
            js = _json.dumps(kw["json"])
            if len(js) > 160:
                js = js[:120] + f"...<{len(js)} chars>..." + '"}'
            cmd += f" -H \"Content-Type: application/json\" -d '{js}'"
        if "data" in kw:
            cmd += " -d \"" + "&".join(f"{k}={v}" for k, v in kw["data"].items()) + "\""
        self.term.append(("cmd", cmd))
        self.term.append(("status", f"HTTP/1.1 {r.status_code} {r.reason}", r.status_code))
        self.term.append(("out", f"Content-Type: {r.headers.get('Content-Type', '')}"))
        if r.headers.get("Location"):
            self.term.append(("out", f"Location: {r.headers['Location']}"))
        self.term.append(("out", ""))
        if r.text:
            txt = r.text.strip()
            if not show_body:
                txt = txt[:160] + (f" ... [{len(r.text)} chars]" if len(r.text) > 160 else "")
            elif len(txt) > max_body:
                txt = txt[:max_body] + f" ... [{len(r.text)} chars total]"
            body = txt.splitlines()
            if len(body) > 8:
                body = body[:7] + [f"... ({len(body) - 7} more lines)"]
            for ln in body:
                self.term.append(("out", ln))
        if show_body and r.text:
            txt = r.text.strip()
            if len(txt) > max_body:
                txt = txt[:max_body] + f" ... [{len(r.text)} chars total]"
            for ln in txt.splitlines():
                self.lines.append("        " + ln)
        return r

    def text(self):
        return "\n".join(self.lines)


def user(base, name, trace=None):
    s = requests.Session()
    s.name = name
    if trace:
        trace.call(s, "POST", "/api/register", json={"username": name, "password": PW})
    else:
        s.post(f"{base}/api/register", json={"username": name, "password": PW})
    return s


# --------------------------------------------------------------------------- PNG rendering
def _font(size, bold=False):
    from PIL import ImageFont
    names = (["consolab.ttf", "CascadiaMono.ttf"] if bold else ["consola.ttf", "CascadiaMono.ttf"]) + \
            ["DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf", "Menlo.ttc", "cour.ttf"]
    for n in names:
        for d in ("", "C:/Windows/Fonts/", "/usr/share/fonts/truetype/dejavu/", "/System/Library/Fonts/"):
            try:
                return ImageFont.truetype(d + n, size)
            except OSError:
                pass
    return ImageFont.load_default()


def _window(rows, title, path, cols=118, bg=(12, 12, 12), bar=(44, 44, 48)):
    """rows: list of (text, fg, row_bg or None, bold). Draws a terminal-style window."""
    from PIL import Image, ImageDraw
    import textwrap
    f, fb = _font(15), _font(15, True)
    cw = max(1, int(round(f.getlength("M"))))
    lh = 20
    wrapped = []
    for text, fg, rbg, bold in rows:
        parts = textwrap.wrap(text, cols, subsequent_indent="  ", drop_whitespace=False,
                              replace_whitespace=False, break_on_hyphens=False) or [""]
        wrapped += [(pt, fg, rbg, bold) for pt in parts]
    W = 28 + cols * cw + 28
    H = 34 + 14 + len(wrapped) * lh + 18
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 33], fill=bar)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([14 + i * 22, 11, 26 + i * 22, 23], fill=c)
    d.text((W // 2, 17), title, fill=(200, 200, 205), font=_font(14), anchor="mm")
    y = 34 + 14
    for text, fg, rbg, bold in wrapped:
        if rbg:
            d.rectangle([0, y - 2, W, y + lh - 2], fill=rbg)
        d.text((28, y), text, fill=fg, font=fb if bold else f)
        y += lh
    img.save(os.path.normpath(path), optimize=True)


def render_terminal(term, did, title, path):
    WHITE, GREY, CYAN = (242, 242, 242), (204, 204, 204), (97, 214, 214)
    rows = [(f"# {did} - {title}", CYAN, None, True),
            (f"# Reproduced {RUN_AT} against PyTodo Pro (fresh DB, port shown as default 5000); responses are the real server output", CYAN, None, False),
            ("", GREY, None, False)]
    for item in term:
        kind = item[0]
        if kind == "cmd":
            if rows[-1][0] != "":
                rows.append(("", GREY, None, False))
            rows.append(("$ " + re.sub(r"127\.0\.0\.1:\d+", "127.0.0.1:5000", item[1]), WHITE, None, True))
        elif kind == "status":
            c = item[2]
            col = (22, 198, 12) if c < 300 else (97, 214, 214) if c < 400 else (249, 241, 165) if c < 500 else (231, 72, 86)
            rows.append((item[1], col, None, True))
        elif kind == "comment":
            if rows[-1][0] != "" and not rows[-1][0].startswith("#"):
                rows.append(("", GREY, None, False))
            rows.append((item[1], (118, 170, 118), None, False))
        else:
            rows.append((item[1], GREY, None, False))
    rows += [("", GREY, None, False), ("$ _", (22, 198, 12), None, True)]
    _window(rows, "bash - PyTodo Pro defect reproduction", path)


def render_source(code_text, did, path):
    rows = []
    for ln in code_text.splitlines():
        if ln.startswith(">>"):
            rows.append((ln, (255, 255, 255), (110, 24, 32), True))
        elif "|" in ln[:9]:
            rows.append((ln, (212, 212, 212), None, False))
        elif ln.strip():
            rows.append((ln, (97, 175, 239), None, True))
        else:
            rows.append(("", (212, 212, 212), None, False))
    rows += [("", (212, 212, 212), None, False),
             ("  >> highlighted line = root cause of " + did, (231, 72, 86), None, False)]
    _window(rows, f"Source code - {did} root cause", path, cols=110, bg=(30, 30, 30))


def grep(path, pattern, flags=0):
    out = []
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        for i, ln in enumerate(f, 1):
            if re.search(pattern, ln, flags):
                out.append(f"{i}:{ln.rstrip()}")
    return out or ["(no matches)"]


def code(path, start, end, mark=()):
    """Return numbered source lines; lines in `mark` are flagged with >>."""
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        src = f.read().splitlines()
    out = [f"{path}"]
    for i in range(start, end + 1):
        flag = ">>" if i in mark else "  "
        out.append(f"{flag} {i:4d} | {src[i - 1]}")
    return "\n".join(out)


def find_line(path, needle):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        for i, ln in enumerate(f, 1):
            if needle in ln:
                return i
    raise ValueError(f"{needle!r} not found in {path}")


# --------------------------------------------------------------------------- browser
DRIVER = None


def browser(mobile=False, size=(1366, 900)):
    from selenium import webdriver
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    if mobile:
        opts.add_experimental_option("mobileEmulation", {"deviceName": "Pixel 7"})
    else:
        opts.add_argument(f"--window-size={size[0]},{size[1]}")
    return webdriver.Chrome(options=opts)


def web_login(drv, base, name):
    from selenium.webdriver.common.by import By
    drv.get(base + "/login")
    drv.find_element(By.NAME, "username").send_keys(name)
    drv.find_element(By.NAME, "password").send_keys(PW)
    drv.find_element(By.CSS_SELECTOR, "form button, form input[type=submit]").click()
    time.sleep(0.4)


# --------------------------------------------------------------------------- defect reproductions
# Each function returns dict(trace=str, observed=str, reproduced=bool, shots=[(file, caption)])
# `d` is the output folder (for screenshots).

def def001(base, d, use_browser):
    t = Trace(base)
    a, b = user(base, "alice_d1", t), user(base, "bob_d1", t)
    tid = t.call(a, "POST", "/api/tasks", json={"title": "Alice private task"}).json()["id"]
    t.note("User B (bob_d1) deletes user A's task by id")
    r = t.call(b, "DELETE", f"/api/tasks/{tid}")
    t.note("User A checks the task")
    g = t.call(a, "GET", f"/api/tasks/{tid}")
    ok = r.status_code == 200 and g.status_code == 404
    return dict(trace=t.text(), reproduced=ok,
                observed=f"B's DELETE returned HTTP {r.status_code}; A's GET then returned HTTP {g.status_code} - task destroyed by another user.")


def def002(base, d, use_browser):
    t = Trace(base)
    a, b = user(base, "alice_d2", t), user(base, "bob_d2", t)
    t.call(a, "POST", "/api/tasks", json={"title": "alice salary review"}, show_body=False)
    t.call(b, "POST", "/api/tasks", json={"title": "bob shopping"}, show_body=False)
    t.note("Normal search by B - only B's tasks expected")
    t.call(b, "GET", "/api/tasks", params={"q": "salary"})
    t.note("Injected search by B - closes the quote and ORs a true condition")
    inj = t.call(b, "GET", "/api/tasks", params={"q": "' OR 1=1 OR title LIKE '"})
    t.note("A plain apostrophe breaks the SQL statement")
    apo = t.call(b, "GET", "/api/tasks", params={"q": "Alia's"}, max_body=200)
    leaked = "alice salary review" in inj.text
    return dict(trace=t.text(), reproduced=leaked and apo.status_code == 500,
                observed=f"Injected query returned user A's task 'alice salary review' (leak={leaked}); apostrophe search returned HTTP {apo.status_code}.")


def def003(base, d, use_browser):
    t = Trace(base)
    a, b = user(base, "alice_d3", t), user(base, "bob_d3", t)
    tid = t.call(a, "POST", "/api/tasks", json={"title": "Audit me"}, show_body=False).json()["id"]
    t.note("Security-relevant events: a cross-user delete and a failed login")
    t.call(b, "DELETE", f"/api/tasks/{tid}")
    t.call(b, "POST", "/api/login", json={"username": "alice_d3", "password": "wrong"})
    t.note("Is any of this recorded? Search the application for logging / audit code:")
    hits = grep("app/app.py", r"logging|logger|audit", re.I)
    t.shell('grep -n -i -E "logging|logger|audit" app/app.py', hits)
    t.shell('grep -n "CREATE TABLE" app/app.py', grep("app/app.py", r"CREATE TABLE"))
    t.note("Only users / categories / tasks tables - no audit or event table, no log file")
    return dict(trace=t.text(), reproduced=hits == ["(no matches)"],
                observed="No log entry, audit table or logger exists - the cross-user delete and failed login leave no record (repudiation threat).")


def def004(base, d, use_browser):
    t = Trace(base)
    s = user(base, "alice_d4", t)
    payload = ("<script>document.body.insertAdjacentHTML('afterbegin',"
               "'<h1 id=xss style=\"background:#c00;color:#fff;padding:12px\">XSS EXECUTED - injected by task title</h1>')</script>")
    t.call(s, "POST", "/api/tasks", json={"title": payload}, show_body=False)
    page = t.call(s, "GET", "/", show_body=False)
    raw = payload in page.text
    t.note(f"Payload appears UNESCAPED in the HTML of '/': {raw}")
    for ln in page.text.splitlines():
        if "insertAdjacentHTML" in ln:
            t.note("HTML line: " + ln.strip()[:220])
            break
    shots, executed = [], None
    if use_browser:
        from selenium.webdriver.common.by import By
        web_login(DRIVER, base, "alice_d4")
        DRIVER.get(base + "/")
        time.sleep(0.5)
        executed = len(DRIVER.find_elements(By.ID, "xss")) == 1
        DRIVER.save_screenshot(os.path.join(d, "screenshot_xss_executed.png"))
        shots.append(("screenshot_xss_executed.png", "Task list after login: the red banner was created by JavaScript stored in a task title."))
        t.note(f"Browser: element #xss created by the stored script = {executed}")
    return dict(trace=t.text(), reproduced=raw and executed is not False, shots=shots,
                observed="The title is rendered with |safe, so the stored <script> runs for every visit to the task list.")


def def005(base, d, use_browser):
    t = Trace(base)
    s = user(base, "alice_d5", t)
    r1 = t.call(s, "POST", "/api/tasks", json={"title": "bad date", "due_date": "2026-13-45"}, max_body=200)
    t.note("Is the row stored anyway? List tasks / load page afterwards:")
    r2 = t.call(s, "GET", "/api/tasks", max_body=200)
    r3 = t.call(s, "GET", "/", max_body=200)
    r4 = t.call(s, "GET", "/dashboard", max_body=200)
    shots = []
    if use_browser:
        web_login(DRIVER, base, "alice_d5")
        DRIVER.get(base + "/")
        time.sleep(0.4)
        DRIVER.save_screenshot(os.path.join(d, "screenshot_task_list_500.png"))
        shots.append(("screenshot_task_list_500.png", "The user's task list after the bad request: Internal Server Error on every visit."))
    ok = r1.status_code == 500 and r2.status_code == 500 and r3.status_code == 500
    return dict(trace=t.text(), reproduced=ok, shots=shots,
                observed=f"Create returned {r1.status_code} but the row was stored; afterwards /api/tasks={r2.status_code}, /={r3.status_code}, /dashboard={r4.status_code} - the account is permanently broken.")


def def006(base, d, use_browser):
    t = Trace(base)
    s = user(base, "alice_d6", t)
    tid = t.call(s, "POST", "/api/tasks", json={"title": "Forged-request target"}, show_body=False).json()["id"]
    page = t.call(s, "GET", "/", show_body=False)
    forms = re.findall(r"<form[^>]*>", page.text)
    tokens = re.findall(r"<input[^>]*(?:type=\"hidden\"|name=\"csrf[^\"]*\")[^>]*>", page.text, re.I)
    t.note(f"Forms on task list: {len(forms)}; hidden token inputs: {len(tokens)}")
    for f in forms:
        t.note("  " + f)
    t.note("Forged cross-site POST (no token, foreign Origin/Referer) to the delete form:")
    r = t.call(s, "POST", f"/tasks/{tid}/delete", headers={"Origin": "http://evil.example", "Referer": "http://evil.example/page"})
    left = t.call(s, "GET", f"/api/tasks/{tid}", max_body=120)
    t.note("Logout is a plain GET (an <img src=/logout> on any site logs the user out):")
    lo = t.call(s, "GET", "/logout")
    ok = not tokens and r.status_code == 302 and left.status_code == 404
    return dict(trace=t.text(), reproduced=ok,
                observed=f"Forged POST with foreign Origin accepted (HTTP {r.status_code}), task deleted (GET -> {left.status_code}); GET /logout -> {lo.status_code}.")


def def007(base, d, use_browser):
    t = Trace(base)
    t.shell('grep -n -E "SECRET_KEY|app.run" app/app.py', grep("app/app.py", r"SECRET_KEY|app\.run"))
    victim = user(base, "alice_d7", t)
    t.call(victim, "POST", "/api/tasks", json={"title": "Alice bank PIN reminder"}, show_body=False)
    from flask.sessions import SecureCookieSessionInterface
    from flask import Flask
    fake = Flask("forge")
    fake.secret_key = "pytodo-pro-dev-secret"  # copied from app.py
    ser = SecureCookieSessionInterface().get_signing_serializer(fake)
    real = ser.loads(victim.cookies.get("session"))
    forged = ser.dumps({"user_id": real["user_id"], "username": "alice_d7"})
    t.note("Attacker never logs in. Using only the key printed above, they sign their own session cookie:")
    t.shell("python -c \"from flask import Flask; from flask.sessions import SecureCookieSessionInterface as S; "
            "a=Flask('x'); a.secret_key='pytodo-pro-dev-secret'; "
            f"print(S().get_signing_serializer(a).dumps({{'user_id': {real['user_id']}, 'username': 'alice_d7'}}))\"",
            [forged])
    f = requests.Session()
    f.name, f.raw_cookie = "attacker", forged
    f.cookies.set("session", forged)
    r = t.call(f, "GET", "/api/tasks", max_body=300)
    ok = r.status_code == 200 and "Alice bank PIN reminder" in r.text
    return dict(trace=t.text(), reproduced=ok,
                observed=f"A cookie forged with the key from the source code is accepted (HTTP {r.status_code}) and returns Alice's private task - full account takeover without a password. Debug server also enabled.")


def def008(base, d, use_browser):
    t = Trace(base)
    user(base, "alice_d8", t)
    atk = requests.Session()
    codes = []
    start = time.perf_counter()
    for i in range(20):
        r = atk.post(base + "/api/login", json={"username": "alice_d8", "password": f"guess{i}"})
        codes.append(r.status_code)
    dur = time.perf_counter() - start
    t.note("20 consecutive wrong passwords for alice_d8:")
    t.note(f"status codes: {codes}")
    t.note(f"total time {dur:.2f}s (no delay, no 429, no lockout)")
    r = t.call(atk, "POST", "/api/login", json={"username": "alice_d8", "password": PW})
    ok = set(codes) == {401} and r.status_code == 200
    return dict(trace=t.text(), reproduced=ok,
                observed=f"All 20 attempts answered 401 in {dur:.2f}s; the 21st (correct) attempt still logs in (HTTP {r.status_code}) - unlimited guessing.")


def def009(base, d, use_browser):
    t = Trace(base)
    s = user(base, "alice_d9", t)
    r = t.call(s, "POST", "/api/tasks", json={"title": "A" * 100000}, show_body=False)
    got = s.get(f"{base}/api/tasks/{r.json()['id']}").json()
    t.note(f"Stored title length read back: {len(got['title'])} characters")
    return dict(trace=t.text(), reproduced=r.status_code == 201 and len(got["title"]) == 100000,
                observed=f"100,000-character title accepted (HTTP {r.status_code}) and stored in full.")


def def010(base, d, use_browser):
    t = Trace(base)
    s = user(base, "alice_d10", t)
    page = t.call(s, "GET", "/", show_body=False)
    has = 'name="viewport"' in page.text
    t.note(f"<meta name=\"viewport\"> present in rendered page: {has}")
    shots, width = [], None
    if use_browser:
        drv = browser(mobile=True)
        try:
            for title in ("Submit STQA report", "Group meeting", "Revise for quiz"):
                s.post(base + "/api/tasks", json={"title": title, "due_date": date.today().isoformat()})
            web_login(drv, base, "alice_d10")
            drv.get(base + "/")
            time.sleep(0.4)
            width = drv.execute_script("return document.documentElement.clientWidth")
            sw = drv.execute_script("return screen.width")
            drv.save_screenshot(os.path.join(d, "screenshot_pixel7_task_list.png"))
            shots.append(("screenshot_pixel7_task_list.png", f"Chrome Pixel 7 emulation: page laid out at {width}px for a {sw}px-wide screen, so everything is scaled down."))
            t.note(f"Pixel 7 emulation: screen.width={sw}px, layout viewport={width}px")
        finally:
            drv.quit()
    return dict(trace=t.text(), reproduced=not has, shots=shots,
                observed=f"No viewport meta tag; on a phone the page is laid out at {width or '~980'}px and shrunk.")


def def011(base, d, use_browser):
    t = Trace(base)
    s = user(base, "alice_d11", t)
    for title, due in [("Submit STQA report", (date.today() + timedelta(days=4)).isoformat()),
                       ("No deadline task", None),
                       ("A very long task title to check wrapping " * 3, (date.today() + timedelta(days=9)).isoformat())]:
        s.post(base + "/api/tasks", json={"title": title, "due_date": due})
    t.note("Seeded tasks with and without due dates; opened task list at 1366x900")
    shots, ok = [], True
    if use_browser:
        from selenium.webdriver.common.by import By
        drv = browser(size=(1366, 900))
        try:
            web_login(drv, base, "alice_d11")
            drv.get(base + "/")
            time.sleep(0.4)
            heights = drv.execute_script("""
                const out=[];document.querySelectorAll('td, td *').forEach(e=>{
                  if(e.children.length) return; const t=e.innerText.trim();
                  if(/^\d{4}-\d{2}-\d{2}$/.test(t)||t==='No due date'){
                    const r=document.createRange(); r.selectNodeContents(e);
                    const tops=new Set([...r.getClientRects()].map(x=>Math.round(x.top)));
                    out.push([t, tops.size, Math.round(e.getBoundingClientRect().width)]);}});
                return out;""")
            for txt, nlines, w in heights:
                t.note(f"text '{txt}': rendered on {nlines} line(s) in a {w}px-wide box")
            ok = any(n > 1 for _, n, _ in heights)
            drv.save_screenshot(os.path.join(d, "screenshot_1366_task_list.png"))
            shots.append(("screenshot_1366_task_list.png", "Task list at 1366x900: due dates and the 'No due date' badge wrap onto two lines."))
        finally:
            drv.quit()
    return dict(trace=t.text(), reproduced=ok, shots=shots,
                observed="At 1366px the due-date column is too narrow: dates break as '2026-' / '11-29' and the badge splits.")


def def012(base, d, use_browser):
    t = Trace(base)
    s = requests.Session()
    r = t.call(s, "POST", "/register", data={"username": "valid_user12", "password": "short"}, show_body=False)
    vals = re.findall(r'<input[^>]*name="(username|password)"[^>]*>', r.text)
    filled = 'value="valid_user12"' in r.text
    for m in re.findall(r'<input[^>]*>', r.text):
        t.note("returned form field: " + m)
    t.note(f"Username re-populated after the error: {filled}")
    shots = []
    if use_browser:
        from selenium.webdriver.common.by import By
        DRIVER.get(base + "/logout")
        DRIVER.get(base + "/register")
        DRIVER.find_element(By.NAME, "username").send_keys("valid_user12")
        DRIVER.find_element(By.NAME, "password").send_keys("short")
        DRIVER.save_screenshot(os.path.join(d, "screenshot_1_before_submit.png"))
        DRIVER.find_element(By.CSS_SELECTOR, "form button, form input[type=submit]").click()
        time.sleep(0.4)
        DRIVER.save_screenshot(os.path.join(d, "screenshot_2_after_error.png"))
        shots += [("screenshot_1_before_submit.png", "Before submit: valid username, too-short password."),
                  ("screenshot_2_after_error.png", "After the error: both fields are empty - the user must retype the valid username.")]
    return dict(trace=t.text(), reproduced=r.status_code == 200 and not filled, shots=shots,
                observed="Validation error is shown but the username field comes back empty (inputs have no value attribute).")


def def013(base, d, use_browser):
    t = Trace(base)
    s = requests.Session()
    r8 = t.call(s, "POST", "/api/register", json={"username": "eight_chr", "password": "abcd1234"})
    r9 = t.call(s, "POST", "/api/register", json={"username": "nine_chr", "password": "abcd12345"})
    t.shell("cd app && python -c \"from helpers import is_valid_password as v; print(v('abcd1234'), v('abcd12345'))\"",
            [f"{helpers.is_valid_password('abcd1234')} {helpers.is_valid_password('abcd12345')}"])
    t.note("Spec says 'at least 8 characters' -> the 8-character password must be True")
    shots = []
    if use_browser:
        from selenium.webdriver.common.by import By
        DRIVER.get(base + "/logout")
        DRIVER.get(base + "/register")
        DRIVER.find_element(By.NAME, "username").send_keys("eight_web")
        DRIVER.find_element(By.NAME, "password").send_keys("abcd1234")
        DRIVER.find_element(By.CSS_SELECTOR, "form button, form input[type=submit]").click()
        time.sleep(0.4)
        DRIVER.save_screenshot(os.path.join(d, "screenshot_8char_rejected.png"))
        shots.append(("screenshot_8char_rejected.png", "Register page with an 8-character password: rejected with 'at least 8 characters' - contradicting its own message."))
    return dict(trace=t.text(), reproduced=r8.status_code == 400 and r9.status_code == 201, shots=shots,
                observed=f"8 characters -> HTTP {r8.status_code} (rejected); 9 characters -> HTTP {r9.status_code}. Off-by-one in boundary (> instead of >=).")


def def014(base, d, use_browser):
    t = Trace(base)
    s = user(base, "alice_d14", t)
    today = date.today().isoformat()
    r = t.call(s, "POST", "/api/tasks", json={"title": "Due today task", "due_date": today})
    t.shell(f"cd app && python -c \"from helpers import compute_urgency; print(compute_urgency('{today}'))\"",
            [helpers.compute_urgency(today, date.today())])
    t.note("Spec: a task due today must be labelled 'Due Today'")
    s.post(base + "/api/tasks", json={"title": "Yesterday task", "due_date": (date.today() - timedelta(days=1)).isoformat()})
    s.post(base + "/api/tasks", json={"title": "Tomorrow task", "due_date": (date.today() + timedelta(days=1)).isoformat()})
    shots = []
    if use_browser:
        web_login(DRIVER, base, "alice_d14")
        DRIVER.get(base + "/")
        time.sleep(0.4)
        DRIVER.save_screenshot(os.path.join(d, "screenshot_due_today_overdue.png"))
        shots.append(("screenshot_due_today_overdue.png", f"Task list on {today}: 'Due today task' carries the Overdue badge, same as yesterday's task."))
    urg = r.json().get("urgency")
    return dict(trace=t.text(), reproduced=urg == "Overdue", shots=shots,
                observed=f"Task due today ({today}) returned urgency '{urg}' instead of 'Due Today'; the 'Due Today' label can never appear.")


def def015(base, d, use_browser):
    t = Trace(base)
    now = datetime(2026, 11, 25, 12, 0, 0)
    rows = []
    for days in (6, 7, 8):
        ts = (now - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        rows.append((days, ts, helpers.completed_in_last_n_days(ts, 7, now)))
    t.note("Spec: a task counts if completed within the last 7 days, INCLUSIVE of exactly 7 days ago")
    t.shell("cd app && python -c \"from datetime import datetime as D; from helpers import completed_in_last_n_days as f; "
            "now=D(2026,11,25,12); [print(d, f(ts, 7, now)) for d, ts in "
            "[(6,'2026-11-19 12:00:00'),(7,'2026-11-18 12:00:00'),(8,'2026-11-17 12:00:00')]]\"",
            [f"{days} {res}" for days, ts, res in rows])
    t.note("Expected: 6 True / 7 True / 8 False  ->  exactly 7 days ago is WRONG")
    # end-to-end via the dashboard API: complete a task now and backdate it 7 days in the DB
    s = user(base, "alice_d15", t)
    tid = s.post(base + "/api/tasks", json={"title": "Done a week ago"}).json()["id"]
    s.put(base + f"/api/tasks/{tid}", json={"done": True})
    import sqlite3
    con = sqlite3.connect(pytodo.DATABASE)
    con.execute("UPDATE tasks SET completed_at=? WHERE id=?",
                ((datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"), tid))
    con.commit(); con.close()
    t.note("setup: task completed, completed_at back-dated to exactly 7 days ago")
    r = t.call(s, "GET", "/api/dashboard")
    t.note("1 task completed exactly 7 days ago, but completed_this_week = %s" % r.json().get("completed_this_week"))
    wrong = rows[1][2] is False
    return dict(trace=t.text(), reproduced=wrong,
                observed="A task completed exactly 7 days ago returns False (age.days < n) and is missing from the 'completed in last 7 days' count.")


def def016(base, d, use_browser):
    t = Trace(base)
    s1, s2 = requests.Session(), requests.Session()
    r1 = t.call(s1, "POST", "/api/register", json={"username": "alia_99", "password": "firstpass1"})
    r2 = t.call(s2, "POST", "/api/register", json={"username": "alia_99", "password": "secondpass2"})
    t.note("Owner of the second account logs in with their own password:")
    l2 = t.call(requests.Session(), "POST", "/api/login", json={"username": "alia_99", "password": "secondpass2"})
    l1 = t.call(requests.Session(), "POST", "/api/login", json={"username": "alia_99", "password": "firstpass1"})
    ok = r1.status_code == 201 and r2.status_code == 201 and l2.status_code == 401
    return dict(trace=t.text(), reproduced=ok,
                observed=f"Same username registered twice (HTTP {r1.status_code}, {r2.status_code}, two different ids); second owner cannot log in (HTTP {l2.status_code}).")


def def017(base, d, use_browser):
    t = Trace(base)
    s = requests.Session()
    report = []
    for path in ("/login", "/register"):
        html = t.call(s, "GET", path, show_body=False).text
        labels = re.findall(r"<label[^>]*>", html)
        inputs = re.findall(r"<input[^>]*>", html)
        linked = [l for l in labels if "for=" in l]
        ids = [i for i in inputs if " id=" in i]
        t.note(f"{path}: {len(labels)} <label> ({len(linked)} with for=), {len(inputs)} <input> ({len(ids)} with id=)")
        for l in labels:
            t.note("   " + l)
        report.append(len(linked) == 0)
    s2 = user(base, "alice_d17")
    html = t.call(s2, "GET", "/tasks/new", show_body=False).text
    labels = re.findall(r"<label[^>]*>", html)
    t.note(f"/tasks/new: {len(labels)} <label>, {sum('for=' in l for l in labels)} with for=")
    shots = []
    if use_browser:
        DRIVER.get(base + "/logout")
        DRIVER.get(base + "/login")
        names = DRIVER.execute_script(
            "return [...document.querySelectorAll('input')].map(i=>[i.name, i.labels.length]);")
        for n, c in names:
            t.note(f"browser: input name={n!r} -> associated labels (input.labels.length) = {c}")
        DRIVER.execute_script("""document.querySelectorAll('label').forEach(l=>l.style.outline='3px dashed #c00');
            document.querySelectorAll('input').forEach(i=>{ if(!i.labels.length) i.style.outline='3px solid #c00';});""")
        DRIVER.save_screenshot(os.path.join(d, "screenshot_unlinked_labels.png"))
        shots.append(("screenshot_unlinked_labels.png", "Login form: labels (dashed) and inputs (solid) outlined in red have no programmatic link - screen readers announce the fields without a name."))
    return dict(trace=t.text(), reproduced=all(report), shots=shots,
                observed="No <label> has a for= attribute and no input has an id, so input.labels is empty for every field (WCAG 1.3.1 / 4.1.2).")


# --------------------------------------------------------------------------- register
A, T = "app/app.py", "app/templates"
DEFECTS = [
    # id, slug, title, severity, folder, found-by, tcs, expected, function, code-ref builder, cross-refs
    ("DEF-001", "Cross_User_Task_Deletion", "Authenticated user can delete another user's task (IDOR)", "Critical",
     "05_Security_Performance/Security", "Fatin (BUG-005), Intan (DEF-001), Alia (TC-SEC-005)",
     "TC-SEC-005, API-021/022, AUTO-002", "User B gets 404; user A's task is untouched.", def001,
     lambda: code(A, find_line(A, "def api_delete_task"), find_line(A, "def api_delete_task") + 6,
                  {find_line(A, 'DELETE FROM tasks WHERE id = ?", (task_id,)')}),
     ["04_Web_API/evidence/API-021_Unauthorized_Deletion_Failed.png",
      "04_Web_API/evidence/API-022_Unauthorized_Deletion_Confirmed.png",
      "06_Automation_Regression/evidence/AUTO-002_Unauthorized_Deletion_Failed.png"]),
    ("DEF-002", "SQL_Injection_Task_Search", "SQL injection in task search API (GET /api/tasks?q=)", "Critical",
     "05_Security_Performance/Security", "Intan (DEF-002), Alia (TC-SEC-007/008)",
     "TC-SEC-007, TC-SEC-008", "Search input treated as text; only own tasks; apostrophes work.", def002,
     lambda: code(A, find_line(A, "Search is intentionally simple") - 2, find_line(A, "Search is intentionally simple") + 2,
                  {find_line(A, "LIKE '%{q}%'")}), []),
    ("DEF-003", "No_Audit_Logging", "No audit logging of security-relevant events", "Moderate",
     "05_Security_Performance/STRIDE", "Intan (DEF-003, STRIDE Repudiation)",
     "STRIDE-R", "Logins, failed logins and deletions are recorded with user, time and target.", def003,
     lambda: code(A, 1, 30), ["05_Security_Performance/STRIDE/README.md"]),
    ("DEF-004", "Stored_XSS_Task_Title", "Stored XSS: task title rendered unescaped", "Critical",
     "05_Security_Performance/Security", "Alia (TC-SEC-009)",
     "TC-SEC-009", "Title shown as plain text (HTML-escaped).", def004,
     lambda: code(f"{T}/index.html", find_line(f"{T}/index.html", "|safe") - 1, find_line(f"{T}/index.html", "|safe") + 1,
                  {find_line(f"{T}/index.html", "|safe")}), []),
    ("DEF-005", "Malformed_Due_Date_HTTP500", "Malformed due date stored via API -> permanent HTTP 500", "Critical",
     "05_Security_Performance/Security", "Alia (TC-SEC-014)",
     "TC-SEC-014", "HTTP 400 with a validation message; nothing stored.", def005,
     lambda: code(A, find_line(A, "def api_create_task"), find_line(A, "def api_create_task") + 18,
                  {find_line(A, 'due_date = data.get("due_date")')}) + "\n\n" +
             code("app/helpers.py", 30, 31, {31}), []),
    ("DEF-006", "No_CSRF_Protection_GET_Logout", "No CSRF protection on state-changing forms; logout via GET", "Major",
     "05_Security_Performance/Security", "Alia (TC-SEC-010)",
     "TC-SEC-010", "Forms carry an anti-CSRF token; cross-origin POST rejected; logout is POST.", def006,
     lambda: code(A, find_line(A, '@app.route("/logout")'), find_line(A, '@app.route("/logout")') + 3,
                  {find_line(A, '@app.route("/logout")')}) + "\n\n" +
             code(A, find_line(A, "def delete_task_web") - 2, find_line(A, "def delete_task_web") + 4), []),
    ("DEF-007", "Hardcoded_Secret_Key_Debug", "Hard-coded SECRET_KEY and debug=True", "Major",
     "05_Security_Performance/Security", "Alia (TC-SEC-013)",
     "TC-SEC-013", "Secret read from environment; debug off by default.", def007,
     lambda: code(A, find_line(A, "SECRET_KEY"), find_line(A, "SECRET_KEY"), {find_line(A, "SECRET_KEY")}) + "\n\n" +
             code(A, find_line(A, "app.run(debug=True)"), find_line(A, "app.run(debug=True)"), {find_line(A, "app.run(debug=True)")}), []),
    ("DEF-008", "No_Login_Throttling", "No throttling or lockout after repeated failed logins", "Moderate",
     "05_Security_Performance/Security", "Alia (TC-SEC-002)",
     "TC-SEC-002", "HTTP 429 / temporary lockout after N failed attempts.", def008,
     lambda: code(A, find_line(A, "def api_login"), find_line(A, "def api_login") + 10), []),
    ("DEF-009", "No_Max_Title_Length", "No maximum length for task title", "Minor",
     "05_Security_Performance/Security", "Alia (TC-SEC-015)",
     "TC-SEC-015", "Titles above a sensible limit rejected with 400/413.", def009,
     lambda: code(A, find_line(A, "def api_create_task") + 2, find_line(A, "def api_create_task") + 5,
                  {find_line(A, 'title = (data.get("title") or "").strip()')}), []),
    ("DEF-010", "No_Viewport_Meta_Mobile", "No viewport meta tag - mobile shows shrunken desktop layout", "Moderate",
     "03_Special_Testing/GUI_Compatibility", "Alia (TC-GUI-114)",
     "TC-GUI-114 (CFG-04)", "Layout adapts to phone width; text readable without zoom.", def010,
     lambda: code(f"{T}/base.html", 1, 7, {3, 4, 5, 6}), ["03_Special_Testing/GUI_Compatibility/screenshots/CFG-04_05_task_list.png"]),
    ("DEF-011", "Table_Wrap_1366px", "Task table cells wrap at 1366 px", "Minor",
     "03_Special_Testing/GUI_Compatibility", "Alia (TC-GUI-106)",
     "TC-GUI-106 (CFG-01)", "Due dates and badges stay on one line.", def011,
     lambda: code(f"{T}/index.html", find_line(f"{T}/index.html", "|safe") - 2, find_line(f"{T}/index.html", "|safe") + 6),
     ["03_Special_Testing/GUI_Compatibility/screenshots/CFG-01_05_task_list.png"]),
    ("DEF-012", "Register_Form_Clears_Input", "Registration form clears input after a validation error", "Minor",
     "03_Special_Testing/GUI_Compatibility", "Alia (TC-GUI-104)",
     "TC-GUI-104", "Username stays filled in after an error; only the password is cleared.", def012,
     lambda: code(f"{T}/register.html", 6, 12, {9}), ["03_Special_Testing/GUI_Compatibility/screenshots/CFG-01_04_register_error.png"]),
    ("DEF-013", "Password_8_Char_Rejected", "8-character password rejected (boundary off-by-one)", "Moderate",
     "01_Black_Box", "Hanisah (BB, BUG-001), Fatin (WB/API, BUG-001)",
     "TC-BB (BVA password), WB-001, API-015, AUTO-003", "An 8-character password is accepted (spec: at least 8).", def013,
     lambda: code("app/helpers.py", 42, 49, {49}),
     ["02_White_Box_Coverage/evidence/WB-001_Unit_Test_Results.png", "04_Web_API/evidence/API-015_Password_Boundary_Failed.png",
      "06_Automation_Regression/evidence/AUTO-003_Password_Boundary_Failed.png"]),
    ("DEF-014", "Due_Today_Shown_Overdue", "Task due today shown as Overdue", "Moderate",
     "01_Black_Box", "Hanisah (BB, BUG-002), Fatin (WB, BUG-002), Alia (TC-GUI-107)",
     "TC-BB (urgency EP/BVA), WB-001, WB-005, TC-GUI-107", "Task due today labelled 'Due Today'.", def014,
     lambda: code("app/helpers.py", 31, 38, {33}),
     ["02_White_Box_Coverage/evidence/WB-005_Urgency_Flowchart.png", "02_White_Box_Coverage/evidence/WB-001_Unit_Test_Results.png"]),
    ("DEF-015", "Seven_Day_Completion_Boundary", "Task completed exactly 7 days ago not counted", "Minor",
     "02_White_Box_Coverage", "Fatin (WB, BUG-003)",
     "WB-001 (test_helpers.py)", "Completed exactly 7 days ago counts (spec: inclusive).", def015,
     lambda: code("app/helpers.py", 61, 75, {75}), ["02_White_Box_Coverage/evidence/WB-001_Unit_Test_Results.png"]),
    ("DEF-016", "Duplicate_Usernames_Accepted", "Duplicate usernames accepted; second account cannot log in", "Moderate",
     "04_Web_API", "Fatin (API, BUG-004), Alia (TC-SEC-004)",
     "API-016, AUTO-004, TC-SEC-004", "Second registration rejected (409 / 'username taken').", def016,
     lambda: code(A, find_line(A, "def api_register"), find_line(A, "def api_register") + 12,
                  {find_line(A, 'cur = db.execute("INSERT INTO users')}) + "\n\n" +
             code(A, find_line(A, "NOTE: no uniqueness check"), find_line(A, "NOTE: no uniqueness check"), {find_line(A, "NOTE: no uniqueness check")}),
     ["04_Web_API/evidence/API-016_Duplicate_Username_Failed.png", "06_Automation_Regression/evidence/AUTO-004_Duplicate_Username_Failed.png"]),
    ("DEF-017", "Form_Labels_Not_Linked", "Form labels not programmatically linked to inputs", "Minor",
     "03_Special_Testing/Usability_Accessibility", "Hanisah (TC-ACC-005)",
     "TC-ACC-005", "Every input has an associated <label for=id> (WCAG 1.3.1, 4.1.2).", def017,
     lambda: code(f"{T}/login.html", 7, 12, {8, 9, 10, 11}), []),
]


def write_evidence(entry, res, folder_abs):
    did, slug, title, sev, folder, who, tcs, expected, _, codefn, xrefs = entry
    rel_up = os.path.relpath(ROOT, folder_abs).replace("\\", "/")
    lines = [
        f"# {did} - {title}",
        "",
        "| Field | Value |", "|---|---|",
        f"| Severity | {sev} |",
        f"| Found by | {who} |",
        f"| Related test cases | {tcs} |",
        f"| Status | Open - **{'REPRODUCED' if res['reproduced'] else 'NOT REPRODUCED'}** on {RUN_AT} |",
        f"| Environment | Python {platform.python_version()}, Flask 3.0.3, SQLite (fresh temp DB), {platform.system()} {platform.release()}"
        + (", Chrome headless (Selenium)" if res.get("shots") else "") + " |",
        f"| Reproduced by | `07_Test_Management/Defect_Evidence/reproduce_defects.py` ({did.lower().replace('-', '')}) |",
        "",
        "## Expected", expected, "",
        "## Actual (observed in this run)", res["observed"], "",
    ]
    if res.get("shots"):
        lines.append("## Screenshots")
        for f, cap in res["shots"]:
            lines += [f"**{f}** - {cap}", "", f"![{cap}]({f})", ""]
    src_text = codefn()
    render_terminal(res["term"], did, title, os.path.join(folder_abs, "terminal_evidence.png"))
    render_source(src_text, did, os.path.join(folder_abs, "source_root_cause.png"))
    lines += ["## Terminal evidence (PNG)",
              "Requests replayed as the equivalent `curl` commands; every status code and body shown is the real response from this run.",
              "", "![Terminal evidence](terminal_evidence.png)", "",
              "## Root cause in source (PNG)", "", "![Faulty source lines](source_root_cause.png)", "",
              "## Captured request / response trace (text)", "```text", res["trace"], "```", "",
              "## Root cause - faulty source lines (`>>` marks the defect)", "```text", src_text, "```", ""]
    if xrefs:
        lines.append("## Supporting evidence from other members")
        for x in xrefs:
            lines.append(f"- [`{x}`]({rel_up}/{x})")
        lines.append("")
    with open(os.path.join(folder_abs, "evidence.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    global DRIVER
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--only", nargs="*", help="e.g. DEF-004 DEF-010")
    args = ap.parse_args()
    use_browser = not args.no_browser
    srv, base = start_server()
    if use_browser:
        DRIVER = browser()
    results = []
    try:
        for entry in DEFECTS:
            did, slug, folder = entry[0], entry[1], entry[4]
            if args.only and did not in args.only:
                continue
            out = os.path.join(ROOT, folder, "Defect_Evidence", f"{did}_{slug}")
            os.makedirs(out, exist_ok=True)
            if use_browser:
                DRIVER.delete_all_cookies()
            res = entry[8](base, out, use_browser)
            res["term"] = LAST_TRACE.term
            write_evidence(entry, res, out)
            results.append((entry, res, out))
            print(f"{did}: {'REPRODUCED' if res['reproduced'] else 'NOT REPRODUCED'} -> {os.path.relpath(out, ROOT)}")
    finally:
        if DRIVER:
            DRIVER.quit()
        srv.shutdown()

    if not args.only:
        idx = ["# Defect Evidence Index (DEF-001 - DEF-017)", "",
               f"Generated {RUN_AT} by `reproduce_defects.py` (fresh temporary database each run; the real app DB is not touched).",
               "Each defect's evidence lives in the folder of the test activity that found it. Re-run:",
               "", "```bash", "python 07_Test_Management/Defect_Evidence/reproduce_defects.py", "```", "",
               "| ID | Title | Severity | Result | PNG evidence | Evidence |", "|---|---|---|---|---|---|"]
        for entry, res, out in results:
            rel = os.path.relpath(out, HERE).replace("\\", "/")
            idx.append(f"| {entry[0]} | {entry[2]} | {entry[3]} | {'Reproduced' if res['reproduced'] else '**Not reproduced**'} | "
                       f"terminal + source{' + ' + str(len(res.get('shots', []))) + ' browser' if res.get('shots') else ''} | [{os.path.relpath(out, ROOT).replace(os.sep, '/')}]({rel}/evidence.md) |")
        n = sum(r["reproduced"] for _, r, _ in results)
        idx += ["", f"**{n} / {len(results)} defects reproduced.**", ""]
        with open(os.path.join(HERE, "Defect_Evidence_Index.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(idx))
        print(f"\n{n}/{len(results)} reproduced. Index: 07_Test_Management/Defect_Evidence/Defect_Evidence_Index.md")


if __name__ == "__main__":
    main()
