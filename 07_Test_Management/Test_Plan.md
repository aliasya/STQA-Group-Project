# Software Test Plan and Test Strategy – PyTodo Pro

**Owner:** Member 1 (QA/Test Lead) · **Structure based on:** IEEE 829 / ISO/IEC/IEEE 29119-3 test plan outline · **Version:** 2.0 (formalised Week 7)

| Version | Week | Change | Reason |
|---|---|---|---|
| 0.1 | 1 | Draft: scope, risk-based priorities, roles | Project start |
| 0.5 | 3 | Added compatibility configurations CFG-01 to CFG-06 | Browsers actually available to the team |
| 0.8 | 5 | Security raised to highest priority; added security exit criterion | Weeks 4–5 confirmed Critical security defects |
| 1.0 | 6 | Added regression strategy (xfail for known defects) | Automation week |
| 2.0 | 7 | Formalised all sections using evidence from Weeks 1–6 | Week 7 requirement |

---

## 1. Introduction

This plan defines how the QA team evaluates the quality of PyTodo Pro v1 (course build). We act as an **independent QA team**: we design, execute and report tests, but we do **not** modify the application.

- **Testing:** executing the app to find defects (Weeks 1–6).
- **Quality control:** checking the product against requirements (test results, defect log).
- **Quality assurance:** improving the *process*: conventions, reviews, traceability, CI recommendations (Weeks 7–9).

## 2. Test items

| Item | Version / location |
|---|---|
| PyTodo Pro web UI + REST API | `app/` (Flask 3.0.3), unmodified course build |
| Business rules | `app/helpers.py` |
| Database schema | created by `init_db()` in `app/app.py` |

## 3. Features to be tested / not tested

**To be tested:** REQ-01 to REQ-17 (see `01_Black_Box/Application_Overview.md`). Priority follows the risk matrix: REQ-03 and REQ-16 (risk 9) first, then the risk-6 features.

**Not tested (with reason):**

| Not tested | Reason |
|---|---|
| Production deployment (HTTPS, WSGI server, reverse proxy) | App is only provided for local use |
| Load above 50 concurrent users, soak/endurance tests | Dev server on student laptops; not representative |
| Uncontrolled penetration testing / automated scanners | Course rule; ethical scope |
| Safari / macOS, legacy browsers | Not available to the team |
| Backup/restore, data migration, localisation | Feature does not exist |

## 4. Test objectives (measurable)

| # | Objective | Target | Result |
|---|---|---|---|
| O1 | Every requirement has at least one executed test | 17 / 17 REQs | see RTM |
| O2 | Every high-risk (≥6) requirement tested with ≥2 techniques | 100 % | see RTM |
| O3 | Branch coverage of `helpers.py` | ≥ 90 % | M3 to report |
| O4 | Branch coverage of `app.py` (all automated suites) | ≥ 70 % | M3 to report |
| O5 | All defects reproducible, classified, traced to a test | 100 % | see defect log |
| O6 | Automated regression suite covers all Critical/Major defects | 100 % | M3 to report |

## 5. Test strategy

| Level / type | Week | Technique | Tool | Applied to (why) | Owner |
|---|---|---|---|---|---|
| Black-box functional | 1 | EP, BVA, decision table, state transition | Manual (browser) + scripted runner | Validation rules (REQ-01, 04), date boundaries (REQ-09), filter combinations (REQ-08), task/session states | M2 |
| White-box unit | 2 | Statement + branch coverage, basis paths, data flow | PyTest, pytest-cov | `helpers.py`: all business rules, highest decision density, pure functions | M3 |
| GUI + compatibility | 3 | Checklist, configuration matrix | Selenium screenshot script + manual review | All pages; browsers the team owns | M1 |
| Usability + accessibility | 3 | Heuristic evaluation, WCAG 2.1 AA checks | Manual, contrast calculator, keyboard | All pages | M4 |
| Web + API | 4 | Valid/invalid/missing/wrong-type/edge requests, status codes, UI-vs-API | PyTest + Flask test client (Postman optional) | All `/api` endpoints | M3 |
| Security | 5 | STRIDE → derived test cases | PyTest | Auth, access control, input handling, config | M1 (tests), M4 (STRIDE) |
| Performance | 5 | Controlled load steps (1–50 users) | Python threaded load script | Busiest endpoints: task list, dashboard, login | M3 run, M4 evaluate |
| Automation + regression | 6 | Candidate selection (repetition, stability, criticality, regression value) | PyTest markers, Selenium | Critical paths + every Critical/Major defect | M3 |

**Principles**
- Expected results are written **before** execution and come from the requirement, not from the app's current behaviour.
- Tools support test design; they don't replace it. Every automated test maps to a designed test case or requirement.
- Earlier artefacts are revised when later evidence changes our understanding (see revision tables).

## 6. Test environment

