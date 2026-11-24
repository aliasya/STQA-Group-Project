# PyTodo Pro — Member 3 handover

**Course:** TEB3433 / TFB3433 — Software Testing and Quality Assurance  
**Scope:** Supporting scripts, testing evidence, metrics and reproducibility material for Sections 4.0 and 5.0. The Word report was already shared separately and is intentionally excluded.  
**Date prepared:** 18 November 2026

## How to use this package

- **Member 1 (report integrator):** the Sections 4.0 and 5.0 report was already provided separately. This package contains only its supporting material. Refer to `02_White_Box_Coverage/`, `04_Web_API/` and `06_Automation_Regression/` for the cited screenshot evidence. Share test IDs and defect IDs with the RTM and master test-case repository.
- **Member 4 (security/performance):** use `05_Security_Performance/` and `07_Test_Management/Member3_Defect_HandOver.csv` for Section 6 and Section 8. Focus on BUG-005 (cross-user task deletion). Report testing environment and workload limitations.
- **Member 2 (black-box and UI):** reconcile overlap with registration boundary BUG-001, task urgency BUG-002 and other regression tests. Avoid duplicating the same defect under different IDs.

## Provenance and important caveat

The `Runnable_Project` application source comes from the *original, supplied* `pytodo_pro_student.zip` and is unmodified. The four test Python scripts were **reconstructed from the code shared in our chat**; the user's locally saved test files were not uploaded. Compare reconstructed scripts with the originals before treating them as byte-for-byte copies. Their original execution is evidenced by chat-uploaded screenshots. This environment verified the white-box script by running it; the API scripts could not be executed here because Flask/Werkzeug could not be installed offline. Do not claim re-execution here.

Screenshot evidence is copied from the images shared in the conversation. `WB-002` is a crop of the actual final terminal screenshot. `PERF-002` is a text summary generated from the actual uploaded `performance_100_results.txt`, **not an original screenshot**.

## Test results to integrate

- White-box `helpers.py`: **23 tests, 20 passed, 3 failed; 100% statement and branch coverage of that module**.
- Manual API: **23 cases, 19 passed, 4 failed** (including the authenticated dashboard check).
- Automated API: **14 cases, 11 passed, 3 failed**.
- Performance: **840 local requests, 0 recorded errors**, across short tests and 1/2/4 worker configurations.
- Defects from Member 3: BUG-001 through BUG-005; the numbering must be reconciled with the group's shared defect log.

## Running tests locally (Windows PowerShell)

```powershell
cd Runnable_Project
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install pytest pytest-cov
python -m pytest tests/test_helpers.py -v
python -m pytest tests/test_api.py -v
python -m pytest tests/test_helpers.py --cov=helpers --cov-branch --cov-report=html --cov-report=term-missing
```

**Expected known failures:** 3 helper tests (password boundary, due-today urgency, seven-day completion boundary), and 3 API regression tests (cross-user deletion, password boundary, duplicate username). Do not change assertions merely to make tests pass.

Run performance tests ONLY on this local app instance. Start `python app.py` in another terminal, then `python tests/performance_test.py` and/or `python tests/performance_dashboard.py`. Authenticated dashboard test prompts for credentials **locally**; do not store or share real passwords.

## Suggested lecturer-aligned merge mapping

- `02_White_Box_Coverage` → group `/02_White_Box_Coverage`
- `04_Web_API` → group `/04_Web_API`
- `05_Security_Performance` → group `/05_Security_Performance`
- `06_Automation_Regression` → group `/06_Automation_Regression`
- `07_Test_Management` → group `/07_Test_Management` (Member 1 should merge, not overwrite)
- `Runnable_Project` → reproducibility/reference source; keep outside the main nine deliverable folders or link it in README

## What is still a team integration task

1. Reconcile defect IDs/statuses and link to requirements/RTM and master test case workbook.
2. Add Member 1/2/4 sections and consistent global figure/table numbering.
3. Confirm report formatting and references and prepare presentation/live demo.
4. Compare original local test scripts and any HTML report generated on the user's laptop with these reproduced files.
