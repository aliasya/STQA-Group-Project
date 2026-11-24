# Week 5 – Security Testing

**Owner:** Member 1 (QA/Test Lead) · **Requirement:** REQ-16 (also REQ-01, 02, 03) · **STRIDE table:** Member 4 (`../STRIDE/`)

## 1. Scope and rules of engagement

- **Target:** a local PyTodo Pro instance only. Each automated test uses its own throw-away SQLite database.
- **No uncontrolled penetration testing:** no scanners (sqlmap, Burp active scan…), no external hosts, no denial-of-service floods. Payloads are minimal proofs that a control is missing.
- **Method:** each threat in the STRIDE table → one or more test cases that assert the *secure* behaviour. A failing test is a confirmed security defect.
- **Execution:** `pytest 05_Security_Performance/Security -v` (file `test_security.py`). Raw output: `security_test_run.txt`.

## 2. Threat → test mapping (STRIDE)

| Threat ID | STRIDE | Asset / function | Threat | Test case(s) | Result |
|---|---|---|---|---|---|
| T-01 | Spoofing | Login | Username enumeration / password guessing | TC-SEC-001, 002 | 001 Pass, **002 Fail** |
| T-02 | Spoofing | Registration | Second account with an existing username | TC-SEC-004 | **Fail** |
| T-03 | Spoofing | Session | Session reuse after logout; forged session cookie | TC-SEC-003, 013 | 003 Pass, **013 Fail** |
| T-04 | Tampering | Task API | Change/delete another user's task (IDOR) | TC-SEC-005, 006 | **005 Fail**, 006 Pass |
| T-05 | Tampering / Info disclosure | Search | SQL injection through `q` | TC-SEC-007, 008 | **Fail, Fail** |
| T-06 | Tampering | Task title | Stored cross-site scripting | TC-SEC-009 | **Fail** |
| T-07 | Tampering | Web forms | Cross-site request forgery | TC-SEC-010 | **Fail** |
| T-08 | Repudiation | All actions | No audit log of who changed what | Review only (no test) | Observation |
| T-09 | Info disclosure | Passwords | Plain-text or weak password storage | TC-SEC-011 | Pass |
| T-10 | Info disclosure | Cookies / errors / config | Readable cookie, stack traces, hard-coded secret | TC-SEC-012, 013, 014 | 012 Pass, **013, 014 Fail** |
| T-11 | Denial of service | Task create | Oversized input stored | TC-SEC-015 | **Fail** |
| T-12 | Elevation of privilege | Protected pages/API | Access without logging in | TC-SEC-016, 017 | Pass |

## 3. Security test cases and results

| Test Case ID | Feature / Req | Technique | Objective | Preconditions | Test Data | Steps | Expected Result | Actual Result | Status | Evidence | Defect ID |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TC-SEC-001 | Login (REQ-02) | Security – Spoofing | No username enumeration | User "victim" exists | wrong pw for victim; unknown user "nobody" | 1. POST /api/login for both | Both 401 with identical message | Both 401 `{"error":"invalid credentials"}` | Pass | run log | – |
| TC-SEC-002 | Login (REQ-02) | Security – Spoofing | Brute force is throttled | User exists | 20 wrong passwords | 1. POST /api/login 20× | 429 / lockout after a few attempts | All 20 → 401, no delay or lockout | Fail | run log | DEF-006 |
| TC-SEC-003 | Session (REQ-02) | Security – Spoofing | Logout invalidates session | Logged in | – | 1. GET /logout 2. GET /api/tasks | 401 | 401 | Pass | run log | – |
| TC-SEC-004 | Registration (REQ-01) | Security – Spoofing | Duplicate username refused | "alice" exists | alice / differentpw1 | 1. POST /api/register | 400/409 | 201 – second "alice" created | Fail | run log | DEF-008 |
| TC-SEC-005 | Delete (REQ-03) | Security – Tampering (IDOR) | Other user cannot delete my task | alice owns task N; mallory logged in | task id N | 1. mallory DELETE /api/tasks/N 2. alice GET it | alice's task still exists | Task deleted; alice gets 404 | Fail | run log | DEF-003 |
| TC-SEC-006 | Update (REQ-03) | Security – Tampering (IDOR) | Other user cannot edit my task | as above | title "hacked" | 1. mallory PUT /api/tasks/N | 404, title unchanged | 404, title unchanged | Pass | run log | – |
| TC-SEC-007 | Search (REQ-08) | Security – SQL injection | `q` treated as data | alice has "alice salary review"; mallory logged in | `q=%' OR 1=1 OR title LIKE '` | 1. mallory GET /api/tasks?q=… | Empty list (no match) | alice's task returned to mallory (user filter bypassed) | Fail | run log | DEF-001 |
| TC-SEC-008 | Search (REQ-08) | Security – SQL injection (error-based) | Apostrophe in search is safe | Logged in | `q=Alia's` | 1. GET /api/tasks?q=Alia's | 200 | 500 (SQL syntax error) | Fail | run log | DEF-001 |
| TC-SEC-009 | Task list (REQ-04) | Security – Stored XSS | Title is HTML-escaped | Logged in | `<script>alert('xss')</script>` | 1. Create task 2. GET / | Script shown as text | Raw `<script>` tag in page (template uses `|safe`) | Fail | run log | DEF-002 |
| TC-SEC-010 | Web forms | Security – CSRF | State-changing forms carry a CSRF token | Logged in, 1 task | – | 1. Inspect task list + new-task HTML | Hidden CSRF token present | No token in any form; logout is a GET link | Fail | run log | DEF-004 |
| TC-SEC-011 | Accounts | Security – Info disclosure | Passwords stored hashed | 1 user | – | 1. Read `users.password_hash` | Salted hash (scrypt/pbkdf2) | `scrypt:…` hash | Pass | run log | – |
| TC-SEC-012 | Session | Security – Info disclosure | Session cookie HttpOnly | – | – | 1. Register 2. Read Set-Cookie | `HttpOnly` set | `HttpOnly; Path=/` (no `Secure` – acceptable on local HTTP) | Pass | run log | – |
| TC-SEC-013 | Configuration | Security – Spoofing / Info disclosure | No hard-coded secret, debug off | – | app.py | 1. Inspect SECRET_KEY and app.run | Secret from env; debug False | `"pytodo-pro-dev-secret"` in source; `debug=True` | Fail | run log; app.py L28, L482 | DEF-005 |
| TC-SEC-014 | Create task (REQ-04) | Security – Error handling | Bad input gives 400, not an unhandled error | Logged in | due_date `2026-13-45` | 1. POST /api/tasks | 400 | 500. Row still saved, so all later list calls also 500 | Fail | run log | DEF-009 |
| TC-SEC-015 | Create task (REQ-04) | Security – DoS / input limits | Oversized title rejected | Logged in | 100,000-char title | 1. POST /api/tasks | 400/413 | 201 – stored | Fail | run log | DEF-007 |
| TC-SEC-016 | Web pages (REQ-03) | Security – Elevation | Protected pages need login | Logged out | /, /dashboard, /tasks/new | 1. GET each | 302 → /login | 302 → /login for all 3 | Pass | run log | – |
| TC-SEC-017 | API (REQ-03) | Security – Elevation | Protected API needs login | Logged out | 4 endpoints | 1. Call each | 401 | 401 for all 4 | Pass | run log | – |

