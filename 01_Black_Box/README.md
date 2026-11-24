# Week 1 – Black-Box Testing  (Member 2: Test Design Coordinator)

> ⬜ **TO FILL by Member 2.** Replace every `<<...>>` and fill the empty table rows.
> Backup copy (use only if needed): `_BACKUP_Members_2_3_4/01_Black_Box/`

Member 1 has already written the **application overview, feature inventory and risk matrix** in `Application_Overview.md`. Use its REQ-IDs and risk priorities.

## 1. Technique selection and justification
| Feature (REQ) | Technique | Why this technique fits the feature |
|---|---|---|
| Registration (REQ-01) | EP + BVA | `<<...>>` |
| Login (REQ-02) | Decision table | `<<...>>` |
| Task urgency (REQ-09) | BVA + state transition | `<<...>>` |
| Filter/search (REQ-08) | Decision table | `<<...>>` |
| Task status (REQ-06/07) | State transition | `<<...>>` |

## 2. Equivalence partitions and boundary values
| Input | Valid partitions | Invalid partitions | Boundary values to test |
|---|---|---|---|
| Username length | `<<...>>` | `<<...>>` | `<<e.g. 2,3,4,19,20,21>>` |
| Username characters | | | |
| Password length | | | |
| Task title | | | |
| Due date vs today | | | |

## 3. Decision tables
### 3.1 Registration
| Condition / Rule | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Username valid? | | | | |
| Password valid? | | | | |
| Username already taken? | | | | |
| **Action** | | | | |

### 3.2 Login  /  3.3 Filters
`<<add tables>>`

## 4. State-transition diagrams
`<<Task: Open ⇄ Done → Deleted ; Urgency: Upcoming → Due Soon → Due Today → Overdue ; Session: Logged out ⇄ Logged in. Include state table + test cases.>>`

## 5. Test cases and execution results
| Test Case ID | Feature / Req | Technique | Objective | Preconditions | Test Data | Steps | Expected Result | Actual Result | Status | Evidence | Defect ID |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TC-BB-001 | | | | | | | | | | | |
| TC-BB-002 | | | | | | | | | | | |
| TC-BB-003 | | | | | | | | | | | |
| TC-BB-004 | | | | | | | | | | | |
| TC-BB-005 | | | | | | | | | | | |
| TC-BB-006 | | | | | | | | | | | |
| TC-BB-007 | | | | | | | | | | | |
| TC-BB-008 | | | | | | | | | | | |
| TC-BB-009 | | | | | | | | | | | |
| TC-BB-010 | | | | | | | | | | | |
| TC-BB-011 | | | | | | | | | | | |
| TC-BB-012 | | | | | | | | | | | |
| TC-BB-013 | | | | | | | | | | | |
| TC-BB-014 | | | | | | | | | | | |
| TC-BB-015 | | | | | | | | | | | |

**Summary:** `<<N executed, N passed, N failed, pass rate %>>`

## 6. Defects found
Log every defect in `07_Test_Management/Defect_Log.md` (your range: DEF-012 – DEF-014). List the IDs here: `<<...>>`

## 7. Evidence
Screenshots in `01_Black_Box/evidence/` named `<TC-ID>_<browser>_<os>.png`.
