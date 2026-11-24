# Week 5 – STRIDE Threat Table (BACKUP – Member 4)

Assets: user accounts (credentials, sessions), task data (confidentiality + integrity per user), application availability, server configuration.
Trust boundaries: browser ⇄ Flask app (HTTP), app ⇄ SQLite file.
Risk = Likelihood (1–3) × Impact (1–3). Test cases are executed by Member 1 (`../Security/`).

| Threat ID | STRIDE | Asset / function | Threat description | Existing control observed | L | I | Risk | Derived test(s) | Outcome |
|---|---|---|---|---|---|---|---|---|---|
| T-01 | **S**poofing | Login | Attacker guesses passwords; learns which usernames exist | Generic error message; slow scrypt hash | 2 | 3 | 6 | TC-SEC-001, 002 | No throttling → DEF-006 |
| T-02 | **S**poofing | Registration | Second account created with a victim's username | None | 3 | 2 | 6 | TC-SEC-004 | DEF-008 |
| T-03 | **S**poofing | Session cookie | Reuse after logout; forge cookie using known secret | `session.clear()` on logout | 2 | 3 | 6 | TC-SEC-003, 013 | Secret in source → DEF-005 |
| T-04 | **T**ampering | Task API | Edit/delete another user's task by changing the id (IDOR) | GET/PUT scoped by user_id | 3 | 3 | **9** | TC-SEC-005, 006 | DELETE unscoped → DEF-003 |
| T-05 | **T**ampering / **I**nfo disclosure | Search `q` | SQL injection to read/alter other data | UI search parameterised | 3 | 3 | **9** | TC-SEC-007, 008 | API search injectable → DEF-001 |
| T-06 | **T**ampering | Task title | Stored XSS runs script in the victim's browser | Jinja autoescape (overridden by `|safe`) | 3 | 3 | **9** | TC-SEC-009 | DEF-002 |
| T-07 | **T**ampering | Web forms | CSRF: external page submits delete/toggle as the user | None | 2 | 2 | 4 | TC-SEC-010 | DEF-004 |
| T-08 | **R**epudiation | All actions | User denies deleting a task; no audit trail | Only `created_at` / `completed_at` | 2 | 1 | 2 | Review only | Observation (no log) |
| T-09 | **I**nfo disclosure | Password store | Passwords readable if DB copied | Werkzeug scrypt hashing | 1 | 3 | 3 | TC-SEC-011 | Control works |
| T-10 | **I**nfo disclosure | Errors, cookies, config | Stack traces / debugger, JS-readable cookie, secret in repo | HttpOnly cookie | 3 | 2 | 6 | TC-SEC-012, 013, 014 | DEF-005, DEF-009 |
| T-11 | **D**enial of service | Task create; login | Huge inputs fill DB; bad date breaks a user's list; login CPU exhaustion | None | 2 | 2 | 4 | TC-SEC-014, 015; perf TC-PERF-004 | DEF-007, DEF-009 |
| T-12 | **E**levation of privilege | Protected pages / API | Use features without logging in | `login_required_*` decorators | 1 | 3 | 3 | TC-SEC-016, 017 | Control works |

**Highest risks (9):** T-04, T-05, T-06. All three were confirmed as Critical defects. Controls that work: password hashing (T-09), route protection (T-12), generic login errors (part of T-01).
