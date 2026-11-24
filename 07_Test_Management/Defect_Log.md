# Consolidated Defect Log  (owner: Member 4 – Defect & Metrics Coordinator)

> ⬜ **TO FILL by Member 4** (and every member for their own defects). Member 1's defects DEF-001 – DEF-011 are already logged.
> Backup copy: `_BACKUP_Members_2_3_4/07_Test_Management/Defect_Log.md` (all 23 defects) and `defect_log.csv`.

Severity / priority definitions: `Team_Conventions.md` §3. Status values: Open / Confirmed / Retest / Closed.

| Defect ID | Title | Affected Feature | Environment | Preconditions | Steps to Reproduce | Expected Result | Actual Result | Severity | Priority | Evidence | Status | Found by |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DEF-001 | SQL injection in task search (GET /api/tasks?q=) exposes other users' tasks | Search / API – `app.py api_list_tasks` | Python 3.13, Flask 3.0.3, SQLite; Chrome 153 | Two users exist; user A has a task 'alice salary review'; logged in as user B | 1. As user B send GET /api/tasks?q=%25' OR 1=1 OR title LIKE '  2. Also try GET /api/tasks?q=Alia's | Search treats input as text; only B's matching tasks returned; apostrophes work | Step 1 returns user A's task (user_id filter bypassed). Step 2 returns HTTP 500 (SQL syntax error) | Critical | High | TC-SEC-007, TC-SEC-008, TC-API-028 | Open | Member 1 (Week 5 Security) |
| DEF-002 | Stored XSS: task title rendered unescaped in task list | Task list (web UI) – `templates/index.html ({{ t.title\|safe }})` | Python 3.13, Flask 3.0.3, SQLite; Chrome 153 | Logged in | 1. Create task with title <script>alert('xss')</script>  2. Open task list | Title shown as plain text | Script tag is inserted into the page and executes in the browser | Critical | High | TC-SEC-009 | Open | Member 1 (Week 5 Security) |
| DEF-003 | API DELETE /api/tasks/<id> deletes any user's task (IDOR) | Delete task / API – `app.py api_delete_task` | Python 3.13, Flask 3.0.3, SQLite; Chrome 153 | User A owns task id N; logged in as user B | 1. As user B send DELETE /api/tasks/N  2. As user A GET /api/tasks/N | 404 for user B; A's task untouched | 200 {"result":"ok"}; A's task is gone (404) | Critical | High | TC-SEC-005, TC-API-039 | Open | Member 1 (Week 5 Security) |
| DEF-004 | No CSRF protection on state-changing forms; logout via GET | Web forms – `templates/*.html, app.py` | Python 3.13, Flask 3.0.3, SQLite; Chrome 153 | Logged in | 1. Inspect create/edit/delete/toggle forms for a CSRF token  2. Note /logout is a GET link | Forms carry an anti-CSRF token; logout is POST | No token in any form; a third-party page could submit delete/toggle requests or log the user out | Major | Medium | TC-SEC-010 | Open | Member 1 (Week 5 Security) |
| DEF-005 | Hard-coded SECRET_KEY and debug=True in app.py | Configuration – `app.py lines 26, 482` | Python 3.13, Flask 3.0.3, SQLite; Chrome 153 | Source code access | 1. Open app.py  2. Read SECRET_KEY and app.run() | Secret from environment; debug off by default | SECRET_KEY='pytodo-pro-dev-secret' (anyone can forge session cookies); app.run(debug=True) enables Werkzeug debugger | Major | Medium | TC-SEC-013 | Open | Member 1 (Week 5 Security) |
| DEF-006 | No throttling or lockout after repeated failed logins | Login – `app.py login_page / api_login` | Python 3.13, Flask 3.0.3, SQLite; Chrome 153 | Account exists | 1. Send 20 wrong passwords in a row to /api/login | Lockout or HTTP 429 after N attempts | All 20 attempts return 401, no delay or lockout | Moderate | Low | TC-SEC-002 | Open | Member 1 (Week 5 Security) |
| DEF-007 | No maximum length for task title | Create task – `app.py new_task / api_create_task` | Python 3.13, Flask 3.0.3, SQLite; Chrome 153 | Logged in | 1. POST /api/tasks with a 100,000-character title | Rejected (400/413) above a sensible limit | Accepted (201) and stored; page renders the whole string | Minor | Low | TC-SEC-015 | Open | Member 1 (Week 5 Security) |
| DEF-008 | Duplicate usernames can be registered; second account cannot log in | Registration – `app.py register_page / api_register` | Python 3.13, Flask 3.0.3, SQLite; Chrome 153 | User 'alia_99' exists | 1. Register 'alia_99' again with another password  2. Log out  3. Log in with the second password | Registration rejected: username taken | Second account created; login with its password fails (first row matched) | Major | High | TC-BB-011, TC-SEC-004, TC-API-008 | Open | Member 1 (Week 1 Black-box / Week 5) |
| DEF-009 | Invalid due date via API causes HTTP 500 and breaks the user's task list | Create task / API – `app.py api_create_task + helpers.compute_urgency` | Python 3.13, Flask 3.0.3, SQLite; Chrome 153 | Logged in | 1. POST /api/tasks {"title":"x","due_date":"2026-13-45"}  2. GET /api/tasks  3. Open / in browser | 400 with validation message; nothing stored | Step 1 returns 500 but the row IS stored; every later list/page load for this user returns 500 | Critical | High | TC-SEC-014, TC-API-020, TC-WB-009 | Open | Member 1 (Week 4/5) |
| DEF-010 | No viewport meta tag - mobile browsers show a shrunken desktop layout | All pages (GUI) – `templates/base.html` | Python 3.13, Flask 3.0.3, SQLite; Chrome 153 mobile emulation (Pixel 7) | Logged in on a phone-sized screen | 1. Open task list on a mobile device / emulator | Layout adapts to the screen width, text readable without zoom | Page rendered at ~980px desktop width and scaled down; text and buttons tiny | Moderate | Medium | TC-GUI-014, screenshots/CFG-04_05_task_list.png | Open | Member 1 (Week 3 GUI) |
| DEF-011 | Task table cells wrap awkwardly at 1366px (due date split over two lines, 'No due date' badge broken) | Task list (GUI) – `static/style.css` | Python 3.13, Flask 3.0.3, SQLite; Chrome 153 | Tasks with due dates and without | 1. Open task list at 1366x900 | Dates and badges on one line | Due date '2026-11-29' wraps to '2026-' / '11-29'; 'No due date' badge splits over 2 lines | Minor | Low | TC-GUI-006, screenshots/CFG-01_05_task_list.png | Open | Member 1 (Week 3 GUI) |
| DEF-012 | | | | | | | | | | | | Member 2 |
| DEF-013 | | | | | | | | | | | | Member 2 |
| DEF-014 | | | | | | | | | | | | Member 2 |
| DEF-015 | | | | | | | | | | | | Member 3 |
| DEF-016 | | | | | | | | | | | | Member 3 |
| DEF-017 | | | | | | | | | | | | Member 3 |
| DEF-018 | | | | | | | | | | | | Member 3 |
| DEF-019 | | | | | | | | | | | | Member 3 |
| DEF-020 | | | | | | | | | | | | Member 3 |
| DEF-021 | | | | | | | | | | | | Member 4 |
| DEF-022 | | | | | | | | | | | | Member 4 |
| DEF-023 | | | | | | | | | | | | Member 4 |

## Summary (Member 4 to complete)
| Severity | Count |
|---|---|
| Critical | |
| Major | |
| Moderate | |
| Minor | |
| **Total** | |
