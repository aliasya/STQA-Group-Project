# Defect Evidence Index (DEF-001 - DEF-017)

Generated 2026-11-25 13:09:04 by `reproduce_defects.py` (fresh temporary database each run; the real app DB is not touched).
Each defect's evidence lives in the folder of the test activity that found it. Re-run:

```bash
python 07_Test_Management/Defect_Evidence/reproduce_defects.py
```

| ID | Title | Severity | Result | Screenshots | Evidence |
|---|---|---|---|---|---|
| DEF-001 | Authenticated user can delete another user's task (IDOR) | Critical | Reproduced | 0 | [05_Security_Performance/Security/Defect_Evidence/DEF-001_Cross_User_Task_Deletion](../../05_Security_Performance/Security/Defect_Evidence/DEF-001_Cross_User_Task_Deletion/evidence.md) |
| DEF-002 | SQL injection in task search API (GET /api/tasks?q=) | Critical | Reproduced | 0 | [05_Security_Performance/Security/Defect_Evidence/DEF-002_SQL_Injection_Task_Search](../../05_Security_Performance/Security/Defect_Evidence/DEF-002_SQL_Injection_Task_Search/evidence.md) |
| DEF-003 | No audit logging of security-relevant events | Moderate | Reproduced | 0 | [05_Security_Performance/STRIDE/Defect_Evidence/DEF-003_No_Audit_Logging](../../05_Security_Performance/STRIDE/Defect_Evidence/DEF-003_No_Audit_Logging/evidence.md) |
| DEF-004 | Stored XSS: task title rendered unescaped | Critical | Reproduced | 1 | [05_Security_Performance/Security/Defect_Evidence/DEF-004_Stored_XSS_Task_Title](../../05_Security_Performance/Security/Defect_Evidence/DEF-004_Stored_XSS_Task_Title/evidence.md) |
| DEF-005 | Malformed due date stored via API -> permanent HTTP 500 | Critical | Reproduced | 1 | [05_Security_Performance/Security/Defect_Evidence/DEF-005_Malformed_Due_Date_HTTP500](../../05_Security_Performance/Security/Defect_Evidence/DEF-005_Malformed_Due_Date_HTTP500/evidence.md) |
| DEF-006 | No CSRF protection on state-changing forms; logout via GET | Major | Reproduced | 0 | [05_Security_Performance/Security/Defect_Evidence/DEF-006_No_CSRF_Protection_GET_Logout](../../05_Security_Performance/Security/Defect_Evidence/DEF-006_No_CSRF_Protection_GET_Logout/evidence.md) |
| DEF-007 | Hard-coded SECRET_KEY and debug=True | Major | Reproduced | 0 | [05_Security_Performance/Security/Defect_Evidence/DEF-007_Hardcoded_Secret_Key_Debug](../../05_Security_Performance/Security/Defect_Evidence/DEF-007_Hardcoded_Secret_Key_Debug/evidence.md) |
| DEF-008 | No throttling or lockout after repeated failed logins | Moderate | Reproduced | 0 | [05_Security_Performance/Security/Defect_Evidence/DEF-008_No_Login_Throttling](../../05_Security_Performance/Security/Defect_Evidence/DEF-008_No_Login_Throttling/evidence.md) |
| DEF-009 | No maximum length for task title | Minor | Reproduced | 0 | [05_Security_Performance/Security/Defect_Evidence/DEF-009_No_Max_Title_Length](../../05_Security_Performance/Security/Defect_Evidence/DEF-009_No_Max_Title_Length/evidence.md) |
| DEF-010 | No viewport meta tag - mobile shows shrunken desktop layout | Moderate | Reproduced | 1 | [03_Special_Testing/GUI_Compatibility/Defect_Evidence/DEF-010_No_Viewport_Meta_Mobile](../../03_Special_Testing/GUI_Compatibility/Defect_Evidence/DEF-010_No_Viewport_Meta_Mobile/evidence.md) |
| DEF-011 | Task table cells wrap at 1366 px | Minor | Reproduced | 1 | [03_Special_Testing/GUI_Compatibility/Defect_Evidence/DEF-011_Table_Wrap_1366px](../../03_Special_Testing/GUI_Compatibility/Defect_Evidence/DEF-011_Table_Wrap_1366px/evidence.md) |
| DEF-012 | Registration form clears input after a validation error | Minor | Reproduced | 2 | [03_Special_Testing/GUI_Compatibility/Defect_Evidence/DEF-012_Register_Form_Clears_Input](../../03_Special_Testing/GUI_Compatibility/Defect_Evidence/DEF-012_Register_Form_Clears_Input/evidence.md) |
| DEF-013 | 8-character password rejected (boundary off-by-one) | Moderate | Reproduced | 1 | [01_Black_Box/Defect_Evidence/DEF-013_Password_8_Char_Rejected](../../01_Black_Box/Defect_Evidence/DEF-013_Password_8_Char_Rejected/evidence.md) |
| DEF-014 | Task due today shown as Overdue | Moderate | Reproduced | 1 | [01_Black_Box/Defect_Evidence/DEF-014_Due_Today_Shown_Overdue](../../01_Black_Box/Defect_Evidence/DEF-014_Due_Today_Shown_Overdue/evidence.md) |
| DEF-015 | Task completed exactly 7 days ago not counted | Minor | Reproduced | 0 | [02_White_Box_Coverage/Defect_Evidence/DEF-015_Seven_Day_Completion_Boundary](../../02_White_Box_Coverage/Defect_Evidence/DEF-015_Seven_Day_Completion_Boundary/evidence.md) |
| DEF-016 | Duplicate usernames accepted; second account cannot log in | Moderate | Reproduced | 0 | [04_Web_API/Defect_Evidence/DEF-016_Duplicate_Usernames_Accepted](../../04_Web_API/Defect_Evidence/DEF-016_Duplicate_Usernames_Accepted/evidence.md) |
| DEF-017 | Form labels not programmatically linked to inputs | Minor | Reproduced | 1 | [03_Special_Testing/Usability_Accessibility/Defect_Evidence/DEF-017_Form_Labels_Not_Linked](../../03_Special_Testing/Usability_Accessibility/Defect_Evidence/DEF-017_Form_Labels_Not_Linked/evidence.md) |

**17 / 17 defects reproduced.**
