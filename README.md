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

> **Status of each part:** see section 6. Anything marked `⬜ TO FILL` is a blank section the owner must complete.

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

All commands run from the **repository root**. Each test gets its own temporary database, so the tests never touch `app/pytodo_pro.db`.

| What | Command (main folder) | Until the owner delivers, use the backup |
|---|---|---|
| Security tests (Wk5, M1) | `pytest 05_Security_Performance/Security -v` | – (done) |
| Black-box execution (Wk1) | *(manual, by M2 – see `01_Black_Box/README.md`)* | - (done) |
| White-box + coverage (Wk2) | `pytest 02_White_Box_Coverage --cov=app --cov-branch --cov-report=term-missing` | `pytest _BACKUP_Members_2_3_4/02_White_Box_Coverage --cov=app --cov-branch --cov-report=term-missing` |
| API suite (Wk4) | `pytest 04_Web_API -v` | `pytest _BACKUP_Members_2_3_4/04_Web_API -v` |
| Performance (Wk5) | python 05_Security_Performance/Performance/perf_test.py | `python _BACKUP_Members_2_3_4/05_Security_Performance/Performance/perf_test.py` |
| Regression suite (Wk6) | `pytest -m regression -v` (finds tests in every folder) | same |
| Selenium UI tests only | `pytest -m ui -v` (set `HEADLESS=0` to watch the browser) | same |
| Metrics (Wk8) | *(M4)* | `python _BACKUP_Members_2_3_4/07_Test_Management/compute_metrics.py` |
| Everything | `pytest` | |
| GUI screenshots (Wk3, M1) | `python 03_Special_Testing/GUI_Compatibility/capture_gui_evidence.py --browser chrome --cfg CFG-01` | – |

**Failing tests are expected.** Detection tests (security, API, white-box) assert the *correct* behaviour, so a failure means a confirmed defect. The defect ID is in each failing test's docstring.
The **regression suite** marks known open defects as `xfail(strict=True)`. It stays green until a defect is fixed, then alerts us to retest it.

---

## 4. Repository structure

```
README.md                      ← this file
MEMBER1_LEAD_GUIDE.md          ← Alia's step-by-step to-do list (QA Lead)
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
06_Automation_Regression/      ← Wk6  Automation candidates, scripts, regression suite (M3)
07_Test_Management/            ← Wk7  Test plan (M1), conventions (M1), RTM (M2), defect log (M4)
08_Final_QA_Report/            ← Wk8  Final integrated report (M1 compiles)
09_Presentation/               ← Wk9  Slides plan + live demo script (M1)
_BACKUP_Members_2_3_4/         ← complete backup of Members 2-4 parts (see its README)
.github/workflows/             ← Wk9  CI example: regression suite on every push
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
| 3 | Usability + accessibility | M4 | ⬜ TO FILL |
| 4 | Web/API test suite | M3 | ✅ Done (23 manual API tests: 19 passed, 4 failed) |
| 5 | STRIDE table | M4 | ⬜ TO FILL |
| 5 | Security tests + findings | M1 | ✅ Done – 22 tests, 10 fail → DEF-001–009 |
| 5 | Performance experiment | M3 / M4 | ✅ Done (840 requests, 0 recorded errors) |
| 6 | Automation + regression | M3 | ✅ Done (14 automated tests: 11 passed, 3 failed) |
| 7 | Test plan + strategy | M1 | ✅ Done (update §6 environment and §9 with real dates) |
| 7 | RTM, master test repository | M2 | ✅ Done – `07_Test_Management/RTM.md` & `Master_Test_Repository.md` (17/17 REQs traced) |
| 7 | Consolidated defect log | M4 | ⬜ TO FILL (M1 defects pre-filled) |
| 8 | Metrics, risk, final report | M4 + M1 | 🟡 Report skeleton ready; member sections to insert |
| 9 | ISO 25010, CI/CD, presentation, demo | M1 | 🟡 Plan + demo script ready; rehearse |

> If a member cannot deliver, a complete version of their part is in `_BACKUP_Members_2_3_4/`. Copy it into the main folder (see that folder's README).
