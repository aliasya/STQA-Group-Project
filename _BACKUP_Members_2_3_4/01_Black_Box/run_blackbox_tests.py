"""
Week 1 - Black-box test execution (BACKUP for Member 2, Test Design Coordinator)

Executes every black-box test case through the WEB INTERFACE the same way a
browser does (HTML form posts + following redirects), on a fresh database.
It writes:
    blackbox_results.csv     - one row per test case (Actual + Status filled in)
    Black_Box_Test_Cases.md  - the full test case table in the course template

Run from the repo root:
    python _BACKUP_Members_2_3_4/01_Black_Box/run_blackbox_tests.py

This produces the Actual Result from a reproducible execution. For the
report you should still reproduce a few cases manually in the browser and
take screenshots (see "Evidence" column).
"""
import csv
import os
import re
import sys
import tempfile
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
def _find_repo_root(start):
    """Walk up until we find app/app.py, so the script works from the main folder or the backup folder."""
    d = start
    while not os.path.exists(os.path.join(d, "app", "app.py")):
        parent = os.path.dirname(d)
        if parent == d:
            raise SystemExit("Run this inside the PyTodo-Pro-QA repository")
        d = parent
    return d


ROOT = _find_repo_root(HERE)
sys.path.insert(0, os.path.join(ROOT, "app"))
import app as pytodo  # noqa: E402

pytodo.app.config["PROPAGATE_EXCEPTIONS"] = False
TODAY = date.today()
D = lambda n: (TODAY + timedelta(days=n)).isoformat()  # noqa: E731
CASES = []


def fresh():
    pytodo.DATABASE = os.path.join(tempfile.mkdtemp(), "bb.db")
    pytodo.init_db()
    return pytodo.app.test_client()


def web_register(c, u, p):
    r = c.post("/register", data={"username": u, "password": p})
    return r


def logged_in_client(u="tester01"):
    c = fresh()
    web_register(c, u, "password123")
    return c


def page_error(html):
    m = re.search(r'<p class="error">(.*?)</p>', html)
    return m.group(1) if m else None


