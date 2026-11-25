# DEF-015 - Task completed exactly 7 days ago not counted

| Field | Value |
|---|---|
| Severity | Minor |
| Found by | Fatin (WB, BUG-003) |
| Related test cases | WB-001 (test_helpers.py) |
| Status | Open - **REPRODUCED** on 2026-11-25 13:40:18 |
| Environment | Python 3.14.7, Flask 3.0.3, SQLite (fresh temp DB), Windows 11 |
| Reproduced by | `07_Test_Management/Defect_Evidence/reproduce_defects.py` (def015) |

## Expected
Completed exactly 7 days ago counts (spec: inclusive).

## Actual (observed in this run)
A task completed exactly 7 days ago returns False (age.days < n) and is missing from the 'completed in last 7 days' count.

## Terminal evidence (PNG)
Requests replayed as the equivalent `curl` commands; every status code and body shown is the real response from this run.

![Terminal evidence](terminal_evidence.png)

## Root cause in source (PNG)

![Faulty source lines](source_root_cause.png)

## Captured request / response trace (text)
```text
# Spec: a task counts if completed within the last 7 days, INCLUSIVE of exactly 7 days ago
$ cd app && python -c "from datetime import datetime as D; from helpers import completed_in_last_n_days as f; now=D(2026,11,25,12); [print(d, f(ts, 7, now)) for d, ts in [(6,'2026-11-19 12:00:00'),(7,'2026-11-18 12:00:00'),(8,'2026-11-17 12:00:00')]]"
    6 True
    7 False
    8 False
# Expected: 6 True / 7 True / 8 False  ->  exactly 7 days ago is WRONG
[1] >>> POST /api/register   json={'username': 'alice_d15', 'password': 'password123'}
    <<< HTTP 201
        {"id":17,"username":"alice_d15"}
# setup: task completed, completed_at back-dated to exactly 7 days ago
[2] >>> GET /api/dashboard
    <<< HTTP 200
        {"completed_this_week":0,"due_soon":0,"open":0,"overdue":0,"total":1}
# 1 task completed exactly 7 days ago, but completed_this_week = 0
```

## Root cause - faulty source lines (`>>` marks the defect)
```text
app/helpers.py
     61 | def completed_in_last_n_days(completed_at_str, n=7, now=None):
     62 |     """
     63 |     Spec: a task counts toward the "completed in the last N days" total
     64 |     if it was completed within the last N days, inclusive of exactly N
     65 |     days ago.
     66 | 
     67 |     completed_at_str: "YYYY-MM-DD HH:MM:SS" string, or falsy if not completed.
     68 |     """
     69 |     if not completed_at_str:
     70 |         return False
     71 |     if now is None:
     72 |         now = datetime.now()
     73 |     completed_at = datetime.strptime(completed_at_str, "%Y-%m-%d %H:%M:%S")
     74 |     age = now - completed_at
>>   75 |     return age.total_seconds() > 0 and age.days < n
```

## Supporting evidence from other members
- [`02_White_Box_Coverage/evidence/WB-001_Unit_Test_Results.png`](../../../02_White_Box_Coverage/evidence/WB-001_Unit_Test_Results.png)
