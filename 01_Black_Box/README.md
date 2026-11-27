# Week 1 – Black-Box Testing (Member 2: Test Design Coordinator)

Member 1 has already written the **application overview, feature inventory and risk matrix** in `Application_Overview.md`. Use its REQ-IDs and risk priorities.

## 1. Technique selection and justification
| Feature (REQ) | Technique | Why this technique fits the feature |
|---|---|---|
| Registration (REQ-01) | EP + BVA + Decision Table | Inputs fall into valid/invalid equivalence classes (character types, uniqueness) and strict length boundaries (username 3–20 chars, password min 8 chars) where off-by-one defects commonly occur. |
| Login (REQ-02) | EP + Decision Table | Credentials partition cleanly into valid vs. invalid pairs, and combined username/password validity conditions determine authentication success or rejection. |
| Task urgency (REQ-09) | EP + BVA + State Transition | Urgency labels change at exact date thresholds (past, today, +1/+2 days, +3 days) and transition across task states (`Open` → `Done` → `Open`). |
| Filter/search (REQ-08) | Decision Table + EP | Category and status filters combine to determine task visibility, while search queries partition into matching vs. non-matching titles. |
| Task status & CRUD (REQ-04/05/06/07) | State Transition + Functional Positive | Tasks move through distinct lifecycle states (`Open` ⇄ `Done` → `Deleted`), and edits require direct verification of persistence. |

## 2. Equivalence partitions and boundary values
| Input | Valid partitions | Invalid partitions | Boundary values to test |
|---|---|---|---|
| Username length | 3 to 20 characters | `< 3` characters; `> 20` characters; empty string | `2` (reject), `3` (accept), `20` (accept), `21` (reject) |
| Username characters | Letters (`A–Z`, `a–z`), numbers (`0–9`), underscores (`_`) | Special characters (`@`, `-`, spaces, symbols) | Valid string (`member2_qa01`) vs. invalid symbol (`member@qa`) |
| Password length | `>= 8` characters | `< 8` characters; empty string | `7` (reject), `8` (accept), `9` (accept) |
| Task title | Non-empty string (e.g., `Test 2 Revision`) | Empty / whitespace-only title | Empty field (blocked by form validation) vs. valid title |
| Due date vs today | No due date; past date; today; `+1` to `+2` days; `>= +3` days | Malformed date string | `-1 day` (`Overdue`), `0 days / today` (`Due Today`), `+1 day` (`Due Soon`), `+2 days` (`Due Soon`), `+3 days` (`Upcoming`) |

## 3. Decision tables
### 3.1 Registration
| Condition / Rule | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Username valid (3–20 chars, alphanumeric/underscore)? | Yes | No | Yes | Yes |
| Password valid (`>= 8` chars)? | Yes | Yes | No | Yes |
| Username already taken? | No | No | No | Yes |
| **Action** | Account created; redirect to My Tasks | Reject with username validation error | Reject with password validation error | Reject with duplicate username error |

### 3.2 Login
| Condition / Rule | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Registered username entered? | Yes | Yes | No | No |
| Matching password entered? | Yes | No | Yes | No |
| **Action** | Login succeeds; open My Tasks | Reject ("Invalid username or password.") | Reject ("Invalid username or password.") | Reject ("Invalid username or password.") |

### 3.3 Filters (Category + Status)
| Condition / Rule | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Task category matches filter (`Study`)? | Yes | Yes | No | No |
| Task status matches filter (`Open`)? | Yes | No | Yes | No |
| **Action (Appears under `Study` + `Open` filter)** | **Yes (Appears)** | **No (Hidden)** | **No (Hidden)** | **No (Hidden)** |

## 4. State-transition diagrams

### 4.1 Lifecycle & Session State Flows
* **Task Lifecycle:** `[Created] ──► Open ⇄ Done ──► Deleted`
* **Urgency Progression (Open Tasks):** `Upcoming (>= +3d) ──► Due Soon (+1d to +2d) ──► Due Today (0d) ──► Overdue (< 0d)` *(Completing any task sets urgency to `Done`; reopening restores date-based urgency).*
* **User Session:** `Logged Out ──(Valid Login)──► Logged In ──(Logout)──► Logged Out`

