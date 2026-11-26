# Week 5 – Performance Testing (Member 3 executes, Member 4 evaluates)

## 1. Objective

The objective of performance testing was to evaluate how PyTodo Pro performs when multiple users access the application simultaneously. Apache JMeter was used to simulate concurrent users and measure response time, throughput and error rate under baseline and stress testing conditions. The results were analysed to identify the workload level at which application performance and reliability began to deteriorate.

## 2. Environment (define BEFORE running)

| Item | Value |
|---|---|
| Machine / CPU / RAM | Laptop, Intel Core i5-12500H, 8 GB DDR5 RAM |
| OS | Windows 11 |
| Server | Flask development server, debug off |
| Tool | Apache JMeter 5.6.3 |
| Supporting software | Java 21.0.2 LTS, Python 3.10 |
| Application URL | `http://127.0.0.1:5000` |

## 3. Workload

| Endpoint / Activity | Users (levels) | Requests per user | Data in DB |
|---|---|---|---|
| Registration and login | 50 baseline; 5, 10, 25, 50, 100, 200, 400 stress | Workflow-based; exact count per user not separately recorded | Local SQLite database |
| Viewing task list | Same test configurations | Workflow-based; exact count per user not separately recorded | Local SQLite database |
| Creating a task | Same test configurations | Workflow-based; exact count per user not separately recorded | Local SQLite database |
| Retrieving tasks through API | Same test configurations | Workflow-based; exact count per user not separately recorded | Local SQLite database |

**Baseline configuration:**
- 50 virtual users
- 10-second ramp-up period
- 100-second test duration
- Random 1–3 second think time between activities

**Stress configuration:**
- 5, 10, 25, 50, 100, 200 and 400 virtual users
- No think time
- Five users starting per second, with a minimum ramp-up of one second
- Test duration: ramp-up period plus 30 seconds

## 4. Results

### 4.1 Baseline and Stress Testing (Set 1)

| Test Type | Users | Mean (ms) | P95 (ms) | Throughput (req/s) | Error Rate (%) |
|---|---:|---:|---:|---:|---:|
| Baseline | 50 | 22.76 | 57.65 | 24.07 | 0.00 |
| Stress | 5 | 64.00 | 144.00 | 76.29 | 0.00 |
| Stress | 10 | 117.80 | 300.50 | 81.55 | 0.00 |
| Stress | 25 | 266.50 | 1082.00 | 76.03 | 0.13 |
| Stress | 50 | 205.60 | 741.40 | 207.09 | 60.86 |
| Stress | 100 | 124.90 | 308.00 | 624.78 | 88.84 |
| Stress | 200 | 122.80 | 509.20 | 1106.74 | 95.06 |
| Stress | 400 | 78.50 | 125.00 | 2514.64 | 98.34 |

### 4.2 Additional Performance Testing (Set 2)

| Test Type | Users | Mean (ms) | P95 (ms) | Throughput (req/s) | Error Rate (%) |
|---|---:|---:|---:|---:|---:|
| Additional | 100 | 71.00 | 207.00 | 48.20 | 0.00 |
| Additional | 300 | 279.00 | 1727.00 | 130.20 | 43.52 |
| Additional | 400 | 279.00 | 1244.00 | 173.80 | 59.08 |

**Note:** Set 1 and Set 2 are presented separately because their test configurations were not identical. Set 1 stress tests used no think time, whereas the additional tests used random 1–3 second think time. The exact ramp-up and duration settings for Set 2 were not confirmed.

## 5. Interpretation, Limitations, Recommendations

### Interpretation

The baseline test showed that the application handled 50 virtual users with no recorded errors. The average response time was 22.76 ms, while the P95 response time was 57.65 ms.

During stress testing, 10 concurrent users was the highest tested workload that met both performance targets:
- P95 response time below 500 ms.
- Error rate below 1%.

At 25 users, the P95 response time increased to 1082 ms, exceeding the response-time target. At 50 users, the error rate increased significantly to 60.86%.

At higher loads, throughput continued to increase. However, this did not indicate better performance because the throughput calculation included failed requests. For example, the 400-user test recorded 2514.64 requests per second but also had a 98.34% error rate.

Database locking errors were also observed when multiple users attempted to create tasks concurrently, suggesting possible SQLite write contention.

Overall, the results indicate that PyTodo Pro performed well under lighter workloads but experienced reliability and response-time issues as the workload increased.

### Limitations

1. The application and JMeter were executed on the same laptop, so available system resources may have influenced the results.
2. CPU and memory utilisation were not monitored.
3. Testing was conducted in a local development environment rather than a production server.
4. The additional test configurations were not fully confirmed, limiting direct comparison between Set 1 and Set 2.
5. Simulated virtual users may not fully represent actual user behaviour.

### Recommendations

1. **Improve Database Management:** Consider migrating from SQLite to PostgreSQL to provide better support for concurrent database operations and reduce database locking issues.
2. **Improve Transaction Handling:** Ensure database connections and transactions are properly managed. If SQLite is retained, evaluate Write-Ahead Logging (WAL) mode and a suitable busy timeout.
3. **Use a Production Server:** Replace Flask's development server with a production WSGI server, such as Waitress, to improve application deployment and request handling.
4. **Conduct Further Performance Testing:** Repeat the tests using a separate machine for JMeter, monitor CPU and memory utilisation, and apply consistent test configurations to obtain more reliable performance measurements.
