# PyTodo Pro – Final Integrated QA Evaluation Report

> **Compiled by Member 1 (QA Lead).** Sections without a ⬜ marker are written. ⬜ sections are inserted from each member's folder. Before submission, re-check every number against section 5 and every DEF-ID against the consolidated defect register (DEF-001 to DEF-017, report Table 7.6).

**Course:** TEB3433 Software Testing and Quality Assurance · **Team:** Alia (QA Lead), Hanisah (Test Design Coordinator), Fatin (Automation Coordinator), Intan (Defect & Metrics Coordinator) · **Date:** 27 November 2026

---

## 1. Executive summary

We evaluated PyTodo Pro, a Flask task manager with a web UI and REST API, over eight testing weeks. We executed **146 test cases** across black-box, white-box, GUI, usability/accessibility, API, security and performance testing, including a **14-test automated API regression suite**.

- **116 passed, 30 failed (pass rate 79.45 %)**. The failures trace to **17 distinct defects** (4 Critical, 2 Major, 6 Moderate, 5 Minor).
- **Overall verdict:** PyTodo Pro works for the common, well-formed single-user path. Registering, managing tasks, filtering and the dashboard all behave correctly for normal input, and in the local JMeter stress test 10 concurrent users was the highest load that met both targets (P95 < 500 ms, < 1 % errors). It is **not fit for release to real users**: four Critical defects let one user read or delete another user's data (SQL injection, IDOR delete), run script in other users' browsers (stored XSS), or permanently break their own task list with one malformed date.
- **Main pattern:** the same rule is implemented in several places and only some copies are correct (UI vs API validation, GET vs DELETE ownership checks, UI vs API search). Plus three off-by-one boundary defects in the business rules.
- Testing reduces uncertainty but cannot prove the absence of defects. Section 10 lists residual risks and untested areas.

## 2. Application overview

See `01_Black_Box/Application_Overview.md` (Member 1). Summary: one user role. 12 functional requirements (REQ-01–12: accounts, task CRUD, filters, urgency, dashboard, API) and 5 non-functional (REQ-13–17: usability, accessibility, compatibility, security, performance). Business rules live in `helpers.py`. Data is in SQLite. Highest initial risks: access control and security (risk 9), then urgency, registration, login, task creation and the API (risk 6).

## 3. Test approach

Full plan: `07_Test_Management/Test_Plan.md`. Testing was risk-based. High-risk requirements were tested first and with at least two techniques. Expected results came from the specification (README, code "Spec:" comments, UI hints), never from observed behaviour. Each week's evidence fed back into the plan (see its revision history). For example, white-box findings in Week 2 raised the urgency risk, and Week 4 API crashes moved security to top priority in Week 5.

| Week | Activity | Main technique / tool | Key outcome |
|---|---|---|---|
| 1 | Black-box | EP, BVA, decision tables, state transition | 27 cases, 2 fail: 8-character password rejected, due today shown as Overdue |
| 2 | White-box | Branch/path coverage, data flow (PyTest, pytest-cov) | 100 % branch coverage of `helpers.py`, 3 off-by-one defects |
| 3 | GUI, compatibility, usability, accessibility | Checklist, config matrix, heuristics, WCAG 2.1 | No mobile layout; form labels not linked to inputs; registration form clears input |
| 4 | Web + API | Valid, invalid and unauthorised requests | 23 manual cases (19 pass, 4 fail): cross-user deletion, 8-character password, duplicate usernames |
| 5 | Security + performance | STRIDE → tests (PyTest + manual); JMeter baseline + stress (5–400 users) | 4 Critical defects; 10 users = highest load meeting targets |
| 6 | Automation + regression | PyTest with Flask test client | 14 automated API tests: 11 pass, 3 fail (known defects) |
| 7 | Test management | Test plan, RTM, defect log | 17/17 requirements traced |
| 8 | Metrics + evaluation | This report | – |

## 4. Results by phase

