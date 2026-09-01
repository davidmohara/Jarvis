#!/usr/bin/env python3
"""
Check daily token usage and flag cost spikes.

Aggregates total_cost_usd across all eval records for a given date,
compares against a configurable threshold, and prints a flagged summary
if the threshold is exceeded.

Silent no-op if under threshold (per exit-behavior pattern).

Usage:
  python3 daily-cost-check.py /path/to/eval-harness/runs/ [YYYY-MM-DD]

If no date given, defaults to today's date.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def load_budget_threshold():
    """Load daily alert threshold from budget.json or default to $15."""
    budget_path = Path(__file__).parent / "budget.json"
    if budget_path.exists():
        try:
            with open(budget_path) as f:
                config = json.load(f)
                return config.get("daily_alert_usd", 15.0)
        except Exception:
            pass
    return 15.0


def check_daily_cost(eval_dir, date_str=None):
    """
    Aggregate daily costs and flag if over threshold.
    Returns (total_cost, flagged) tuple.
    """
    if not date_str:
        date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    eval_path = Path(eval_dir)
    if not eval_path.exists():
        return 0.0, False

    threshold = load_budget_threshold()
    runs = []
    total_cost = 0.0

    for f in sorted(eval_path.glob("eval-*.json")):
        try:
            with open(f) as file:
                data = json.load(file)

            started = data.get("started", "")
            if not started.startswith(date_str):
                continue

            cost = data.get("total_cost_usd", 0) or 0
            status = data.get("status", "unknown")
            name = data.get("name", "unknown")

            total_cost += cost
            runs.append({
                "id": data.get("id"),
                "name": name,
                "cost": cost,
                "status": status,
                "started": started,
            })
        except Exception:
            pass

    # Sort by cost descending
    runs.sort(key=lambda x: x["cost"], reverse=True)

    flagged = total_cost > threshold

    if flagged:
        print(f"\n{'='*70}")
        print(f"DAILY COST ALERT — {date_str}")
        print(f"{'='*70}")
        print(f"Total today: ${total_cost:.2f} (threshold: ${threshold:.2f})")
        print(f"Runs: {len(runs)}\n")

        print("Top 3 most expensive:")
        for i, run in enumerate(runs[:3], 1):
            status_label = f" [{run['status'].upper()}]" if run["status"] != "success" else ""
            waste = " — wasted spend" if run["status"] in ["aborted", "failure"] else ""
            print(f"  {i}. {run['name'][:45]:45s} ${run['cost']:7.2f}{status_label}{waste}")

        print(f"\n{'='*70}\n")

    return total_cost, flagged


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check daily token usage and flag cost spikes"
    )
    parser.add_argument("eval_dir", help="Path to eval-harness/runs directory")
    parser.add_argument(
        "date",
        nargs="?",
        default=None,
        help="Date to check (YYYY-MM-DD), defaults to today",
    )
    args = parser.parse_args()

    total, flagged = check_daily_cost(args.eval_dir, args.date)
    exit(1 if flagged else 0)
