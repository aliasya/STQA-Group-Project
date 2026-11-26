# PyTodo Pro – Final Integrated QA Evaluation Report

> **Compiled by Member 1 (QA Lead).** Sections without a ⬜ marker are written. ⬜ sections are inserted from each member's folder. Before submission, re-check every number against `Metrics.md` and every DEF-ID against `Defect_Log.md`.

**Course:** TEB3433 Software Testing and Quality Assurance · **Team:** Alia (QA Lead), Hanisah (Test Design Coordinator), `<<M3>>`, `<<M4>>` · **Date:** `<<submission date>>`

---

## 1. Executive summary

We evaluated PyTodo Pro, a Flask task manager with a web UI and REST API, over eight testing weeks. We ran **`<<N>>` detection test executions** across black-box, white-box, GUI, usability/accessibility, API, security and performance testing, plus a **`<<N>>`-check automated regression suite**.

- **`<<passed>>` passed, `<<failed>>` failed (pass rate `<<%>>`)**. The failures trace to **`<<N>>` distinct defects** (`<<n>>` Critical, `<<n>>` Major, `<<n>>` Moderate, `<<n>>` Minor). *(Fill from Metrics.md once Member 4 delivers.)*
- **Overall verdict:** PyTodo Pro works for the common, well-formed single-user path. Registering, managing tasks, filtering and the dashboard all behave correctly for normal input, and performance is adequate for 20 concurrent users. It is **not fit for release to real users**: four Critical defects let one user read or delete another user's data (SQL injection, IDOR delete), run script in other users' browsers (stored XSS), or permanently break their own task list with one malformed date.
- **Main pattern:** the same rule is implemented in several places and only some copies are correct (UI vs API validation, GET vs DELETE ownership checks, UI vs API search). Plus three off-by-one boundary defects in the business rules.
- Testing reduces uncertainty but cannot prove the absence of defects. Section 10 lists residual risks and untested areas.

## 2. Application overview

See `01_Black_Box/Application_Overview.md` (Member 1). Summary: one user role. 12 functional requirements (REQ-01–12: accounts, task CRUD, filters, urgency, dashboard, API) and 5 non-functional (REQ-13–17: usability, accessibility, compatibility, security, performance). Business rules live in `helpers.py`. Data is in SQLite. Highest initial risks: access control and security (risk 9), then urgency, registration, login, task creation and the API (risk 6).

## 3. Test approach

Full plan: `07_Test_Management/Test_Plan.md`. Testing was risk-based. High-risk requirements were tested first and with at least two techniques. Expected results came from the specification (README, code "Spec:" comments, UI hints), never from observed behaviour. Each week's evidence fed back into the plan (see its revision history). For example, white-box findings in Week 2 raised the urgency risk, and Week 4 API crashes moved security to top priority in Week 5.

| Week | Activity | Main technique / tool | Key outcome |
|---|---|---|---|
| 1 | Black-box | EP, BVA, decision tables, state transition | 35 cases, 7 fail: password = 8, due today, duplicate user, blank title |
| 2 | White-box | Branch/path coverage, data flow (PyTest, pytest-cov) | 100 % branch coverage of `helpers.py`, 3 off-by-one defects |
| 3 | GUI, compatibility, usability, accessibility | Checklist, config matrix, heuristics, WCAG 2.1 | No mobile layout; missing labels; low contrast |
| 4 | Web + API | Valid/invalid/type/edge requests | 3 server crashes, weak validation on PUT/DELETE |
| 5 | Security + performance | STRIDE → tests; load steps 1–50 users | 3 Critical security defects; meets 20-user target |
| 6 | Automation + regression | PyTest markers, Selenium, strict xfail | 28 checks in ~7 s, stable over 3 runs |
| 7 | Test management | Test plan, RTM, defect log | 17/17 requirements traced |
| 8 | Metrics + evaluation | This report | – |

## 4. Results by phase

### 4.1 Black-box (Week 1)
Manual black-box testing evaluated core user workflows (registration, login, task CRUD, filtering, search, and urgency classification) via the web UI in Chrome on Windows, without inspecting internal source code. **27 test cases** (`TC-BB-001` to `TC-BB-027`) were executed using Equivalence Partitioning (7), Boundary Value Analysis (12), decision tables (4), state-transition testing (3), and positive functional testing (1): **25 passed, 2 failed (92.59% pass rate)**.

| Technique | Executed | Passed | Failed | Key Findings / Defect ID |
|---|---|---|---|---|
| Equivalence Partitioning (EP) | 7 | 7 | 0 | Valid/invalid inputs, no due date, and title search behaved as specified |
| Boundary Value Analysis (BVA) | 12 | 10 | 2 | 8-char password rejected (`DEF-012`); due-today task labelled "Overdue" (`DEF-013`) |
| Decision Table | 4 | 4 | 0 | Category (`Study`) + status (`Open`) filter combinations worked as expected |
| State Transition | 3 | 3 | 0 | `Open → Done`, `Done → Open`, and task deletion transitions persisted accurately |
| Functional Positive | 1 | 1 | 0 | Edits to completed tasks saved and retained `Done` status |
| **Total** | **27** | **25** | **2** | **2 boundary defects confirmed** |

