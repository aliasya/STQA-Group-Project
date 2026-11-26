r"""Turn JMeter result files (.jtl, CSV format) into numbers and graphs for your report.

Usage:
    python analyze_results.py results\users_50\results.jtl            # one run
    python analyze_results.py results\users_*\results.jtl --steps      # several runs (load steps)

Outputs (in the folder called "analysis"):
    summary.csv              per-request statistics (samples, RPS, mean, 90/95/99 percentile, error %)
    percentiles_over_time.png  response time p50/p90/p95/p99 over the test
    error_rate_over_time.png   error rate (%) over the test
    throughput_vs_users.png    (only with --steps) throughput and p95 for every load level
"""
import argparse
import glob
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

SLA_MS = 500            # example SLA: 95% of requests under 500 ms
WINDOW = "5s"           # size of the time buckets in the graphs


def load(path):
    df = pd.read_csv(path)
    df = df[~df["label"].str.match(r"^\d\d .*-\d+$")].copy()   # drop redirect sub-samples
    df["time"] = pd.to_datetime(df["timeStamp"], unit="ms")
    df["error"] = (~df["success"].astype(str).str.lower().eq("true")).astype(int)
    return df


def stats(df):
    secs = max((df["timeStamp"].max() + df["elapsed"].iloc[-1] - df["timeStamp"].min()) / 1000.0, 1e-9)
    e = df["elapsed"]
    return {
        "samples": len(df), "throughput_rps": round(len(df) / secs, 2),
        "mean_ms": round(e.mean(), 1), "median_ms": round(e.median(), 1),
        "p90_ms": round(e.quantile(0.90), 1), "p95_ms": round(e.quantile(0.95), 1),
        "p99_ms": round(e.quantile(0.99), 1), "max_ms": int(e.max()),
        "error_pct": round(100 * df["error"].mean(), 2),
    }


def summary_table(df):
    rows = {label: stats(g) for label, g in df.groupby("label")}
    rows["TOTAL"] = stats(df)
    return pd.DataFrame(rows).T


def graphs_for_run(df, outdir, tag=""):
    d = df.set_index("time").sort_index()
    q = d["elapsed"].resample(WINDOW)
    pct = pd.DataFrame({"p50": q.quantile(0.50), "p90": q.quantile(0.90),
                        "p95": q.quantile(0.95), "p99": q.quantile(0.99)}).dropna()
    t0 = d.index.min()
    pct = pct.iloc[:-1] if len(pct) > 3 else pct          # last bucket is partial
    x = (pct.index - t0).total_seconds()
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for col, style in (("p50", "-"), ("p90", "-"), ("p95", "-"), ("p99", "-")):
        ax.plot(x, pct[col], style, label=col.replace("p", "") + "th percentile", linewidth=2)
    ax.axhline(SLA_MS, color="red", linestyle="--", label=f"SLA {SLA_MS} ms")
    ax.set_xlabel("Elapsed time (s)"); ax.set_ylabel("Response time (ms)")
    ax.set_title("Response time percentiles over time"); ax.legend(); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(os.path.join(outdir, f"percentiles_over_time{tag}.png"), dpi=150); plt.close(fig)

    err = d["error"].resample(WINDOW).mean().dropna() * 100
    thr = d["elapsed"].resample(WINDOW).count() / pd.Timedelta(WINDOW).total_seconds()
    if len(thr) > 3: err, thr = err.iloc[:-1], thr.iloc[:-1]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar((err.index - t0).total_seconds(), err, width=4, color="#A6402A")
    ax.set_ylim(0, max(5, err.max() * 1.2)); ax.set_xlabel("Elapsed time (s)"); ax.set_ylabel("Error rate (%)")
    ax.set_title("Error rate over time"); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(os.path.join(outdir, f"error_rate_over_time{tag}.png"), dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot((thr.index - t0).total_seconds(), thr, color="#2E5E3E", linewidth=2, label="Throughput (requests/s)")
    ax2 = ax.twinx()
    users = d["allThreads"].resample(WINDOW).max()
    ax2.plot((users.index - t0).total_seconds(), users, color="#4A2E17", linestyle=":", label="Active users")
    ax.set_xlabel("Elapsed time (s)"); ax.set_ylabel("Requests per second"); ax2.set_ylabel("Active users")
    ax.set_title("Throughput and active users over time"); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(os.path.join(outdir, f"throughput_over_time{tag}.png"), dpi=150); plt.close(fig)


def steps_graph(files, outdir):
    rows = []
    for f in files:
        df = load(f)
        m = re.search(r"users_(\d+)", f.replace("\\", "/"))
        users = int(m.group(1)) if m else int(df["allThreads"].max())
        s = stats(df); s["users"] = users; rows.append(s)
    t = pd.DataFrame(rows).sort_values("users")
    t.to_csv(os.path.join(outdir, "steps.csv"), index=False)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(t["users"], t["throughput_rps"], "o-", color="#2E5E3E", linewidth=2, label="Throughput (requests/s)")
    ax.set_xlabel("Concurrent users"); ax.set_ylabel("Requests per second")
    ax2 = ax.twinx(); ax2.plot(t["users"], t["p95_ms"], "s--", color="#A6402A", label="95th percentile (ms)")
    ax2.set_ylabel("95th percentile response time (ms)")
    ax.set_title("Throughput and p95 versus load"); ax.grid(alpha=.3)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax.legend(h1 + h2, l1 + l2, loc="upper left")
    fig.tight_layout(); fig.savefig(os.path.join(outdir, "throughput_vs_users.png"), dpi=150); plt.close(fig)
    best = t.loc[t["throughput_rps"].idxmax()]
    print(f"\nMaximum throughput: {best['throughput_rps']} requests/s at {int(best['users'])} users "
          f"(p95 = {best['p95_ms']} ms, errors = {best['error_pct']} %)")
    print(t[["users", "throughput_rps", "mean_ms", "p95_ms", "p99_ms", "error_pct"]].to_string(index=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+"); ap.add_argument("--steps", action="store_true")
    ap.add_argument("--out", default="analysis")
    a = ap.parse_args()
    files = sorted({f for pat in a.files for f in glob.glob(pat)})
    os.makedirs(a.out, exist_ok=True)
    df = load(files[0]) if not a.steps else load(max(files, key=lambda f: int(re.search(r"users_(\d+)", f.replace("\\", "/")).group(1)) if re.search(r"users_(\d+)", f.replace("\\", "/")) else 0))
    table = summary_table(df)
    table.to_csv(os.path.join(a.out, "summary.csv"))
    print(table.to_string())
    graphs_for_run(df, a.out)
    if a.steps and len(files) > 1:
        steps_graph(files, a.out)
    print(f"\nFiles written to: {os.path.abspath(a.out)}")


if __name__ == "__main__":
    main()
