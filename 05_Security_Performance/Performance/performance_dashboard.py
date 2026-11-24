import json
import time
import statistics
import urllib.request
import http.cookiejar
import getpass
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://127.0.0.1:5000"
URL = BASE_URL + "/api/dashboard"

username = input("Test username: ")
password = getpass.getpass("Test password: ")
cookies = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
login_request = urllib.request.Request(
    BASE_URL + "/api/login",
    data=json.dumps({"username": username, "password": password}).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with opener.open(login_request, timeout=5) as response:
    if response.status != 200:
        raise RuntimeError("Login failed")
print("Login successful!")
cookie_header = "; ".join(f"{cookie.name}={cookie.value}" for cookie in cookies)


def send_request():
    start = time.perf_counter()
    try:
        request = urllib.request.Request(URL, headers={"Cookie": cookie_header})
        with urllib.request.urlopen(request, timeout=5) as response:
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
