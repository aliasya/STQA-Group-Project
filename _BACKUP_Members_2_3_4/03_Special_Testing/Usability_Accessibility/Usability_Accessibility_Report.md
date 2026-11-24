# Week 3 – Usability and Accessibility Evaluation (BACKUP – Member 4)

**Requirements:** REQ-13 (usability), REQ-14 (accessibility). Evidence screenshots are shared with Member 1's GUI folder: `03_Special_Testing/GUI_Compatibility/screenshots/`.

## 1. Method

- **Usability:** heuristic walkthrough of the five core tasks (register, log in, add task, find a task, complete/delete a task). Criteria from the brief: ease of navigation, feedback, consistency, error prevention, understandability.
- **Accessibility:** basic WCAG 2.1 level AA review. Template HTML inspected for labels/names, contrast computed from `style.css` colours with the WCAG relative-luminance formula, keyboard-only navigation tried, page language and titles checked.
- **Rating:** Pass / Fail per check. Usability issues are rated Minor / Moderate / Major.

## 2. Usability evaluation

| Test Case ID | Feature / Req | Technique | Objective | Preconditions | Test Data | Steps | Expected Result | Actual Result | Status | Evidence | Defect ID |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TC-USA-001 | Navigation (REQ-13) | Heuristic – navigation | User reaches every feature within 1 click from the nav bar | Logged in | – | 1. From any page, find Tasks, Dashboard, New Task, Log out | All reachable in ≤ 1 click; current user visible | All reachable; username shown in nav | Pass | CFG-01_05_task_list.png | – |
| TC-USA-002 | Error prevention (REQ-13) | Heuristic – error prevention | Rules shown before mistakes; destructive actions confirmed | Logged out / in | – | 1. View register hints 2. Click Delete | Hints visible; delete asks to confirm | Hints shown; "Delete this task?" confirm dialog | Pass | CFG-01_03_register.png | – |
| TC-USA-003 | Feedback (REQ-13) | Heuristic – feedback | User gets confirmation after create/edit/delete | Logged in | – | 1. Create, edit, delete a task | Short success message ("Task created") | Silent redirect to list; no message. User must scan the list to confirm | Fail | CFG-01_05_task_list.png | DEF-023 |
| TC-USA-004 | Feedback (REQ-13) | Heuristic – feedback | Error messages are specific and polite | Logged out | short username; bad login | 1. Trigger each error | Specific, plain-language message | "Username must be 3-20 characters…", "Invalid username or password." Clear | Pass | CFG-01_02_login_error.png, CFG-01_04_register_error.png | – |
| TC-USA-005 | Error recovery (REQ-13) | Heuristic – error prevention | Valid input kept after a validation error | Logged out | username ok, password 7 chars | 1. Submit register form with short password | Username field still filled | Both fields emptied, user retypes everything | Fail | CFG-01_04_register_error.png | DEF-023 |
| TC-USA-006 | Understandability (REQ-09/13) | Heuristic – understandability | Urgency labels match user expectations | Task due today | – | 1. Look at a task due today | "Due Today" | "Overdue" for a task that is not late yet. Misleading | Fail | CFG-01_05_task_list.png | DEF-013 |
| TC-USA-007 | Consistency (REQ-13) | Heuristic – consistency | Same rules on every input path | Logged in | blank title via UI vs API | 1. Create blank-title task in UI and API | Same validation everywhere | API rejects, UI accepts | Fail | TC-API-041 | DEF-014 |
| TC-USA-008 | Understandability (REQ-13) | Heuristic – understandability | Dashboard meaning is clear | Logged in | – | 1. Read dashboard cards | Labels self-explanatory | Clear labels; "Completed (last 7 days)" explicit | Pass | CFG-01_10_dashboard.png | – |

## 3. Accessibility review (WCAG 2.1 AA)