### 4.1 Black-box (Week 1)
Manual black-box testing evaluated core user workflows (registration, login, task CRUD, filtering, search, and urgency classification) via the web UI in Chrome on Windows, without inspecting internal source code. **27 test cases** (`TC-BB-001` to `TC-BB-027`) were executed using Equivalence Partitioning (7), Boundary Value Analysis (12), decision tables (4), state-transition testing (3), and positive functional testing (1): **25 passed, 2 failed (92.59% pass rate)**.

| Technique | Executed | Passed | Failed | Key Findings / Defect ID |
|---|---|---|---|---|
| Equivalence Partitioning (EP) | 7 | 7 | 0 | Valid/invalid inputs, no due date, and title search behaved as specified |
| Boundary Value Analysis (BVA) | 12 | 10 | 2 | 8-char password rejected (`DEF-013`); due-today task labelled "Overdue" (`DEF-014`) |
| Decision Table | 4 | 4 | 0 | Category (`Study`) + status (`Open`) filter combinations worked as expected |
| State Transition | 3 | 3 | 0 | `Open → Done`, `Done → Open`, and task deletion transitions persisted accurately |
| Functional Positive | 1 | 1 | 0 | Edits to completed tasks saved and retained `Done` status |
| **Total** | **27** | **25** | **2** | **2 boundary defects confirmed** |

**Interpretation:** BVA was the most effective black-box technique, uncovering both off-by-one boundary defects (`DEF-013` on password length `= 8` and `DEF-014` on `due == today`), which were later confirmed independently during white-box testing of `helpers.py`.

### 4.2 White-box and coverage (Week 2)

White-box testing targeted the four business-rule functions in `helpers.py` (`is_valid_password`, `is_valid_username`, `compute_urgency`, `completed_in_last_n_days`), using control-flow analysis (V(G) = 3 for password validation, 5 for urgency) to derive path and boundary tests. **23 PyTest unit tests were executed: 20 passed, 3 failed**, with **100 % statement and branch coverage of `helpers.py`**. The three failures are off-by-one boundary defects: an 8-character password is rejected (`DEF-013`), a task due today is classified as Overdue (`DEF-014`), and a task completed exactly seven days ago is excluded from the dashboard count (`DEF-015`). Full coverage did not mean defect-free code: every failing branch was executed but compared against the wrong boundary. Coverage was measured for `helpers.py` only; `app.py` was not measured (residual risk).

### 4.3 GUI and compatibility (Week 3, Member 1)
18 GUI checks (`TC-GUI-101`–`118`) on Chrome desktop and Chrome mobile emulation: 14 Pass, 4 Fail. Forms, navigation, messages, confirmation dialogs and keyboard order work well. **No viewport meta tag**, so phones show a shrunken desktop page (DEF-010). Dates and badges wrap awkwardly at 1366 px (DEF-011). The registration form clears the entered values after a validation error (DEF-012), and a task due today is labelled Overdue (DEF-014). Edge was covered by Member 2's compatibility checks; Firefox and a real phone were not tested and are listed as residual risk.
- **Member 2 Week 3 Checks (GUI, Compatibility & WCAG Accessibility):** Executed **16 manual checks** on Chrome and Edge (`TC-GUI-001–007`, `TC-COMP-001–003`, `TC-ACC-001–006`): **15 passed, 1 failed**. Core layouts, Edge cross-browser workflows, keyboard focus/navigation, 200% zoom, non-colour status cues, and text contrast (`16.83:1`) passed, while `TC-ACC-005` failed because `<label>` elements on the New Task form lack native `for`/`id` associations (`DEF-017`).

### 4.4 Usability and Accessibility (Week 3)

Usability evaluation showed that PyTodo Pro provided generally clear navigation, consistent interface layouts and understandable feedback across the tested workflows. The empty-title validation displayed an appropriate error message, and the Cancel function prevented unintended task creation in the tested scenario. However, inconsistencies in password guidance and task urgency information could confuse users.

