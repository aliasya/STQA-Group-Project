# Week 5 – STRIDE Threat Table  (Member 4)

> ⬜ **TO FILL by Member 4.** Replace every `<<...>>` and fill the empty table rows.
> Backup copy (use only if needed): `_BACKUP_Members_2_3_4/05_Security_Performance/STRIDE/`

Member 1 derives and runs the security **test cases** from this table (`../Security/`). The threat IDs T-01…T-12 are already used in Member 1's report, so keep the same numbering.

| Threat ID | STRIDE | Asset / function | Threat description | Likelihood | Impact | Derived test(s) |
|---|---|---|---|---|---|---|
| T-01 | Spoofing | Login | Password guessing / brute force | | | TC-SEC-001, 002 |
| T-02 | Spoofing | Registration | Duplicate username impersonation | | | TC-SEC-004 |
| T-03 | Spoofing | Session | Session reuse after logout / forged cookie | | | TC-SEC-003, 013 |
| T-04 | Tampering | Task API | Modify/delete another user's task (IDOR) | | | TC-SEC-005, 006 |
| T-05 | Tampering | Search | SQL injection via `q` | | | TC-SEC-007, 008 |
| T-06 | Tampering | Task title | Stored XSS | | | TC-SEC-009 |
| T-07 | Tampering | Web forms | Cross-site request forgery | | | TC-SEC-010 |
| T-08 | Repudiation | All actions | No audit trail of changes | | | (review) |
| T-09 | Info disclosure | Password storage | Plain-text / weak hashes | | | TC-SEC-011 |
| T-10 | Info disclosure | Errors / config | Tracebacks, debug mode, hard-coded secret | | | TC-SEC-012, 013, 014 |
| T-11 | Denial of service | Task create | Oversized input | | | TC-SEC-015 |
| T-12 | Elevation | Protected routes | Access without login | | | TC-SEC-016, 017 |
