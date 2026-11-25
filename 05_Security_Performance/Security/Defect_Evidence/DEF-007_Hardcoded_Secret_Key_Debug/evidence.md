# DEF-007 - Hard-coded SECRET_KEY and debug=True

| Field | Value |
|---|---|
| Severity | Major |
| Found by | Alia (TC-SEC-013) |
| Related test cases | TC-SEC-013 |
| Status | Open - **REPRODUCED** on 2026-11-25 13:09:04 |
| Environment | Python 3.14.7, Flask 3.0.3, SQLite (fresh temp DB), Windows 11 |
| Reproduced by | `07_Test_Management/Defect_Evidence/reproduce_defects.py` (def007) |

## Expected
Secret read from environment; debug off by default.

## Actual (observed in this run)
A cookie forged with the key from the source code is accepted (HTTP 200) - full impersonation of user id 1. Debug server enabled.

## Captured request / response trace
```text
# setup: registered 'alice_d7' -> HTTP 201
# Session cookie issued by the app: eyJ1c2VyX2lkIjoxMCwidXNlcm5hbWUiOiJhbGljZV9kNyJ9.awZtdg.MJqQ...
# Attacker signs their own cookie with the hard-coded key: {'user_id': 1}
[1] >>> GET /api/tasks
    <<< HTTP 200
        []
# app.run(debug=True) present in source: True
```

## Root cause - faulty source lines (`>>` marks the defect)
```text
app/app.py
>>   28 | app.config["SECRET_KEY"] = "pytodo-pro-dev-secret"

app/app.py
>>  482 |     app.run(debug=True)
```
