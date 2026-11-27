

# PyTodo Pro – Software Quality Assurance Project (TEB3433 STQA)

An independent QA evaluation of **PyTodo Pro**, a Flask task-management web app. We test the application; we don't change it.
This repository holds every QA artefact (test cases, scripts, evidence, defects, metrics, report and presentation).

---

## 1. Team

| Member | Name | Role | Main responsibility |
|---|---|---|---|
| Member 1 | Alia | QA / Test Lead | Application overview, test planning, GUI & compatibility testing, security testing, final report, presentation |
| Member 2 | Nur Hanisah | Test Design Coordinator | Black-box testing (EP, BVA, decision tables, state transitions), manual test cases, execution, RTM |
| Member 3 | Fatin Nurfarahanani | Automation / Tool Coordinator | White-box + PyTest, coverage, API testing, performance execution, automated regression |
| Member 4 | Intan Zahra Sofea | Defect & Metrics Coordinator | Usability & accessibility, defect tracking, STRIDE, performance evaluation, metrics, risk |

> **Status of each part:** see section 6.

---

## 2. Setup

Requirements: Python 3.10+ and Google Chrome (only needed for the Selenium UI tests). Selenium 4 downloads the matching ChromeDriver automatically.

```bash
# 1. create and activate a virtual environment
python -m venv venv
venv\Scripts\activate            # Windows
source venv/bin/activate         # macOS / Linux

# 2. install the app + test tools
pip install -r requirements-test.txt

# 3. run the application (only needed for manual testing)
cd app
python app.py                    # open http://127.0.0.1:5000/
```

`app/` contains the **unmodified** PyTodo Pro source code (the application under test).

---

## 3. Running the automated tests

All commands run from the **repository root** with the venv active. Each PyTest test gets its own temporary database, so the tests never touch `app/pytodo_pro.db`.

