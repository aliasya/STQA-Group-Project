# Consolidated Defect Log  (owner: Member 4 – Defect & Metrics Coordinator; consolidated by Member 1)

This is the single defect register for the project: **17 unique defects, DEF-001 to DEF-017** (final report Table 7.6). Defects found by more than one member or technique are logged once, and the local IDs each member used are listed under "Found by".

Severity / priority definitions: `Team_Conventions.md` §3 and report Table 7.5. Status values: Open / Confirmed (reproduced by a second member or technique) / Fixed / Retest / Closed. The application was tested as delivered and not modified, so no defect can go beyond Confirmed.

Every defect was reproduced on a fresh temporary database by `07_Test_Management/Defect_Evidence/reproduce_defects.py`. The evidence folder for each defect (steps, request/response trace, faulty source lines, screenshots) is listed in `Defect_Evidence/Defect_Evidence_Index.md`.

**Environment for all rows:** Windows 11, Python 3.14, Flask 3.0.3, SQLite (fresh temporary database); Chrome for browser-visible defects.

| Defect ID | Title | Affected Feature | Preconditions | Steps to Reproduce | Expected Result | Actual Result | Severity | Priority | Evidence | Status | Found by (local IDs) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DEF-001 | Authenticated user can delete another user's task (IDOR) | Delete task / API – `app.py api_delete_task` | User A owns task id N; logged in as user B | 1. As user B send DELETE /api/tasks/N  2. As user A GET /api/tasks/N | 403/404 for user B; A's task untouched | 200 {"result":"ok"}; A's task is gone (404). Reading and editing check ownership, deleting does not | Critical | High | `05_Security_Performance/Security/Defect_Evidence/DEF-001_Cross_User_Task_Deletion/`; API-021, API-022, SEC-003, TC-SEC-005 | Confirmed | M3 BUG-005 (API-021, 022); M4 DEF-001 (SEC-003); M1 TC-SEC-005 |
| DEF-002 | SQL injection in task search API (GET /api/tasks?q=) exposes other users' tasks | Search / API – `app.py api_list_tasks` | Two users; user A has a task; logged in as user B | 1. As user B send GET /api/tasks?q=%25' OR 1=1 OR title LIKE '  2. Send GET /api/tasks?q=Alia's | Input treated as text; only B's matching tasks returned; apostrophes work | Step 1 returns user A's task (user filter bypassed). Step 2 returns HTTP 500 with an SQLite error | Critical | High | `05_Security_Performance/Security/Defect_Evidence/DEF-002_SQL_Injection_Task_Search/`; SEC-004, TC-SEC-007, TC-SEC-008 | Confirmed | M4 DEF-002 (SEC-004); M1 TC-SEC-007, 008 |
| DEF-003 | No audit logging of security-relevant events | Whole application – `app.py` (no logger / audit table) | Logged in | 1. Delete a task, fail a login  2. Look for any log entry or audit table | Logins, failed logins and deletions recorded with user, time and target | No logging or audit mechanism exists; actions leave no record (STRIDE repudiation) | Moderate | Medium | `05_Security_Performance/STRIDE/Defect_Evidence/DEF-003_No_Audit_Logging/`; SEC-008 | Open | M4 DEF-003 (SEC-008) |
| DEF-004 | Stored XSS: task title rendered unescaped in task list | Task list (web UI) – `templates/index.html ({{ t.title\|safe }})` | Logged in | 1. Create task with title `<script>alert('xss')</script>`  2. Open task list | Title shown as plain text | Script is inserted into the page and executes in the browser | Critical | High | `05_Security_Performance/Security/Defect_Evidence/DEF-004_Stored_XSS_Task_Title/`; TC-SEC-009 | Open | M1 TC-SEC-009 |
| DEF-005 | Malformed due date via API is stored and causes permanent HTTP 500 | Create task / API – `app.py api_create_task` + `helpers.compute_urgency` | Logged in | 1. POST /api/tasks {"title":"x","due_date":"2026-13-45"}  2. GET /api/tasks  3. Open / in the browser | 400 with a validation message; nothing stored | Step 1 returns 500 but the row IS stored; every later list or page load for this user returns 500 | Critical | High | `05_Security_Performance/Security/Defect_Evidence/DEF-005_Malformed_Due_Date_HTTP500/`; TC-SEC-014 | Open | M1 TC-SEC-014 |
| DEF-006 | No CSRF protection on state-changing forms; logout via GET | Web forms – `templates/*.html`, `app.py` | Logged in | 1. Inspect create/edit/delete/toggle forms for a CSRF token  2. Note /logout is a GET link | Forms carry an anti-CSRF token; logout is POST | No token in any form; a third-party page could submit delete/toggle requests or log the user out | Major | High | `05_Security_Performance/Security/Defect_Evidence/DEF-006_No_CSRF_Protection_GET_Logout/`; TC-SEC-010 | Open | M1 TC-SEC-010 |
| DEF-007 | Hard-coded SECRET_KEY and debug=True | Configuration – `app.py` | Source code access | 1. Open app.py  2. Read SECRET_KEY and app.run() | Secret loaded from the environment; debug off by default | SECRET_KEY='pytodo-pro-dev-secret' (anyone can forge session cookies); app.run(debug=True) enables the Werkzeug debugger | Major | High | `05_Security_Performance/Security/Defect_Evidence/DEF-007_Hardcoded_Secret_Key_Debug/`; TC-SEC-013 | Open | M1 TC-SEC-013 |
| DEF-008 | No throttling or lockout after repeated failed logins | Login – `app.py login_page / api_login` | Account exists | 1. Send 20 wrong passwords in a row to /api/login | Lockout or HTTP 429 after N attempts | All 20 attempts return 401, with no delay or lockout | Moderate | Medium | `05_Security_Performance/Security/Defect_Evidence/DEF-008_No_Login_Throttling/`; TC-SEC-002 | Open | M1 TC-SEC-002 |
| DEF-009 | No maximum length for task title | Create task – `app.py new_task / api_create_task` | Logged in | 1. POST /api/tasks with a 100,000-character title | Rejected (400/413) above a sensible limit | Accepted (201) and stored; the page renders the whole string | Minor | Low | `05_Security_Performance/Security/Defect_Evidence/DEF-009_No_Max_Title_Length/`; TC-SEC-015 | Open | M1 TC-SEC-015 |
| DEF-010 | No viewport meta tag – mobile browsers show a shrunken desktop layout | All pages (GUI) – `templates/base.html` | Logged in on a phone-sized screen (Pixel 7 emulation) | 1. Open the task list on a mobile device / emulator | Layout adapts to the screen width; text readable without zoom | Page rendered at ~980 px desktop width and scaled down; text and buttons tiny | Moderate | Medium | `03_Special_Testing/GUI_Compatibility/Defect_Evidence/DEF-010_No_Viewport_Meta_Mobile/`; TC-GUI-114 | Open | M1 TC-GUI-114 |
| DEF-011 | Task table cells wrap awkwardly at 1366 px | Task list (GUI) – `static/style.css` | Tasks with and without due dates | 1. Open the task list at 1366×900 | Dates and badges stay on one line | Due date '2026-11-29' wraps to '2026-' / '11-29'; 'No due date' badge splits over two lines | Minor | Low | `03_Special_Testing/GUI_Compatibility/Defect_Evidence/DEF-011_Table_Wrap_1366px/`; TC-GUI-106 | Open | M1 TC-GUI-106 |
| DEF-012 | Registration form clears input after a validation error | Registration (GUI) – `templates/register.html` | Logged out | 1. Open /register  2. Enter a valid username and a too-short password  3. Click Register | Error shown; username stays filled in, only the password is cleared | Error shown but both fields are empty; the user must retype the valid username | Minor | Low | `03_Special_Testing/GUI_Compatibility/Defect_Evidence/DEF-012_Register_Form_Clears_Input/`; TC-GUI-104 | Open | M1 TC-GUI-104 |
| DEF-013 | 8-character password rejected (boundary off-by-one) | Registration – `helpers.is_valid_password` | Logged out | 1. Register with password 'abcd1234' (8 chars)  2. Register with 'abcd12345' (9 chars) | Both accepted (spec: at least 8 characters) | 8 characters → HTTP 400 'invalid password'; 9 characters → 201. Comparison uses > instead of >= | Moderate | High | `01_Black_Box/Defect_Evidence/DEF-013_Password_8_Char_Rejected/`; TC-BB-004, TC-WB-002, API-015 | Confirmed | M2 BUG-001 (TC-BB-004); M3 BUG-001 (TC-WB-002, API-015) |
| DEF-014 | Task due today shown as Overdue | Urgency label – `helpers.compute_urgency` | Logged in | 1. Create a task due today  2. Open the task list / GET the task | Label 'Due Today' | Label 'Overdue'; the 'Due Today' label can never appear, and the dashboard counts the task as overdue | Moderate | High | `01_Black_Box/Defect_Evidence/DEF-014_Due_Today_Shown_Overdue/`; TC-BB-013, TC-WB-008, TC-GUI-107 | Confirmed | M2 BUG-002 (TC-BB-013); M3 BUG-002 (TC-WB-008); M1 TC-GUI-107 |
| DEF-015 | Task completed exactly 7 days ago not counted on the dashboard | Dashboard – `helpers.completed_in_last_n_days` | A task completed exactly 7 days ago | 1. Open the dashboard / GET /api/dashboard | Counted in 'completed in last 7 days' (spec: inclusive) | completed_this_week = 0; the function uses age.days < n instead of <= n | Minor | Low | `02_White_Box_Coverage/Defect_Evidence/DEF-015_Seven_Day_Completion_Boundary/`; TC-WB-010 | Open | M3 BUG-003 (TC-WB-010) |
| DEF-016 | Duplicate usernames accepted; second account cannot log in | Registration – `app.py register_page / api_register` | User 'alia_99' exists | 1. Register 'alia_99' again with another password  2. Log in with the second password | Second registration rejected (409 / 'username taken') | Second account created (201); login with its password fails (401) because the first row is matched | Moderate | Medium | `04_Web_API/Defect_Evidence/DEF-016_Duplicate_Usernames_Accepted/`; API-016, TC-SEC-004 | Confirmed | M3 BUG-004 (API-016); M1 TC-SEC-004 |
| DEF-017 | Form labels not programmatically linked to inputs | Login, register and task forms – `templates/*.html` | – | 1. Open the New Task form  2. Click each label / inspect the HTML | Every input has an associated `<label for=id>` (WCAG 1.3.1, 4.1.2) | No label has a for= attribute and no input has an id; clicking a label does not focus its field; screen readers announce fields without a name | Minor | Medium | `03_Special_Testing/Usability_Accessibility/Defect_Evidence/DEF-017_Form_Labels_Not_Linked/`; TC-ACC-005 | Open | M2 TC-ACC-005 |

