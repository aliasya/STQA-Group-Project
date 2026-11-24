# Week 6 – Test Automation and Regression (BACKUP – Member 3)

Scripts: `test_regression.py` (19 tests, 23 executions, PyTest + Flask client) and `test_ui_selenium.py` (5 Selenium tests, headless Chrome).
Run the whole regression suite: `pytest -m regression -v`.

## 1. Automation candidate selection

Criteria from the brief: **repetition** (run after every change?), **stability** (same result every run, no timing/visual judgement), **criticality** (core feature or high risk), **regression value** (likely to break when code changes).

| Manual / earlier test | Repeated | Stable | Critical | Regression value | Automate? | Reason |
|---|---|---|---|---|---|---|
| Register / login / logout (TC-BB-001, 012, 013, 032) | ✔ | ✔ | ✔ | ✔ | **Yes** | Gateway to every feature |
| Password & username boundaries (TC-BB-004–010) | ✔ | ✔ | ✔ | ✔ | **Yes** (boundary 8 chars) | Off-by-one defect already found here |
| Duplicate username (TC-BB-011) | ✔ | ✔ | ✔ | ✔ | **Yes** | Open Major defect |
| Task CRUD (TC-BB-015, 029, 030, 034; TC-API-014, 031, 036) | ✔ | ✔ | ✔ | ✔ | **Yes** | Core function |
| Urgency boundaries (TC-BB-018–023) | ✔ | ✔ (relative dates) | ✔ | ✔ | **Yes** | Date logic easy to break |
| Filters (TC-BB-024–028) | ✔ | ✔ | ◐ | ✔ | **Yes** | SQL built in two places |
| IDOR, SQLi, XSS, bad date (TC-SEC-005, 007, 009, 014) | ✔ | ✔ | ✔ | ✔ | **Yes** | Critical defects must never silently return |
| Dashboard counts (TC-API-040) | ✔ | ✔ | ◐ | ✔ | **Yes** | Aggregates depend on urgency |
| Browser flows (register, create/toggle/delete, filter dropdown) | ✔ | ◐ (needs waits) | ✔ | ✔ | **Yes, few** (Selenium) | End-to-end check of templates + forms; kept small because UI tests are slower and more brittle |
| GUI layout / visual (TC-GUI-006, 014, 016) | ◐ | ✘ (pixel/visual judgement) | ✘ | ◐ | **No** | Needs human judgement; screenshots are captured by script instead |
| Usability / accessibility heuristics | ✘ | ✘ | ◐ | ✘ | **No** | Subjective evaluation |
| Performance load steps | ◐ | ✘ (varies by machine) | ◐ | ◐ | **Separate script** | Not pass/fail per commit |
| CSRF / secret-in-source checks | ◐ | ✔ | ✔ | ◐ | Kept in security suite | Configuration checks, not functional regression |

## 2. Manual-to-automated traceability