For accessibility, **6 test cases were executed, with 5 passed and 1 failed**, achieving an 83.3% pass rate. Keyboard navigation, visible focus indicators, 200% zoom, non-colour status indicators and the inspected text contrast passed. The failed test, **TC-ACC-005**, identified missing HTML label associations for the Title, Description, Category and Due Date fields, recorded as **DEF-017 (Minor)**. This may affect users relying on assistive technologies.

Overall, the application demonstrated acceptable usability and basic accessibility in the selected test scenarios. However, improvements to form-label associations and further accessibility testing, particularly with screen readers and additional contrast checks, are recommended. These results do not establish full WCAG 2.1 AA compliance.

### 4.5 Web and API (Week 4)

Web/API testing covered registration, login, task CRUD, completion, categories, the dashboard and cross-user access through the JSON API. **23 manual API test cases were executed (`API-001`–`023`): 19 passed, 4 failed.** Authentication was enforced (HTTP 401 without a session), and cross-user retrieval and modification were correctly refused (HTTP 404). The failures trace to three defects: an authenticated user can delete another user's task (`API-021`, `API-022` → `DEF-001`, Critical), an 8-character password is rejected (`API-015` → `DEF-013`), and duplicate usernames are accepted (`API-016` → `DEF-016`). The inconsistency is notable: ownership is checked for reading and editing a task but not for deleting it.

### 4.6 Security (Week 5, Member 1)
12 STRIDE threats → 17 test cases (22 executions): 7 cases pass, 10 fail. Critical: IDOR delete (DEF-001), SQL injection in API search (DEF-002), stored XSS (DEF-004), invalid date breaking a user's list (DEF-005). Also: no CSRF (DEF-006), hard-coded secret + debug mode (DEF-007), no login throttling (DEF-008), no input length limit (DEF-009), duplicate usernames (DEF-016). Member 4's manual security cases (SEC-001–008: 5 pass, 2 fail, 1 review finding) independently confirmed DEF-001 and DEF-002 and found the missing audit log (DEF-003). Working controls: scrypt password hashing, HttpOnly session cookie, login required on every protected route, no username enumeration.

### 4.7 Performance (Week 5)

Performance testing was conducted using Apache JMeter to evaluate PyTodo Pro under different concurrent user loads. The baseline test with 50 users recorded an average response time of 22.8 ms, a P95 response time of 57.7 ms and a 0% error rate. During stress testing, 10 concurrent users was the highest tested load that met both performance targets (P95 below 500 ms and error rate below 1%). Beyond this level, the error rate increased significantly, reaching 98.34% at 400 users. Database locking errors were also observed during concurrent task creation, indicating limitations in SQLite write handling. However, the tests were conducted locally on the same laptop, so the results should not be treated as production capacity measurements.

| Stress-test users | P95 response time | Error rate |
|---:|---:|---:|
| 5 | 144 ms | 0% |
| 10 | 301 ms | 0% |
| 25 | 1,082 ms | 0.13% |
| 50 | 741 ms | 60.86% |
| 100 | 308 ms | 88.84% |
| 200 | 509 ms | 95.06% |
| 400 | 125 ms | 98.34% |

Note: At high loads, response times can appear lower because many requests fail quickly. Therefore, response time must be interpreted together with the error rate.

### 4.8 Automation and regression (Week 6)

Repeatable, stable and high-risk manual API cases were selected for automation. **14 automated PyTest tests (`04_Web_API/test_api.py`, Flask test client, fresh temporary database per test) were executed: 11 passed, 3 failed.** Each automated test is mapped to its manual case in `06_Automation_Regression/Automation_Manual_Traceability.csv`. The three failures are the known defects `DEF-001` (cross-user deletion), `DEF-013` (8-character password) and `DEF-016` (duplicate usernames); the assertions state the correct behaviour, so these tests will pass once the defects are fixed. Together with the white-box and security suites, the group has 59 automated tests (43 pass, 16 fail) that run in under a minute and are executed by the CI pipeline (section 8).

## 5. Metrics

