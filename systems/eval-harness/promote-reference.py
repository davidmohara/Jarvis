#!/usr/bin/env python3
"""
promote-reference.py — Promote a run's output to the canonical reference solution
for a capability.

A reference solution is a pinned copy of a known-good accepted output. It proves
the task is solvable and that the graders are configured correctly. When a future
run fails, the reference disambiguates: if the reference still passes assertions
but the new run does not, the agent regressed. If the reference also fails, the
eval drifted.

Usage:
  # Automatic promotion (called by the exit-sweep when a run is rated positive):
  python3 promote-reference.py --eval-id eval-20260623T021234-DH9VSD

  # Manual override — pin a specific eval run regardless of feedback rating:
  python3 promote-reference.py --eval-id eval-20260623T021234-DH9VSD --force

  # Promote with an explicit source file (if auto-discovery doesn't find it):
  python3 promote-reference.py --eval-id eval-20260623T021234-DH9VSD \\
      --source-file memory/working/morning-briefing-2026-06-23.md

Promotion rules:
  1. Eval record must have controller_feedback.rating == "positive" (or --force bypasses).
  2. All assertions must have passed at the time of the run (assertions_passed ==
     assertions_checked > 0). A positive rating on a run with failing assertions is
     logged but NOT promoted; it is printed as a warning for controller review.
  3. If a prior reference exists, it is archived to references/<cap>/history/ before
     the new one is written. Promotion is idempotent — re-promoting the same eval-id
     does not create a duplicate history entry.

Output files:
  systems/eval-harness/references/<capability>/reference.md
  systems/eval-harness/references/<capability>/reference.meta.json
  systems/eval-harness/references/<capability>/history/reference-<date>.md  (if prior existed)
"""

import argparse
import glob
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

IES_ROOT = Path(__file__).resolve().parents[2]
EVAL_RUNS_DIR = IES_ROOT / "systems" / "eval-harness" / "runs"
REFERENCES_DIR = IES_ROOT / "systems" / "eval-harness" / "references"

# Capabilities whose primary output is a single markdown file in memory/working/
# Key: capability name, Value: glob pattern relative to IES_ROOT
OUTPUT_PATTERNS = {
    "morning-briefing":      "memory/working/morning-briefing-*.md",
    "daily-review":          "memory/working/daily-review-*.md",
    "rock1-revenue-monthly": "memory/working/rock1-revenue-*.md",
    "rock4-pipeline-weekly": "memory/working/rock4-pipeline-*.md",
    "follow-up-nudges":      "memory/working/follow-up-nudges-*.md",
    "inbox-processing":      "memory/working/inbox-processing-*.md",
    "client-meeting-prep":   "memory/working/client-meeting-prep-*.md",
    "pipeline-review":       "memory/working/pipeline-review-*.md",
    "presentation-builder":  "memory/working/presentation-builder-*.md",
}


def load_record(eval_id: str) -> dict:
    path = EVAL_RUNS_DIR / f"{eval_id}.json"
    if not path.exists():
        # Also search structured evals dirs
        matches = list((IES_ROOT / "systems" / "evals").rglob(f"{eval_id}.json"))
        if not matches:
            print(f"ERROR: eval record not found: {eval_id}", file=sys.stderr)
            sys.exit(1)
        path = matches[0]
    return json.loads(path.read_text())


def find_source_file(record: dict) -> Path | None:
    """Auto-discover the primary output file for this capability."""
    capability = record.get("name", "")
    pattern = OUTPUT_PATTERNS.get(capability)
    if not pattern:
        return None

    # Find the most recently modified match
    matches = sorted(
        glob.glob(str(IES_ROOT / pattern)),
        key=lambda p: Path(p).stat().st_mtime,
        reverse=True,
    )
    return Path(matches[0]) if matches else None


def assertions_all_passed(record: dict) -> tuple[bool, str]:
    """Return (ok, reason) — ok is True only when all assertions passed."""
    structural = record.get("assessment", {}).get("structural", {})
    checked = structural.get("assertions_checked", 0)
    passed = structural.get("assertions_passed", 0)
    if checked == 0:
        return False, "assertions_checked=0 — no assertions were evaluated"
    if passed < checked:
        return False, f"assertions_passed={passed} < assertions_checked={checked}"
    return True, f"{passed}/{checked}"


