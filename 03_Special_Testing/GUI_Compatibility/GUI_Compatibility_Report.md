# Week 3 – GUI and Compatibility Testing

**Owner:** Member 1 (QA/Test Lead) · **Requirements:** REQ-13, REQ-15 (plus GUI aspects of REQ-01–10)
Usability and accessibility are covered separately in `../Usability_Accessibility/` (Member 2 accessibility checks TC-ACC-001–006, Member 4 usability review).

> **Numbering:** this checklist uses **TC-GUI-101 to TC-GUI-118** so that it does not clash with Member 2's TC-GUI-001 to TC-GUI-007. Defect IDs follow the consolidated register DEF-001 to DEF-017 (`07_Test_Management/Defect_Log.md`).

## 1. Approach

1. **GUI checklist** (section 2): forms, buttons, links, labels, navigation, messages, visual consistency. Run in full on the reference configuration CFG-01.
2. **Compatibility** (section 3): re-run a core subset of 8 GUI checks on every browser/configuration available to the team.
3. **Evidence:** `capture_gui_evidence.py` opens every page in a real browser on seeded demo data and saves screenshots to `screenshots/<CFG>_<page>.png`. Interactive checks (dropdowns, cancel, delete dialog, keyboard tab order) were run with Selenium and confirmed by viewing the screenshots.

Seeded data: one task per urgency state (yesterday, **today**, +2 days, +10 days, no date), one very long title, one completed task.

## 2. GUI checklist results (reference configuration CFG-01)

CFG-01 = Chrome 153, Linux, 1366×900 window.

| Test Case ID | Feature / Req | Technique | Objective | Preconditions | Test Data | Steps | Expected Result | Actual Result | Status | Evidence | Defect ID |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TC-GUI-101 | Login page (REQ-02) | GUI checklist | Page elements present and labelled | Logged out | – | 1. Open /login | Title "Log in", Username + Password fields with labels, "Log in" button, link to Register | All present; fields marked required | Pass | CFG-01_01_login.png | – |
| TC-GUI-102 | Login error (REQ-02) | GUI – messages | Clear error on bad credentials | Logged out | gui_tester / wrongpass1 | 1. Enter wrong password 2. Click Log in | Red error message, user stays on page | "Invalid username or password." shown in red box. Username field is cleared (minor inconvenience) | Pass | CFG-01_02_login_error.png | – |
| TC-GUI-103 | Register page (REQ-01) | GUI checklist | Rules visible before input (error prevention) | Logged out | – | 1. Open /register | Username and password hints visible | Hints "(3-20 chars, letters/numbers/underscore)" and "(min 8 characters)" shown | Pass | CFG-01_03_register.png | – |
| TC-GUI-104 | Register error (REQ-01) | GUI – messages | Specific validation message, input kept | Logged out | username "ab" | 1. Enter short username 2. Click Register | Specific error; entered values kept | Specific error shown, but **both fields are emptied** | Fail | CFG-01_04_register_error.png | DEF-012 |
| TC-GUI-105 | Navigation bar | GUI – navigation | Nav links work and show who is logged in | Logged in | – | 1. Click Tasks, Dashboard, brand, Log out | Each opens correct page; username shown | All links correct; username shown; brand goes to task list | Pass | CFG-01_05_task_list.png | – |
| TC-GUI-106 | Task list layout (REQ-08) | GUI – visual | Table readable, no broken wrapping | 7 tasks incl. long title | seeded data | 1. Open task list at 1366×900 | Long title wraps cleanly; dates and badges stay on one line | Long title wraps fine. Due dates split over two lines ("2026-" / "11-29"); "No due date" badge breaks over 2 lines | Fail | CFG-01_05_task_list.png | DEF-011 |
| TC-GUI-107 | Urgency badges (REQ-09) | GUI – visual | Each urgency shows correct label/colour | Task due today | due = today | 1. Open task list | Task due today shows "Due Today" badge (style exists in CSS) | "Group meeting" (due today) shows red **Overdue**. "Due Today" badge never appears | Fail | CFG-01_05_task_list.png | DEF-014 |
| TC-GUI-108 | Filters (REQ-08) | GUI – controls | Dropdowns auto-apply; Filter button applies search | Tasks in Study + Work | category = Study | 1. Choose "Study" in category dropdown | List refreshes immediately to Study tasks only | Page reloaded with `?category=Study`; only Study task shown | Pass | CFG-01_06_task_list_filtered.png | – |
| TC-GUI-109 | Empty state | GUI – messages | Helpful message when nothing matches | Logged in | q = zzzz | 1. Search "zzzz" | Friendly empty-state text | "No tasks match your filters." shown (light grey text, observation only) | Pass | CFG-01_07_task_list_empty.png | – |
| TC-GUI-110 | New task form (REQ-04) | GUI – forms | Required title enforced in browser | Logged in | empty title | 1. Open New Task 2. Click Create Task with empty title | Browser blocks submit with message | Blocked: "Please fill out this field." (only fully empty; a title of only spaces passes, observation only) | Pass | CFG-01_08_new_task_form.png | – |
| TC-GUI-111 | Edit form (REQ-05) | GUI – forms | Form pre-filled with current values | Task Alpha / Study / 2026-12-31 | – | 1. Click Edit | Title, category and due date pre-filled | All three pre-filled correctly; heading "Edit Task", button "Save Changes" | Pass | CFG-01_09_edit_task_form.png | – |
| TC-GUI-112 | Cancel button (REQ-05) | GUI – buttons | Cancel discards changes | Editing task Alpha | title changed to "Changed" | 1. Change title 2. Click Cancel | Back to list, title unchanged | Returned to list; title still "Alpha" | Pass | Selenium run log | – |
| TC-GUI-113 | Delete confirmation (REQ-07) | GUI – error prevention | Delete asks for confirmation; Cancel keeps task | 2 tasks | – | 1. Click Delete 2. Choose Cancel in dialog | Confirmation dialog; task kept | "Delete this task?" dialog; Cancel keeps both tasks | Pass | Selenium run log | – |
| TC-GUI-114 | Mobile layout (REQ-15) | GUI – responsive | Pages usable on a phone-sized screen | Logged in | Pixel 7 emulation (412 px) | 1. Open task list and forms on mobile | Layout fits screen width, text readable without zooming | Page drawn at ~980 px desktop width and shrunk. Text and buttons very small; large blank area below | Fail | CFG-04_05_task_list.png, CFG-04_08_new_task_form.png | DEF-010 |
| TC-GUI-115 | Dashboard (REQ-10) | GUI – visual | Cards labelled, values readable, colours meaningful | Seeded data | – | 1. Open Dashboard | 5 labelled cards; colours match meaning | 5 cards with clear labels and colours. Overdue = 2 because the task due today is counted (functional issue) | Pass | CFG-01_10_dashboard.png | DEF-014 (related) |
| TC-GUI-116 | Visual consistency | GUI – visual | Link styles consistent across pages | – | – | 1. Compare links on login/register with links in the app | Same link colour/style everywhere | "Register" / "Log in" links use browser default blue/purple, unlike the app's teal links | Pass (Observation O-1) | CFG-01_01_login.png | – |
| TC-GUI-117 | Keyboard navigation | GUI – navigation | Logical Tab order on forms | Logged out | – | 1. On /login press Tab 5 times | Brand → Username → Password → Log in → Register | Exactly that order | Pass | Selenium run log | – |
| TC-GUI-118 | Page titles | GUI – labels | Each page has a meaningful browser-tab title | – | – | 1. Open each page, read tab title | Distinct title per page | "Log in — PyTodo Pro", "Tasks — …", "New Task — …", "Edit Task — …", "Dashboard — …" | Pass | source `templates/*.html` | – |

