"""
End-to-end curl proof for JWT auth + RBAC.
Tests:
  1. No token on protected route -> 401
  2. Valid admin token on admin-only route -> 200
  3. Valid employee token on admin-only route -> 403
"""
import subprocess
import sys
import time
import urllib.request
import urllib.error
import json
import os

# Set JWT_SECRET for the server process
os.environ["JWT_SECRET"] = "devhive-production-jwt-secret-2026-change-me"

# Start the backend server
print("=== Starting server ===")
server = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "api.index:app", "--host", "127.0.0.1", "--port", "8020"],
    cwd=r"c:\Users\Nandi\DevHive-next\frontend",
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env={**os.environ},
)

# Wait for server to be ready
time.sleep(4)

BASE = "http://127.0.0.1:8020"

def http_request(method, path, body=None, headers=None):
    """Make HTTP request and return (status_code, response_body)."""
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    hdrs = {"Content-Type": "application/json"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except Exception as e:
        return 0, {"error": str(e)}

try:
    # -------------------------------------------------------
    # TEST 1: No token on protected route -> expect 401
    # -------------------------------------------------------
    print("\n=== TEST 1: GET /api/analytics/dashboard with NO token ===")
    status, body = http_request("GET", "/api/analytics/dashboard")
    print(f"  Status: {status}")
    print(f"  Body:   {json.dumps(body)}")
    assert status == 401, f"FAIL: Expected 401, got {status}"
    print("  PASS ✓")

    # -------------------------------------------------------
    # Login as admin to get a real JWT
    # -------------------------------------------------------
    print("\n=== LOGIN: admin@devhive.ai ===")
    status, body = http_request("POST", "/api/auth/login", {
        "email": "admin@devhive.ai",
        "password": "admin123"
    })
    print(f"  Status: {status}")
    assert status == 200, f"FAIL: Login failed with {status}: {body}"
    admin_token = body["token"]
    print(f"  Token:  {admin_token[:50]}...")
    print("  PASS ✓")

    # -------------------------------------------------------
    # TEST 2: Valid admin token on admin-only route -> expect 200
    # -------------------------------------------------------
    print("\n=== TEST 2: GET /api/analytics/dashboard with ADMIN token ===")
    status, body = http_request("GET", "/api/analytics/dashboard", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    print(f"  Status: {status}")
    print(f"  Body:   {json.dumps(body)[:200]}...")
    assert status == 200, f"FAIL: Expected 200, got {status}"
    print("  PASS ✓")

    # -------------------------------------------------------
    # Login as employee to get a different JWT
    # -------------------------------------------------------
    print("\n=== LOGIN: employee@devhive.ai ===")
    status, body = http_request("POST", "/api/auth/login", {
        "email": "employee@devhive.ai",
        "password": "emp@123"
    })
    print(f"  Status: {status}")
    assert status == 200, f"FAIL: Login failed with {status}: {body}"
    employee_token = body["token"]
    print(f"  Token:  {employee_token[:50]}...")
    print("  PASS ✓")

    # -------------------------------------------------------
    # TEST 3: Employee token on admin-only route -> expect 403
    # -------------------------------------------------------
    print("\n=== TEST 3: GET /api/analytics/dashboard with EMPLOYEE token ===")
    status, body = http_request("GET", "/api/analytics/dashboard", headers={
        "Authorization": f"Bearer {employee_token}"
    })
    print(f"  Status: {status}")
    print(f"  Body:   {json.dumps(body)}")
    assert status == 403, f"FAIL: Expected 403, got {status}"
    print("  PASS ✓")

    print("\n" + "="*60)
    print("ALL 3 TESTS PASSED ✓✓✓")
    print("="*60)

finally:
    server.terminate()
    server.wait(timeout=5)
    print("\nServer stopped.")