def archive_existing(cap_dir: Path, promoted_on_str: str):
    """Archive current reference.md and reference.meta.json to history/ if they exist."""
    ref_md = cap_dir / "reference.md"
    ref_meta = cap_dir / "reference.meta.json"
    history_dir = cap_dir / "history"
    history_dir.mkdir(parents=True, exist_ok=True)

    # Use a date prefix from the existing meta if available, else use current date
    archive_date = promoted_on_str[:10]  # YYYY-MM-DD
    if ref_meta.exists():
        try:
            meta = json.loads(ref_meta.read_text())
            archive_date = meta.get("promoted_on", promoted_on_str)[:10]
        except (json.JSONDecodeError, OSError):
            pass

    if ref_md.exists():
        dest = history_dir / f"reference-{archive_date}.md"
        if not dest.exists():
            shutil.copy2(ref_md, dest)
    if ref_meta.exists():
        dest = history_dir / f"reference-{archive_date}.meta.json"
        if not dest.exists():
            shutil.copy2(ref_meta, dest)


def promote(eval_id: str, source_file: Path, record: dict, force: bool, assertions_summary: str):
    capability = record.get("name", "unknown")
    cap_dir = REFERENCES_DIR / capability
    cap_dir.mkdir(parents=True, exist_ok=True)

    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Idempotency check — don't re-promote the same eval-id
    ref_meta_path = cap_dir / "reference.meta.json"
    if ref_meta_path.exists():
        try:
            existing_meta = json.loads(ref_meta_path.read_text())
            if existing_meta.get("source_eval_id") == eval_id and not force:
                print(f"SKIP: {capability} reference already points to {eval_id} (idempotent). Use --force to re-promote.")
                return
        except (json.JSONDecodeError, OSError):
            pass

    # Archive prior reference before overwriting
    archive_existing(cap_dir, now_iso)

    # Write new reference content
    ref_md_path = cap_dir / "reference.md"
    shutil.copy2(source_file, ref_md_path)

    # Build meta
    try:
        source_rel = str(source_file.relative_to(IES_ROOT))
    except ValueError:
        source_rel = str(source_file)  # outside IES_ROOT (e.g. /tmp during tests)
    promoted_by = "controller_feedback:positive" if not force else "manual_override"
    meta = {
        "capability": capability,
        "source_eval_id": eval_id,
        "source_path": source_rel,
        "promoted_on": now_iso,
        "promoted_by": promoted_by,
        "workflow_version_hash": record.get("version_hash"),
        "assertions_passed_at_promotion": assertions_summary,
        "assertions_total_at_promotion": record.get("assessment", {}).get("structural", {}).get("assertions_checked", 0),
        "notes": None,
    }
    ref_meta_path.write_text(json.dumps(meta, indent=2) + "\n")

    print(f"PROMOTED: {capability} reference → {ref_md_path.relative_to(IES_ROOT)}")
    print(f"  source:   {source_rel}")
    print(f"  eval:     {eval_id}")
    print(f"  by:       {promoted_by}")
    print(f"  asserts:  {assertions_summary}")


def main():
    parser = argparse.ArgumentParser(description="Promote an eval run to reference solution")
    parser.add_argument("--eval-id", required=True, help="Eval record ID to promote")
    parser.add_argument("--source-file", help="Explicit path to the output file to pin (overrides auto-discovery)")
    parser.add_argument("--force", action="store_true",
                        help="Bypass feedback-rating and assertion checks (manual override)")
    args = parser.parse_args()

    record = load_record(args.eval_id)
    capability = record.get("name", "unknown")

    # Check 1: feedback rating (skip if --force)
    if not args.force:
        rating = record.get("assessment", {}).get("controller_feedback", {}).get("rating")
        if rating != "positive":
            print(
                f"SKIP: {capability} ({args.eval_id}) — feedback rating is '{rating}', "
                f"not 'positive'. Use --force to override.",
                file=sys.stderr,
            )
            sys.exit(0)

    # Check 2: assertions all passed (skip if --force)
    assertions_ok, assertions_summary = assertions_all_passed(record)
    if not assertions_ok and not args.force:
        print(
            f"WARNING: {capability} ({args.eval_id}) — rated positive but assertions did not all pass.\n"
            f"  Reason: {assertions_summary}\n"
            f"  NOT promoting. Review the run before pinning. Use --force to override.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Resolve source file
    if args.source_file:
        source = Path(args.source_file)
        if not source.is_absolute():
            source = IES_ROOT / source
        if not source.exists():
            print(f"ERROR: source file not found: {source}", file=sys.stderr)
            sys.exit(1)
    else:
        source = find_source_file(record)
        if source is None:
            print(
                f"ERROR: could not auto-discover output file for '{capability}'.\n"
                f"  Add an OUTPUT_PATTERNS entry or pass --source-file explicitly.",
                file=sys.stderr,
            )
            sys.exit(1)

    promote(args.eval_id, source, record, args.force, assertions_summary)


if __name__ == "__main__":
    main()
