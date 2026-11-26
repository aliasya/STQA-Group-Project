# Week 2 – White-Box Testing and Coverage  (Member 3: Automation/Tool Coordinator)

> ⬜ **TO FILL by Member 3.** Replace every `<<...>>` and fill the empty table rows.
> Backup copy (use only if needed): `_BACKUP_Members_2_3_4/02_White_Box_Coverage/`

## 1. Selected code units and justification
| Unit (file:function) | Why selected (importance / complexity / risk) |
|---|---|
| helpers.py: is_valid_password()        | Validates password requirements. Incorrect boundary conditions may reject valid registrations. |
| helpers.py: is_valid_username()        | Validates username length, characters and data type to ensure input correctness. |
| helpers.py: compute_urgency()          | Classifies task urgency using date comparisons. Incorrect conditions may affect task prioritisation. |
| helpers.py: completed_in_last_n_days() | Evaluates recent task completion. Boundary errors may produce inaccurate dashboard statistics. |

## 2. Control-flow analysis
Control-flow analysis was conducted to identify decision points and alternative execution paths within the selected helper functions.

Password validation — is_valid_password()

Decision points: Input data type and password length.

Three representative paths:

P1: Input is not a string → False

P2: Password length is eight characters or fewer → False

P3: Password length is greater than eight characters → True

Cyclomatic complexity of the illustrated control-flow graph: V(G) = 3.

Defect: The implementation rejects passwords containing exactly eight characters (BUG-001).

Task urgency — compute_urgency()

Decision points: Default current date, missing due date, overdue comparison and upcoming deadline range.

Representative paths:

P1: No due date → No due date

P2: Due date on or before today → Overdue

P3: Due date within the next one or two days → Due Soon

P4: Due date three or more days ahead → Upcoming

Cyclomatic complexity of the illustrated control-flow graph: V(G) = 5.

Defect: A task due today is incorrectly classified as overdue (BUG-002).

Username validation — is_valid_username()

Tested paths include valid usernames, minimum and maximum boundaries, invalid characters and invalid data types.

Recent completion — completed_in_last_n_days()

Tested paths include incomplete tasks, completions inside and outside the time window, future dates and default date handling.

Control-flow evidence: Attach the password-validation and task-urgency control-flow diagrams from the white-box report.

## 3. Path / data-flow considerations
Password input: Validate the input type before evaluating password length. Check the minimum length boundary.

Username input: Validate the data type, length restrictions and allowed characters.

Due-date input: Track due_date_str from the function argument through date parsing and urgency classification.

Completion date: Compare completion timestamps against the configured time window, including the exact seven-day boundary.

Boundary risks: Incorrect comparison operators were identified in password validation, task urgency and completion-date calculations.

Additional malformed-date and exception-handling paths would require separate verification.

## 4. White-box test cases
| Test Case ID | Unit | Path / branch covered | Input | Expected | Actual | Status | Defect ID |
|---|---|---|---|---|---|---|---|
| TC-WB-001 | Password | Valid length | Valid password greater than 8 chars | True | True | Pass | - |
| TC-WB-002 | Password | Minimum boundary | Exactly 8 chars | True | False | Fail | BUG-001 |
| TC-WB-003 | Password | Below minimum | Fewer than 8 chars | False | False | Pass | - |
| TC-WB-004 | Password | Invalid data type | Non-string input | False | False | Pass | - |
| TC-WB-005 | Username | Invalid characters | Username with disallowed characters | False | False | Pass | - |
| TC-WB-006 | Urgency | Missing due date | Empty due date | No due date | No due date | Pass | - |
| TC-WB-007 | Urgency | Overdue branch | Past due date | Overdue | Overdue | Pass | - |
| TC-WB-008 | Urgency | Today boundary | Due today | Due Today | Overdue | Fail | BUG-002 |
| TC-WB-009 | Completion | Inside time window | Completed within 7 days | True | True | Pass | - |
| TC-WB-010 | Completion | Seven-day boundary | Completed exactly 7 days ago | True | False | Fail | BUG-003 |


Overall execution: 23 unit tests — 20 passed, 3 failed. 

## 5. Automated test file
Test framework: PyTest

Actual test file: tests/test_helpers.py

Execution command: python -m pytest tests/test_helpers.py -v

The test suite covers four helper functions using valid, invalid, boundary and default-parameter test cases.

Three tests failed because the implementation did not satisfy the expected boundary requirements.

## 6. Coverage report and interpretation
Coverage command:

python -m pytest tests/test_helpers.py --cov=helpers --cov-branch --cov-report=term-missing -v

| File | Statements | Branch | Coverage % | Uncovered lines |
|---|---|---|---|---|
| helpers.py | 31 | 18 | 100% | None |
| app.py | Not measured | Not measured | N/A | Not measured |

Interpretation: The white-box tests achieved 100% statement and branch coverage for helpers.py, indicating that all measured executable statements and branch outcomes were exercised.

However, three unit tests failed because of boundary-condition defects in password validation, urgency classification and recent-completion calculations.

Therefore, complete code coverage does not guarantee defect-free software. Further boundary-value verification and regression testing are necessary.

The reported coverage applies only to helpers.py and should not be interpreted as coverage of the entire Flask application.