**CFG-01 summary:** 18 executed · 14 Pass · 4 Fail · pass rate 77.8 %. Defects found: DEF-010, DEF-011, DEF-012 (first found here) and DEF-014 (also found by Member 2 black-box and Member 3 white-box testing).

## 3. Compatibility / configuration matrix

**Core subset run on every configuration:** TC-GUI-101, 102, 105, 106, 108, 110, 113, 117 (+ TC-GUI-114 on phone-sized configurations).

| Config ID | Device / OS | Browser + version | Viewport | Core checks Pass / Run | Result notes | Defects |
|---|---|---|---|---|---|---|
| CFG-01 | Laptop, Linux | Chrome 153 | 1366×900 | 7 / 8 | Only TC-GUI-106 (wrapping) fails | DEF-011 |
| CFG-04 | Phone emulation (Pixel 7) | Chrome 153 mobile emulation | 412×915 | 3 / 5 run | 101, 102, 105 Pass; 106 and 114 Fail (desktop layout shrunk, tiny text). 108, 110, 113, 117 **Not Run** | DEF-010, DEF-011 |
| CFG-02 | Laptop, Windows 11 | Firefox | 1366×768 | – | **Not Run** (residual risk) – to run: `capture_gui_evidence.py --browser firefox --cfg CFG-02` | |
| CFG-03 | Laptop, Windows 11 | Microsoft Edge 157 | desktop | 3 / 3 (Member 2) | Covered by Member 2's TC-COMP-001–003 (My Tasks, New Task form, Dashboard): all Pass, no overlap or clipping. Member 1's core subset was not re-run on Edge | – |
| CFG-05 | Real Android / iPhone | Chrome / Safari mobile | phone | – | **Not Run** (residual risk; mobile was evaluated only through Chrome emulation, CFG-04) – to run, on the laptop: `cd app`, `python app.py` once (creates the DB), stop it, then `flask --app app run --host 0.0.0.0` (no code change). Open `http://<laptop-IP>:5000` on a phone on the same Wi-Fi | |
| CFG-06 | Laptop | Chrome, browser zoom 200 % | 1366×900 | 1 / 1 (Member 2) | Covered by Member 2's TC-ACC-003 (WCAG 1.4.4): at 200 % zoom the task list, New Task and Cancel worked. Member 1's core subset was not re-run at 200 % | – |

**Not available to the team:** Safari on macOS, older browsers, screen sizes above 1920 px. These are listed as residual compatibility risk in the final report.

## 4. Findings summary

| Defect | Title | Severity / Priority |
|---|---|---|
| DEF-010 | No viewport meta tag – mobile shows shrunken desktop layout | Moderate / Medium |
| DEF-011 | Task table cells wrap awkwardly (dates, "No due date" badge) | Minor / Low |
| DEF-012 | Registration form clears the entered values after a validation error | Minor / Low |
| DEF-014 (shared) | Task due today shown as Overdue; "Due Today" badge never appears | Moderate / High |
| O-1 (observation) | Login/Register links use default browser colours | – |

## 5. Recommendations

1. Add `<meta name="viewport" content="width=device-width, initial-scale=1">` to `base.html`, and stack the task table on small screens. Fixes DEF-010.
2. Add `white-space: nowrap` to the due-date cell and badges. Fixes DEF-011.
3. Re-populate the username field after a registration error (`value="{{ username }}"`). Fixes DEF-012.
4. Style `.auth-card a` with the app link colour (O-1).
5. Run the remaining configurations (CFG-02 Firefox, CFG-05 real phone) and retest CFG-01 to CFG-06 after any CSS change. TC-GUI-106 and 114 are good candidates for screenshot-based regression.
