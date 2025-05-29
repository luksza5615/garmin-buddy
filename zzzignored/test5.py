import json
from fuzzywuzzy import fuzz
from collections import defaultdict

SIMILARITY_THRESHOLD = 80  # tweak this as needed (0–100)


def flatten_json(y, prefix=''):
    """Flatten nested JSON into a dictionary with dot-separated keys."""
    out = {}
    if isinstance(y, dict):
        for k, v in y.items():
            out.update(flatten_json(v, f"{prefix}{k}." if prefix else k))
    elif isinstance(y, list):
        for i, v in enumerate(y):
            out.update(flatten_json(v, f"{prefix}[{i}]."))
    else:
        out[prefix.rstrip('.')] = y
    return out


def compare_keys(json1, json2):
    flat1 = flatten_json(json1)
    flat2 = flatten_json(json2)

    matches = defaultdict(list)

    for key1 in flat1:
        for key2 in flat2:
            similarity = fuzz.ratio(key1, key2)
            if similarity >= SIMILARITY_THRESHOLD:
                matches[key1].append((key2, similarity))

    return matches


# Example payloads (replace these with your actual JSONs)
json_payload1 = {
    "userId": 123,
    "user_name": "john",
    "details": {
        "email": "john@example.com",
        "phoneNumber": "123456789"
    }
}

json_payload2 = {
    "user_id": 123,
    "username": "johnny",
    "contact": {
        "email_address": "john@example.com",
        "phone": "123456789"
    }
}

similar_keys = compare_keys(json_payload1, json_payload2)

print("Similar Keys Found:\n")
for key1, matches in similar_keys.items():
    print(f"Key from JSON1: '{key1}'")
    for key2, score in sorted(matches, key=lambda x: -x[1]):
        print(f"  ↪ Similar to JSON2 key: '{key2}' (Score: {score})")
    print()