| What | Owner | Command | Expected result |
|---|---|---|---|
| Security tests (Wk5) | M1 | `pytest 05_Security_Performance/Security -v` | 22 tests: 12 pass, 10 fail |
| White-box unit tests (Wk2) | M3 | `pytest 02_White_Box_Coverage -v` | 23 tests: 20 pass, 3 fail |
| White-box coverage (Wk2) | M3 | `pytest 02_White_Box_Coverage --cov=app --cov-branch --cov-report=term-missing` | 100 % statement + branch coverage of `helpers.py` |
| API suite = automated regression (Wk4/Wk6) | M3 | `pytest 04_Web_API -v` | 14 tests: 11 pass, 3 fail (AUTO-001…014, mapped in `06_Automation_Regression/Automation_Manual_Traceability.csv`) |
| All automated suites | – | `pytest` | 59 tests: 43 pass, 16 fail |
| Performance, Python scripts (Wk5) | M3 | Start the app (`cd app && python app.py`), then in a 2nd terminal: `python 05_Security_Performance/Performance/performance_test.py` (`performance_dashboard.py` asks for a test login) | 840 requests, 0 errors (M3's run) |
| Performance, JMeter load/stress (Wk5) | M4 | With the app running, open `05_Security_Performance/Performance/PyTodo_Load_Test.jmx` in Apache JMeter 5.6.3. Analyse a run: `python 05_Security_Performance/Performance/analyze_results.py <results.jtl> [--steps]` | 10 users = highest tested load meeting P95 < 500 ms and < 1 % errors |
| Defect reproduction, DEF-001 to DEF-017 | M1 | `python 07_Test_Management/Defect_Evidence/reproduce_defects.py` (add `--no-browser` to skip Selenium screenshots) | Rewrites every `Defect_Evidence/` folder and the index |
| GUI screenshots (Wk3) | M1 | `python 03_Special_Testing/GUI_Compatibility/capture_gui_evidence.py --browser chrome --cfg CFG-01` | Screenshots in `GUI_Compatibility/screenshots/` |

**Manual (not automated) parts:** M2's black-box, GUI, compatibility and accessibility cases are in `01_Black_Box/Member2_Manual_Testing_and_RTM.xlsx`. M3's manual API cases are in `04_Web_API/Manual_API_Test_Index.csv`. M4's manual security cases SEC-001 to SEC-008 are in `Security_Test_Cases_SEC001-SEC008.csv`, with screenshots in `05_Security_Performance/Security/Security_Test_Cases_Evidence/`.

**Failing tests are expected.** Every automated test asserts the *correct* behaviour, so each failure is a confirmed defect, not a broken test. Do not change assertions to make them pass.

| Failing test(s) | Defect found |
|---|---|
| 10 security tests (`test_TC_SEC_002/004/005/007/008/009/010/013/014/015`) | see each test's docstring |
| `test_password_exactly_8_characters`, `test_password_minimum_boundary` | 8-character password rejected |
| `test_urgency_due_today` | task due today shown as overdue |
| `test_completed_exactly_7_days_ago` | seven-day completion boundary |
| `test_unauthorized_task_deletion` | cross-user task deletion |
| `test_duplicate_username_registration` | duplicate usernames accepted |

---

## 4. Repository structure

```
README.md                      ← this file
conftest.py / pytest.ini       ← shared PyTest fixtures (fresh DB per test, live server, browser)
requirements-test.txt
app/                           ← PyTodo Pro (application under test, unmodified)
01_Black_Box/                  ← Wk1  Application overview (M1) + black-box tests (M2)
02_White_Box_Coverage/         ← Wk2  White-box tests + coverage (M3)
03_Special_Testing/
   GUI_Compatibility/          ← Wk3  GUI checklist, compatibility matrix, screenshots (M1)
   Usability_Accessibility/    ← Wk3  Usability + WCAG review (M4)
04_Web_API/                    ← Wk4  Web + API test suite (M3)
05_Security_Performance/
   Security/                   ← Wk5  Security test cases + PyTest (M1)
   STRIDE/                     ← Wk5  Threat table (M4)
   Performance/                ← Wk5  Load experiment (M3 run, M4 evaluate)
06_Automation_Regression/      ← Wk6  Automation-to-manual traceability + evidence (M3; the tests are in 04_Web_API)
07_Test_Management/            ← Wk7  Test plan (M1), conventions (M1), RTM (M2), defect log (M4)
08_Final_QA_Report/            ← Wk8  Final integrated report (M1 compiles)
09_Presentation/               ← Wk9  Slides plan + live demo script (M1)
.github/workflows/             ← Wk9  CI example: runs all automated suites on every push
```

---

## 5. Team conventions (summary)

Full rules: `07_Test_Management/Team_Conventions.md`.

- **Test case IDs:** `TC-BB-` black-box · `TC-WB-` white-box · `TC-GUI-` GUI · `TC-CMP-` compatibility · `TC-USA-` usability · `TC-ACC-` accessibility · `TC-API-` API · `TC-SEC-` security · `TC-PERF-` performance · `REG-`/`UI-` automated regression
- **Requirement IDs:** `REQ-01` … `REQ-17` (defined in `01_Black_Box/Application_Overview.md`)
- **Defect IDs:** one shared log, `DEF-001` upward. Pre-allocated: **DEF-001–011 Member 1**, DEF-012–014 Member 2, DEF-015–020 Member 3, DEF-021 onward Member 4
- **Evidence files:** `<TC-ID>_<browser>_<os>.png`, stored in the folder's `evidence/` or `screenshots/`
- **Severity:** Critical / Major / Moderate / Minor. **Priority:** High / Medium / Low

---

## 6. Deliverable status

| Week | Deliverable | Owner | Status |
|---|---|---|---|
| 1 | Application overview, feature inventory, scope/risk matrix | M1 | ✅ Done – `01_Black_Box/Application_Overview.md` |
| 1 | Black-box test cases + execution | M2 | ✅ Done – `01_Black_Box/README.md` (27 cases, 25 pass, 2 fail → DEF-012, DEF-013) |
| 2 | White-box analysis, unit tests, coverage | M3 | ✅ Done – `02_White_Box_Coverage/README.md`(23 tests: 20 passed, 3 failed. 100% statement and branch coverage) |
| 3 | GUI checklist + compatibility matrix | M1 | 🟡 Chrome desktop + mobile done; Firefox / Edge / real phone still to run |
| 3 | Usability + accessibility | M4 |  ✅ Done – usability review completed; accessibility: 6 test cases, 5 passed and 1 failed (83.3%) |
| 4 | Web/API test suite | M3 | ✅ Done (23 manual API tests: 19 passed, 4 failed) |
| 5 | STRIDE table | M4 | ✅ Done – 6 threats identified across all STRIDE categories |
| 5 | Security tests + findings | M1 + M4 | ✅ Done – M1: 22 automated tests, 10 fail; M4: 8 manual cases SEC-001–008 (2 fail, 1 review finding) |
| 5 | Performance experiment | M3 / M4 | ✅ Done – M3: 840 requests, 0 recorded errors; M4: JMeter baseline (50 users) + stress (5–400 users), 10 users = highest load meeting targets |
| 6 | Automation + regression | M3 | ✅ Done (14 automated API tests: 11 passed, 3 failed; this is the regression suite) |
| 7 | Test plan + strategy | M1 | 🟡 Written – still fill §6 environment and §9 real dates |
| 7 | RTM, master test repository | M2 | ✅ Done – `07_Test_Management/RTM.md` & `Master_Test_Repository.md` (17/17 REQs traced) |
| 7 | Consolidated defect log | M4 | ✅ Done – consolidated duplicate findings into 17 unique defects (4 Critical, 2 Major, 6 Moderate, 5 Minor) |
| 8 | Metrics, risk, final report | M4 + M1 | 🟡 In Progress – consolidated test metrics, defect severity and risk evaluation prepared; final report sections and member contributions being compiled. |
| 9 | ISO 25010, CI/CD, presentation, demo | M1 | 🟡 Plan + demo script ready; rehearse |


## 7. Live Demo
https://github.com/user-attachments/assets/15c164bd-e8e6-4b61-926c-1e29314f1199
