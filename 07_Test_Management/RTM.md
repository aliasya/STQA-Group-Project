# Requirements Traceability Matrix  (owner: Member 2 – Test Design Coordinator)

> ⬜ **TO FILL by Member 2.** Member 1's GUI, compatibility and security rows are filled in. Add the black-box, white-box, API, usability/accessibility, performance and automation test IDs for every requirement.
> Backup copy: `_BACKUP_Members_2_3_4/07_Test_Management/RTM.md`.

Result: P = all passed · F = at least one failed (defect linked) · NR = not run.

| Requirement / Feature | Test Scenario | Test Case ID(s) | Test Type / Technique | Result | Defect ID |
|---|---|---|---|---|---|
| REQ-01 Registration | Valid account creation | `<<TC-BB-...>>` | EP / Functional | | |
| REQ-01 Registration | Duplicate username | TC-SEC-004 `<<+ TC-BB-...>>` | Security / Decision table | F | DEF-008 |
| REQ-02 Login | Valid / invalid authentication | TC-SEC-001 `<<+ TC-BB-...>>` | Decision table / Security | P | – |
| REQ-02 Login | Brute-force protection | TC-SEC-002 | Security | F | DEF-006 |
| REQ-02 Login | Session ends on logout | TC-SEC-003 `<<+ ...>>` | State transition / Security | P | – |
| REQ-03 Access control | Login required | TC-SEC-016, 017 | Security | P | – |
| REQ-03 Access control | Own tasks only (read/edit) | TC-SEC-006 | Security | P | – |
| REQ-03 Access control | Own tasks only (delete) | TC-SEC-005 | Security (IDOR) | F | DEF-003 |
| REQ-04 Create task | Valid / blank title | TC-GUI-010 `<<+ TC-BB-..., TC-API-...>>` | GUI / EP / API | | |
| REQ-04 Create task | Invalid date / oversized input | TC-SEC-014, 015 `<<+ TC-API-...>>` | Security / API | F | DEF-009, DEF-007 |
| REQ-05 Edit task | Edit, pre-fill, cancel | TC-GUI-011, 012 `<<+ ...>>` | GUI / EP | P | – |
| REQ-06 Complete / reopen | Open ⇄ Done | `<<...>>` | State transition | | |
| REQ-07 Delete task | Delete with confirmation | TC-GUI-013 `<<+ ...>>` | GUI / State transition | P | – |
| REQ-08 Filter / search | Filter combinations | TC-GUI-008 `<<+ TC-BB-...>>` | Decision table / GUI | P | – |
| REQ-08 Filter / search | Injection-safe search | TC-SEC-007, 008 | Security | F | DEF-001 |
| REQ-09 Urgency | Boundary around due date | TC-GUI-007 `<<+ TC-BB-..., TC-WB-...>>` | BVA / State / GUI | F | DEF-013 |
| REQ-10 Dashboard | Counters | TC-GUI-015 `<<+ ...>>` | GUI / EP | | |
| REQ-11 REST API | Status codes & JSON | `<<TC-API-...>>` | API | | |
| REQ-12 Categories | Seeded list | `<<TC-API-...>>` | API | | |
| REQ-13 Usability | Navigation, messages, consistency | TC-GUI-001–005, 009, 016, 018 `<<+ TC-USA-...>>` | GUI / Heuristic | F | DEF-023 |
| REQ-14 Accessibility | WCAG basics | TC-GUI-017 `<<+ TC-ACC-...>>` | WCAG | | |
| REQ-15 Compatibility | Browsers / screen sizes | TC-GUI-006, 014, CFG-01–06 | Configuration matrix | F | DEF-010, DEF-011 |
| REQ-16 Security | STRIDE threats T-01–T-12 | TC-SEC-001–017 | Security | F | DEF-001–009 |
| REQ-17 Performance | Response time under load | `<<TC-PERF-...>>` | Load test | | |
