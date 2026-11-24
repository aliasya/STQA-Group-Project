# Live Demo Script (≈ 5 minutes)

Run from the repository root with the virtual environment active. Tested commands. Open two terminals and one browser before starting.

## 0. Before the session (setup, not shown)

```bash
pip install -r requirements-test.txt
cd app && python app.py          # terminal 1 – leave running at http://127.0.0.1:5000
```
In the browser, register **alice** / password123, add 3 tasks (one due **today**, one tomorrow, one next week). Open a second browser profile/incognito window for **mallory**.

## 1. The bug a user sees: "Due Today" is Overdue (≈ 45 s) – DEF-013
1. Show alice's task list: the task due **today** has a red **Overdue** badge.
2. Open Dashboard: Overdue counts it.
3. Say: "Found by BVA on the due date (TC-BB-019) and confirmed white-box: `due <= today` (TC-WB-004)."

## 2. Stored XSS (≈ 30 s) – DEF-002
1. As alice create a task titled: `<b style="color:red">Hacked</b>`
2. The title renders **bold red**: HTML was executed, not escaped. (Use `<b>`, not `<script>alert`, to avoid a blocking dialog.)
3. Say: "With a script tag this runs JavaScript in any viewer's browser."

## 3. Security test suite run (≈ 60 s) – Member 1
```bash
pytest 05_Security_Performance/Security -v          # terminal 2
```
Point to: 12 passed / 10 failed. Each failure = a confirmed defect (docstring shows the DEF-ID). Open `test_security.py` at `test_TC_SEC_005` (IDOR) to show how a test encodes the expected secure behaviour.

## 4. Regression suite + CI idea (≈ 60 s) – Member 3
```bash
pytest -m regression -v
```
- Point to **20 passed, 8 xfailed**. Explain strict xfail: green now, turns red when a defect is fixed or something new breaks.
- Optional, visual: `HEADLESS=0 pytest -m ui -v` (Windows: `set HEADLESS=0` first). Chrome opens and clicks through register → create → toggle → delete.
- Show `.github/workflows/regression.yml` (10 seconds).

## 5. Coverage (≈ 30 s)
```bash
pytest _BACKUP_Members_2_3_4/02_White_Box_Coverage --cov=app --cov-branch --cov-report=term-missing
```
(Use `02_White_Box_Coverage` if Member 3's own tests are in place.) Point to `helpers.py 100 %`, then: "100 % coverage, yet 3 tests fail. Coverage ≠ correctness."

## 6. Close (≈ 15 s)
"Every finding follows the chain requirement → risk → technique → test → result → defect → recommendation. See the RTM."

## If something goes wrong
- App won't start → use the test suites only (they don't need the running app).
- Chrome/driver error → skip the UI tests: `pytest -m "regression and not ui" -v`.
- Anything else → play the backup screen recording.
