# Team Conventions (owner: Member 1, QA Lead)

Every member follows these rules. They keep IDs, statuses and evidence consistent across all artefacts so the final report and RTM line up.

## 1. IDs

| Item | Format | Example | Owner of the range |
|---|---|---|---|
| Requirement | `REQ-nn` | REQ-09 Urgency | M1 (defined in Application_Overview.md) |
| Black-box test | `TC-BB-nnn` | TC-BB-019 | M2 |
| White-box test | `TC-WB-nnn` | TC-WB-004 | M3 |
| GUI / compatibility | `TC-GUI-nnn`, `CFG-nn` | TC-GUI-006, CFG-02 | M1 |
| Usability / accessibility | `TC-USA-nnn`, `TC-ACC-nnn` | TC-ACC-005 | M4 |
| API | `TC-API-nnn` | TC-API-020 | M3 |
| Security | `TC-SEC-nnn` | TC-SEC-007 | M1 |
| STRIDE threat | `T-nn` | T-04 | M4 |
| Performance | `TC-PERF-nnn` | TC-PERF-002 | M3 / M4 |
| Automated regression | `REG-nnn`, `UI-nnn` | REG-011 | M3 |
| Defect | `DEF-nnn` | DEF-013 | **one shared log.** Pre-allocated ranges: M1 001–011, M2 012–014, M3 015–020, M4 021+ (extend upward if you need more and tell M4) |
| Risk | `R-nn` | R-03 | M4 |

An ID is **never reused**, even if a test is deleted. Mark it `Withdrawn` instead.

## 2. Test case template (mandatory columns)

`Test Case ID | Feature/Requirement | Technique/Test Type | Objective | Preconditions | Test Data | Steps | Expected Result | Actual Result | Status | Evidence | Defect ID`

- Write the **Expected Result before executing**.
- **Status** values: `Pass`, `Fail`, `Blocked`, `Not Run`. Nothing else.
- Every `Fail` must have a `Defect ID` (or "Observation" if it is not a defect).

## 3. Defect template

`Defect ID | Title | Affected Feature | Environment | Preconditions | Steps to Reproduce | Expected | Actual | Severity | Priority | Evidence | Status`

**Severity** measures impact on the product:

| Severity | Definition | Example |
|---|---|---|
| Critical | Security breach, data loss/corruption, or a crash that blocks a core feature with no workaround | SQL injection, another user can delete your data |
| Major | Core feature gives wrong result; workaround awkward | Task due today shown as Overdue |
| Moderate | Feature partly wrong or poor validation; easy workaround | Blank title accepted |
| Minor | Cosmetic, wording, rare edge case | Wrong status code for a rare request |

**Priority** sets how soon to fix it. High = before release. Medium = next iteration. Low = backlog.

**Status lifecycle:** `Open` → `Confirmed` (reproduced by a second member) → `Fixed` (dev) → `Retest` → `Closed` / `Reopened`.
Since we do not modify the app, our defects normally end at **Open** or **Confirmed**.

## 4. Evidence

- Screenshots: `<TC-ID>_<browser>_<os>.png`, e.g. `TC-GUI-006_firefox_win11.png`
- Logs / test output: save as `.txt` (`pytest ... > results_week4.txt`)
- Put evidence in the `evidence/` or `screenshots/` folder of the week it belongs to.

## 5. Review routine

- Each Friday, members commit their artefacts. M1 reviews them against these rules within 2 days.
- M1 checks: unique IDs, expected results present, statuses valid, every Fail linked to a defect, defect also in the shared log.
- Changes to earlier artefacts are allowed (progressive project). Record the reason in that document's **Revision history** table.
