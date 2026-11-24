import time
import statistics
import urllib.request
from concurrent.futures import ThreadPoolExecutor

URL = "http://127.0.0.1:5000/api/categories"


def send_request():
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(URL, timeout=5) as response:
            status = response.status
            response.read()
    except Exception:
        status = 0
    elapsed = time.perf_counter() - start
    return elapsed, status


def run_test(workers, total_requests=100):
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(lambda _: send_request(), range(total_requests)))
    duration = time.perf_counter() - start
    times = [result[0] for result in results]
    errors = sum(1 for _, status in results if status != 200)
    print(f"\nConcurrent workers: {workers}")
    print(f"Total requests: {total_requests}")
    print(f"Average response time: {statistics.mean(times)*1000:.2f} ms")
    print(f"Maximum response time: {max(times)*1000:.2f} ms")
    print(f"Throughput: {total_requests/duration:.2f} requests/sec")
    print(f"Error rate: {errors/total_requests*100:.2f}%")


if __name__ == "__main__":
    for workers in [1, 2, 4]:
        run_test(workers)
