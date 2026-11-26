# Week 3 – Usability and Accessibility  (Member 4: Defect & Metrics Coordinator)

> Backup copy (use only if needed): `_BACKUP_Members_2_3_4/03_Special_Testing/Usability_Accessibility/`

GUI correctness and the compatibility matrix are done by Member 1 in `../GUI_Compatibility/`. Screenshots there can be reused as evidence.

## 1. Usability evaluation

| **ID** | **Heuristic** | **Task / screen** | **Observation** | **Severity** | **Recommendation** | **Defect ID** |
|---|---|---|---|---|---|---|
| TC-USA-001 | Navigation | Dashboard and Registration/Login | Dashboard navigation and the registration-to-login link worked correctly. New Task and Cancel navigation also worked in the tested workflows. | None | Maintain consistent navigation across all pages. | - |
| TC-USA-002 | Feedback | New Task form | Submitting an empty Title field displayed "Please fill out this field" and focused the input field. | None | Maintain clear and immediate validation feedback. | - |
| TC-USA-003 | Error prevention | New Task form | The Cancel function returned users to My Tasks without saving the entered task in the tested Edge workflow. | None | Keep the Cancel function available to prevent unintended task creation. | - |
| TC-USA-004 | Consistency | Login, Registration, My Tasks and Dashboard | The inspected pages used similar navigation styling, form containers and action-control presentation. | None | Maintain consistent layouts, buttons and navigation styles. | - |
| TC-USA-005 | Understandability | My Tasks page | Task status badges included descriptive text and completion indicators instead of relying only on colour. | None | Continue using text labels and visual indicators to communicate task status. | - |
| TC-USA-006 | Feedback and instruction accuracy | Registration and My Tasks | Registration guidance stated a minimum of 8 password characters, but the system rejected an 8-character password. A task due today was also incorrectly labelled as Overdue. | Major | Correct password validation and task urgency classification so that displayed information matches actual system behaviour. | DEF-013, DEF-014 |

## 2. Accessibility review (WCAG 2.1 AA concepts)

| **ID** | **WCAG criterion** | **Check** | **Result (Pass/Fail)** | **Evidence** | **Defect ID** |
|---|---|---|---|---|---|
| TC-ACC-001 | 2.1.1 Keyboard | Keyboard navigation on Login page | Pass | Login fields and button were accessible using the keyboard. Visible focus was observed, and pressing Enter successfully opened My Tasks. | - |
| TC-ACC-002 | 2.1.1 Keyboard | Keyboard navigation on New Task page | Pass | Form controls were reachable using the keyboard, and the Cancel button successfully returned users to My Tasks. | - |
| TC-ACC-003 | 1.4.4 Resize Text | My Tasks page at 200% zoom | Pass | Task information remained accessible without reported clipping. New Task and Cancel navigation also worked. | - |
| TC-ACC-004 | 1.4.1 Use of Colour | Task status and urgency indicators | Pass | All displayed badges contained text labels, and completed tasks also displayed a tick mark. | - |
| TC-ACC-005 | 1.3.1 Info and Relationships | Form-label association | Fail | Clicking the Title, Description, Category and Due Date labels did not activate their corresponding fields. HTML inspection showed missing label associations. | DEF-017 |
| TC-ACC-006 | 1.4.3 Contrast (Minimum) | Title label text contrast | Pass | The inspected text/background pair achieved a contrast ratio of 16.83:1, exceeding the WCAG AA minimum of 4.5:1. | - |
| TC-ACC-007 | Not assessed | Screen-reader compatibility | Not Tested | Screen-reader operation was not included in the recorded accessibility evaluation. | - |
| TC-ACC-008 | Not assessed | Additional interactive states and contrast checks | Not Tested | Additional contrast combinations and interactive states were outside the selected test scope. | - |

## 3. Summary and improvement recommendations

The usability evaluation showed that PyTodo Pro provides generally clear navigation, consistent page layouts and understandable feedback for its main workflows. Users could navigate between the Dashboard, Registration, Login and New Task pages. The application also provided immediate feedback when the Title field was left empty and allowed users to cancel task creation without saving the entered information.

However, some issues affected the overall user experience. The registration page displayed password guidance that did not match the actual password validation, while tasks due on the current date were incorrectly labelled as Overdue. These issues could confuse users and reduce their confidence in the information displayed.

For accessibility, 5 out of 6 tested cases passed. Keyboard navigation, visible focus indicators, 200% zoom and non-colour status indicators worked in the selected workflows. However, the form labels did not activate their corresponding input fields because the required HTML label associations were missing. This may affect users who rely on assistive technologies.

The following improvements are recommended:

1. Correct the password validation and task urgency classification to ensure that system behaviour matches the displayed instructions and information.
2. Associate each form label with its corresponding input field using appropriate HTML `for` and `id` attributes.
3. Extend accessibility testing to include screen readers, additional contrast combinations and more interactive states.
4. Continue testing keyboard navigation and responsive layouts across different browsers and screen sizes.

Overall, PyTodo Pro demonstrated acceptable usability in the selected workflows, but further improvements are required to address the identified issues and strengthen accessibility. The evaluation was limited to selected manual checks and should not be considered a full WCAG 2.1 AA conformance assessment.
