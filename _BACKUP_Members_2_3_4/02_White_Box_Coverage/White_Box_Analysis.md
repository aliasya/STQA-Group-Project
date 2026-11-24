# Week 2 – White-Box Testing and Coverage (BACKUP – Member 3)

Test file: `test_whitebox_helpers.py` (31 executions). Coverage HTML: `coverage_html/index.html`.

## 1. Selected units and justification

We test **all four functions in `helpers.py`**, not the whole application (as the brief requires).

| Unit | Importance | Complexity | Risk |
|---|---|---|---|
| `compute_urgency` | Drives the urgency column and 2 dashboard counters | 4 decisions, date arithmetic | High (REQ-09 risk 6) |
| `is_valid_password` | Gate for every account | 2 decisions, boundary rule | High (REQ-01) |
| `is_valid_username` | Gate for every account | 3 decisions + loop with compound condition | High (REQ-01) |
| `completed_in_last_n_days` | Dashboard "completed" counter | 3 decisions incl. compound `and` | Medium (REQ-10) |

All four are pure functions with injectable `today`/`now`, so every branch can be reached deterministically. `app.py` routes are exercised by the API and security suites instead (see coverage, section 5).

## 2. Control-flow analysis

### 2.1 `compute_urgency(due_date_str, today=None)`

```
N1  if today is None:            D1
N2      today = date.today()
N3  if not due_date_str:         D2 ──T──► N4 return "No due date"
N5  due = strptime(...)
N6  if due <= today:             D3 ──T──► N7 return "Overdue"
N8  delta = (due - today).days
N9  if delta <= 2:               D4 ──T──► N10 return "Due Soon"
N11 return "Upcoming"
```

Cyclomatic complexity **V(G) = decisions + 1 = 4 + 1 = 5**. Basis paths:

| Path | Route | Test |
|---|---|---|
| P1 | D1 F, D2 T | TC-WB-001, 002 |
| P2 | D1 F, D2 F, D3 T | TC-WB-003, 004 |
| P3 | D1 F, D2 F, D3 F, D4 T | TC-WB-005, 006 |
| P4 | D1 F, D2 F, D3 F, D4 F | TC-WB-007 |
| P5 | D1 T, … | TC-WB-008 |

**Finding from the CFG:** the spec has **five** outputs (incl. "Due Today") but the code has only **four** return statements. No path can ever return "Due Today", because D3 uses `<=`. A white-box review spots this without running anything; TC-WB-004 confirms it (DEF-013).

### 2.2 `is_valid_password` – V(G) = 3

`D1 not isinstance(str)` → False; `D2 len > 8`. Paths: non-str (TC-WB-010, 011), ≤ 8 (012, 013), > 8 (014). Boundary TC-WB-013 (`len == 8`) fails: the code uses `>` where the spec says "at least 8" (DEF-012).

### 2.3 `is_valid_username` – V(G) = 4 (+ loop)

`D1 not str`, `D2 not 3 <= len <= 20`, loop `D3 c.isalnum() or c == "_"` (compound). Tests cover each operand of the OR: alnum (018), `_` (020), neither (021), plus length branches (016, 017, 019) and empty string (022).

### 2.4 `completed_in_last_n_days` – V(G) = 5

`D1 not completed_at_str`, `D2 now is None`, `D3a total_seconds() > 0`, `D3b age.days < n`. Condition coverage of the compound `and`: D3a false (future, TC-WB-030), D3a true + D3b true (025–027), D3a true + D3b false (028, 029). TC-WB-028 (exactly 7 days) fails: spec says inclusive, code uses `<` (DEF-015).

## 3. Path and data-flow considerations

| Variable | Definition | Use | Issue |
|---|---|---|---|
| `due_date_str` | parameter (from DB / API JSON) | `strptime(...)` at N5 | **No validation between def and use.** Any string reaches `strptime`; a malformed one raises `ValueError`. In `app.py` the API stores the raw string, so the exception fires on *every later read* → HTTP 500 (DEF-009). TC-WB-009 documents this |
| `today` | parameter or N2 | N6, N8 | Correct: dependency injection makes the unit testable |
| `completed_at_str` | DB column written by `toggle_task` / PUT | `strptime` | Format guaranteed by the app's own writer. Safe as long as only the app writes it |
| `password` | parameter | `len()` | `isinstance` guard prevents type errors (good) |

## 4. White-box test cases and results

