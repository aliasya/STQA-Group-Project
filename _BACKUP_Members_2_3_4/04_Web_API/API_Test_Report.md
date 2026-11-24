# Week 4 – Web and API Testing (BACKUP – Member 3)

Suite: `test_api.py` (PyTest + Flask test client, fresh DB per test). Run: `pytest _BACKUP_Members_2_3_4/04_Web_API -v`.
Postman can be used for the live demo with the same requests. The PyTest suite is the source of truth.

## 1. Endpoints under test

| Endpoint | Method | Auth | Priority | Reason |
|---|---|---|---|---|
| `/api/register` | POST | No | High | Account creation, validation rules |
| `/api/login` | POST | No | High | Authentication |
| `/api/tasks` | GET | Yes | High | Filters, search, paging (SQL built here) |
| `/api/tasks` | POST | Yes | High | Input validation |
| `/api/tasks/<id>` | GET / PUT / DELETE | Yes | High | Ownership checks, partial update |
| `/api/dashboard` | GET | Yes | Medium | Aggregates |
| `/api/categories` | GET | No | Low | Seeded, read-only |

## 2. Web workflow scenarios

| Scenario | Steps | Covered by |
|---|---|---|
| W1 New user journey | register → create task → edit → complete → delete | TC-BB-001/015/034/029/030, UI-003 |
| W2 Find a task | create several → filter by category/status → search | TC-BB-024–028, TC-API-024 |
| W3 Client vs server validation | blank title in browser (blocked by `required`) vs spaces (passes) vs API (400) | TC-GUI-010, TC-BB-016, TC-API-041 |

## 3. API test cases – expected vs actual

| Test Case ID | Endpoint | Request / data | Expected status + body | Actual | Status | Defect ID |
|---|---|---|---|---|---|---|
| TC-API-001 | POST /api/register | valid | 201 `{id, username}` | 201 | Pass | – |
| TC-API-002–006 | POST /api/register | missing username / password, short username, short password, `{}` | 400 `{"error": …}` | 400 each | Pass | – |
| TC-API-007 | POST /api/register | password = 8 chars | 201 | 400 "invalid password" | Fail | DEF-012 |
| TC-API-008 | POST /api/register | existing username | 400/409 | 201 | Fail | DEF-008 |
| TC-API-009 | POST /api/login | valid | 200 `{id, username}` | 200 | Pass | – |
| TC-API-010 | POST /api/login | wrong password | 401 `{"error":"invalid credentials"}` | 401 | Pass | – |
| TC-API-011 | POST /api/login | non-JSON body | 400 (or 401) | 401 | Pass (observation: 400 would be more accurate) | – |
| TC-API-012 | 6 protected endpoints | no session | 401 `{"error":"authentication required"}` | 401 for all 6 | Pass | – |
| TC-API-013 | GET /api/categories | – | 200, 4 seeded names | Personal, Study, Urgent, Work | Pass | – |
| TC-API-014 | POST /api/tasks | all fields | 201, 10 keys, category name, urgency | 201, correct | Pass | – |
| TC-API-015 | POST /api/tasks | title only | 201, "No due date" | 201 | Pass | – |
| TC-API-016–018 | POST /api/tasks | no title / "" / "   " | 400 "title is required" | 400 | Pass | – |
| TC-API-019 | POST /api/tasks | `"title": 123` (wrong type) | 400 | **500** | Fail | DEF-016 |
| TC-API-020 | POST /api/tasks | `due_date "2026-13-45"` | 400; list still works | **500**, row saved, list then **500** | Fail | DEF-009 |
| TC-API-021 | POST /api/tasks | `category_id 999` | 400 | 201 (category null) | Fail | DEF-019 |
| TC-API-022 | GET /api/tasks | 12 tasks, defaults | 10 items, newest first | 10, "Task 11" first | Pass | – |
| TC-API-023 | GET /api/tasks?page=1 | – | last 2 items | Task 01, Task 00 | Pass | – |
| TC-API-024 | GET /api/tasks filters | category / status / q | only matching tasks | correct | Pass | – |
| TC-API-025–027 | GET /api/tasks | per_page=-1 / 0, page=-1 | 400 | 200 (per_page=-1 returns **all** rows) | Fail | DEF-020 |
| TC-API-028 | GET /api/tasks?q=Alia's | apostrophe | 200 | **500** (SQL error) | Fail | DEF-001 |
| TC-API-029 | GET /api/tasks/<id> | own task | 200 | 200 | Pass | – |
| TC-API-030 | GET /api/tasks/9999 | missing | 404 | 404 | Pass | – |
| TC-API-031 | PUT | `{"title":"y"}` only | other fields unchanged | description kept | Pass | – |
| TC-API-032 | PUT | done true → false | completed_at set then cleared; urgency Done | correct | Pass | – |
| TC-API-033 | PUT | `{"title":""}` | 400 | 200, title emptied | Fail | DEF-017 |
| TC-API-034 | PUT | `{"done":"false"}` | 400 or done=false | done = **true** | Fail | DEF-017 |
| TC-API-035 | PUT /api/tasks/9999 | missing | 404 | 404 | Pass | – |
| TC-API-036 | DELETE own task | – | 200, then GET 404 | correct | Pass | – |
| TC-API-037 | DELETE /api/tasks/9999 | missing | 404 | 200 `{"result":"ok"}` | Fail | DEF-018 |
| TC-API-038 | GET other user's task | – | 404 | 404 | Pass | – |
| TC-API-039 | DELETE other user's task | – | owner's task survives | deleted | Fail | DEF-003 |
| TC-API-040 | GET /api/dashboard | 4 tasks | `{total 4, open 3, overdue 1, due_soon 1, completed 1}` | exact match | Pass | – |
| TC-API-041 | UI vs API | blank title both ways | both reject | API 400, UI creates blank task | Fail | DEF-014 |
| TC-API-042 | UI vs API | task due tomorrow | same urgency in JSON and HTML | "Due Soon" in both | Pass | – |

**Executions:** 47 (parameterised cases expanded) · **33 Pass · 14 Fail** · 70.2 %.

## 4. Interpretation

- **Happy paths are solid:** every valid request returns the right status and complete JSON. Paging, filters and partial update behave as documented.
- **Error handling is the weak area:** 3 inputs crash the server with 500 (wrong type, bad date, apostrophe). Several invalid inputs are silently accepted (unknown category, negative paging, empty title on PUT). The API validates on POST but not on PUT/DELETE.
- **UI and API disagree** on title validation (DEF-014). Server-side rules should live in one shared function.
- **Status codes:** DELETE always returns 200, even for missing or foreign tasks. This hides the IDOR (DEF-003) from API clients.

## 5. Limitations

Tested through Flask's test client (same WSGI stack, no network). One live run with `requests` against the dev server (performance script) gave the same codes. JSON schema validation and API rate limits were not tested.
