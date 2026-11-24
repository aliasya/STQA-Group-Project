# Application Overview, Feature Inventory and Initial Scope/Risk Matrix

**Owner:** Member 1 (QA/Test Lead) · **Week:** 1 · **Version:** 1.2

| Version | Date | Change | Reason |
|---|---|---|---|
| 1.0 | Week 1 | Initial inventory and risk matrix from exploring the UI and README | Project start |
| 1.1 | Week 2 | Raised REQ-09 likelihood to 3 | White-box review: `due <= today` boundary looked wrong |
| 1.2 | Week 5 | Raised REQ-03, REQ-08 and REQ-16 impact/likelihood | Security testing confirmed IDOR, SQL injection, XSS |

---

## 1. Purpose of the application

PyTodo Pro is a single-user-per-account task manager. A user registers, logs in, and manages personal tasks. Each task has a title, description, category, due date and done flag. The app shows an urgency label for each task and a summary dashboard. All features are available as a web UI (Flask + Jinja templates) and as a JSON REST API.

## 2. Architecture (as observed)

| Layer | Technology | Notes relevant to testing |
|---|---|---|
| Web UI | Flask 3.0.3, Jinja2 templates, one CSS file | Server-rendered HTML forms; no JavaScript framework |
| API | Flask JSON routes under `/api` | Session-cookie authentication (same session as the UI) |
| Business rules | `helpers.py` (pure Python) | Urgency, password/username validation, 7-day window. Ideal for white-box testing |
| Data | SQLite file `pytodo_pro.db` | Tables `users`, `categories` (seeded Work/Personal/Study/Urgent), `tasks` |
| Auth | Werkzeug password hashing + Flask signed session cookie | `SECRET_KEY` is set in source code |

## 3. Users

| User type | Description | Can do |
|---|---|---|
| Guest (logged out) | Anyone who opens the site | Register, log in, read `/api/categories` |
| Registered user | Logged-in account owner | Manage **own** tasks, view own dashboard, log out |
| API client | Script/app using the JSON API with a session cookie | Same as a registered user |
| *(No admin role)* | – | – |

## 4. Feature inventory and requirements

Requirements come from the app README, the code docstrings ("Spec:" comments) and the on-screen hints.

| REQ ID | Feature | Expected behaviour (test basis) | UI | API |
|---|---|---|---|---|
| REQ-01 | Registration | Username 3–20 chars, letters/numbers/underscore. Password **at least 8** chars. Username unique (implied). | `/register` | `POST /api/register` |
| REQ-02 | Login / logout | Valid credentials log in; invalid → generic error; logout ends session | `/login`, `/logout` | `POST /api/login` |
| REQ-03 | Access control | Must be logged in for task pages/API. A user can only see/change/delete **own** tasks | all | all |
| REQ-04 | Create task | Title required; description, category, due date optional | `/tasks/new` | `POST /api/tasks` |
| REQ-05 | Edit task | Change title/description/category/due date | `/tasks/<id>/edit` | `PUT /api/tasks/<id>` (partial) |
| REQ-06 | Complete / reopen | Toggle done ↔ open; completion time recorded | ○/✓ button | `PUT {"done": true}` |
| REQ-07 | Delete task | Task removed after confirmation | Delete button | `DELETE /api/tasks/<id>` |
| REQ-08 | List, filter, search | Filter by category and status; search title (partial) | `/` | `GET /api/tasks?category=&status=&q=&page=&per_page=` |
| REQ-09 | Urgency label | No due date / Overdue (past) / **Due Today** / Due Soon (1–2 days) / Upcoming (3+) / Done | Urgency column | `urgency` field |
| REQ-10 | Dashboard | Total, open, overdue, due soon, completed in last 7 days (inclusive) | `/dashboard` | `GET /api/dashboard` |
| REQ-11 | REST API behaviour | Correct JSON, status codes (201/400/401/404), pagination | – | all `/api/*` |
| REQ-12 | Categories | Four seeded categories available | dropdowns | `GET /api/categories` |
| REQ-13 | Usability (NFR) | Clear navigation, feedback, error prevention, consistency | all | – |
| REQ-14 | Accessibility (NFR) | Basic WCAG 2.1 AA: labels, contrast, keyboard use | all | – |
| REQ-15 | Compatibility (NFR) | Works on current Chrome, Firefox, Edge and a mobile browser | all | – |
| REQ-16 | Security (NFR) | Protects accounts and data: injection, XSS, CSRF, authZ, secrets | all | all |
| REQ-17 | Performance (NFR) | Acceptable response time for typical concurrent use | busy pages | busy endpoints |

