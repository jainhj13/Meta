"""Quick Docker endpoint test script."""
import httpx
import sys

BASE = "http://localhost:8000"
results = []

# Test 1: Health
try:
    r = httpx.get(f"{BASE}/health", timeout=10)
    ok = r.status_code == 200 and r.json()["status"] == "healthy"
    print(f"[1/4] GET  /health  -> {r.status_code} {r.json()}")
    results.append(("health", ok))
except Exception as e:
    print(f"[1/4] GET  /health  -> FAIL: {e}")
    results.append(("health", False))

# Test 2: Reset
try:
    r = httpx.post(f"{BASE}/reset", json={"task_name": "email_triage", "seed": 0}, timeout=10)
    data = r.json()
    n_emails = len(data["visible_data"]["emails"])
    ok = r.status_code == 200 and n_emails == 5
    print(f"[2/4] POST /reset   -> {r.status_code} task={data['task_name']} emails={n_emails}")
    results.append(("reset", ok))
except Exception as e:
    print(f"[2/4] POST /reset   -> FAIL: {e}")
    results.append(("reset", False))

# Test 3: Step
try:
    r = httpx.post(f"{BASE}/step", json={
        "task_name": "email_triage",
        "action_type": "classify_email",
        "payload": {"email_id": "email_001", "category": "urgent", "priority": 0.92}
    }, timeout=10)
    data = r.json()
    ok = r.status_code == 200 and data["reward"] > 0
    print(f"[3/4] POST /step    -> {r.status_code} reward={data['reward']} done={data['done']}")
    results.append(("step", ok))
except Exception as e:
    print(f"[3/4] POST /step    -> FAIL: {e}")
    results.append(("step", False))

# Test 4: State
try:
    r = httpx.get(f"{BASE}/state", timeout=10)
    data = r.json()
    ok = r.status_code == 200 and data["step_count"] == 1
    print(f"[4/4] GET  /state   -> {r.status_code} steps={data['step_count']} task={data['task_name']}")
    results.append(("state", ok))
except Exception as e:
    print(f"[4/4] GET  /state   -> FAIL: {e}")
    results.append(("state", False))

# Summary
print()
passed = sum(1 for _, ok in results if ok)
total = len(results)
for name, ok in results:
    status = "PASS" if ok else "FAIL"
    print(f"  {status}: {name}")
print(f"\nResult: {passed}/{total} endpoints passed")
sys.exit(0 if passed == total else 1)
