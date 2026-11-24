# Member 1 (QA/Test Lead) – What Alia Needs To Do

Most of your artefacts are drafted and tested already. This list covers what is **left for you** and **what to check** before submission, in priority order. Tick each box as you finish it.

---

## A. Do first (today, ~1 hour) – make sure everything runs on your laptop

- [ ] Unzip the repo, open a terminal in the root folder
- [ ] `python -m venv venv` → activate it → `pip install -r requirements-test.txt`
- [ ] `pytest 05_Security_Performance/Security -v` → expect **12 passed, 10 failed** (failures = defects, that's correct)
- [ ] `pytest -m regression -v` → expect **20 passed, 8 xfailed** (needs Chrome for the 5 UI tests)
- [ ] `cd app && python app.py` → open http://127.0.0.1:5000 and click around once
- [ ] Fill in team names in `README.md` §1

> If a command fails, check: venv active? Run from the repo **root**? Chrome installed?

## B. Your own deliverables – status and what is left

| # | Deliverable | File | Status | What YOU still do |
|---|---|---|---|---|
| 1 | Application overview, feature inventory, risk matrix (Wk1) | `01_Black_Box/Application_Overview.md` | ✅ Written | Read it once so you can explain the risk scores (L × I) in the presentation |
| 2 | Test plan + strategy (Wk7) | `07_Test_Management/Test_Plan.md` | ✅ Written | Fill §6 **E2** (your laptop specs, browser versions) and §9 **dates** |
| 3 | Team conventions | `07_Test_Management/Team_Conventions.md` | ✅ Written | Send to the group chat so everyone uses the same IDs/DEF ranges |
| 4 | GUI checklist + compatibility matrix (Wk3) | `03_Special_Testing/GUI_Compatibility/` | 🟡 Chrome desktop + mobile done | **Run Firefox and Edge** (step C1), fill CFG-02/03/06 rows |
| 5 | Security tests + findings (Wk5) | `05_Security_Performance/Security/` | ✅ 17 cases run, report written | Re-run on your laptop; keep `security_test_run.txt` as evidence |
| 6 | Pre-logged defects DEF-001 – 011 | `07_Test_Management/Defect_Log.md` | ✅ Logged | Nothing, unless you find new ones |
| 7 | Final report compilation (Wk8) | `08_Final_QA_Report/Final_QA_Report.md` | 🟡 Your sections written, 9 ⬜ INSERT sections | Paste members' summaries (step D) |
| 8 | ISO 25010 + CI/CD + process improvements (Wk9) | Final report §7–9, `.github/workflows/regression.yml` | ✅ Written | Be ready to explain the CI pipeline |
| 9 | Presentation + demo (Wk9) | `09_Presentation/` | 🟡 Plan + script ready | Build slides, assign speakers, rehearse twice (step E) |

## C. Hands-on testing you still have to do yourself

### C1. Compatibility runs (~30 min)
```bash
python 03_Special_Testing/GUI_Compatibility/capture_gui_evidence.py --browser firefox --cfg CFG-02
python 03_Special_Testing/GUI_Compatibility/capture_gui_evidence.py --browser edge    --cfg CFG-03
```
1. Open the new screenshots in `screenshots/`. Compare each with the CFG-01 versions.
2. In `GUI_Compatibility_Report.md` §3, fill the CFG-02/03 rows: browser version (printed by the script), `x / 8` core checks passed, notes.
3. **CFG-06 (200 % zoom):** in Chrome, open the app, press Ctrl + "+" until 200 %, screenshot the task list and form, record the result.
4. **CFG-05 (real phone, optional):** steps are in the report row. If you skip it, leave it as "Not Run" and it stays in the residual-risk list. That is acceptable.
5. Any new problem → add `DEF-0xx` (you own DEF-001–011, so ask Member 4 for the next free number) and a row in the defect log.

### C2. Manually reproduce 2 security defects in the browser for screenshots (~15 min)
- **XSS:** create a task titled `<b style="color:red">Hacked</b>` → screenshot → save as `05_Security_Performance/Security/evidence/TC-SEC-009_chrome.png`
- **SQL injection:** log in as user B, open `http://127.0.0.1:5000/api/tasks?q=%25' OR 1=1 OR title LIKE '` → user A's task appears → screenshot `TC-SEC-007_chrome.png`

## D. Lead duties: chase, review, integrate

1. **Today:** message the group:
   *"Repo structure + templates are ready. Each of you has a README in your folder with blanks (⬜ TO FILL). Please use the IDs in Team_Conventions.md. Deadline for your part: `<<date>>`."*
2. **Review** each member's folder when it arrives:
   - [ ] Test case IDs unique, follow the prefix rules
   - [ ] Expected result written for every case; Status is Pass/Fail/Blocked/Not Run only
   - [ ] Every Fail has a DEF-ID that exists in `07_Test_Management/Defect_Log.md`
   - [ ] Their tests run with the README command
3. **If someone doesn't deliver by the deadline**, use the backup (see `_BACKUP_Members_2_3_4/README.md`):
   - **Move** (don't copy) their backup folder's files into the main folder, so tests don't run twice
   - Tell them, and ask them to at least read it so they can present it
4. **Integrate the report:** in `08_Final_QA_Report/Final_QA_Report.md`, replace each ⬜ INSERT block with a short summary of that member's results (backup text is in `Final_QA_Report_COMPLETE.md`, same section numbers). Then update the Executive Summary numbers from `Metrics.md`.
5. **Final consistency check** (from the official checklist):
   - [ ] RTM test IDs exist in the test files; RTM results match
   - [ ] DEF-IDs + statuses identical in test cases, RTM, defect log and report
   - [ ] Metrics add up (run `python _BACKUP_Members_2_3_4/07_Test_Management/compute_metrics.py` to regenerate if you used the backups)
   - [ ] Performance section states workload + environment
   - [ ] Report states limitations and residual risks and never says "defect-free"
   - [ ] README setup works on a second member's laptop

## E. Presentation (Week 9)

- [ ] Build slides from `09_Presentation/Presentation_Plan.md` (16 slides, speaker assigned per slide)
- [ ] Your slides: 1–4, 8, 11 (second half), 15, 16
- [ ] Practise the demo from `Demo_Script.md` on the presenting laptop, **twice**
- [ ] Record a backup video of the demo
- [ ] Learn the Q&A answers in the plan §3

## F. Key facts to remember when presenting

- **23 defects:** 4 Critical (SQL injection, XSS, IDOR delete, bad-date crash), 5 Major, 6 Moderate, 8 Minor
- **174 test executions, 72.4 % pass** (if the backups are used; otherwise use your team's numbers)
- **Your security results:** 17 cases, 7 pass / 10 fail, 9 defects (DEF-001–009)
- **Your GUI results:** 18 checks, 14 pass / 4 fail; 2 of 6 configurations done (more after step C1)
- **Verdict:** works on the normal path; **not release-ready** because of the Critical security defects
- **Testing finds defects; it cannot prove there are none.** Say this in the conclusion