| Test Case ID | Unit | Path / branch | Input | Expected | Actual | Status | Defect ID |
|---|---|---|---|---|---|---|---|
| TC-WB-001 | compute_urgency | P1 | None | No due date | No due date | Pass | – |
| TC-WB-002 | compute_urgency | P1 | "" | No due date | No due date | Pass | – |
| TC-WB-003 | compute_urgency | P2 (past) | 2026-11-23 (today 11-24) | Overdue | Overdue | Pass | – |
| TC-WB-004 | compute_urgency | P2 (= today) | 2026-11-24 | Due Today | **Overdue** | Fail | DEF-013 |
| TC-WB-005 | compute_urgency | P3 (d=1) | 2026-11-25 | Due Soon | Due Soon | Pass | – |
| TC-WB-006 | compute_urgency | P3 (d=2) | 2026-11-26 | Due Soon | Due Soon | Pass | – |
| TC-WB-007 | compute_urgency | P4 (d=3) | 2026-11-27 | Upcoming | Upcoming | Pass | – |
| TC-WB-008 | compute_urgency | P5 (default today) | 2999-01-01 | Upcoming | Upcoming | Pass | – |
| TC-WB-009 | compute_urgency | data flow | "2026-13-45" | raises ValueError (documents risk) | ValueError | Pass | (DEF-009) |
| TC-WB-010–011 | is_valid_password | D1 T | None, 12345678 | False | False | Pass | – |
| TC-WB-012 | is_valid_password | D2 F | 7 chars | False | False | Pass | – |
| TC-WB-013 | is_valid_password | D2 boundary | 8 chars | True | **False** | Fail | DEF-012 |
| TC-WB-014 | is_valid_password | D2 T | 9 chars | True | True | Pass | – |
| TC-WB-015–022 | is_valid_username | D1, D2, loop T/F | 123, "ab", 21×a, "abc", 20×a, "ab_c9", "ab-c", "" | F,F,F,T,T,T,F,F | as expected | Pass | – |
| TC-WB-023 | is_valid_username | isalnum Unicode | "café" | (observation) | True | Pass | Observation |
| TC-WB-024–027 | completed_in_last_n_days | D1 T; D3 T | None; 1 h; 6 d; 6 d 23:59:59 | F, T, T, T | as expected | Pass | – |
| TC-WB-028 | completed_in_last_n_days | D3b boundary | exactly 7 days | True | **False** | Fail | DEF-015 |
| TC-WB-029–031 | completed_in_last_n_days | D3b F; D3a F; D2 T | 8 d; future; default now | F, F, F | as expected | Pass | – |

**31 executions: 28 Pass, 3 Fail.** All three failures are off-by-one comparison operators (`<=` vs `<`, `>` vs `>=`, `<` vs `<=`). This is the classic boundary defect that BVA and branch testing target.

## 5. Coverage report and interpretation

Command: `pytest _BACKUP_Members_2_3_4/02_White_Box_Coverage --cov=app --cov-branch --cov-report=term-missing`

| Suite(s) | File | Statements | Branches | Coverage |
|---|---|---|---|---|
| White-box only | helpers.py | 31 | 18 | **100 %** statement + branch |
| White-box only | app.py | 299 | 64 | 21 % (only import-time code) |
| White-box + API + security + regression | helpers.py | 31 | 18 | 100 % |
| White-box + API + security + regression | app.py | 299 | 64 | **76 %** (TOTAL 79 %) |

**Uncovered code in app.py (combined run) and why:**

| Lines | Code | Why uncovered | Matters? |
|---|---|---|---|
| 140–160, 165–176 | Web `register_page` / `login_page` POST | Unit/API suites use the JSON API; the web forms are exercised by the black-box runner and Selenium, which run outside this coverage session | Low: covered by other levels |
| 248–266 | Web `edit_task` | same | Low: covered by TC-BB-034/035 |
| 287–290, 296–305 | Web delete, web dashboard | same | Low |
| 202–212, 375 | Filter branches of the **web** task list (category/status/search) and the API `status=open` branch | Web filters only exercised by the black-box runner/Selenium; no API test uses `status=open` | Medium: add an API test for `status=open` |
| 481–482 | `if __name__ == "__main__"` | Never runs under a test runner | No |

**Interpretation:** 100 % branch coverage of `helpers.py` still left three real defects to be caught by **assertions on correct expected values**. Coverage shows what was executed, not what was verified. Combined coverage of 79 % is above the plan's 70 % target. The gaps are web-form routes tested at other levels, so remaining structural risk is low.
