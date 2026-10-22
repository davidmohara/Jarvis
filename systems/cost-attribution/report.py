#!/usr/bin/env python3
"""Unified cost view: Fireworks (Jarvis harness) + Anthropic (Cowork/Chat/Code-direct).

Combines:
  - Fireworks metered usage (reconcile.py data path, account-scoped)
  - Anthropic Admin cost_report (rated dollars, org-scoped)
  - Local transcript attribution (attribute.py) for session/skill detail

Outputs a single per-day table with both sources, plus a totals block.

METER SCOPE (why these numbers differ from attribute.py and from
reconcile-workflows.py — measured 2026-10-21, $41.13 Fireworks vs $13.72
attribute.py vs $8.80 local-truth):
  - The Fireworks column here is ACCOUNT-scoped /billingUsage: every request
    authed with the X-Fireworks-Api-Key in ~/.claude/settings.json, from any
    client (this Mac's Claude Code, Cowork's bundled CLI running scheduled
    tasks inside its VM, anything else on the key), whether or not a local
    transcript exists. Most of today's gap was kimi-k3: 52.4M tokens metered
    vs 5.1M in local transcripts — Cowork/scheduled runs whose transcripts
    never land under ~/.claude/projects.
  - attribute.py is LOCAL transcript-derived but under-scans: it globs only
    top-level <project>/*.jsonl (missing <session>/subagents/*.jsonl), never
    dedupes repeated message.id lines (~1.75x inflation on a busy session),
    and substring-matches models (glm-5p3-flash prices at glm-5p3 rates).
  - reconcile-workflows.py is the local-truth reconciliation: deduped,
    per-turn-priced, subagent transcripts included, workflow fully-loaded
    costs checked against the session metered total.

Usage:
    python3 report.py --since 2026-10-01 --until 2026-10-21
    ANTHROPIC_ADMIN_KEY=... python3 report.py ...   # or config/.env
"""
import argparse
import importlib.util
import json
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def fireworks_daily(since, until):
    rec = load("reconcile")
    resp = rec.get("/billingUsage", {
        "startTime": f"{since}T00:00:00Z",
        "endTime": f"{until}T00:00:00Z",
        "groupBy": "model_name",
    }, rec.api_key())
    daily = defaultdict(float)
    for row in resp.get("serverlessCosts", []):
        d = row["startTime"][:10]
        m = rec.short(row["modelName"])
        ri, ro = rec.RATES.get(m, (0, 0))
        u = int(row.get("uncachedPromptTokens", 0))
        c = int(row.get("cachedPromptTokens", 0))
        o = int(row.get("completionTokens", 0))
        daily[d] += (u * ri + c * ri * 0.115 + o * ro) / 1e6
    return daily


def anthropic_daily(since, until):
    au = load("anthropic_usage")
    key = au.admin_key()
    resp = au.get("/v1/organizations/cost_report", {
        "starting_at": f"{since}T00:00:00Z",
        "ending_at": f"{until}T00:00:00Z",
        "bucket_width": "1d",
    }, key)
    daily = {}
    for bucket in resp.get("data", []):
        day = bucket.get("starting_at", "")[:10]
        daily[day] = sum(int(r.get("amount", "0")) for r in bucket.get("results", [])) / 100.0
    return daily


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-10-01")
    ap.add_argument("--until", default="2026-10-21")
    args = ap.parse_args()

    fw = fireworks_daily(args.since, args.until)
    try:
        an = anthropic_daily(args.since, args.until)
        an_ok = True
    except SystemExit as e:
        print(f"[anthropic side skipped: {e}]\n", file=sys.stderr)
        an, an_ok = {}, False

    days = sorted(set(fw) | set(an))
    print(f"{'day':<12} {'fireworks':>10} {'anthropic':>10} {'total':>10}")
    tf = ta = 0.0
    for d in days:
        f, a = fw.get(d, 0.0), an.get(d, 0.0)
        tf += f
        ta += a
        print(f"{d:<12} ${f:>9.2f} {('$'+format(a,'.2f')) if an_ok else 'n/a':>10} ${f+a:>9.2f}")
    print(f"\n{'TOTAL':<12} ${tf:>9.2f} {('$'+format(ta,'.2f')) if an_ok else 'n/a':>10} ${tf+ta:>9.2f}")
    print("\nNote: Fireworks column is account-scoped metered usage priced at configured rates")
    print("(cached tokens at 11.5% of input rate, calibrated 2026-10-20). Anthropic column")
    print("is rated dollars from the org cost report. See attribute.py for session/skill detail")
    print("and reconcile-workflows.py for the workflow/day-level local reconciliation")


if __name__ == "__main__":
    main()