def rows(c, qs=""):
    html = c.get("/" + qs).get_data(as_text=True)
    out = []
    for tr in re.findall(r"<tr class=\"[^\"]*\">(.*?)</tr>", html, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        title = re.sub(r"<.*?>", "", cells[1]).strip()
        urg = re.sub(r"<.*?>", "", cells[4]).strip()
        out.append((title, urg))
    return out


def tc(id, feature, req, technique, objective, pre, data, steps, expected):
    def deco(fn):
        CASES.append(dict(id=id, feature=feature, req=req, technique=technique, objective=objective,
                          pre=pre, data=data, steps=steps, expected=expected, fn=fn))
        return fn
    return deco


# ---------------------------------------------------------------- Registration
def reg_outcome(u, p):
    c = fresh()
    r = web_register(c, u, p)
    if r.status_code == 302:
        return True, "Account created, redirected to task list"
    return False, f"Rejected: '{page_error(r.get_data(as_text=True))}'"


def reg_case(id, tech, u, p, should_pass, objective, defect=None):
    exp = "Account created and user redirected to task list" if should_pass else "Registration rejected with an error message"
    shown_u = u if len(u) < 25 else f"'{u[:4]}...' ({len(u)} chars)"

    @tc(id, "Registration", "REQ-01", tech, objective, "Logged out; username not yet registered",
        f"username={shown_u!s} ({len(u)} chars), password length={len(p)}",
        "1. Open /register  2. Enter username and password  3. Click Register", exp)
    def _():
        ok, msg = reg_outcome(u, p)
        return msg, ok == should_pass, defect


reg_case("TC-BB-001", "EP (valid class)", "alia_99", "password123", True, "Valid username and password are accepted")
reg_case("TC-BB-002", "EP (invalid: illegal chars)", "alia-99", "password123", False, "Username with '-' is rejected")
reg_case("TC-BB-003", "EP (invalid: space)", "alia 99", "password123", False, "Username with a space is rejected")
reg_case("TC-BB-004", "BVA (min-1)", "ab", "password123", False, "Username of 2 chars is rejected")
reg_case("TC-BB-005", "BVA (min)", "abc", "password123", True, "Username of exactly 3 chars is accepted")
reg_case("TC-BB-006", "BVA (max)", "a" * 20, "password123", True, "Username of exactly 20 chars is accepted")
reg_case("TC-BB-007", "BVA (max+1)", "a" * 21, "password123", False, "Username of 21 chars is rejected")
reg_case("TC-BB-008", "BVA (min-1)", "alia_99", "a" * 7, False, "Password of 7 chars is rejected")
reg_case("TC-BB-009", "BVA (min)", "alia_99", "a" * 8, True, "Password of exactly 8 chars is accepted (spec: at least 8)", "DEF-012")
reg_case("TC-BB-010", "BVA (min+1)", "alia_99", "a" * 9, True, "Password of 9 chars is accepted")


@tc("TC-BB-011", "Registration", "REQ-01", "Decision table (R4: valid, valid, username taken)",
    "Duplicate username is refused", "User 'alia_99' already exists",
    "username=alia_99, password=otherpass99", "1. Register alia_99  2. Log out  3. Register alia_99 again",
    "Second registration rejected: username already taken")
def _():
    c = fresh()
    web_register(c, "alia_99", "password123")
    c.get("/logout")
    r = web_register(c, "alia_99", "otherpass99")
    if r.status_code == 302:
        c.get("/logout")
        r2 = c.post("/login", data={"username": "alia_99", "password": "otherpass99"})
        return ("Second account created (HTTP 302). Logging in with the 2nd password then FAILS: "
                f"'{page_error(r2.get_data(as_text=True))}'"), False, "DEF-008"
    return "Rejected", True, None


# ---------------------------------------------------------------- Login
def login_case(id, rule, user_exists, pw_ok, expected_ok):
    @tc(id, "Login", "REQ-02", f"Decision table ({rule})", "Login outcome for each condition combination",
        "User 'alia_99' / 'password123' registered; logged out",
        f"username={'alia_99' if user_exists else 'ghost_user'}, password={'password123' if pw_ok else 'wrongpass1'}",
        "1. Open /login  2. Enter credentials  3. Click Log in",
        "Logged in, redirected to task list" if expected_ok else "Stays on login page with 'Invalid username or password.'")
    def _():
        c = fresh()
        web_register(c, "alia_99", "password123"); c.get("/logout")
        r = c.post("/login", data={"username": "alia_99" if user_exists else "ghost_user",
                                   "password": "password123" if pw_ok else "wrongpass1"})
        ok = r.status_code == 302
        msg = "Redirected to task list" if ok else f"Login page shown: '{page_error(r.get_data(as_text=True))}'"
        return msg, ok == expected_ok, None


login_case("TC-BB-012", "R1: user exists, pw correct", True, True, True)
login_case("TC-BB-013", "R2: user exists, pw wrong", True, False, False)
login_case("TC-BB-014", "R3: user unknown", False, True, False)


# ---------------------------------------------------------------- Task title
def title_case(id, tech, title, should_create, objective, defect=None):
    @tc(id, "Create task", "REQ-04", tech, objective, "Logged in, no tasks", f"title={title!r}",
        "1. Click + New Task  2. Enter title  3. Click Create Task",
        "Task created and listed" if should_create else "Task NOT created; validation message shown")
    def _():
        c = logged_in_client()
        c.post("/tasks/new", data={"title": title})
        r = rows(c)
        created = len(r) == 1
        return (f"Task created; list shows title {r[0][0]!r}" if created else "No task created"), created == should_create, defect


title_case("TC-BB-015", "EP (valid)", "Buy groceries", True, "Normal title is accepted")
title_case("TC-BB-016", "EP (invalid: whitespace only)", "   ", False,
           "Whitespace-only title is rejected (HTML 'required' only blocks a truly empty field)", "DEF-014")
title_case("TC-BB-017", "BVA (1 char)", "A", True, "Single-character title is accepted")


# ---------------------------------------------------------------- Urgency (BVA)
def urg_case(id, offset, expected, defect=None):
    due = None if offset is None else D(offset)
    label = "none" if offset is None else f"today{offset:+d} ({due})"

    @tc(id, "Task urgency", "REQ-09", "BVA" if offset is not None else "EP", f"Urgency label for due date {label}",
        f"Logged in; test date = {TODAY.isoformat()}", f"due_date={label}",
        "1. Create task with the due date  2. View the task list Urgency column", f"Badge shows '{expected}'")
    def _():
        c = logged_in_client()
        c.post("/tasks/new", data={"title": "u", "due_date": due or ""})
        actual = rows(c)[0][1]
        return f"Badge shows '{actual}'", actual == expected, (defect if actual != expected else None)


urg_case("TC-BB-018", -1, "Overdue")
urg_case("TC-BB-019", 0, "Due Today", "DEF-013")
urg_case("TC-BB-020", 1, "Due Soon")
urg_case("TC-BB-021", 2, "Due Soon")
urg_case("TC-BB-022", 3, "Upcoming")
urg_case("TC-BB-023", None, "No due date")


# ---------------------------------------------------------------- Filters (decision table)
def filter_case(id, rule, qs, expected_titles):
    @tc(id, "Filter / search", "REQ-08", f"Decision table ({rule})", "Correct tasks shown for filter combination",
        "Tasks: 'Report' (Study, open), 'Gym' (Personal, done), 'Study plan' (Study, done)", qs or "(no filter)",
        "1. Choose category/status, type search  2. Click Filter", f"Only {sorted(expected_titles)} listed")
    def _():
        c = logged_in_client()
        for t, cat in [("Report", 3), ("Gym", 2), ("Study plan", 3)]:
            c.post("/tasks/new", data={"title": t, "category_id": cat})
        ids = {t: i for i, t in enumerate(["Report", "Gym", "Study plan"], 1)}
        c.post(f"/tasks/{ids['Gym']}/toggle"); c.post(f"/tasks/{ids['Study plan']}/toggle")
        got = sorted(t for t, _ in rows(c, qs))
        return f"Listed {got}", got == sorted(expected_titles), None


filter_case("TC-BB-024", "no filters", "", ["Report", "Gym", "Study plan"])
filter_case("TC-BB-025", "category=Study", "?category=Study", ["Report", "Study plan"])
filter_case("TC-BB-026", "category=Study & status=done", "?category=Study&status=done", ["Study plan"])
filter_case("TC-BB-027", "status=open & q=gym", "?status=open&q=gym", [])
filter_case("TC-BB-028", "q=plan (partial, case-insensitive)", "?q=PLAN", ["Study plan"])


# ---------------------------------------------------------------- State transitions
@tc("TC-BB-029", "Task status", "REQ-06", "State transition (Open -> Done -> Open)",
    "Toggle moves task between Open and Done and sets/clears completion",
    "Logged in; one open task due in 5 days", "toggle x2",
    "1. Click ○ on the task  2. Check urgency/style  3. Click ✓ again",
    "After 1st click: 'Done' + strike-through, dashboard 'Completed (last 7 days)'=1. After 2nd: back to 'Upcoming', counter=0")
def _():
    c = logged_in_client()
    c.post("/tasks/new", data={"title": "T", "due_date": D(5)})
    c.post("/tasks/1/toggle"); s1 = rows(c)[0][1]
    d1 = re.findall(r'stat-value">(\d+)', c.get("/dashboard").get_data(as_text=True))[-1]
    c.post("/tasks/1/toggle"); s2 = rows(c)[0][1]
    d2 = re.findall(r'stat-value">(\d+)', c.get("/dashboard").get_data(as_text=True))[-1]
    ok = (s1, d1, s2, d2) == ("Done", "1", "Upcoming", "0")
    return f"After 1st: '{s1}', completed={d1}; after 2nd: '{s2}', completed={d2}", ok, None


@tc("TC-BB-030", "Task status", "REQ-07", "State transition (Open -> Deleted)",
    "Deleted task disappears and cannot be edited", "Logged in; one task", "task id 1",
    "1. Click Delete, confirm  2. Open /tasks/1/edit", "Task gone; edit URL redirects to task list")
def _():
    c = logged_in_client()
    c.post("/tasks/new", data={"title": "T"})
    c.post("/tasks/1/delete")
    r = c.get("/tasks/1/edit")
    ok = rows(c) == [] and r.status_code == 302
    return f"List empty={rows(c) == []}, edit URL -> HTTP {r.status_code}", ok, None


@tc("TC-BB-031", "Task urgency", "REQ-09", "State transition (Upcoming -> Due Soon -> Due Today -> Overdue)",
    "Urgency moves through every state as the due date approaches (simulated by editing the due date)",
    "Logged in; one open task", "due = today+3, +2, 0, -1",
    "1. Edit due date to each value  2. Read urgency after each edit",
    "Upcoming -> Due Soon -> Due Today -> Overdue")
def _():
    c = logged_in_client()
    c.post("/tasks/new", data={"title": "T", "due_date": D(3)})
    seq = []
    for n in (3, 2, 0, -1):
        c.post("/tasks/1/edit", data={"title": "T", "due_date": D(n)})
        seq.append(rows(c)[0][1])
    exp = ["Upcoming", "Due Soon", "Due Today", "Overdue"]
    return " -> ".join(seq) + " ('Due Today' state is never reached)" * (seq != exp), seq == exp, "DEF-013" if seq != exp else None


@tc("TC-BB-032", "Session", "REQ-02", "State transition (Logged in -> Logged out)",
    "Logout ends the session; protected pages then redirect to login", "Logged in", "-",
    "1. Click Log out  2. Open / and /dashboard", "Both redirect to /login")
def _():
    c = logged_in_client()
    c.get("/logout")
    codes = [(c.get(p).status_code, c.get(p).headers.get("Location", "")) for p in ("/", "/dashboard")]
    ok = all(s == 302 and "/login" in loc for s, loc in codes)
    return f"Responses: {codes}", ok, None


@tc("TC-BB-033", "Dashboard", "REQ-10", "EP (one task per urgency class)",
    "Dashboard counters match the tasks", "Logged in; tasks due today-1, today, today+1, today+5, one done",
    "5 tasks", "1. Create tasks  2. Open Dashboard",
    "Total 5, Open 4, Overdue 1, Due Soon 1, Completed 1 (task due today should not count as overdue)")
def _():
    c = logged_in_client()
    for n in (-1, 0, 1, 5):
        c.post("/tasks/new", data={"title": f"t{n}", "due_date": D(n)})
    c.post("/tasks/new", data={"title": "done"}); c.post("/tasks/5/toggle")
    v = re.findall(r'stat-value">(\d+)', c.get("/dashboard").get_data(as_text=True))
    ok = v == ["5", "4", "1", "1", "1"]
    return f"Total {v[0]}, Open {v[1]}, Overdue {v[2]}, Due Soon {v[3]}, Completed {v[4]}", ok, None if ok else "DEF-013"


@tc("TC-BB-034", "Edit task", "REQ-05", "EP (valid edit)", "Editing title/category/due date saves changes",
    "Logged in; task 'Old'", "title=New, category=Work, due=today+5",
    "1. Click Edit  2. Change fields  3. Save Changes", "List shows 'New', Work, Upcoming")
def _():
    c = logged_in_client()
    c.post("/tasks/new", data={"title": "Old"})
    c.post("/tasks/1/edit", data={"title": "New", "category_id": "1", "due_date": D(5)})
    html = c.get("/").get_data(as_text=True)
    ok = rows(c)[0] == ("New", "Upcoming") and "<td>Work</td>" in html
    return f"List row = {rows(c)[0]}, category Work shown={'<td>Work</td>' in html}", ok, None


@tc("TC-BB-035", "Edit task", "REQ-05", "EP (invalid: blank title on edit)", "Clearing the title on edit is rejected",
    "Logged in; task 'Old'", "title='   '", "1. Click Edit  2. Replace title with spaces  3. Save",
    "Change rejected; title stays 'Old'")
def _():
    c = logged_in_client()
    c.post("/tasks/new", data={"title": "Old"})
    c.post("/tasks/1/edit", data={"title": "   "})
    t = rows(c)[0][0]
    return f"Title is now {t!r}", t == "Old", None if t == "Old" else "DEF-014"


# ---------------------------------------------------------------- run
def main():
    results = []
    for case in CASES:
        try:
            actual, passed, defect = case["fn"]()
        except Exception as e:  # pragma: no cover
            actual, passed, defect = f"ERROR: {e!r}", False, None
        results.append({**{k: v for k, v in case.items() if k != "fn"},
                        "actual": actual, "status": "Pass" if passed else "Fail",
                        "defect": defect if not passed else "",
                        "evidence": f"blackbox_results.csv; screenshot evidence/{case['id']}.png"})
    with open(os.path.join(HERE, "blackbox_results.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader(); w.writerows(results)

    esc = lambda s: str(s).replace("|", "\\|").replace("\n", " ")  # noqa: E731
    lines = ["# Black-Box Test Cases and Execution Results (Week 1)", "",
             f"Executed: {TODAY.isoformat()} - environment: see 07_Test_Management/Test_Plan.md section 6. "
             "Generated by `run_blackbox_tests.py`.", "",
             "| Test Case ID | Feature / Req | Technique | Objective | Preconditions | Test Data | Steps | Expected Result | Actual Result | Status | Evidence | Defect ID |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        lines.append("| " + " | ".join(esc(x) for x in [r["id"], f"{r['feature']} ({r['req']})", r["technique"], r["objective"],
                     r["pre"], r["data"], r["steps"], r["expected"], r["actual"], f"**{r['status']}**",
                     r["evidence"].split(";")[1].strip(), r["defect"] or "-"]) + " |")
    p = sum(r["status"] == "Pass" for r in results)
    lines += ["", f"**Summary:** {len(results)} executed, {p} passed, {len(results) - p} failed, "
              f"pass rate {p / len(results):.1%}."]
    with open(os.path.join(HERE, "Black_Box_Test_Cases.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    for r in results:
        print(f"{r['id']}  {r['status']:4}  {r['defect'] or ''}  {r['actual'][:90]}")
    print(f"\n{len(results)} executed, {p} passed, {len(results) - p} failed")


if __name__ == "__main__":
    main()