| Automated test | Manual test(s) / requirement | Known defect (xfail) |
|---|---|---|
| REG-001 register_and_login | TC-BB-001, TC-BB-012 / REQ-01, 02 | – |
| REG-002 wrong_password_rejected | TC-BB-013 / REQ-02 | – |
| REG-003 logout_ends_session | TC-BB-032, TC-SEC-003 / REQ-02 | – |
| REG-004 password_min_length_boundary | TC-BB-009, TC-WB-013 / REQ-01 | DEF-012 |
| REG-005 duplicate_username_rejected | TC-BB-011, TC-SEC-004 / REQ-01 | DEF-008 |
| REG-006 create_read_update_delete | TC-BB-015, 034, 030; TC-API-014, 031, 036 / REQ-04, 05, 07 | – |
| REG-007 toggle_done_and_reopen | TC-BB-029 / REQ-06 | – |
| REG-008 blank_title_rejected_by_api | TC-API-018 / REQ-04 | – |
| REG-009 blank_title_rejected_by_web_form | TC-BB-016 / REQ-04 | DEF-014 |
| REG-010 urgency_labels (×5) | TC-BB-018, 020–023 / REQ-09 | – |
| REG-011 urgency_due_today | TC-BB-019, TC-WB-004 / REQ-09 | DEF-013 |
| REG-012 filters | TC-BB-025, 028 / REQ-08 | – |
| REG-013 cannot_read_or_edit_other_users_task | TC-SEC-006, TC-API-038 / REQ-03 | – |
| REG-014 cannot_delete_other_users_task | TC-SEC-005, TC-API-039 / REQ-03 | DEF-003 |
| REG-015 search_is_injection_safe | TC-SEC-007 / REQ-08, 16 | DEF-001 |
| REG-016 title_is_escaped | TC-SEC-009 / REQ-16 | DEF-002 |
| REG-017 invalid_due_date_rejected | TC-SEC-014, TC-API-020 / REQ-04, 11 | DEF-009 |
| REG-018 protected_routes_require_login | TC-SEC-016, 017 / REQ-03 | – |
| REG-019 dashboard_counts | TC-API-040 / REQ-10 | – |
| UI-001 register_lands_on_task_list | TC-BB-001, TC-GUI-005 | – |
| UI-002 invalid_login_shows_error | TC-BB-013, TC-GUI-002 | – |
| UI-003 create_toggle_delete_task | TC-BB-015, 029, 030; TC-GUI-013 | – |
| UI-004 filter_by_status | TC-BB-026, TC-GUI-008 | – |
| UI-005 logged_out_user_redirected | TC-BB-032 | – |

## 3. Execution report

Command: `pytest _BACKUP_Members_2_3_4/06_Automation_Regression -v` (environment E1, Chrome 153 headless). Run 3 times in a row to check for flakiness:

| Run | Passed | XFAIL (known defects) | Failed | Time |
|---|---|---|---|---|
| 1 | 20 | 8 | 0 | 7.0 s |
| 2 | 20 | 8 | 0 | 7.0 s |
| 3 | 20 | 8 | 0 | 7.9 s |

The first Selenium version failed 3/5 tests: they read the page before the form submission had finished loading. Adding an explicit wait (`staleness_of` the old page) and resetting cookies before each test made the suite stable. This is a concrete example of automation brittleness.

## 4. Regression suite design

- **Marker-based:** every regression test carries `@pytest.mark.regression`, so `pytest -m regression` runs exactly this suite. UI tests also carry `ui`, so they can be skipped on machines without Chrome (`-m "regression and not ui"`).
- **Known defects as strict xfail:** a test that asserts correct behaviour for an open defect is marked `xfail(strict=True, reason="DEF-xxx")`.
  - While the defect is open, the suite is **green**, so it can gate CI without being permanently red.
  - When a developer fixes the defect, the test unexpectedly passes. Strict mode turns that into a **failure**, which tells QA to retest, close the defect and remove the marker.
- **Independent and repeatable:** each test gets a fresh SQLite DB (`conftest.py`). Dates are relative to today, so tests don't go stale.
- **When to run:** on every commit / pull request (≈ 7 s), and before every release.

## 5. Reflection: benefits and limitations

**Benefits**
- 28 checks in ~7 s versus ~45 min to repeat them by hand. Cheap enough to run on every change.
- Exact, repeatable assertions (status codes, JSON fields, counts) that humans skim over.
- Turns each confirmed defect into a permanent guard against reintroduction.

**Limitations**
- Automation only checks what we told it to check. It found **no new defects**; all of them came from designed manual/black-box tests.
- Selenium tests are slower and needed waits to stop flakiness. They also break if the HTML structure changes, even when behaviour is still correct.
- Visual, usability and accessibility quality can't be judged by these scripts.
- Tests rely on the current HTML (class names such as `.task-table`). A redesign would need script maintenance.
