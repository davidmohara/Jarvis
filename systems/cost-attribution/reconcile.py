#!/usr/bin/env python3
"""Reconcile local attribution estimates against Fireworks metered usage.

Pulls billingUsage from the Fireworks API (daily buckets grouped by model,
with cached/uncached prompt-token splits) using the API key already present in
~/.claude/settings.json, prices it at the configured serverless rates, and
prints a day x model table plus the implied cached-token price (solved against
the dashboard total you pass in with --actual).

Usage:
    python3 reconcile.py [--since 2026-10-01] [--until 2026-10-21] [--actual 606]
"""
import argparse
import json
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

SETTINGS = Path.home() / ".claude" / "settings.json"
BASE = "https://api.fireworks.ai/v1/accounts/improving"

# $ per Mtok (input, output), matching attribute.py
RATES = {
    "kimi-k3": (3.0, 15.0),
    "glm-5p3": (1.4, 4.4),
    "glm-5p3-flash": (0.15, 0.5),
    "deepseek-v4p1-flash": (0.3, 1.2),
    "deepseek-v4p1-flash-1017": (0.3, 1.2),
}


def api_key():
    headers = json.load(open(SETTINGS))["env"]["ANTHROPIC_CUSTOM_HEADERS"]
    for line in headers.splitlines():
        if line.startswith("X-Fireworks-Api-Key:"):
            return line.split(":", 1)[1].strip()
    raise SystemExit("No Fireworks API key found in settings.json")


def get(path, params, key):
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def short(model):
    return model.rsplit("/", 1)[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-10-01")
    ap.add_argument("--until", default="2026-10-21")
    ap.add_argument("--actual", type=float, default=0.0,
                    help="Actual Fireworks dashboard total for the window; solves implied cache price")
    args = ap.parse_args()

    resp = get("/billingUsage", {
        "startTime": f"{args.since}T00:00:00Z",
        "endTime": f"{args.until}T00:00:00Z",
        "groupBy": "model_name",
    }, api_key())

    # rows: (day, model) -> tokens
    uncached = defaultdict(float)
    cached = defaultdict(float)
    output = defaultdict(float)
    models = set()
    days = set()
    for row in resp.get("serverlessCosts", []):
        m = short(row["modelName"])
        d = row["startTime"][:10]
        models.add(m)
        days.add(d)
        uncached[(d, m)] += int(row.get("uncachedPromptTokens", 0))
        cached[(d, m)] += int(row.get("cachedPromptTokens", 0))
        output[(d, m)] += int(row.get("completionTokens", 0))

    def price(cached_frac):
        """Total $ with cached tokens priced at cached_frac of input rate."""
        tot = 0.0
        for (d, m), u in uncached.items():
            ri, ro = RATES.get(m, (0, 0))
            tot += (u * ri + cached[(d, m)] * ri * cached_frac + output[(d, m)] * ro) / 1e6
        return tot

    models = sorted(models)
    print(f"Fireworks metered usage {args.since} .. {args.until} (daily buckets)\n")
    header = f"{'day':<11}" + "".join(f"{m[:14]:>16}" for m in models)
    print(header)
    for d in sorted(days):
        cells = []
        for m in models:
            tot = uncached[(d, m)] + cached[(d, m)]
            cells.append(f"{tot/1e6:>15.1f}M" if tot else f"{'-':>16}")
        print(f"{d:<11}" + "".join(cells))

    print("\n== Model totals (Mtok) ==")
    print(f"{'model':<26} {'uncached in':>12} {'cached in':>12} {'output':>10}")
    for m in models:
        u = sum(uncached[(d, m)] for d in days)
        c = sum(cached[(d, m)] for d in days)
        o = sum(output[(d, m)] for d in days)
        print(f"{m:<26} {u/1e6:>12.1f} {c/1e6:>12.1f} {o/1e6:>10.2f}")

    p0, p1 = price(0.0), price(1.0)
    print(f"\nCost if cached tokens are FREE:     ${p0:,.2f}")
    print(f"Cost if cached tokens at full rate: ${p1:,.2f}")
    if args.actual:
        if p1 > p0:
            frac = (args.actual - p0) / (p1 - p0)
            print(f"Implied cached-token price vs input rate: {frac:.1%} (solved against ${args.actual})")
        else:
            print("Cannot solve: full-rate total <= free-total total.")


if __name__ == "__main__":
    main()
