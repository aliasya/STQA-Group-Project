# Week 5 – Performance Testing (BACKUP – Member 3 execution, Member 4 evaluation)

## 1. Objective

Measure how response time, throughput and error rate of PyTodo Pro's busiest endpoints change as simulated concurrent users increase. Find the point where response time stops being acceptable.

**Acceptance target** (defined before execution; no official NFR exists, so the team set one): at **20 concurrent users**, p95 response time **< 1000 ms** and error rate **0 %** for each endpoint. The 50-user level is exploratory (stress).

## 2. Environment (E1)

| Item | Value |
|---|---|
| Machine | Linux container, 2 logical CPUs (client and server on the same machine) |
| Software | Python 3.13, Flask 3.0.3 development server (`threaded=True`), debug off, SQLite |
| Tool | `perf_test.py` (Python threads + `requests`). Each virtual user = one thread with its own logged-in session |
| Database | Fresh DB, one user with 50 tasks (mixed categories and due dates) |

## 3. Workload

| Endpoint | Why chosen | Requests per user | Load levels (concurrent users) |
|---|---|---|---|
| `GET /api/tasks?per_page=50` | Most frequent call; one extra category query per row | 20 | 1, 5, 10, 20, 50 |
| `GET /api/dashboard` | Reads all tasks and computes urgency in Python | 20 | same |
| `GET /` (HTML task list) | Busiest page; DB + template rendering | 20 | same |
| `POST /api/login` | CPU-heavy (scrypt password hash) | 5 | same |

No think time (worst case). One warm-up run before measuring.

## 4. Results

Full table: `perf_results.md` / `perf_results.csv`. Chart: `perf_chart.png`.

| Endpoint | Users | Mean (ms) | p95 (ms) | Throughput (req/s) | Error rate |
|---|---|---|---|---|---|
| GET /api/tasks | 1 | 2.9 | 3.1 | 134.0 | 0 % |
| | 20 | 135.6 | 303.5 | 105.6 | 0 % |
| | 50 | 542.7 | 811.3 | 74.9 | 0 % |
| GET /api/dashboard | 1 | 3.2 | 3.4 | 122.4 | 0 % |
| | 20 | 70.0 | 107.2 | 172.0 | 0 % |
| | 50 | 204.9 | 287.2 | 159.4 | 0 % |
| GET / (HTML) | 1 | 4.5 | 4.7 | 112.8 | 0 % |
| | 20 | 156.5 | 325.2 | 96.0 | 0 % |
| | 50 | 673.8 | 947.6 | 62.5 | 0 % |
| POST /api/login | 1 | 102.3 | 104.8 | 8.0 | 0 % |
| | 20 | 772.5 | 919.7 | 20.7 | 0 % |
| | 50 | 1974.9 | **2318.7** | 19.9 | 0 % |

## 5. Test cases

| Test Case ID | Feature / Req | Technique | Objective | Preconditions | Test Data | Steps | Expected Result | Actual Result | Status | Evidence | Defect ID |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TC-PERF-001 | Task list API (REQ-17) | Load test | p95 < 1 s, 0 errors at 20 users | 50 tasks | 20 users × 20 req | Run perf_test.py | p95 < 1000 ms, errors 0 % | p95 303.5 ms, 0 % | Pass | perf_results.csv | – |
| TC-PERF-002 | Dashboard API (REQ-17) | Load test | as above | 50 tasks | 20 × 20 | Run perf_test.py | p95 < 1000 ms, errors 0 % | p95 107.2 ms, 0 % | Pass | perf_results.csv | – |
| TC-PERF-003 | HTML task list (REQ-17) | Load test | as above | 50 tasks | 20 × 20 | Run perf_test.py | p95 < 1000 ms, errors 0 % | p95 325.2 ms, 0 % | Pass | perf_results.csv | – |
| TC-PERF-004 | Login (REQ-17) | Load test | as above | 1 user | 20 × 5 | Run perf_test.py | p95 < 1000 ms, errors 0 % | p95 919.7 ms, 0 % (close to limit) | Pass | perf_results.csv | – |

## 6. Interpretation

- **No errors at any level.** The app stays functionally stable up to 50 concurrent users, so the threaded server handles concurrency without crashes or SQLite lock errors in this read-heavy workload.
- **Throughput plateaus early.** Once users go above ~5, extra users just queue: response time rises almost linearly and throughput stays flat (dashboard ~170 req/s) or even drops (task list 134 → 75 req/s). The machine is CPU-bound with only 2 CPUs.
- **Task list degrades faster than dashboard.** Both read all tasks, but the list runs **one extra `SELECT` per task** for the category name (N+1 query pattern) and serialises 50 rows. That is the likely cause of its lower throughput. Joining categories in one query would help.
- **Login is the bottleneck:** ~100 ms each because of scrypt hashing (good for security). Throughput saturates at ~20 logins/s; at 50 simultaneous logins p95 is 2.3 s. Acceptable for a to-do app, where logins are rare compared with page views.
- **Verdict:** meets the team's 20-user target on every endpoint. Login is close to the limit and is the first thing to fail under higher load.

## 7. Limitations

- Client and server share 2 CPUs, so the load generator steals CPU from the server. Absolute numbers are pessimistic. Trends are what matter.
- Flask development server, not a production WSGI server (gunicorn/waitress). Results are not production capacity.
- Read-heavy workload only. No concurrent writes, so SQLite write locking is untested.
- Short runs (≤ 1,000 requests per level). No soak test, no memory measurement.
- Results vary by laptop. Rerun on the presentation laptop and record its specs before quoting numbers.

## 8. Recommendations

1. Replace the per-row category lookup with a `JOIN` (N+1 query).
2. Deploy with a production WSGI server and several workers if real users are expected.
3. Keep scrypt; add login rate limiting (also fixes DEF-006) so heavy login traffic cannot exhaust CPU.
4. Future work: mixed read/write workload with Locust; a longer soak test; a second machine as load generator.
