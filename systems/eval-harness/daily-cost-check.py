#!/usr/bin/env python3
"""
Check daily token usage and flag cost spikes.

Aggregates total_cost_usd across all eval records for a given date,
compares against a configurable threshold, and prints a flagged summary
if the threshold is exceeded.

Silent no-op if under threshold (per exit-behavior pattern).

Usage:
  python3 daily-cost-check.py /path/to/eval-harness/runs/ [YYYY-MM-DD] [--verbose]

If no date given, defaults to today's date.
With --verbose, shows per-turn breakdown for top 3 expensive runs.
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


def extract_transcript_turns(transcript_path):
    """Read transcript JSONL and return list of assistant turns with token counts.

    For subagent transcripts, sidechains are normal (agent's own turns).
    Returns list of dicts: {model, input_tokens, output_tokens, cache_read, cache_creation_5m, cache_creation_1h}
    """
    turns = {}
    order = []
    try:
        with open(transcript_path, "r", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if obj.get("type") != "assistant":
                    continue
                msg = obj.get("message", {})
                mid = msg.get("id")
                if not mid or mid in turns:
                    continue
                usage = msg.get("usage", {}) or {}
                cache_creation = usage.get("cache_creation", {}) or {}
                entry = {
                    "model": msg.get("model"),
                    "input_tokens": usage.get("input_tokens", 0) or 0,
                    "output_tokens": usage.get("output_tokens", 0) or 0,
                    "cache_read": usage.get("cache_read_input_tokens", 0) or 0,
                    "cache_creation_5m": cache_creation.get("ephemeral_5m_input_tokens", 0) or 0,
                    "cache_creation_1h": cache_creation.get("ephemeral_1h_input_tokens", 0) or 0,
                }
                turns[mid] = entry
                order.append(mid)
    except Exception:
        return []
    return [turns[mid] for mid in order]


def analyze_run_tokens(run_data, eval_dir):
    """Analyze token usage for a single run. Returns breakdown dict or None."""
    transcript_path = run_data.get("agent_transcript_path")
    if not transcript_path or not Path(transcript_path).exists():
        return None

    turns = extract_transcript_turns(transcript_path)
    if not turns:
        return None

    total_input = sum(t["input_tokens"] + t["cache_read"] + t["cache_creation_5m"] + t["cache_creation_1h"] for t in turns)
    total_output = sum(t["output_tokens"] for t in turns)
    avg_input_per_turn = total_input / len(turns) if turns else 0
    avg_output_per_turn = total_output / len(turns) if turns else 0

    return {
        "turn_count": len(turns),
        "total_input": total_input,
        "total_output": total_output,
        "avg_input_per_turn": avg_input_per_turn,
        "avg_output_per_turn": avg_output_per_turn,
    }


def check_daily_cost(eval_dir, date_str=None, verbose=False):
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
                "agent_transcript_path": data.get("agent_transcript_path"),
                "full_record": data,
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

            if verbose:
                breakdown = analyze_run_tokens(run, eval_dir)
                if breakdown:
                    print(f"     ├─ {breakdown['turn_count']} turns, "
                          f"{breakdown['total_input']:,} input tokens, "
                          f"{breakdown['total_output']:,} output tokens")
                    print(f"     └─ avg {breakdown['avg_input_per_turn']:,.0f} input/turn, "
                          f"{breakdown['avg_output_per_turn']:,.0f} output/turn")

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
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show per-turn token breakdown for top 3 expensive runs"
    )
    args = parser.parse_args()

    total, flagged = check_daily_cost(args.eval_dir, args.date, verbose=args.verbose)
    exit(1 if flagged else 0)
