# BACKUP – Complete versions of Members 2, 3 and 4's parts

**Purpose:** a safety net. Use a folder here **only if** the owner can't deliver their part. Every test here was actually executed. Results, logs, coverage and charts come from real runs (environment E1 in the Test Plan).

## What's inside

| Folder | Owner | Contents | Key result |
|---|---|---|---|
| `01_Black_Box/` | M2 | `Technique_Justification.md` (EP/BVA tables, decision tables, state diagrams), `Black_Box_Test_Cases.md` (35 cases), `run_blackbox_tests.py`, `blackbox_results.csv` | 28 pass / 7 fail |
| `02_White_Box_Coverage/` | M3 | `White_Box_Analysis.md` (selection, CFGs, V(G), data flow, coverage interpretation), `test_whitebox_helpers.py`, `coverage_html/` | helpers.py 100 % branch; 3 fail |
| `03_Special_Testing/Usability_Accessibility/` | M4 | `Usability_Accessibility_Report.md` (8 usability + 9 WCAG checks, contrast table) | 7 pass / 10 fail |
| `04_Web_API/` | M3 | `API_Test_Report.md`, `test_api.py` | 47 exec: 33 pass / 14 fail |
| `05_Security_Performance/STRIDE/` | M4 | `STRIDE_Threat_Table.md` (T-01–T-12 with L×I) | 3 threats at risk 9 |
| `05_Security_Performance/Performance/` | M3/M4 | `perf_test.py`, `Performance_Report.md`, `perf_results.csv/.md`, `perf_chart.png` | 0 % errors; meets 20-user target |
| `06_Automation_Regression/` | M3 | `Automation_Report.md`, `test_regression.py`, `test_ui_selenium.py` | 20 pass / 8 xfail / 0 fail |
| `07_Test_Management/` | M2/M4 | `RTM.md`, `Master_Test_Repository.md`, `Defect_Log.md` + `defect_log.csv` (23 defects), `Metrics.md`, charts, `compute_metrics.py` | – |
| `08_Final_QA_Report/` | M1 | `Final_QA_Report_COMPLETE.md`: the full report as if everyone delivered | – |

## How to use a backup part

1. **Move** (not copy) the needed files into the matching main folder, e.g.
   `_BACKUP_Members_2_3_4/04_Web_API/*` → `04_Web_API/`, then delete or replace the blank `README.md` there.
   Moving matters: if the same tests exist in both places, `pytest` runs them twice and the counts double.
2. Re-run the scripts **on your own laptop** so the evidence shows your environment:
   ```bash
   python 01_Black_Box/run_blackbox_tests.py                 # regenerates the black-box table + CSV
   pytest 02_White_Box_Coverage --cov=app --cov-branch --cov-report=html
   python 05_Security_Performance/Performance/perf_test.py   # takes ~2-4 min; record your CPU/RAM
   ```
   (Paths inside the scripts are relative to the repo root, so they work from either location.)
3. Update the environment lines (Test Plan §6, Performance_Report §2) if numbers change.
4. Regenerate metrics: `python <location>/07_Test_Management/compute_metrics.py`. If you moved folders, update the paths in its `SUITES` / `MANUAL` lists at the top.
5. Ask the original owner to read their part so they can present it and answer questions.

## Notes

- Dates in the black-box and regression tests are **relative to today**, so they stay valid on any day. Expected results won't change unless the app changes.
- The white-box tests use a fixed `today = 2026-11-24` via injection, so they are fully deterministic.
- Performance numbers depend on the machine. Quote trends, and always state the environment.
