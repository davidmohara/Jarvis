#!/usr/bin/env python3
"""
Export the per-step audit trail for a set of eval run records as CSV and JSON.

This is the artifact Tim Rayburn's Stage 5 report asks for: for each real
workflow execution, every step's model name, input tokens, output tokens, and
cost in dollars, exportable as CSV or JSON.

Usage:
    python3 systems/eval-harness/export-step-audit.py --runs <ids-or-glob> --out <dir>

    --runs    Comma-separated list of run ids, record filenames, or glob
              patterns. Examples:
                --runs eval-20261008T183732-HSDQ6F
                --runs 'eval-20261008*.json'
                --runs eval-A,eval-B,eval-202609*.json
              Default: every eval-*.json in runs/.
    --out     Output directory (created if missing).
              Default: systems/eval-harness/audit-exports/
    --workflow  Optional: only include records whose `name` matches.

Writes <out>/step-audit.csv and <out>/step-audit.json.

Reads tolerate every historical step shape: `steps: []`, `steps: ["a","b"]`
(legacy bare strings), and `steps: [{...}]` (canonical dicts). A record whose
steps are bare strings still exports, with null audit fields, rather than
crashing the whole export.
"""

import argparse
import csv
import glob
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

IES_ROOT = Path(__file__).resolve().parents[2]
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
DEFAULT_OUT = IES_ROOT / "systems" / "eval-harness" / "audit-exports"

sys.path.insert(0, str(IES_ROOT / "systems" / "eval-harness"))
from step_audit import normalize_step, step_totals, workflow_owner_agent  # noqa: E402

CSV_COLUMNS = [
    "run_id", "run_name", "run_agent", "run_owning_agent", "run_status",
    "run_started", "run_completed",
    "step_index", "step_name", "step_id", "step_agent", "step_owning_agent", "model",
    "tokens_input", "tokens_output", "cost_usd", "token_source",
    "step_status", "step_started", "step_completed", "duration_seconds",
]


def resolve_run_paths(runs_arg: str | None) -> list[Path]:
    """Turn --runs (ids, filenames, globs) into a de-duplicated list of paths."""
    if not runs_arg:
        return sorted(EVAL_RUNS_DIR.glob("eval-*.json"))

    paths: list[Path] = []
    seen: set[Path] = set()
    for token in runs_arg.split(","):
        token = token.strip()
        if not token:
            continue
        candidates: list[Path] = []
        p = Path(token)
        if p.is_file():
            candidates = [p]
        else:
            # Bare id -> runs/<id>.json ; otherwise treat as a glob (absolute
            # or relative to runs/).
            by_id = EVAL_RUNS_DIR / f"{token}.json"
            if by_id.is_file():
                candidates = [by_id]
            else:
                pattern = token if any(ch in token for ch in "*?[") else f"*{token}*"
                candidates = [Path(m) for m in glob.glob(str(EVAL_RUNS_DIR / pattern))]
        for c in candidates:
            if c not in seen:
                seen.add(c)
                paths.append(c)
    return paths


