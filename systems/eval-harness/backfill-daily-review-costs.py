#!/usr/bin/env python3
"""
Backfill cost_usd for daily-review eval records that are missing cost tracking.

For eval records without agent_transcript_path (headless scheduled runs):
- Estimate based on typical daily-review token consumption
- Use documented pricing from model-pricing.json
- Log which records were updated

For records with agent_transcript_path:
- Use token_usage.usage_between() to extract real costs
"""

import json
import sys
from pathlib import Path
from datetime import datetime

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


def estimate_cost_for_headless_run(model: str, pricing: dict) -> float:
    """Estimate cost for a headless daily-review run.

    Typical daily-review headless run (auto mode, no OmniFocus):
    - Reads delegation tracker, quarterly objectives (small files)
    - Reads 72-hour calendar (medium)
    - Synthesizes narrative (low computation)
    - Estimate: ~5,000 input tokens, ~2,000 output tokens (Sonnet)
    """
    if model not in pricing:
        model = "sonnet"

    rates = pricing.get(model, {"input_per_mtok": 3.00, "output_per_mtok": 15.00})

    # Headless run estimates (conservative)
    input_tokens = 5000
    output_tokens = 2000

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
                    print(f"  Warning: Failed to extract from transcript: {e}")

        # Fallback: estimate based on model and typical daily-review consumption
        estimated_cost = estimate_cost_for_headless_run(model, pricing)
        record["total_cost_usd"] = estimated_cost
        record["cost_estimation_note"] = "estimated — no transcript available"

        with open(record_path, "w") as f:
            json.dump(record, f, indent=2)

        return True

    except Exception as e:
        print(f"  Error processing {record_path.name}: {e}")
        return False


def main():
    """Backfill all daily-review eval records."""
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

    # Find all daily-review eval records
    daily_review_evals = []
    for f in EVAL_RUNS_DIR.glob("*.json"):
        try:
            with open(f, "r") as file:
                record = json.load(file)
            if record.get("name") == "daily-review":
                daily_review_evals.append(f)
        except Exception:
            continue

    if not daily_review_evals:
        print("No daily-review eval records found.")
        return

    print(f"Found {len(daily_review_evals)} daily-review eval records")
    print(f"Pricing table: {list(pricing.keys())}\n")

    updated = 0
    already_have_cost = 0

    for record_path in sorted(daily_review_evals):
        try:
            with open(record_path, "r") as f:
                record = json.load(f)

            if record.get("total_cost_usd") is not None:
                already_have_cost += 1
                continue

            print(f"Updating {record_path.name}...", end=" ")
            if backfill_record(record_path, pricing):
                print("✓")
                updated += 1
            else:
                print("(already has cost)")
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\n✓ Backfill complete:")
    print(f"  Updated: {updated} records")
    print(f"  Already had costs: {already_have_cost} records")
    print(f"  Total: {len(daily_review_evals)} records")


if __name__ == "__main__":
    main()
