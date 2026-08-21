#!/usr/bin/env python3
"""
Backfill cost_usd for ALL eval records system-wide.

Covers: daily-review, morning-briefing, general-purpose, system-eval, fork,
and all other workflow types.

Estimated token consumption by workflow type:
  - daily-review (scheduled): ~5K input, ~2K output
  - morning-briefing (scheduled): ~8K input, ~3K output
  - general-purpose: ~10K input, ~4K output
  - system-eval: ~3K input, ~1K output
  - fork: ~5K input, ~2K output
  - skill/plugin runs: ~4K input, ~1.5K output
  - default (unknown type): ~5K input, ~2K output
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

IES_ROOT = Path(__file__).resolve().parents[2]
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
PRICING_PATH = IES_ROOT / "systems" / "eval-harness" / "model-pricing.json"

sys.path.insert(0, str(IES_ROOT / "systems" / "eval-harness"))
try:
    from token_usage import usage_between
except ImportError:
    usage_between = None


def load_pricing() -> dict:
    """Load pricing table."""
    try:
        with open(PRICING_PATH, "r") as f:
            return json.load(f).get("models", {})
    except Exception as e:
        print(f"Failed to load pricing: {e}")
        return {}


# Workflow-specific token estimates
WORKFLOW_ESTIMATES = {
    "daily-review": {"input": 5000, "output": 2000},
    "morning-briefing": {"input": 8000, "output": 3000},
    "general-purpose": {"input": 10000, "output": 4000},
    "system-eval": {"input": 3000, "output": 1000},
    "fork": {"input": 5000, "output": 2000},
    "boot": {"input": 6000, "output": 2500},
    "plaud-ingest": {"input": 7000, "output": 3000},
    "watchtower-weekly": {"input": 12000, "output": 5000},
    "partner-meeting-prep": {"input": 8000, "output": 3000},
    "obsidian-source-note": {"input": 4000, "output": 1500},
    "remarkable-upload": {"input": 3000, "output": 1000},
    "error-improvement": {"input": 4000, "output": 1500},
    "claude-code-guide": {"input": 5000, "output": 2000},
    "content-approval": {"input": 6000, "output": 2500},
    "Explore": {"input": 4000, "output": 1500},
    "genius-spark-meeting-prep": {"input": 7000, "output": 3000},
}


def estimate_cost_for_workflow(workflow_name: str, model: str, pricing: dict) -> float:
    """Estimate cost based on workflow type."""
    if model not in pricing:
        model = "sonnet"

    rates = pricing.get(model, {"input_per_mtok": 3.00, "output_per_mtok": 15.00})

    # Get workflow-specific estimate, fall back to default
    estimate = WORKFLOW_ESTIMATES.get(workflow_name, WORKFLOW_ESTIMATES["fork"])
    input_tokens = estimate["input"]
    output_tokens = estimate["output"]

    input_cost = (input_tokens / 1_000_000) * rates.get("input_per_mtok", 3.00)
    output_cost = (output_tokens / 1_000_000) * rates.get("output_per_mtok", 15.00)

    return round(input_cost + output_cost, 6)


def backfill_record(record_path: Path, pricing: dict) -> bool:
    """Backfill cost_usd for a single eval record. Returns True if updated."""
    try:
        with open(record_path, "r") as f:
            record = json.load(f)

        # Skip if already has cost
        if record.get("total_cost_usd") is not None:
            return False

        model = record.get("model", "sonnet")
        workflow = record.get("name", "unknown")

        # Try to compute from transcript if available
        if record.get("agent_transcript_path"):
            transcript_path = record.get("agent_transcript_path")
            if Path(transcript_path).exists() and usage_between:
                try:
                    usage = usage_between(
                        transcript_path,
                        record.get("started"),
                        record.get("completed"),
                        exclude_sidechain=False,
                    )
                    if usage and usage.get("cost_usd"):
                        record["total_cost_usd"] = usage["cost_usd"]
                        record["total_tokens_input"] = usage.get("tokens_input")
                        record["total_tokens_output"] = usage.get("tokens_output")
                        record["model"] = usage.get("model", model)
                        with open(record_path, "w") as f:
                            json.dump(record, f, indent=2)
                        return True
                except Exception as e:
                    pass  # Fall through to estimation

        # Fallback: estimate based on workflow type
        estimated_cost = estimate_cost_for_workflow(workflow, model, pricing)
        record["total_cost_usd"] = estimated_cost
        record["cost_estimation_note"] = f"estimated based on {workflow} workflow type"

        with open(record_path, "w") as f:
            json.dump(record, f, indent=2)

        return True

    except Exception as e:
        print(f"  Error processing {record_path.name}: {e}")
        return False


def main():
    """Backfill all eval records."""
    if not EVAL_RUNS_DIR.exists():
        print(f"Eval runs directory not found: {EVAL_RUNS_DIR}")
        return

    pricing = load_pricing()
    if not pricing:
        print("Warning: Could not load pricing table. Using defaults.")
        pricing = {
            "sonnet": {"input_per_mtok": 3.00, "output_per_mtok": 15.00},
            "haiku": {"input_per_mtok": 1.00, "output_per_mtok": 5.00},
        }

    # Find all eval records
    all_evals = []
    for f in EVAL_RUNS_DIR.glob("*.json"):
        try:
            with open(f) as file:
                record = json.load(file)
            all_evals.append(f)
        except Exception:
            continue

    if not all_evals:
        print("No eval records found.")
        return

    print(f"Found {len(all_evals)} eval records across all workflows")
    print(f"Pricing table: {list(pricing.keys())}\n")

    # Group by workflow
    by_workflow = defaultdict(list)
    for record_path in all_evals:
        try:
            with open(record_path) as f:
                record = json.load(f)
            by_workflow[record.get("name", "unknown")].append(record_path)
        except:
            pass

    # Process by workflow
    updated = 0
    already_have_cost = 0
    total_cost = 0.0

    for workflow in sorted(by_workflow.keys()):
        records = by_workflow[workflow]
        workflow_updated = 0
        workflow_cost = 0.0

        for record_path in records:
            try:
                with open(record_path) as f:
                    record = json.load(f)

                if record.get("total_cost_usd") is not None:
                    already_have_cost += 1
                    workflow_cost += record.get("total_cost_usd", 0)
                    continue

                if backfill_record(record_path, pricing):
                    workflow_updated += 1
                    # Re-read to get updated cost
                    with open(record_path) as f:
                        record = json.load(f)
                    workflow_cost += record.get("total_cost_usd", 0)
                    updated += 1
            except Exception as e:
                print(f"  Error: {e}")

        if workflow_updated > 0 or workflow_cost > 0:
            print(f"{workflow:30s}: {workflow_updated:3d} updated, "
                  f"${workflow_cost:.2f} total cost")
        total_cost += workflow_cost

    print(f"\n✓ Backfill complete:")
    print(f"  Updated: {updated} records")
    print(f"  Already had costs: {already_have_cost} records")
    print(f"  Total eval cost: ${total_cost:.2f}")
    print(f"  Grand total: {len(all_evals)} records")


if __name__ == "__main__":
    main()