## 5. Initial scope / risk matrix

**Likelihood (L)** = how likely the feature fails (1 low – 3 high). **Impact (I)** = harm if it fails (1 low – 3 high). **Risk = L × I** (1–9). High risk (≥6) features get the most techniques and are tested first.

| REQ | Feature | L | I | Risk | L/I justification | In scope | Planned techniques | Priority |
|---|---|---|---|---|---|---|---|---|
| REQ-03 | Access control | 3 | 3 | **9** | Several routes, each must scope by `user_id`. Easy to miss one. A miss leaks/destroys other users' data | Yes | Security (IDOR), API, decision table | 1 |
| REQ-16 | Security | 3 | 3 | **9** | Raw SQL in places, Jinja `|safe`, hard-coded secret. Breach = data loss | Yes | STRIDE-derived tests | 1 |
| REQ-09 | Urgency | 3 | 2 | **6** | Several date boundaries (today, +2, +3); `<=` vs `<` mistakes common | Yes | BVA, state transition, white-box | 1 |
| REQ-01 | Registration | 2 | 3 | **6** | Two validation rules with boundaries + uniqueness. Wrong rule locks users out | Yes | EP, BVA, decision table, white-box | 1 |
| REQ-02 | Login/logout | 2 | 3 | **6** | Gateway to everything; session handling | Yes | Decision table, state transition, security | 1 |
| REQ-04 | Create task | 2 | 3 | **6** | Two input paths (form + API) with separate validation code | Yes | EP, BVA, API | 1 |
| REQ-11 | REST API | 2 | 3 | **6** | Status codes and type handling often neglected | Yes | API testing | 2 |
| REQ-08 | Filter/search | 2 | 2 | 4 | Combinations of 3 filters; API builds SQL differently from UI | Yes | Decision table, API, security | 2 |
| REQ-10 | Dashboard | 2 | 2 | 4 | Depends on urgency + 7-day rule | Yes | EP, white-box | 2 |
| REQ-05 | Edit task | 2 | 2 | 4 | Re-uses create logic, partial updates | Yes | EP, API | 2 |
| REQ-07 | Delete task | 1 | 3 | 3 | Simple, but irreversible | Yes | State transition, API, security | 2 |
| REQ-06 | Complete/reopen | 1 | 2 | 2 | Simple toggle | Yes | State transition | 3 |
| REQ-14 | Accessibility | 2 | 2 | 4 | No ARIA, unlinked labels seen on first look | Yes | WCAG checklist | 2 |
| REQ-15 | Compatibility | 2 | 2 | 4 | Plain HTML/CSS, but no viewport tag seen | Yes | Config matrix | 2 |
| REQ-13 | Usability | 2 | 1 | 2 | Small app, few screens | Yes | Heuristic review | 3 |
| REQ-17 | Performance | 1 | 2 | 2 | Dev server + SQLite; low expected load | Yes (controlled) | Load experiment | 3 |
| REQ-12 | Categories | 1 | 1 | 1 | Seeded, read-only | Yes (light) | API | 3 |

**Out of scope:** production deployment (HTTPS, WSGI server, hosting), backup/restore, multi-language, load beyond 50 concurrent users, uncontrolled penetration testing.

## 6. Quality expectations (ISO/IEC 25010 view)

| Characteristic | Expectation for PyTodo Pro | Where it is tested |
|---|---|---|
| Functional suitability | Rules in section 4 hold, including boundaries | Wk 1, 2, 4 |
| Security | Confidentiality and integrity of each user's tasks | Wk 5 |
| Usability (incl. accessibility) | First-time user completes core tasks without help | Wk 3 |
| Compatibility | Same behaviour across browsers/screens | Wk 3 |
| Performance efficiency | Typical pages < 1 s at expected load | Wk 5 |
| Maintainability (testability) | Business logic unit-testable | Wk 2 |
| Reliability | No unhandled errors on bad input | Wk 4, 5 |

## 7. Initial observations from exploration (Week 1)

- Registration hint says "min 8 characters". Verify the boundary (BVA): exactly 8 must pass.
- Urgency CSS has a `badge-due-today` style, but no task ever showed "Due Today" during exploration. Test today's date.
- Code comments say "no uniqueness check" (register) and "deletes by id only" (API delete). Confirm both.
- The API search builds SQL with an f-string, unlike the UI search. Confirm in the security week.
- `templates/index.html` renders the title with `|safe`. Confirm it is exploitable.
