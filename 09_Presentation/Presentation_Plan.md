# Week 9 – Final Presentation and Live Demo Plan (owner: Member 1)

**Length:** `<<check lecturer's limit, e.g. 20 min + 5 min Q&A>>` · **Format:** Slides + live demo · Every member presents their own part.

## 1. Slide outline (≈ 16 slides)

| # | Slide | Presenter | Content (keep to 3–4 bullets or 1 visual) | Time |
|---|---|---|---|---|
| 1 | Title | M1 | Project, team, roles | 0:30 |
| 2 | PyTodo Pro & our mission | M1 | What the app does; "independent QA team"; testing vs QA vs QC | 1:00 |
| 3 | Requirements & risk matrix | M1 | REQ-01–17; top risks (access control, security = 9) → test priorities | 1:30 |
| 4 | Test strategy | M1 | Table: week → technique → tool; risk-based; evidence chain | 1:00 |
| 5 | Black-box design | M2 | One BVA table (password 7/8/9; due −1/0/+1/+2/+3) + one decision table | 1:30 |
| 6 | Black-box results | M2 | 35 cases, 7 fail; all on designed boundaries | 1:00 |
| 7 | White-box + coverage | M3 | CFG of `compute_urgency` (5 outcomes vs 4 returns), V(G)=5, coverage 100 % / 79 % | 1:30 |
| 8 | GUI & compatibility | M1 | Desktop vs mobile screenshot side-by-side (DEF-010); config matrix | 1:00 |
| 9 | Usability & accessibility | M4 | Contrast table; unlabeled controls; feedback gaps | 1:00 |
| 10 | API testing | M3 | 47 executions; three HTTP 500 crashes; UI vs API inconsistency | 1:00 |
| 11 | STRIDE → security tests | M4 → M1 | STRIDE table (top 3 risks = 9) → 4 Critical defects | 1:30 |
| 12 | Performance | M3/M4 | Chart p95 & throughput vs users; login bottleneck; limitations | 1:00 |
| 13 | Automation & regression | M3 | Strict-xfail idea; 28 checks in 7 s; CI pipeline | 1:00 |
| 14 | Metrics & defects | M4 | Pass rate by level; severity chart; interpretation | 1:00 |
| 15 | ISO 25010, residual risk, process improvements | M1 | Evaluated vs not evaluated; top residual risks; Agile/DevOps practices | 1:30 |
| 16 | Verdict & recommendations | M1 | "Not release-ready: 4 Critical"; top 3 fixes; testing ≠ proof of no defects | 1:00 |
| – | **Live demo** (see `Demo_Script.md`) | M1 + M3 | 5 min | 5:00 |

## 2. Visuals to reuse (already in the repo)

- `03_Special_Testing/GUI_Compatibility/screenshots/CFG-01_05_task_list.png` vs `CFG-04_05_task_list.png` (desktop vs mobile)
- `_BACKUP_Members_2_3_4/05_Security_Performance/Performance/perf_chart.png`
- `_BACKUP_Members_2_3_4/07_Test_Management/defects_by_severity.png`, `defects_by_area.png`
- Coverage HTML page (screenshot of `helpers.py` 100 %)

## 3. Likely questions and prepared answers

| Question | Answer (owner) |
|---|---|
| Why these techniques for these features? | Risk matrix + feature nature: ranges → BVA, combinations → decision table, states → state transition (M2) |
| Coverage is 100 %. Why were there still defects? | Coverage shows code was executed, not that results were correct. All 3 defects were found by asserting spec values (M3) |
| What is the biggest remaining risk? | Cross-user data exposure (SQLi/IDOR/XSS). Fix before release (M1) |
| How do you know performance is acceptable? | 20-user target set before the run; met; limits stated (one machine, dev server) (M4) |
| Why are known-failing tests "xfail" and not just failing? | Keeps CI usable and gives an automatic signal when a defect is fixed (M3) |
| Did you prove the app is correct? | No. Testing reveals defects; we report residual risk and untested areas (M1) |
| What would you do with more time? | Remaining browser configs, Locust mixed load + soak, screen-reader test, retest after fixes (M1) |

## 4. Rehearsal checklist

- [ ] Slides final 2 days before; each member rehearses their part (≤ time)
- [ ] Full run-through **twice** on the presenting laptop, including the demo
- [ ] `pip install -r requirements-test.txt` done on presenting laptop; Chrome updated
- [ ] Demo commands tested on that laptop (see Demo_Script.md)
- [ ] Backup screen recording of the demo saved locally (in case Wi-Fi/laptop fails)
- [ ] Performance numbers re-run on the presenting laptop OR clearly labelled "measured on E1"
