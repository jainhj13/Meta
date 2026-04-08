import json
import sys

try:
    with open('validate_result.json', encoding='utf-8-sig') as f:
        d = json.load(f)
    print("FAILED TESTS:")
    for t in d['tests']:
        if not t['passed']:
            print(f"- {t['id']}: {t['description']}")
            print(f"  Expected: {t.get('expected')}")
            print(f"  Actual: {t.get('actual')}")
except Exception as e:
    print("Error:", e)