## Summary

| Severity | Count | Defects |
|---|---|---|
| Critical | 4 | DEF-001, 002, 004, 005 |
| Major | 2 | DEF-006, 007 |
| Moderate | 6 | DEF-003, 008, 010, 013, 014, 016 |
| Minor | 5 | DEF-009, 011, 012, 015, 017 |
| **Total** | **17** | 5 Confirmed (found independently by more than one member or technique), 12 Open, 0 Closed |

## Mapping from earlier IDs

Members logged defects under local IDs before consolidation. Use this table to find a defect from an older document.

| Earlier ID (where used) | Final ID |
|---|---|
| M1 repo DEF-001 (SQL injection) | DEF-002 |
| M1 repo DEF-002 (stored XSS) | DEF-004 |
| M1 repo DEF-003 (IDOR delete) | DEF-001 |
| M1 repo DEF-004 (no CSRF) | DEF-006 |
| M1 repo DEF-005 (secret key / debug) | DEF-007 |
| M1 repo DEF-006 (no login throttling) | DEF-008 |
| M1 repo DEF-007 (no title length limit) | DEF-009 |
| M1 repo DEF-008 (duplicate usernames) | DEF-016 |
| M1 repo DEF-009 (malformed due date) | DEF-005 |
| M1 repo DEF-010, DEF-011 | unchanged |
| M1 GUI form clearing (TC-GUI-104) | DEF-012 |
| M2 / M3 BUG-001 (8-char password) | DEF-013 |
| M2 / M3 BUG-002 (due today) | DEF-014 |
| M3 BUG-003 (seven-day boundary) | DEF-015 |
| M3 BUG-004 (duplicate usernames) | DEF-016 |
| M3 BUG-005 (cross-user deletion) | DEF-001 |
| M4 DEF-001 / DEF-002 / DEF-003 (Section 6) | DEF-001 / DEF-002 / DEF-003 |
| M2 TC-ACC-005 ("pending team allocation") | DEF-017 |