**Interpretation:** BVA was the most effective black-box technique, uncovering both off-by-one boundary defects (`DEF-012` on password length `= 8` and `DEF-013` on `due == today`), which were later confirmed independently during white-box testing of `helpers.py`[cite: 18, 19, 25, 26, 82, 83, 103].

### 4.2 White-box and coverage (Week 2)

> ⬜ **INSERT (Member 3).** Summarise results from `02_White_Box_Coverage/README.md`: executed / passed / failed, key defects, interpretation (3–6 sentences or a short table).
> Backup text: `_BACKUP_Members_2_3_4/08_Final_QA_Report/Final_QA_Report_COMPLETE.md` – same section.

### 4.3 GUI and compatibility (Week 3, Member 1)
18 GUI checks on Chrome desktop: 14 Pass, 4 Fail. Forms, navigation, messages, confirmation dialogs and keyboard order work well. **No viewport meta tag**, so phones show a shrunken desktop page (DEF-010). Dates and badges wrap awkwardly (DEF-011). 2 of 6 planned configurations were executed. Firefox, Edge and a real phone are listed as residual risk.
- **Member 2 Week 3 Checks (GUI, Compatibility & WCAG Accessibility):** Executed **16 manual checks** on Chrome and Edge (`TC-GUI-001–007`, `TC-COMP-001–003`, `TC-ACC-001–006`): **15 passed, 1 failed**. Core layouts, Edge cross-browser workflows, keyboard focus/navigation, 200% zoom, non-colour status cues, and text contrast (`16.83:1`) passed, while `TC-ACC-005` failed because `<label>` elements on the New Task form lack native `for`/`id` associations (`DEF-017`).

### 4.4 Usability and Accessibility (Week 3)

Usability evaluation showed that PyTodo Pro provided generally clear navigation, consistent interface layouts and understandable feedback across the tested workflows. The empty-title validation displayed an appropriate error message, and the Cancel function prevented unintended task creation in the tested scenario. However, inconsistencies in password guidance and task urgency information could confuse users.

For accessibility, **6 test cases were executed, with 5 passed and 1 failed**, achieving an 83.3% pass rate. Keyboard navigation, visible focus indicators, 200% zoom, non-colour status indicators and the inspected text contrast passed. The failed test, **TC-ACC-005**, identified missing HTML label associations for the Title, Description, Category and Due Date fields, recorded as **DEF-017 (Minor)**. This may affect users relying on assistive technologies.

Overall, the application demonstrated acceptable usability and basic accessibility in the selected test scenarios. However, improvements to form-label associations and further accessibility testing, particularly with screen readers and additional contrast checks, are recommended. These results do not establish full WCAG 2.1 AA compliance.

### 4.5 Web and API (Week 4)

> ⬜ **INSERT (Member 3).** Summarise results from `04_Web_API/README.md`: executed / passed / failed, key defects, interpretation (3–6 sentences or a short table).
> Backup text: `_BACKUP_Members_2_3_4/08_Final_QA_Report/Final_QA_Report_COMPLETE.md` – same section.

### 4.6 Security (Week 5, Member 1)
12 STRIDE threats → 17 test cases (22 executions): 7 cases pass, 10 fail. Critical: SQL injection in API search (DEF-001), stored XSS (DEF-002), IDOR delete (DEF-003), invalid date breaking a user's list (DEF-009). Also: no CSRF (DEF-004), hard-coded secret + debug mode (DEF-005), duplicate usernames (DEF-008), no login throttling (DEF-006), no input length limit (DEF-007). Working controls: scrypt password hashing, HttpOnly session cookie, login required on every protected route, no username enumeration.

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

> ⬜ **INSERT (Member 3).** Summarise results from `06_Automation_Regression/README.md`: executed / passed / failed, key defects, interpretation (3–6 sentences or a short table).
> Backup text: `_BACKUP_Members_2_3_4/08_Final_QA_Report/Final_QA_Report_COMPLETE.md` – same section.

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
| Compatibility | Co-existence, interoperability (browsers) | Config matrix | **Partial** (2/6 configs) |
| Performance efficiency | Time behaviour, capacity | Load experiment | **Direct, limited** (one machine) |
| Reliability | Faultlessness, fault tolerance | Error handling found by API/security tests | **Indirect** |
| Maintainability | Testability, modularity | Unit-testability of `helpers.py`; duplicated logic seen in review | **Indirect** |
| Flexibility / portability | Installability | Install from README | Indirect only |

**Not adequately evaluated:** reliability over time (availability, recoverability, soak), portability (other OS/hosting), compatibility on Safari/real devices, accountability (no audit log to test), maintainability metrics (complexity/duplication measures across `app.py`).

