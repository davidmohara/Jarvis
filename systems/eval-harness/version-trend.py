#!/usr/bin/env python3
"""
version-trend.py — Show whether a workflow's runs improved across prompt
revisions.

Stage 4's audit-trail requirement isn't satisfied by a single snapshot of
tokens/cost/grade — it has to demonstrate that a change to the workflow
prompt measurably improved something (the same question Stage 3 asks of a
single prompt: "when you change it, how do you know you made it better?").

This groups eval records for one workflow by version_hash (recorded per run
at execution time), in chronological order, and reports per-version:
  - run count
  - average total tokens per run (sum of tokens_input+tokens_output across
    all steps that have them)
  - average composite score (via score_eval.py, when computable)
  - pass rate (status == "success")
Then prints a delta between the two most recent versions.

Usage:
  python3 version-trend.py <workflow-name>
  python3 version-trend.py <workflow-name> --json
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
IES_ROOT = SCRIPT_DIR.parent.parent
EVAL_RUNS_DIR = SCRIPT_DIR / "runs"
SCORE_SCRIPT = SCRIPT_DIR / "scoring" / "score_eval.py"


def load_records(workflow_name: str) -> list[dict]:
    records = []
    for f in EVAL_RUNS_DIR.glob("eval-*.json"):
        try:
            with open(f, "r") as file:
                data = json.load(file)
        except Exception:
            continue
        if data.get("name") == workflow_name:
            data["_file"] = f.name
            records.append(data)
    records.sort(key=lambda r: r.get("started") or "")
    return records


def total_tokens(record: dict) -> int | None:
    """Sum tokens_input+tokens_output across steps that report them, plus
    the whole-run total_tokens_* fields written for subagent-executed runs."""
    total = 0
    found_any = False
    for step in record.get("steps", []):
        if not isinstance(step, dict):
            continue  # older/legacy records store steps as bare name strings
        ti = step.get("tokens_input")
        to = step.get("tokens_output")
        if ti is not None or to is not None:
            found_any = True
            total += (ti or 0) + (to or 0)
    if record.get("total_tokens_input") is not None or record.get("total_tokens_output") is not None:
        found_any = True
        total += (record.get("total_tokens_input") or 0) + (record.get("total_tokens_output") or 0)
    return total if found_any else None


def composite_score(eval_id: str) -> float | None:
    if not SCORE_SCRIPT.exists():
        return None
    try:
        result = subprocess.run(
            [sys.executable, str(SCORE_SCRIPT), "--record", eval_id],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        return data.get("score")
    except Exception:
        return None


def group_by_version(records: list[dict]) -> list[dict]:
    """Bucket records by version_hash, preserving first-seen chronological order."""
    buckets: dict[str, dict] = {}
    order: list[str] = []
    for r in records:
        vh = r.get("version_hash") or "unknown"
        if vh not in buckets:
            buckets[vh] = {"version_hash": vh, "records": [], "first_seen": r.get("started")}
            order.append(vh)
        buckets[vh]["records"].append(r)
    return [buckets[vh] for vh in order]


def summarize_bucket(bucket: dict) -> dict:
    records = bucket["records"]
    run_count = len(records)
    token_values = [t for t in (total_tokens(r) for r in records) if t is not None]
    avg_tokens = round(sum(token_values) / len(token_values), 0) if token_values else None

    scores = [s for s in (composite_score(r["id"]) for r in records) if s is not None]
    avg_score = round(sum(scores) / len(scores), 3) if scores else None

    successes = sum(1 for r in records if r.get("status") == "success")
    pass_rate = round(successes / run_count, 3) if run_count else None

    return {
        "version_hash": bucket["version_hash"],
        "first_seen": bucket["first_seen"],
        "run_count": run_count,
        "runs_with_token_data": len(token_values),
        "avg_tokens_per_run": avg_tokens,
        "runs_scored": len(scores),
        "avg_composite_score": avg_score,
        "pass_rate": pass_rate,
    }


def print_report(workflow_name: str, summaries: list[dict]):
    if not summaries:
        print(f"No eval records found for workflow '{workflow_name}'.")
        return

    print(f"Version trend for '{workflow_name}' — {len(summaries)} version(s) observed\n")
    header = f"{'version_hash':<18} {'first_seen':<22} {'runs':>5} {'avg_tokens':>12} {'avg_score':>10} {'pass_rate':>10}"
    print(header)
    print("-" * len(header))
    for s in summaries:
        vh_short = (s["version_hash"] or "unknown")[:16]
        first_seen = (s["first_seen"] or "?")[:19]
        avg_tokens = f"{s['avg_tokens_per_run']:,.0f}" if s["avg_tokens_per_run"] is not None else "n/a"
        avg_score = f"{s['avg_composite_score']:.3f}" if s["avg_composite_score"] is not None else "n/a"
        pass_rate = f"{s['pass_rate']:.0%}" if s["pass_rate"] is not None else "n/a"
        print(f"{vh_short:<18} {first_seen:<22} {s['run_count']:>5} {avg_tokens:>12} {avg_score:>10} {pass_rate:>10}")

    if len(summaries) < 2:
        print("\nOnly one version observed — no delta to report yet. A trend requires at "
              "least two distinct version_hash values with token data attached, i.e. this "
              "workflow needs to run again after its next prompt revision before this "
              "mechanism has anything to show.")
        return

    prev, curr = summaries[-2], summaries[-1]
    print(f"\nMost recent change ({prev['version_hash'][:12]} -> {curr['version_hash'][:12]}):")

    if prev["avg_tokens_per_run"] is not None and curr["avg_tokens_per_run"] is not None:
        delta = curr["avg_tokens_per_run"] - prev["avg_tokens_per_run"]
        pct = (delta / prev["avg_tokens_per_run"] * 100) if prev["avg_tokens_per_run"] else 0
        direction = "fewer" if delta < 0 else "more"
        print(f"  Tokens/run: {abs(delta):,.0f} {direction} ({pct:+.1f}%)")
    else:
        print("  Tokens/run: not comparable — one or both versions lack token data")

    if prev["avg_composite_score"] is not None and curr["avg_composite_score"] is not None:
        delta = curr["avg_composite_score"] - prev["avg_composite_score"]
        direction = "improved" if delta > 0 else ("regressed" if delta < 0 else "unchanged")
        print(f"  Composite score: {direction} ({delta:+.3f})")
    else:
        print("  Composite score: not comparable — one or both versions lack scored records")

    if prev["pass_rate"] is not None and curr["pass_rate"] is not None:
        delta = curr["pass_rate"] - prev["pass_rate"]
        direction = "improved" if delta > 0 else ("regressed" if delta < 0 else "unchanged")
        print(f"  Pass rate: {direction} ({delta:+.1%})")


def main():
    if len(sys.argv) < 2:
        print("Usage: version-trend.py <workflow-name> [--json]")
        sys.exit(1)

    workflow_name = sys.argv[1]
    as_json = "--json" in sys.argv[2:]

    records = load_records(workflow_name)
    buckets = group_by_version(records)
    summaries = [summarize_bucket(b) for b in buckets]

    if as_json:
        print(json.dumps(summaries, indent=2))
    else:
        print_report(workflow_name, summaries)


if __name__ == "__main__":
    main()
