"""
Veryfyn API Test Suite
Run with: python test_backend.py

Tests all backend endpoints and reports pass/fail with details.
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
PASS = "\033[92m✅ PASS\033[0m"
FAIL = "\033[91m❌ FAIL\033[0m"
WARN = "\033[93m⚠️  WARN\033[0m"

results = []

def test(name, fn):
    try:
        result = fn()
        status = PASS if result["ok"] else FAIL
        print(f"{status} {name}")
        if not result["ok"]:
            print(f"       → {result.get('error', 'Unknown error')}")
        results.append((name, result["ok"]))
        return result
    except Exception as e:
        print(f"{FAIL} {name}")
        print(f"       → Exception: {e}")
        results.append((name, False))
        return {"ok": False, "error": str(e)}


# ─── SERVER REACHABILITY ──────────────────────────────────────────────────────

def check_server_running():
    try:
        r = requests.get(f"{BASE_URL}/", timeout=3)
        return {"ok": r.status_code == 200, "data": r.json()}
    except requests.ConnectionError:
        return {"ok": False, "error": "Server not running. Start with: uvicorn backend.main:app --reload --port 8000"}

def check_health_endpoint():
    r = requests.get(f"{BASE_URL}/health", timeout=3)
    data = r.json()
    ok = r.status_code == 200 and data.get("status") == "healthy"
    return {"ok": ok, "data": data, "error": f"Got status: {data.get('status')}"}

def check_api_status_endpoint():
    r = requests.get(f"{BASE_URL}/api/status", timeout=3)
    return {"ok": r.status_code == 200, "data": r.json()}

def check_db_connection():
    r = requests.get(f"{BASE_URL}/api/db/test", timeout=3)
    data = r.json()
    ok = data.get("status") == "connected"
    return {"ok": ok, "data": data, "error": data.get("message", "")}

def check_docs_available():
    r = requests.get(f"{BASE_URL}/docs", timeout=3)
    return {"ok": r.status_code == 200, "error": f"HTTP {r.status_code}"}


# ─── CORS HEADERS ─────────────────────────────────────────────────────────────

def check_cors_headers():
    r = requests.options(
        f"{BASE_URL}/api/habits",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
        timeout=3,
    )
    has_cors = "access-control-allow-origin" in r.headers
    origin = r.headers.get("access-control-allow-origin", "MISSING")
    return {
        "ok": has_cors,
        "data": {"cors_origin_header": origin},
        "error": "CORS headers missing — React frontend will be blocked",
    }


# ─── HABITS ENDPOINTS ─────────────────────────────────────────────────────────

created_habit_id = None

def check_get_habits():
    r = requests.get(f"{BASE_URL}/api/habits", timeout=3)
    data = r.json()
    ok = r.status_code == 200 and "habits" in data and "total" in data
    return {"ok": ok, "data": data, "error": f"Expected {{habits, total}}, got: {list(data.keys())}"}

def check_create_habit():
    global created_habit_id
    payload = {
        "name": "Test Habit - DELETE ME",
        "description": "Created by test suite",
        "frequency": "daily",
        "icon": "🧪",
        "color": "#FF5733",
        "habit_type": "boolean",
        "category": "test",
    }
    r = requests.post(f"{BASE_URL}/api/habits", json=payload, timeout=3)
    data = r.json()
    ok = r.status_code == 201 and "id" in data
    if ok:
        created_habit_id = data["id"]
    return {"ok": ok, "data": data, "error": f"HTTP {r.status_code}: {data}"}

def check_get_single_habit():
    if not created_habit_id:
        return {"ok": False, "error": "No habit ID from create test — skipping"}
    r = requests.get(f"{BASE_URL}/api/habits/{created_habit_id}", timeout=3)
    data = r.json()
    ok = r.status_code == 200 and data.get("id") == created_habit_id
    return {"ok": ok, "data": data, "error": f"HTTP {r.status_code}"}

def check_update_habit():
    if not created_habit_id:
        return {"ok": False, "error": "No habit ID — skipping"}
    r = requests.put(
        f"{BASE_URL}/api/habits/{created_habit_id}",
        json={"name": "Test Habit - UPDATED"},
        timeout=3,
    )
    data = r.json()
    ok = r.status_code == 200 and data.get("name") == "Test Habit - UPDATED"
    return {"ok": ok, "data": data, "error": f"HTTP {r.status_code}: {data}"}

def check_delete_habit():
    if not created_habit_id:
        return {"ok": False, "error": "No habit ID — skipping"}
    r = requests.delete(f"{BASE_URL}/api/habits/{created_habit_id}", timeout=3)
    ok = r.status_code == 204
    return {"ok": ok, "error": f"Expected 204, got {r.status_code}"}

def check_habit_404():
    r = requests.get(f"{BASE_URL}/api/habits/nonexistent-id-999", timeout=3)
    ok = r.status_code == 404
    return {"ok": ok, "error": f"Expected 404, got {r.status_code} — missing error handling"}

def check_habit_validation():
    # Send empty payload — should return 422
    r = requests.post(f"{BASE_URL}/api/habits", json={}, timeout=3)
    ok = r.status_code == 422
    return {"ok": ok, "error": f"Expected 422 validation error, got {r.status_code}"}


# ─── OTHER DOMAIN ENDPOINTS ───────────────────────────────────────────────────

def check_get_tasks():
    r = requests.get(f"{BASE_URL}/api/tasks", timeout=3)
    return {"ok": r.status_code == 200, "error": f"HTTP {r.status_code}"}

def check_get_goals():
    r = requests.get(f"{BASE_URL}/api/goals", timeout=3)
    return {"ok": r.status_code == 200, "error": f"HTTP {r.status_code}"}

def check_get_health_metrics():
    r = requests.get(f"{BASE_URL}/api/health", timeout=3)
    return {"ok": r.status_code == 200, "error": f"HTTP {r.status_code}"}


# ─── ROUTE PREFIX AUDIT ───────────────────────────────────────────────────────

def check_no_unscoped_routes():
    """Verify routes are under /api/ not root"""
    bad = []
    for path in ["/habits", "/tasks", "/goals"]:
        r = requests.get(f"{BASE_URL}{path}", timeout=3)
        if r.status_code == 200:
            bad.append(path)
    ok = len(bad) == 0
    return {
        "ok": ok,
        "error": f"Routes accessible without /api/ prefix: {bad} — prefix not set on router",
        "data": {"unscoped_routes": bad},
    }


# ─── RUN ALL TESTS ────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("  VERYFYN API TEST SUITE")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*60)

print("\n📡 SERVER")
server_result = test("Server is running on :8000", check_server_running)
if not server_result["ok"]:
    print(f"\n{FAIL} Cannot reach server. Aborting remaining tests.")
    print("  Start your server with:")
    print("  uvicorn backend.main:app --reload --port 8000\n")
    sys.exit(1)

test("GET /health returns healthy", check_health_endpoint)
test("GET /api/status exists (no conflict with health router)", check_api_status_endpoint)
test("GET /api/db/test — database connected", check_db_connection)
test("GET /docs — Swagger UI available", check_docs_available)

print("\n🌐 CORS")
test("OPTIONS /api/habits — CORS headers present for :5173", check_cors_headers)

print("\n🔍 ROUTE PREFIX AUDIT")
test("Routes not accessible without /api/ prefix", check_no_unscoped_routes)

print("\n✅ HABITS (full CRUD cycle)")
test("GET  /api/habits — list habits", check_get_habits)
test("POST /api/habits — create habit (status 201)", check_create_habit)
test("GET  /api/habits/{id} — get single habit", check_get_single_habit)
test("PUT  /api/habits/{id} — update habit", check_update_habit)
test("DEL  /api/habits/{id} — delete habit (status 204)", check_delete_habit)
test("GET  /api/habits/bad-id — returns 404", check_habit_404)
test("POST /api/habits {} — returns 422 validation error", check_habit_validation)

print("\n📋 OTHER DOMAINS")
test("GET /api/tasks", check_get_tasks)
test("GET /api/goals", check_get_goals)
test("GET /api/health", check_get_health_metrics)

# ─── SUMMARY ─────────────────────────────────────────────────────────────────

passed = sum(1 for _, ok in results if ok)
failed = sum(1 for _, ok in results if not ok)
total = len(results)

print("\n" + "="*60)
print(f"  RESULTS: {passed}/{total} passed  |  {failed} failed")
print("="*60)

if failed == 0:
    print("\n  🎉 All tests passed! Backend is ready for frontend.")
else:
    print(f"\n  Fix the {failed} failing test(s) before connecting the frontend.")
    print("\n  Failed tests:")
    for name, ok in results:
        if not ok:
            print(f"    ✗ {name}")

print()