| Test Case ID | Feature / Req | Technique | Objective | Preconditions | Test Data | Steps | Expected Result | Actual Result | Status | Evidence | Defect ID |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TC-ACC-001 | Forms (REQ-14) | WCAG 1.3.1 Info & relationships | Labels programmatically linked to inputs | – | login, register, task form | 1. Inspect `<label>` for `for=` and input `id=` | Each label linked | `<label>Username</label>` with no `for`/`id` on any form. Clicking a label does not focus its field | Fail | templates/login.html, register.html, task_form.html | DEF-021 |
| TC-ACC-002 | Search (REQ-14) | WCAG 4.1.2 Name, role, value | Search box has an accessible name | – | – | 1. Inspect search input | `<label>` or `aria-label` | Placeholder "Search title..." only. Category/status selects also unlabeled | Fail | templates/index.html | DEF-021 |
| TC-ACC-003 | Toggle button (REQ-14) | WCAG 4.1.2 / 1.1.1 | Icon button has a meaningful name | – | – | 1. Inspect ○/✓ button | e.g. `aria-label="Mark as done"` | Screen reader would read "○" / "✓" only | Fail | templates/index.html | DEF-021 |
| TC-ACC-004 | All pages (REQ-14) | WCAG 2.1.1 Keyboard, 2.4.3 Focus order | Everything usable by keyboard in logical order | – | – | 1. Tab through login and task list | Logical order; all controls reachable | Order Brand → Username → Password → Log in → Register; list controls reachable | Pass | TC-GUI-017 | – |
| TC-ACC-005 | Text contrast (REQ-14) | WCAG 1.4.3 Contrast (min) | Text ≥ 4.5:1 | – | colours from style.css | 1. Compute ratios | ≥ 4.5:1 | Most text passes (nav 8.8:1, buttons 5.8–11.6:1, badges 4.8–5.9:1, hint 4.54:1). **Fails:** empty-state text and completed-task titles `#999` on white = **2.85:1** | Fail | contrast table §4 | DEF-022 |
| TC-ACC-006 | Input borders (REQ-14) | WCAG 1.4.11 Non-text contrast | Form field boundaries ≥ 3:1 | – | `#d0d0d5` on `#fff` | 1. Compute ratio | ≥ 3:1 | **1.54:1**. Field edges hard to see for low-vision users | Fail | contrast table §4 | DEF-022 |
| TC-ACC-007 | Page structure (REQ-14) | WCAG 3.1.1 Language, 2.4.2 Page titled | Page language and titles set | – | – | 1. Check `<html lang>` and `<title>` | lang set; unique titles | `lang="en"`; unique titles per page | Pass | templates/base.html | – |
| TC-ACC-008 | Status by colour (REQ-14) | WCAG 1.4.1 Use of colour | Urgency not conveyed by colour alone | – | – | 1. View urgency badges | Text + colour | Each badge has a text label | Pass | CFG-01_05_task_list.png | – |
| TC-ACC-009 | Zoom / reflow (REQ-14) | WCAG 1.4.4 Resize text, 1.4.10 Reflow | Usable at 200 % / 320 px width | – | Pixel 7 emulation | 1. View on narrow screen | Content reflows | No viewport tag, so the page does not reflow on mobile (see GUI report) | Fail | CFG-04_05_task_list.png | DEF-010 |

## 4. Contrast measurements

| Element | Foreground | Background | Ratio | AA requirement | Result |
|---|---|---|---|---|---|
| Nav links | #cfe2f7 | #1B3A5C | 8.79:1 | 4.5:1 | Pass |
| Nav username | #8fb0d6 | #1B3A5C | 5.18:1 | 4.5:1 | Pass |
| Primary button | #ffffff | #1B3A5C | 11.63:1 | 4.5:1 | Pass |
| Filter button / links | #ffffff / #2C6B8F | #2C6B8F / #ffffff | 5.82:1 | 4.5:1 | Pass |
| Muted text, stat labels | #666666 | #ffffff | 5.74:1 | 4.5:1 | Pass |
| Field hint | #8d6e76 | #ffffff | 4.54:1 | 4.5:1 | Pass (barely) |
| Badge Due Soon / Overdue / Upcoming / Done | various | various | 4.78 / 5.72 / 5.89 / 4.95 | 4.5:1 | Pass |
| **Empty-state text, completed titles** | #999999 | #ffffff | **2.85:1** | 4.5:1 | **Fail** |
| **Input border** | #d0d0d5 | #ffffff | **1.54:1** | 3:1 (non-text) | **Fail** |

## 5. Summary

- **Usability:** 8 checks, 4 Pass, 4 Fail. The app is simple and learnable. Its weak points are **feedback** (no success messages), **error recovery** (forms cleared), and **inconsistent rules** between UI and API.
- **Accessibility:** 9 checks, 3 Pass, 6 Fail. Main barrier: **screen-reader users** (no programmatic labels, icon-only toggle). Second: **low-vision users** (2 contrast failures, no mobile reflow).

## 6. Recommendations

1. Add `for`/`id` pairs to every label; add `aria-label` to the search box, the filter selects and the toggle button ("Mark 'X' as done"). Fixes DEF-021.
2. Change `#999` to `#6b6b6b` or darker (≥ 4.5:1) and input borders to `#8a8a8a` (≥ 3:1). Fixes DEF-022.
3. Use Flask `flash()` messages after create/edit/delete, and re-fill the username after a registration error. Fixes DEF-023.
4. Add the viewport meta tag (see DEF-010).
5. Limitation: no real screen reader (NVDA/VoiceOver) or automated checker (axe, WAVE, Lighthouse) was used. Recommend a Lighthouse accessibility run as future work.
