import requests

BASE_URL = "http://localhost:8000"

def reset(task_name="email_triage", seed=0):
    return requests.post(f"{BASE_URL}/reset", json={
        "task_name": task_name,
        "seed": seed
    }).json()

def step(task_name, action_type, payload):
    return requests.post(f"{BASE_URL}/step", json={
        "task_name": task_name,
        "action_type": action_type,
        "payload": payload
    }).json()

def state():
    return requests.get(f"{BASE_URL}/state").json()