| ID | Used for | Hardware / OS | Software |
|---|---|---|---|
| E1 | Automated suites, screenshots CFG-01/04, performance run | Linux container, 2 logical CPUs | Python 3.13, Flask 3.0.3, PyTest 9, pytest-cov, Selenium 4.54, Chrome 153 (headless) |
| E2 | Manual testing, CFG-02/03 | `<<Member laptop: model, CPU, RAM>>`, Windows 11 | `<<Python 3.x>>`, Firefox `<<ver>>`, Edge `<<ver>>` |
| E3 | Mobile check CFG-05 | `<<phone model>>`, Android/iOS `<<ver>>` | Chrome/Safari mobile |

Database: SQLite. Automated tests create a new temporary DB per test (`conftest.py`), so runs are independent and repeatable.

## 7. Test data

- Accounts created per test (`alice`, `mallory`, `tester01`…). No shared accounts, no real personal data.
- Boundary data: usernames of 2/3/20/21 chars; passwords of 7/8/9 chars; due dates today−1, today, today+1, +2, +3; titles of 0, 1 and 100,000 chars.
- Security payloads: `' OR 1=1` style strings, `<script>` tag, malformed dates, wrong JSON types.
- Performance: one user with 50 tasks.

## 8. Roles and responsibilities

| Member | Role | Responsibilities |
|---|---|---|
| M1 Alia | QA/Test Lead | Scope, schedule, conventions, reviews, overview, GUI/compatibility, security tests, test plan, final report, presentation |
| M2 | Test Design Coordinator | Requirements analysis, black-box design + execution, RTM, master test repository |
| M3 | Automation/Tool Coordinator | White-box, coverage, API suite, performance execution, automation, regression suite |
| M4 | Defect & Metrics Coordinator | Usability/accessibility, STRIDE, defect log, metrics, risk register, performance evaluation |

All members install the app, execute tests, collect evidence and present.

## 9. Schedule

| Week | Activity | Deliverable | Due |
|---|---|---|---|
| 1 | Explore app, black-box | Overview, risk matrix, black-box cases | `<<date>>` |
| 2 | White-box + coverage | Unit tests, coverage report | `<<date>>` |
| 3 | GUI, compatibility, usability, accessibility | Checklists, matrix, findings | `<<date>>` |
| 4 | Web + API | API suite | `<<date>>` |
| 5 | Security + performance | STRIDE, security tests, perf results | `<<date>>` |
| 6 | Automation + regression | Regression suite | `<<date>>` |
| 7 | Test management | This plan, RTM, defect log | `<<date>>` |
| 8 | Metrics + evaluation | Final QA report | `<<date>>` |
| 9 | Standards + presentation | Slides, live demo | `<<date>>` |

## 10. Entry criteria

- App installs with `pip install -r requirements.txt` and starts on `http://127.0.0.1:5000`.
- Requirement list (REQ-01–17) agreed by the team.
- Test cases for the week peer-reviewed by M1 (IDs, expected results present).
- Test environment recorded (section 6).

## 11. Exit criteria

- 100 % of planned High-priority test cases executed; ≥ 90 % of all planned cases executed.
- Every failed test has a logged, reproducible defect with severity and priority.
- RTM complete: every REQ traced to ≥1 executed test.
- Coverage targets O3/O4 met, or the shortfall explained.
- **Open Critical defects do not block exit** (we cannot fix the app). They must be reported as residual risk with a recommendation.

## 12. Suspension and resumption criteria

| Suspend when | Resume when |
|---|---|
| App cannot start or login is broken (blocks > 50 % of tests) | Environment fixed; smoke test (TC-BB-001, 012) passes |
| A defect corrupts the test database (e.g. DEF-009 breaks a user's task list) | Fresh database/user created; affected tests re-run |
| Tool failure (WebDriver/browser mismatch) | Driver updated; UI tests re-run |

## 13. Risks and contingencies

| Risk | Type | L | I | Contingency |
|---|---|---|---|---|
| A member misses a deliverable | Project | 2 | 3 | Backup artefacts kept in `_BACKUP_Members_2_3_4/`; M1 reassigns |
| Browser/WebDriver version mismatch | Project | 2 | 2 | Selenium Manager; screenshots as fallback evidence |
| Date-dependent tests change result over time | Project | 2 | 2 | Tests use relative dates or injected `today` |
| Performance results vary between laptops | Project | 3 | 1 | Record environment; compare trends, not absolute numbers |
| Critical security defects in product | Product | 3 | 3 | Report first, with fix recommendation and regression tests |
| Untested configurations (Safari, production) | Product | 2 | 2 | Listed as residual risk |

## 14. Deliverables

Test plan (this file), test cases per week, automated scripts, execution logs/screenshots, RTM, defect log, metrics, final QA report, presentation and live demo. See `README.md` section 6.

## 15. Limitations

- The application is tested as delivered. Fixes are recommended, never applied, so retesting of fixes is out of scope.
- Specification is informal (README + code comments). Where the spec is ambiguous (e.g. whether "letters" includes accented letters), we record an **observation**, not a defect.
- Testing shows the presence of defects, not their absence. Passing tests do not prove the app is defect-free.
