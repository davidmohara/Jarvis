#!/usr/bin/env python3
"""
Quick discovery script for Knox — lists all Plaud recordings without downloading transcripts.
"""

import json
import os
from datetime import datetime
import sys

# Load token
token_path = os.path.expanduser("~/.config/plaud/token.json")
creds_path = os.path.expanduser("~/.config/plaud/credentials.json")

if not os.path.exists(token_path):
    print("ERROR: No cached token found at ~/.config/plaud/token.json")
    sys.exit(1)

with open(token_path) as f:
    token_data = json.load(f)
    token = token_data.get("access_token")

with open(creds_path) as f:
    creds = json.load(f)
    region = creds.get("region", "us")

api_base = "https://api.plaud.ai" if region == "us" else "https://api-euc1.plaud.ai"

# Make API calls
import requests

def list_recordings():
    """List all recordings via /file/simple/web with pagination."""
    all_recordings = []
    skip = 0
    limit = 50

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://web.plaud.ai",
        "Referer": "https://web.plaud.ai/",
        "app-platform": "web",
        "edit-from": "web",
    }

    while True:
        params = {
            "skip": skip,
            "limit": limit,
            "is_trash": 0,
            "sort_by": "start_time",
            "is_desc": "true",
        }

        resp = requests.get(
            f"{api_base}/file/simple/web",
            headers=headers,
            params=params,
            timeout=30
        )

        if resp.status_code != 200:
            print(f"ERROR: API returned {resp.status_code}")
            print(resp.text[:500])
            break

        data = resp.json()
        recordings = data.get("data_file_list", data.get("data", []))
        if isinstance(recordings, dict):
            recordings = recordings.get("items", recordings.get("list", []))

        if not recordings:
            break

        all_recordings.extend(recordings)

        if len(recordings) < limit:
            break

        skip += limit

    # Filter out trashed
    all_recordings = [r for r in all_recordings if not r.get("is_trash", False)]

    return all_recordings

# Run discovery
print("Discovering all Plaud recordings...")
recordings = list_recordings()

print(f"Total recordings: {len(recordings)}")
print()

# Print in YAML format suitable for state.yaml
for rec in recordings[:10]:  # Show first 10
    file_id = rec.get("id", rec.get("file_id", ""))
    name = rec.get("filename", rec.get("fullname", ""))
    start = rec.get("start_time", rec.get("create_time", 0))
    if isinstance(start, (int, float)) and start > 1e12:
        start = int(start / 1000)
    elif isinstance(start, (int, float)):
        start = int(start)

    dt = datetime.fromtimestamp(start) if start else datetime.now()
    date_str = dt.strftime("%Y-%m-%d")

    duration = rec.get("duration", 0)
    has_trans = rec.get("is_trans", 0)
    trans_status_code = rec.get("trans_status", 0)

    if has_trans:
        if trans_status_code == 1:
            status = "ready"
        else:
            status = "pending"
    else:
        status = "missing"

    print(f"  - file_id: {file_id}")
    print(f"    name: '{name}'")
    print(f"    date: '{date_str}'")
    print(f"    duration_seconds: {duration}")
    print(f"    has_transcript: {bool(has_trans)}")
    print(f"    transcript_status: {status}")

# Output summary
print()
print(f"Total recordings found: {len(recordings)}")
ready_count = sum(1 for r in recordings if r.get("is_trans") and r.get("trans_status") == 1)
pending_count = sum(1 for r in recordings if r.get("is_trans") and r.get("trans_status") != 1)
missing_count = sum(1 for r in recordings if not r.get("is_trans"))

print(f"Ready: {ready_count}")
print(f"Pending: {pending_count}")
print(f"Missing: {missing_count}")

# Save to JSON for later processing
with open("/tmp/plaud_discovery.json", "w") as f:
    json.dump(recordings, f, indent=2, default=str)
print(f"\nFull list saved to /tmp/plaud_discovery.json")