A total of 146 test cases were executed across the group's testing activities. Out of these, 116 passed and 30 failed, resulting in an overall pass rate of 79.45% and a failure rate of 20.55%. Security testing was the weakest area, with 12 out of 25 security test cases passing (48%). The STRIDE-related testing contributed 8 test cases, with 5 passed and 3 failed. These findings indicate that although most tested functions behaved as expected, security weaknesses and other defects still require attention.

| Metric | Result |
|---|---:|
| Planned test cases | 146 |
| Executed test cases | 146 |
| Passed | 116 |
| Failed | 30 |
| Blocked | 0 |
| Overall pass rate | 79.45% |
| Overall failure rate | 20.55% |
| Unique defects | 17 |

## 6. Defect analysis

The testing activities identified 17 unique defects after duplicate findings from different testing activities were consolidated. These consisted of 4 Critical, 2 Major, 6 Moderate and 5 Minor defects. The major root-cause themes included missing ownership checks, unsafe SQL query construction, insufficient input validation and incorrect boundary conditions. For example, an authenticated user could delete another user's task, SQL injection could expose other users' data, and certain date inputs could cause the task list to fail. All 17 defects remained open because the application was evaluated without applying fixes, meaning none could proceed to retesting or closure.

| Severity | Number of defects |
|---|---:|
| Critical | 4 |
| Major | 2 |
| Moderate | 6 |
| Minor | 5 |
| **Total** | **17** |

## 7. ISO/IEC 25010 mapping (Week 9)

| Characteristic | Sub-characteristics evaluated | How | Evidence quality |
|---|---|---|---|
| Functional suitability | Completeness, correctness, appropriateness | Black-box, white-box, API | **Direct, strong** |
| Security | Confidentiality, integrity, authenticity, accountability | STRIDE + security tests | **Direct** (accountability: review only) |
| Interaction capability (usability) | Learnability, operability, user error protection, UI aesthetics, inclusivity/accessibility | GUI checklist, heuristics, WCAG | **Direct, partial** (no real users, no screen reader) |
| Compatibility | Co-existence, interoperability (browsers) | Config matrix | **Partial** (Chrome desktop, Chrome mobile emulation, Edge; no Firefox, Safari or real device) |
| Performance efficiency | Time behaviour, capacity | Load experiment | **Direct, limited** (one machine) |
| Reliability | Faultlessness, fault tolerance | Error handling found by API/security tests | **Indirect** |
| Maintainability | Testability, modularity | Unit-testability of `helpers.py`; duplicated logic seen in review | **Indirect** |
| Flexibility / portability | Installability | Install from README | Indirect only |

**Not adequately evaluated:** reliability over time (availability, recoverability, soak), portability (other OS/hosting), compatibility on Safari/real devices, accountability (no audit log to test), maintainability metrics (complexity/duplication measures across `app.py`).

## 8. CI/CD and continuous testing (Week 9)

The automated suites are designed for continuous testing. `.github/workflows/regression.yml` shows the pipeline:

1. **On every push / pull request:** install dependencies, then run the white-box, API (regression) and security suites (59 tests, under a minute) and publish the results as a JUnit report.
2. **Known defects stay visible:** the tests assert the correct behaviour, so the 16 known-defect failures are reported on every run without blocking the build. When a defect is fixed its test turns green, which tells QA to retest and close it; any new failure shows up as a change from the expected count.
3. **Nightly:** a branch-coverage report of the application (`--cov=app --cov-branch`) is generated and stored as an artifact.
4. **Later stages (recommended):** turn known-defect tests into strict expected failures so the pipeline can gate merges, add a coverage threshold, a dependency audit (`pip-audit`), static analysis (`bandit`, which would flag the f-string SQL and `debug=True`) and an automated accessibility check.

## 9. QA and process improvements (Agile/DevOps)

QA activities that would have **prevented** these defects:

