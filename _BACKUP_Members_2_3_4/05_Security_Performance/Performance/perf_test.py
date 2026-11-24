"""
Week 5 - Controlled performance experiment (BACKUP for Member 3 execution / Member 4 evaluation)

Objective
    How do response time, throughput and error rate of PyTodo Pro's busiest
    endpoints change as simulated concurrent users increase?

Workload (defined BEFORE execution)
    * Server: PyTodo Pro on the Flask/Werkzeug development server (threaded),
      debug OFF, fresh SQLite DB, started by this script on 127.0.0.1.
    * Data: one user with 50 tasks (mixed categories/due dates).
    * Endpoints: GET /api/tasks?per_page=50, GET /api/dashboard,
      GET / (HTML task list), POST /api/login (password hashing).
    * Load levels: 1, 5, 10, 20, 50 concurrent virtual users (threads);
      each user sends REQS_PER_USER requests back-to-back (no think time).
    * Metrics: mean / median / p95 / max response time (ms),
      throughput (requests/s), error rate (% non-2xx or exceptions).

Run from repo root:   python _BACKUP_Members_2_3_4/05_Security_Performance/Performance/perf_test.py
Outputs:              perf_results.csv, perf_results.md, perf_chart.png (if matplotlib installed)

Limitations: client and server share one machine (they compete for CPU);
development server, not a production WSGI server; SQLite; short runs. Results
show RELATIVE trends on this machine, not production capacity.
"""
import csv
import os
import platform
import statistics
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
def _find_repo_root(start):
    """Walk up until we find app/app.py, so the script works from the main folder or the backup folder."""
    d = start
    while not os.path.exists(os.path.join(d, "app", "app.py")):
        parent = os.path.dirname(d)
        if parent == d:
            raise SystemExit("Run this inside the PyTodo-Pro-QA repository")
        d = parent
    return d


ROOT = _find_repo_root(HERE)
sys.path.insert(0, os.path.join(ROOT, "app"))
import app as pytodo  # noqa: E402

LEVELS = [1, 5, 10, 20, 50]
REQS_PER_USER = 20
LOGIN_REQS_PER_USER = 5          # login is slow (hashing) - fewer requests
USER, PW = "perf_user", "password123"


def start_server():
    import logging
    from werkzeug.serving import make_server
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    pytodo.DATABASE = os.path.join(tempfile.mkdtemp(), "perf.db")
    pytodo.init_db()
    srv = make_server("127.0.0.1", 0, pytodo.app, threaded=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_port}"


def seed(base):
    s = requests.Session()
    s.post(f"{base}/api/register", json={"username": USER, "password": PW})
    for i in range(50):
        due = (date.today() + timedelta(days=(i % 10) - 3)).isoformat() if i % 5 else None
        s.post(f"{base}/api/tasks", json={"title": f"Perf task {i}", "category_id": i % 4 + 1, "due_date": due})


def one_user(base, method, path, n, body):
    s = requests.Session()
    s.post(f"{base}/api/login", json={"username": USER, "password": PW})
    out = []
    for _ in range(n):
        t0 = time.perf_counter()
        try:
            r = s.request(method, base + path, json=body, timeout=30)
            ok = 200 <= r.status_code < 300
        except requests.RequestException:
            ok = False
        out.append(((time.perf_counter() - t0) * 1000, ok))
    return out


def run_level(base, name, method, path, users, n, body=None):
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=users) as ex:
        futures = [ex.submit(one_user, base, method, path, n, body) for _ in range(users)]
        samples = [x for f in futures for x in f.result()]
    wall = time.perf_counter() - t0
    times = sorted(t for t, _ in samples)
    errors = sum(1 for _, ok in samples if not ok)
    return {
        "endpoint": name, "users": users, "requests": len(samples),
        "mean_ms": round(statistics.mean(times), 1), "median_ms": round(statistics.median(times), 1),
        "p95_ms": round(times[int(0.95 * (len(times) - 1))], 1), "max_ms": round(times[-1], 1),
        "throughput_rps": round(len(samples) / wall, 1), "error_rate_pct": round(100 * errors / len(samples), 2),
    }


def main():
    srv, base = start_server()
    seed(base)
    endpoints = [("GET /api/tasks?per_page=50", "GET", "/api/tasks?per_page=50", REQS_PER_USER, None),
                 ("GET /api/dashboard", "GET", "/api/dashboard", REQS_PER_USER, None),
                 ("GET / (HTML list)", "GET", "/", REQS_PER_USER, None),
                 ("POST /api/login", "POST", "/api/login", LOGIN_REQS_PER_USER, {"username": USER, "password": PW})]
    one_user(base, "GET", "/api/tasks", 5, None)   # warm-up, not measured
    rows = []
    for name, m, p, n, body in endpoints:
        for u in LEVELS:
            r = run_level(base, name, m, p, u, n, body)
            rows.append(r)
            print(f"{name:28} users={u:3}  mean={r['mean_ms']:8.1f}ms  p95={r['p95_ms']:8.1f}ms  "
                  f"rps={r['throughput_rps']:7.1f}  err={r['error_rate_pct']}%")
    srv.shutdown()

    with open(os.path.join(HERE, "perf_results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    env = (f"{platform.system()} {platform.release()}, Python {platform.python_version()}, "
           f"{os.cpu_count()} logical CPUs, Flask dev server (threaded), SQLite")
    md = ["# Performance Results (generated)", "", f"Environment: {env}", "",
          f"Workload: levels {LEVELS} concurrent users; {REQS_PER_USER} requests/user "
          f"({LOGIN_REQS_PER_USER} for login); 50 tasks in DB; no think time.", "",
          "| Endpoint | Users | Requests | Mean (ms) | Median (ms) | p95 (ms) | Max (ms) | Throughput (req/s) | Error rate (%) |",
          "|---|---|---|---|---|---|---|---|---|"]
    md += [f"| {r['endpoint']} | {r['users']} | {r['requests']} | {r['mean_ms']} | {r['median_ms']} | {r['p95_ms']} | "
           f"{r['max_ms']} | {r['throughput_rps']} | {r['error_rate_pct']} |" for r in rows]
    open(os.path.join(HERE, "perf_results.md"), "w").write("\n".join(md) + "\n")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(11, 4))
        for name in dict.fromkeys(r["endpoint"] for r in rows):
            rs = [r for r in rows if r["endpoint"] == name]
            ax[0].plot([r["users"] for r in rs], [r["p95_ms"] for r in rs], marker="o", label=name)
            ax[1].plot([r["users"] for r in rs], [r["throughput_rps"] for r in rs], marker="o", label=name)
        ax[0].set(title="p95 response time vs users", xlabel="Concurrent users", ylabel="ms")
        ax[1].set(title="Throughput vs users", xlabel="Concurrent users", ylabel="requests/s")
        for a in ax:
            a.grid(alpha=.3); a.spines[["top", "right"]].set_visible(False)
        ax[0].set_yscale("log"); ax[1].legend(fontsize=8, frameon=False)
        fig.tight_layout(); fig.savefig(os.path.join(HERE, "perf_chart.png"), dpi=130)
    except ImportError:
        print("matplotlib not installed - skipping chart")


if __name__ == "__main__":
    main()
