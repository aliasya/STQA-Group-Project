# Member 3 metrics and handoff for Member 1 & Member 4

## Confirmed from recorded execution

| Category | Executed | Passed | Failed | Notes |
|---|---:|---:|---:|---|
| White-box helper tests | 23 | 20 | 3 | 100% statement and branch coverage **only for `helpers.py`** |
| Manual API tests | 23 | 19 | 4 | Includes API-023 dashboard test; API-021 and API-022 are two failing cases from one defect |
| Automated API tests | 14 | 11 | 3 | Failing tests expose known defects BUG-001, BUG-004, BUG-005 |
| Local performance | 840 requests | 840 HTTP success | 0 errors | 60 initial + 180 repeated + 300 categories + 300 authenticated dashboard |

### Distinct defects associated with Member 3

- BUG-001: eight-character passwords rejected (Moderate proposed)
- BUG-002: task due today classified overdue (Moderate proposed)
- BUG-003: exact seven-day completion boundary excluded (Minor proposed)
- BUG-004: duplicate username accepted (Moderate proposed)
- BUG-005: cross-user task deletion accepted and confirmed (Critical proposed)

**Important:** IDs and severity must be reconciled against the team's master defect register. This sheet is a Member 3 handoff, not a replacement for the master RTM or group test repository.

Performance results are short-duration local tests. The highest measured throughput is **not** a sustainable or production capacity claim.