def load_record(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except Exception as e:
        print(f"  skipping {path.name}: {e}", file=sys.stderr)
        return None


def record_has_audit_data(record: dict) -> bool:
    """True if at least one step carries model + tokens + cost."""
    for s in (record.get("steps") or []):
        s = normalize_step(s)
        if s.get("model") and s.get("tokens_input") is not None and s.get("cost_usd") is not None:
            return True
    return False


def build_export(records: list[tuple[Path, dict]]) -> tuple[list[dict], list[dict]]:
    """Return (csv_rows, json_runs)."""
    csv_rows: list[dict] = []
    json_runs: list[dict] = []

    for path, record in records:
        steps = record.get("steps") or []
        run_owner = workflow_owner_agent(record.get("name")) or record.get("agent")
        json_steps = []
        for idx, raw in enumerate(steps):
            s = normalize_step(raw)
            step_owner = s.get("owning_agent") or run_owner
            json_steps.append({
                "index": idx,
                "name": s.get("name"),
                "step_id": s.get("step_id", s.get("name")),
                "agent": s.get("agent"),
                "owning_agent": step_owner,
                "model": s.get("model"),
                "tokens_input": s.get("tokens_input"),
                "tokens_output": s.get("tokens_output"),
                "cost_usd": s.get("cost_usd"),
                "token_source": s.get("token_source"),
                "status": s.get("status"),
                "started": s.get("started"),
                "completed": s.get("completed"),
                "duration_seconds": s.get("duration_seconds"),
            })
            csv_rows.append({
                "run_id": record.get("id", path.stem),
                "run_name": record.get("name"),
                "run_agent": record.get("agent"),
                "run_owning_agent": run_owner,
                "run_status": record.get("status"),
                "run_started": record.get("started"),
                "run_completed": record.get("completed"),
                "step_index": idx,
                "step_name": s.get("name"),
                "step_id": s.get("step_id", s.get("name")),
                "step_agent": s.get("agent"),
                "step_owning_agent": step_owner,
                "model": s.get("model"),
                "tokens_input": s.get("tokens_input"),
                "tokens_output": s.get("tokens_output"),
                "cost_usd": s.get("cost_usd"),
                "token_source": s.get("token_source"),
                "step_status": s.get("status"),
                "step_started": s.get("started"),
                "step_completed": s.get("completed"),
                "duration_seconds": s.get("duration_seconds"),
            })

        totals = step_totals(record)
        json_runs.append({
            "run_id": record.get("id", path.stem),
            "run_name": record.get("name"),
            "run_agent": record.get("agent"),
            "run_owning_agent": run_owner,
            "run_type": record.get("type"),
            "run_status": record.get("status"),
            "run_started": record.get("started"),
            "run_completed": record.get("completed"),
            "source_file": path.name,
            "instrumented": record_has_audit_data(record),
            "step_count": len(json_steps),
            "totals": totals,
            "steps": json_steps,
        })

    return csv_rows, json_runs


def main():
    ap = argparse.ArgumentParser(description="Export per-step audit trail as CSV and JSON")
    ap.add_argument("--runs", default=None,
                    help="Comma-separated run ids, filenames, or globs. Default: all runs.")
    ap.add_argument("--out", default=str(DEFAULT_OUT),
                    help="Output directory (default: systems/eval-harness/audit-exports)")
    ap.add_argument("--workflow", default=None,
                    help="Only include records whose name matches this workflow")
    args = ap.parse_args()

    paths = resolve_run_paths(args.runs)
    if not paths:
        print(f"No run records matched --runs '{args.runs}'", file=sys.stderr)
        return 1

    records: list[tuple[Path, dict]] = []
    for p in paths:
        rec = load_record(p)
        if rec is None:
            continue
        if args.workflow and rec.get("name") != args.workflow:
            continue
        records.append((p, rec))

    if not records:
        print("No records to export after filtering", file=sys.stderr)
        return 1

    csv_rows, json_runs = build_export(records)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "step-audit.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(csv_rows)

    json_path = out_dir / "step-audit.json"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_runs": [r["source_file"] for r in json_runs],
        "run_count": len(json_runs),
        "step_count": len(csv_rows),
        "instrumented_run_count": sum(1 for r in json_runs if r["instrumented"]),
        "runs": json_runs,
    }
    json_path.write_text(json.dumps(payload, indent=2) + "\n")

    instrumented_steps = sum(
        1 for row in csv_rows
        if row["model"] and row["tokens_input"] is not None and row["cost_usd"] is not None
    )
    print(f"Exported {len(json_runs)} run(s), {len(csv_rows)} step(s) "
          f"({instrumented_steps} with full model/tokens/cost)")
    print(f"  CSV:  {csv_path}")
    print(f"  JSON: {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