### 4.2 State-Transition Table
| Current State | Event / Trigger | Next State | Verification Test Case |
|---|---|---|---|
| `Open` (Overdue task) | User marks task complete | `Done` (Urgency badge changes to `Done`) | `TC-BB-018` |
| `Done` | User reopens task | `Open` (Urgency badge reverts to `Overdue`) | `TC-BB-019` |
| `Existing` (`Open` or `Done`) | User deletes task and confirms | `Deleted` (Removed from list and search) | `TC-BB-027` |

## 5. Test cases and execution results
Executed manually via the web interface (`http://127.0.0.1:5000/`) on Windows using Google Chrome (reference execution dates: 14–15 November 2026).

| Test Case ID | Feature / Req | Technique | Objective | Preconditions | Test Data | Steps | Expected Result | Actual Result | Status | Evidence | Defect ID |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TC-BB-001 | Registration (REQ-01) | EP | Verify valid account registration | On `/register` page; username unused | User: `member2_qa01`, Pass: `TestPass123!` | 1. Enter valid username and password. 2. Click Register. | Account created; My Tasks opens showing username | My Tasks opened and username was shown | Pass | `TC-BB-001_chrome_win.png` | – |
| TC-BB-002 | Login (REQ-02) | EP | Verify valid user sign-in | Registered account exists; on `/login` | Registered credentials (`member2_qa01`) | 1. Enter registered username and password. 2. Click Log in. | User signed in and redirected to My Tasks | My Tasks opened | Pass | `TC-BB-002_chrome_win.png` | – |
| TC-BB-003 | Login (REQ-02) | EP | Verify login rejection with wrong password | Registered username exists; on `/login` | Valid user, Pass: `WrongPass123!` | 1. Enter valid username and wrong password. 2. Click Log in. | Login rejected with generic error message | `"Invalid username or password."` shown | Pass | `TC-BB-003_chrome_win.png` | – |
| TC-BB-004 | Registration (REQ-01) | BVA | Verify minimum password boundary (8 chars) | On `/register` page | User: `bva_pwd8`, Pass: `Abcd123!` (len 8) | 1. Enter valid username and 8-char password. 2. Click Register. | Registration succeeds (min 8 chars allowed) | Rejected with `"Password must be at least 8 characters."` | Fail | `TC-BB-004_chrome_win.png` | DEF-012 |
| TC-BB-005 | Registration (REQ-01) | BVA | Verify password just above minimum boundary (9 chars) | On `/register` page | User: `bva_pwd9`, Pass: `Abcd123!X` (len 9) | 1. Enter valid username and 9-char password. 2. Click Register. | Registration succeeds | Accepted; account created | Pass | `TC-BB-005_chrome_win.png` | – |
| TC-BB-006 | Registration (REQ-01) | BVA | Verify password just below minimum boundary (7 chars) | On `/register` page | User: `bva_pwd7`, Pass: `Abcd12!` (len 7) | 1. Enter valid username and 7-char password. 2. Click Register. | Registration rejected | Rejected with length validation message | Pass | `TC-BB-006_chrome_win.png` | – |
| TC-BB-007 | Registration (REQ-01) | BVA | Verify username below minimum boundary (2 chars) | On `/register` page | User: `ab` (len 2), Pass: `TestPass123!` | 1. Enter 2-char username and valid password. 2. Click Register. | Registration rejected | Rejected with username length error | Pass | `TC-BB-007_chrome_win.png` | – |
| TC-BB-008 | Registration (REQ-01) | BVA | Verify username at minimum boundary (3 chars) | On `/register` page | User: `abc` (len 3), Pass: `TestPass123!` | 1. Enter 3-char username and valid password. 2. Click Register. | Registration accepted | Accepted; account created | Pass | `TC-BB-008_chrome_win.png` | – |
| TC-BB-009 | Registration (REQ-01) | BVA | Verify username at maximum boundary (20 chars) | On `/register` page | 20-char alphanumeric username, Pass: `TestPass123!` | 1. Enter 20-char username and valid password. 2. Click Register. | Registration accepted | Accepted; account created | Pass | `TC-BB-009_chrome_win.png` | – |
| TC-BB-010 | Registration (REQ-01) | BVA | Verify username above maximum boundary (21 chars) | On `/register` page | 21-char username, Pass: `TestPass123!` | 1. Enter 21-char username and valid password. 2. Click Register. | Registration rejected | Rejected (`"Username must be 3-20 characters..."`) | Pass | `TC-BB-010_chrome_win.png` | – |
| TC-BB-011 | Registration (REQ-01) | EP | Verify username with invalid special character | On `/register` page | User: `member@qa`, Pass: `TestPass123!` | 1. Enter username containing `@`. 2. Click Register. | Registration rejected | Username validation message shown | Pass | `TC-BB-011_chrome_win.png` | – |
| TC-BB-012 | Create Task / Urgency (REQ-04, REQ-09) | EP | Verify task creation with no due date | Logged in; on New Task page | Title: `Test 2 Revision`, Category: `Study`, Due: empty | 1. Fill title and category, leave due date blank. 2. Submit. | Task created with urgency `"No due date"` | Task appeared with `"No due date"` | Pass | `TC-BB-012_chrome_win.png` | – |
| TC-BB-013 | Urgency Label (REQ-09) | BVA | Verify urgency boundary for task due today (0 days) | Logged in; on New Task page | Due date = execution date (today) | 1. Create task with due date set to today. 2. Check urgency badge. | Urgency displays `"Due Today"` | Urgency displayed `"Overdue"` | Fail | `TC-BB-013_chrome_win.png` | DEF-013 |
| TC-BB-014 | Urgency Label (REQ-09) | BVA | Verify urgency lower boundary for Due Soon (+1 day) | Logged in; on New Task page | Due date = execution date + 1 day | 1. Create task due tomorrow. 2. Check urgency badge. | Urgency displays `"Due Soon"` | Urgency displayed `"Due Soon"` | Pass | `TC-BB-014_chrome_win.png` | – |
| TC-BB-015 | Urgency Label (REQ-09) | BVA | Verify urgency upper boundary for Due Soon (+2 days) | Logged in; on New Task page | Due date = execution date + 2 days | 1. Create task due in 2 days. 2. Check urgency badge. | Urgency displays `"Due Soon"` | Urgency displayed `"Due Soon"` | Pass | `TC-BB-015_chrome_win.png` | – |
| TC-BB-016 | Urgency Label (REQ-09) | BVA | Verify urgency boundary for Upcoming (+3 days) | Logged in; on New Task page | Due date = execution date + 3 days | 1. Create task due in 3 days. 2. Check urgency badge. | Urgency displays `"Upcoming"` | Urgency displayed `"Upcoming"` | Pass | `TC-BB-016_chrome_win.png` | – |
| TC-BB-017 | Urgency Label (REQ-09) | BVA | Verify urgency boundary for Overdue (-1 day) | Logged in; on New Task page | Due date = execution date - 1 day | 1. Create task due yesterday. 2. Check urgency badge. | Urgency displays `"Overdue"` | Urgency displayed `"Overdue"` | Pass | `TC-BB-017_chrome_win.png` | – |
| TC-BB-018 | Complete Task (REQ-06) | State Transition | Verify transition from Open to Done | Logged in; open overdue task exists | Existing open overdue task | 1. Click complete toggle on open task. 2. Observe status and badge. | Urgency changes to `"Done"`, task listed under Done | As expected | Pass | `TC-BB-018_chrome_win.png` | – |
| TC-BB-019 | Reopen Task (REQ-06) | State Transition | Verify transition from Done back to Open | Logged in; completed overdue task exists | Existing completed overdue task | 1. Click reopen toggle on completed task. 2. Observe status and badge. | Urgency `"Overdue"` restored, task listed under Open | As expected | Pass | `TC-BB-019_chrome_win.png` | – |
| TC-BB-020 | Filter/Search (REQ-08) | Decision Table | Rule 1: Category=Study AND Status=Open with Study+Open filter | Logged in; tasks in Study/Work & Open/Done | Filter: `Study` + `Open`; Task: `Study` / `Open` | 1. Select `Study` and `Open` filters. 2. Click Filter. | Matching `Study` + `Open` task appears | Appeared | Pass | `TC-BB-020_chrome_win.png` | – |
| TC-BB-021 | Filter/Search (REQ-08) | Decision Table | Rule 2: Category=Study AND Status=Done with Study+Open filter | Logged in; `Study` + `Done` task exists | Filter: `Study` + `Open`; Task: `Study` / `Done` | 1. Select `Study` and `Open` filters. 2. Click Filter. | `Study` + `Done` task is absent from results | Absent | Pass | `TC-BB-021_chrome_win.png` | – |
| TC-BB-022 | Filter/Search (REQ-08) | Decision Table | Rule 3: Category=Work AND Status=Open with Study+Open filter | Logged in; `Work` + `Open` task exists | Filter: `Study` + `Open`; Task: `Work` / `Open` | 1. Select `Study` and `Open` filters. 2. Click Filter. | `Work` + `Open` task is absent from results | Absent | Pass | `TC-BB-022_chrome_win.png` | – |
| TC-BB-023 | Filter/Search (REQ-08) | Decision Table | Rule 4: Category=Work AND Status=Done with Study+Open filter | Logged in; `Work` + `Done` task exists | Filter: `Study` + `Open`; Task: `Work` / `Done` | 1. Select `Study` and `Open` filters. 2. Click Filter. | `Work` + `Done` task is absent from results | Absent | Pass | `TC-BB-023_chrome_win.png` | – |
| TC-BB-024 | Edit Task (REQ-05) | Functional Positive | Verify editing title, description, and category of completed task | Logged in; completed task exists | Updated title: `QA Edited Task 01`, new description & category | 1. Click Edit on completed task. 2. Modify fields and save. 3. Refresh page. | Updated values stored, persisted after refresh, `Done` status retained | As expected | Pass | `TC-BB-024_chrome_win.png` | – |
| TC-BB-025 | Filter/Search (REQ-08) | EP | Verify search with a matching task title | Logged in; task `QA Edited Task 01` exists | Search query: `QA Edited Task 01` | 1. Enter matching title in search box. 2. Click Filter. | Matching task returned, no unrelated tasks shown | Matching task returned, no other tasks | Pass | `TC-BB-025_chrome_win.png` | – |
| TC-BB-026 | Filter/Search (REQ-08) | EP | Verify search with a non-matching title | Logged in; on My Tasks | Search query: `ZZZ NoSuchTask 926` | 1. Enter non-existent title in search box. 2. Click Filter. | Empty-results message displayed | `"No tasks match your filters."` shown | Pass | `TC-BB-026_chrome_win.png` | – |
| TC-BB-027 | Delete Task (REQ-07) | State Transition | Verify transition from Existing to Deleted state | Logged in; task exists | Existing task | 1. Click Delete on task and confirm. 2. Refresh and repeat search. | Task removed and absent after refresh and repeat search | As expected | Pass | `TC-BB-027_chrome_win.png` | – |

**Summary:** 27 executed, 25 passed, 2 failed, pass rate 92.59%.

## 6. Defects found
Logged in `07_Test_Management/Defect_Log.md` (local Week 1 IDs `BUG-001` and `BUG-002` consolidated into the master register):
* **DEF-012** *(local `BUG-001`)* — Registration rejects a valid password of exactly 8 characters (`TC-BB-004`, Moderate severity / Medium priority, Status: Open).
* **DEF-013** *(local `BUG-002`)* — A task due today is misclassified as `"Overdue"` instead of `"Due Today"` (`TC-BB-013`, Moderate severity / Medium priority, Status: Open).

## 7. Evidence
Screenshots in `01_Black_Box/evidence/` named `<TC-ID>_<browser>_<os>.png` (e.g., `TC-BB-004_chrome_win.png`, `TC-BB-013_chrome_win.png`).