**Summary:** 17 test cases (22 executions incl. parameters) · **7 Pass · 10 Fail** · pass rate 41.2 %. Defects: DEF-001–009 (4 Critical, 3 Major, 1 Moderate, 1 Minor).

## 4. Security defects found

| Defect | Title | Severity | Priority |
|---|---|---|---|
| DEF-001 | SQL injection in `GET /api/tasks?q=` exposes other users' tasks | Critical | High |
| DEF-002 | Stored XSS – task title rendered with `|safe` | Critical | High |
| DEF-003 | `DELETE /api/tasks/<id>` deletes any user's task (IDOR) | Critical | High |
| DEF-009 | Invalid due date → HTTP 500 and the user's task list stays broken | Critical | High |
| DEF-004 | No CSRF protection; logout via GET | Major | Medium |
| DEF-005 | Hard-coded `SECRET_KEY` + `debug=True` | Major | Medium |
| DEF-008 | Duplicate usernames allowed | Major | High |
| DEF-006 | No login throttling / lockout | Moderate | Low |
| DEF-007 | No maximum title length | Minor | Low |

Full reproduction steps: `07_Test_Management/Defect_Log.md`.

## 5. Interpretation

- **Authorisation is inconsistent, not absent.** GET and PUT check ownership (TC-SEC-006 Pass), DELETE does not (TC-SEC-005 Fail). The UI search uses a parameterised query but the API search uses an f-string. Same features, different code paths, different security. This points to missing code review rather than missing knowledge.
- **The most serious chain:** XSS (DEF-002) + no CSRF (DEF-004) + IDOR (DEF-003) together let a malicious task title or external page act as the victim and destroy other users' data.
- **Positive findings:** passwords are hashed with scrypt, the session cookie is HttpOnly, every protected route requires login, and login errors do not reveal whether a username exists.

## 6. Limitations

- Local HTTP only. HTTPS, `Secure` cookie flag, security headers and hosting configuration were not evaluated.
- Payloads prove the weakness exists; we did not explore its full extent (e.g. extracting the `users` table via UNION injection).
- Brute-force testing was limited to 20 attempts. Real attack speed was not measured. Login takes ~100 ms, which slows guessing but does not stop it.
- No dependency vulnerability scan (e.g. `pip-audit`) and no manual code-wide review beyond the routes tested.

## 7. Recommendations (priority order)

1. Parameterise the API search: `query += " AND title LIKE ?"; params.append(f"%{q}%")` (DEF-001).
2. Remove `|safe` from `index.html` (DEF-002).
3. Scope DELETE by owner: `... WHERE id = ? AND user_id = ?` and return 404 if nothing deleted (DEF-003).
4. Validate `due_date` with `strptime` before inserting; return 400 (DEF-009).
5. Add Flask-WTF CSRF tokens; make logout a POST (DEF-004).
6. Load `SECRET_KEY` from an environment variable; default `debug=False` (DEF-005).
7. Add a UNIQUE constraint on `users.username` + 409 response (DEF-008); rate-limit login (DEF-006); cap title length (DEF-007).
8. Add the security tests to the CI regression suite so these weaknesses cannot silently return.
