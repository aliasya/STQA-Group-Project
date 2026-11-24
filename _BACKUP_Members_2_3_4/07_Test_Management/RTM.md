# Requirements Traceability Matrix (BACKUP – Member 2, updated Week 7)

Result codes: **P** = all cases passed · **F** = at least one case failed (defect linked) · **NR** = not run.

| Requirement / Feature | Test Scenario | Test Case ID(s) | Test Type / Technique | Result | Defect ID |
|---|---|---|---|---|---|
| REQ-01 Registration | Valid account creation | TC-BB-001, TC-API-001, REG-001, UI-001 | EP / Functional / API / Automated | P | – |
| REQ-01 Registration | Invalid username classes | TC-BB-002, 003, TC-WB-015–022, TC-API-002, 004, 006 | EP / White-box / API | P | – |
| REQ-01 Registration | Username length boundaries | TC-BB-004–007 | BVA | P | – |
| REQ-01 Registration | Password length boundaries | TC-BB-008–010, TC-WB-010–014, TC-API-005, 007, REG-004 | BVA / White-box / API | F | DEF-012 |
| REQ-01 Registration | Duplicate username | TC-BB-011, TC-SEC-004, TC-API-008, REG-005 | Decision table / Security | F | DEF-008 |
| REQ-02 Login / logout | Valid / invalid authentication | TC-BB-012–014, TC-API-009–011, TC-SEC-001, REG-001, 002, UI-002 | Decision table / API / Security | P | – |
| REQ-02 Login / logout | Brute-force protection | TC-SEC-002 | Security (STRIDE T-01) | F | DEF-006 |
| REQ-02 Login / logout | Session ends on logout | TC-BB-032, TC-SEC-003, REG-003, UI-005 | State transition / Security | P | – |
| REQ-03 Access control | Login required | TC-SEC-016, 017, TC-API-012, REG-018 | Security / API | P | – |
| REQ-03 Access control | Own tasks only (read/edit) | TC-SEC-006, TC-API-038, REG-013 | Security / API | P | – |
| REQ-03 Access control | Own tasks only (delete) | TC-SEC-005, TC-API-039, REG-014 | Security (IDOR) / API | F | DEF-003 |
| REQ-04 Create task | Valid title / minimal / full | TC-BB-015, 017, TC-API-014, 015, REG-006, UI-003 | EP / BVA / API | P | – |
| REQ-04 Create task | Empty / whitespace title | TC-BB-016, TC-API-016–018, 041, TC-GUI-010, REG-008, 009 | EP / API / GUI | F | DEF-014 |
| REQ-04 Create task | Invalid types / dates / category / length | TC-API-019–021, TC-SEC-014, 015, REG-017 | API / Security | F | DEF-016, DEF-009, DEF-019, DEF-007 |
| REQ-05 Edit task | Valid edit, cancel, pre-fill | TC-BB-034, TC-GUI-011, 012, TC-API-031 | EP / GUI / API | P | – |
| REQ-05 Edit task | Blank title on edit / PUT validation | TC-BB-035, TC-API-033, 034 | EP / API | F | DEF-014, DEF-017 |
| REQ-06 Complete / reopen | Open ⇄ Done | TC-BB-029, TC-API-032, REG-007, UI-003 | State transition / API | P | – |
| REQ-07 Delete task | Delete with confirmation | TC-BB-030, TC-GUI-013, TC-API-036, UI-003 | State transition / GUI / API | P | – |
| REQ-07 Delete task | Delete non-existent id | TC-API-037 | API | F | DEF-018 |
| REQ-08 Filter / search | Filter combinations | TC-BB-024–028, TC-API-024, TC-GUI-008, REG-012, UI-004 | Decision table / API / GUI | P | – |
| REQ-08 Filter / search | Paging parameters | TC-API-022, 023, 025–027 | API (BVA) | F | DEF-020 |
| REQ-08 Filter / search | Injection-safe search | TC-SEC-007, 008, TC-API-028, REG-015 | Security | F | DEF-001 |
| REQ-09 Urgency | Boundary around due date | TC-BB-018–023, TC-WB-001–008, REG-010, 011, TC-GUI-007 | BVA / White-box | F | DEF-013 |
| REQ-09 Urgency | Urgency state progression | TC-BB-031 | State transition | F | DEF-013 |
| REQ-10 Dashboard | Counters | TC-BB-033, TC-API-040, REG-019, TC-GUI-015 | EP / API / GUI | F | DEF-013 |
| REQ-10 Dashboard | 7-day completed window | TC-WB-024–031 | White-box (BVA) | F | DEF-015 |
| REQ-11 REST API | Status codes & JSON content | TC-API-001–042 | API | F | DEF-016–020 |
| REQ-12 Categories | Seeded list | TC-API-013 | API | P | – |
| REQ-13 Usability | Navigation, feedback, error prevention, consistency | TC-USA-001–008, TC-GUI-001–005, 009, 016, 018 | Heuristic / GUI | F | DEF-023, DEF-013, DEF-014 |
| REQ-14 Accessibility | WCAG 2.1 AA basics | TC-ACC-001–009, TC-GUI-017 | WCAG review | F | DEF-021, DEF-022, DEF-010 |
| REQ-15 Compatibility | Browsers / screen sizes | TC-GUI-006, 014, CFG-01–06 | Configuration matrix | F (4 configs NR) | DEF-010, DEF-011 |
| REQ-16 Security | STRIDE threats T-01–T-12 | TC-SEC-001–017 | Security | F | DEF-001–009 |
| REQ-17 Performance | Response time under load | TC-PERF-001–004 | Load test | P | – |

**Coverage check:** 17/17 requirements have executed tests (objective O1 met). Every high-risk requirement (risk ≥ 6: REQ-01, 02, 03, 04, 09, 11, 16) is covered by ≥ 2 techniques (O2 met).