## 8. CI/CD and continuous testing (Week 9)

The regression suite is designed for continuous testing. `.github/workflows/regression.yml` shows the pipeline:

1. **On every push / pull request:** install dependencies, then run `pytest -m "regression and not ui"`. Takes seconds and gates the merge.
2. **Nightly:** full suite including Selenium UI tests, security tests and the coverage report (artifact).
3. **Strict xfail** keeps the pipeline green while known defects are open, and turns red when a defect is fixed or a new failure appears. QA then retests and closes the defect.
4. **Coverage threshold** (`--cov-fail-under=75`) stops coverage from quietly dropping.
5. **Later stages (recommended):** dependency audit (`pip-audit`), static analysis (`bandit`, which would flag the f-string SQL and `debug=True`), and a Lighthouse accessibility check.

## 9. QA and process improvements (Agile/DevOps)

QA activities that would have **prevented** these defects:

| Improvement | Prevents | When in the workflow |
|---|---|---|
| Acceptance criteria with explicit boundary examples ("8 chars → accepted", "due today → Due Today") in each user story | DEF-012, 013, 015 | Backlog refinement |
| Developer unit tests with BVA before merge (TDD for `helpers.py`) | DEF-012, 013, 015 | Development |
| Single shared validation/service layer used by both UI and API | DEF-014, 017, 001, 003 | Design / code review |
| Peer code review checklist: parameterised SQL, owner scoping on every query, no `|safe`, secrets from env | DEF-001–005 | Pull request |
| Static analysis (bandit, flake8) in CI | DEF-001, 005 | CI |
| Security user stories from a STRIDE session per feature | DEF-003, 004, 006, 008 | Sprint planning |
| Definition of Done includes responsive + basic WCAG check | DEF-010, 011, 021, 022 | Sprint review |
| Automated regression suite in CI (section 8) | Reintroduction of all of the above | Continuous |

## 10. Residual risk assessment

Despite completing the planned testing activities, several risks remain unresolved. All 17 identified defects remain open, including four Critical defects that could affect data confidentiality, integrity and application functionality. In addition, code coverage was only measured for selected functions in `helpers.py`, while `app.py` coverage was not measured. Performance testing was conducted in a local environment using the same laptop for JMeter and the application, and therefore may not represent actual production workloads. Further testing is also required on Firefox, real mobile devices and other deployment environments. Security assessment was limited to the selected test cases and code review, without a dedicated vulnerability scanner or full penetration test. These limitations should be addressed before the application is considered ready for production use.

## 11. Prioritised recommendations

1. **(Critical, now)** Parameterise API search; remove `|safe`; scope DELETE by owner; validate due dates (DEF-001, 002, 003, 009).
2. **(High)** CSRF tokens + POST logout; secret from environment, debug off; UNIQUE usernames (DEF-004, 005, 008).
3. **(High)** Fix the three boundary operators in `helpers.py` and add a "Due Today" dashboard counter (DEF-012, 013, 015).
4. **(Medium)** One shared validation function for UI and API (title, types, category, paging) (DEF-014, 016–020, 007).
5. **(Medium)** Viewport tag, responsive table, labelled controls, contrast fixes, flash messages (DEF-010, 011, 021–023).
6. **(Process)** Adopt the CI pipeline in section 8 and the practices in section 9.
7. **(Future testing)** Run the remaining compatibility configurations; Locust mixed read/write + soak test; Lighthouse/axe + NVDA accessibility pass; retest all 23 defects once fixed.

## 12. Limitations

- The app was tested as delivered; no fixes were applied, so no defect could be retested or closed.
- Informal specification. Ambiguities (e.g. accented letters in usernames) were recorded as observations.
- Automated runs and performance figures come from one environment (E1). Other machines will give different absolute numbers.
- Compatibility limited to the browsers available to the team. Usability judged by the team, not by representative users.
- Security testing was controlled and minimal. It proves the weaknesses exist but does not measure their full extent.
- **Testing shows the presence of defects, not their absence.** A 72 % pass rate does not mean the remaining behaviour is defect-free.

## 13. Conclusion

PyTodo Pro is functionally solid on its main path but has serious, easily fixable weaknesses in security, input validation and boundary logic, and its accessibility is limited. The evidence chain for every finding runs requirement → risk → technique → test case → observed result → defect → residual risk → recommendation, and can be followed through the RTM and defect log. Fixing the four Critical defects and running the regression suite in CI would raise the product to an acceptable quality level for a first release.

## Appendices

A. Test Plan – `07_Test_Management/Test_Plan.md` · B. RTM – `07_Test_Management/RTM.md` · C. Master test repository – `07_Test_Management/Master_Test_Repository.md` · D. Defect log – `07_Test_Management/Defect_Log.md` · E. Metrics – `07_Test_Management/Metrics.md` · F. Coverage HTML – `02_White_Box_Coverage/coverage_html/index.html` · G. Performance data – `05_Security_Performance/Performance/`