| Improvement | Prevents | When in the workflow |
|---|---|---|
| Acceptance criteria with explicit boundary examples ("8 chars → accepted", "due today → Due Today") in each user story | DEF-013, 014, 015 | Backlog refinement |
| Developer unit tests with BVA before merge (TDD for `helpers.py`) | DEF-013, 014, 015 | Development |
| Single shared validation/service layer used by both UI and API | DEF-001, 002, 005, 009 | Design / code review |
| Peer code review checklist: parameterised SQL, owner scoping on every query, no `|safe`, secrets from env | DEF-001, 002, 004, 007 | Pull request |
| Static analysis (bandit, flake8) in CI | DEF-002, 007 | CI |
| Security user stories from a STRIDE session per feature | DEF-003, 006, 008, 016 | Sprint planning |
| Definition of Done includes responsive + basic WCAG check | DEF-010, 011, 012, 017 | Sprint review |
| Automated regression suite in CI (section 8) | Reintroduction of all of the above | Continuous |

## 10. Residual risk assessment

Despite completing the planned testing activities, several risks remain unresolved. All 17 identified defects remain open, including four Critical defects that could affect data confidentiality, integrity and application functionality. In addition, code coverage was only measured for selected functions in `helpers.py`, while `app.py` coverage was not measured. Performance testing was conducted in a local environment using the same laptop for JMeter and the application, and therefore may not represent actual production workloads. Further testing is also required on Firefox, real mobile devices and other deployment environments. Security assessment was limited to the selected test cases and code review, without a dedicated vulnerability scanner or full penetration test. These limitations should be addressed before the application is considered ready for production use.

## 11. Prioritised recommendations

1. **(Critical, now)** Scope DELETE by owner; parameterise API search; remove `|safe`; validate due dates (DEF-001, 002, 004, 005).
2. **(High)** CSRF tokens + POST logout; secret from environment, debug off; throttle failed logins; UNIQUE usernames; audit logging of task changes (DEF-003, 006, 007, 008, 016).
3. **(High)** Fix the three boundary operators in `helpers.py` and add a "Due Today" dashboard counter (DEF-013, 014, 015).
4. **(Medium)** One shared validation function for UI and API (title length, types, category, paging) (DEF-009).
5. **(Medium)** Viewport tag, responsive table, labelled form controls, keep entered values after a validation error (DEF-010, 011, 012, 017).
6. **(Process)** Adopt the CI pipeline in section 8 and the practices in section 9.
7. **(Future testing)** Run the remaining compatibility configurations (Firefox, real phone); longer JMeter soak test with the server on a separate machine and CPU/memory recorded; Lighthouse/axe + NVDA accessibility pass; retest all 17 defects once fixed.

## 12. Limitations

- The app was tested as delivered; no fixes were applied, so no defect could be retested or closed.
- Informal specification. Ambiguities (e.g. accented letters in usernames) were recorded as observations.
- Automated runs and performance figures come from one environment (E1). Other machines will give different absolute numbers.
- Compatibility limited to the browsers available to the team. Usability judged by the team, not by representative users.
- Security testing was controlled and minimal. It proves the weaknesses exist but does not measure their full extent.
- **Testing shows the presence of defects, not their absence.** A 79.45 % pass rate does not mean the remaining behaviour is defect-free.

## 13. Conclusion

PyTodo Pro is functionally solid on its main path but has serious, easily fixable weaknesses in security, input validation and boundary logic, and its accessibility is limited. The evidence chain for every finding runs requirement → risk → technique → test case → observed result → defect → residual risk → recommendation, and can be followed through the RTM and defect log. Fixing the four Critical defects and running the regression suite in CI would raise the product to an acceptable quality level for a first release.

## Appendices

A. Test Plan – `07_Test_Management/Test_Plan.md` · B. RTM – `07_Test_Management/RTM.md` · C. Master test repository – `07_Test_Management/Master_Test_Repository.md` · D. Defect log – `07_Test_Management/Defect_Log.md`, defect evidence – `07_Test_Management/Defect_Evidence/Defect_Evidence_Index.md` · E. Member 3 metrics – `07_Test_Management/Member3_Metrics_and_HandOff.md` · F. Coverage – run the coverage command in README §3 (writes `htmlcov/index.html`) · G. Performance data – `05_Security_Performance/Performance/`
