#!/usr/bin/env python3
"""Pull Anthropic-side rated cost and usage for the unified cost view.

Uses the Anthropic Admin API:
  - /v1/organizations/cost_report            (rated dollars, daily buckets)
  - /v1/organizations/usage_report/messages  (token counts, daily buckets)

Auth: set ANTHROPIC_ADMIN_KEY in the environment, or put it in
config/.env as ANTHROPIC_ADMIN_KEY=... (the file is gitignored elsewhere
in IES; this script reads but never writes it).

Admin keys are created in console.anthropic.com -> Settings -> Admin keys.
Regular API keys (sk-ant-api*) do NOT work for these endpoints.

Usage:
    python3 anthropic_usage.py --since 2026-10-01 --until 2026-10-21 [--json]
"""
import argparse
import json
import os
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

BASE = "https://api.anthropic.com"
ENV_FILE = Path(__file__).resolve().parents[2] / "config" / ".env"


def admin_key():
    k = os.environ.get("ANTHROPIC_ADMIN_KEY")
    if k:
        return k
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if line.startswith("ANTHROPIC_ADMIN_KEY="):
                return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit(
        "No ANTHROPIC_ADMIN_KEY found. Set it in the environment or config/.env. "
        "Create one in console.anthropic.com -> Settings -> Admin keys."
    )


def get(path, params, key):
    url = BASE + path + "?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers={
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
    })
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True)
    ap.add_argument("--until", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    key = admin_key()

    cost = get("/v1/organizations/cost_report", {
        "starting_at": f"{args.since}T00:00:00Z",
        "ending_at": f"{args.until}T00:00:00Z",
        "bucket_width": "1d",
    }, key)

    usage = get("/v1/organizations/usage_report/messages", {
        "starting_at": f"{args.since}T00:00:00Z",
        "ending_at": f"{args.until}T00:00:00Z",
        "bucket_width": "1d",
        "group_by[]": "model",
    }, key)

    if args.json:
        print(json.dumps({"cost_report": cost, "usage_report": usage}, indent=1))
        return

    print("== Anthropic cost report (daily, cents) ==")
    for bucket in cost.get("data", []):
        day = bucket.get("starting_at", "")[:10]
        total = sum(int(r.get("amount", "0")) for r in bucket.get("results", [])) / 100.0
        print(f"{day}  ${total:.2f}")

    print("\n== Anthropic usage report (daily x model, Mtok) ==")
    for bucket in usage.get("data", []):
        day = bucket.get("starting_at", "")[:10]
        by_model = defaultdict(lambda: [0, 0])
        for r in bucket.get("results", []):
            m = r.get("model", "?")
            by_model[m][0] += int(r.get("uncached_input_tokens", 0)) + int(r.get("cache_creation_input_tokens", 0))
            by_model[m][0] += int(r.get("cache_read_input_tokens", 0))
            by_model[m][1] += int(r.get("output_tokens", 0))
        parts = ", ".join(f"{m}: {v[0]/1e6:.1f}M in / {v[1]/1e6:.2f}M out" for m, v in sorted(by_model.items()))
        print(f"{day}  {parts}")


if __name__ == "__main__":
    main()
