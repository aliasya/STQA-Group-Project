# Week 5 – STRIDE Threat Table (Member 4)

| Threat ID | STRIDE | Asset / function | Threat description | Likelihood | Impact | Derived test(s) |
|---|---|---|---|---|---|---|
| T-01 | Spoofing | Login | Password guessing / brute force | High | High | TC-SEC-001, 002 |
| T-02 | Spoofing | Registration | Duplicate username impersonation | High | Medium | TC-SEC-004 |
| T-03 | Spoofing | Session | Session reuse after logout / forged cookie | Low | High | TC-SEC-003, 013 |
| T-04 | Tampering | Task API | Modify/delete another user's task (IDOR) | High | High | TC-SEC-005, 006 |
| T-05 | Tampering | Search | SQL injection via `q` | High | High | TC-SEC-007, 008 |
| T-06 | Tampering | Task title | Stored XSS | Medium | High | TC-SEC-009 |
| T-07 | Tampering | Web forms | Cross-site request forgery | Medium | High | TC-SEC-010 |
| T-08 | Repudiation | All actions | No audit trail of changes | High | Moderate | Code review (Failed – no audit logging) |
| T-09 | Info disclosure | Password storage | Plain-text / weak hashes | Low | High | TC-SEC-011 |
| T-10 | Info disclosure | Errors / config | Tracebacks, debug mode, hard-coded secret | High | High | TC-SEC-012, 013, 014 |
| T-11 | Denial of service | Task create | Oversized input | Medium | High | TC-SEC-015 |
| T-12 | Elevation | Protected routes | Access without login | Low | High | TC-SEC-016, 017 |

### Risk Assessment Criteria

Likelihood:
- High: The threat is supported by confirmed weaknesses or insufficient security controls.
- Medium: The threat is possible under certain conditions.
- Low: Existing testing indicates that the relevant security control is functioning, or the weakness has not been confirmed.

Impact:
- High: Could result in unauthorised access, sensitive information exposure, data manipulation or significant disruption.
- Moderate: Could affect accountability, investigation or the ability to trace user activities.

The ratings represent qualitative assessments based on the identified threats and observed testing results. They do not represent measured attack probabilities.
