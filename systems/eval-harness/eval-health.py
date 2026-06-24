#!/usr/bin/env python3
"""
eval-health.py — Re-run assertions against each capability's reference solution
and report drift.

Purpose: If a reference stops passing its own assertions, the eval itself broke
(grader drift, assertion rot, or path changes) — not the agent. This script makes
that immediately visible.

For unattended capabilities: failures are gating (reference health = eval integrity).
For live-mode or high-stakes capabilities: failures are advisory.

Usage:
  python3 eval-health.py                   # check all capabilities with references
  python3 eval-health.py --capability morning-briefing
  python3 eval-health.py --pretty          # pretty-print JSON output
  python3 eval-health.py --exit-code       # exit 1 if any gated capability is unhealthy

Output: JSON report with per-capability health status and drift details.

Drift detection:
  A reference is "healthy" if it passes all its assertions.
  A reference is "drifted" if it was healthy at promotion time but now fails.
  A reference is "missing" if no reference.md exists yet.
  A capability is "gated" if it is in the unattended or high-stakes tier.
"""

import argparse
import glob
import json
import re
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path

IES_ROOT = Path(__file__).resolve().parents[2]
ASSERTIONS_DIR = IES_ROOT / "systems" / "eval-harness" / "assertions"
REFERENCES_DIR = IES_ROOT / "systems" / "eval-harness" / "references"

# Gated tiers — failures here are blocking, not advisory
GATED_TIERS = {"unattended", "high-stakes"}

# Capability → tier mapping (kept in sync with reliability.py)
CAPABILITY_TIERS = {
    "morning-briefing":      "unattended",
    "daily-review":          "unattended",
    "rock1-revenue-monthly": "unattended",
    "rock4-pipeline-weekly": "unattended",
    "follow-up-nudges":      "unattended",
    "inbox-processing":      "unattended",
    "client-meeting-prep":   "high-stakes",
    "pipeline-review":       "high-stakes",
    "presentation-builder":  "high-stakes",
}


def resolve_glob_path(pattern: str) -> list[Path]:
    """Resolve a glob pattern relative to IES_ROOT. Returns all matches."""
    matches = glob.glob(str(IES_ROOT / pattern))
    return [Path(m) for m in matches]


def resolve_single_path(pattern: str) -> Path | None:
    """Return most recently modified match for a glob, or None."""
    matches = sorted(
        resolve_glob_path(pattern),
        key=lambda p: p.stat().st_mtime if p.exists() else 0,
        reverse=True,
    )
    return matches[0] if matches else None


def run_assertion(assertion: dict, reference_path: Path) -> dict:
    """
    Run a single assertion against a reference file (or the reference's path context).

    For file-based assertions (file_exists, file_min_bytes, file_contains,
    yaml_field_equals), we redirect the check to the reference file itself
    when the assertion's path matches the capability's typical output path.

    Returns: {"assertion_id": str, "passed": bool, "reason": str}
    """
    check = assertion.get("check", "")
    pattern = assertion.get("path", "")
    assertion_id = assertion.get("id", "unknown")
    description = assertion.get("description", "")

    def fail(reason):
        return {"assertion_id": assertion_id, "passed": False, "reason": reason, "description": description}

    def ok(reason=""):
        return {"assertion_id": assertion_id, "passed": True, "reason": reason, "description": description}

    if check == "file_exists":
        # Check if the reference file exists (it should, since we just loaded it)
        if reference_path.exists():
            return ok(f"reference file exists: {reference_path.name}")
        return fail(f"reference file missing: {reference_path}")

    elif check == "file_min_bytes":
        min_bytes = assertion.get("min_bytes", 0)
        if not reference_path.exists():
            return fail(f"reference file missing")
        size = reference_path.stat().st_size
        if size >= min_bytes:
            return ok(f"reference is {size} bytes >= {min_bytes}")
        return fail(f"reference is {size} bytes < required {min_bytes}")

    elif check == "file_contains":
        regex_pattern = assertion.get("pattern", "")
        if not reference_path.exists():
            return fail("reference file missing")
        content = reference_path.read_text(errors="replace")
        try:
            if re.search(regex_pattern, content, re.IGNORECASE):
                return ok(f"pattern '{regex_pattern}' found in reference")
            return fail(f"pattern '{regex_pattern}' NOT found in reference")
        except re.error as e:
            return fail(f"invalid regex pattern: {e}")

    elif check == "yaml_field_equals":
        # For state.yaml assertions, we can't really check these against the
        # markdown reference file. Mark as advisory/skipped with a note.
        return {
            "assertion_id": assertion_id,
            "passed": True,
            "reason": "yaml_field_equals: skipped in eval-health (checks state.yaml, not output file)",
            "description": description,
            "skipped": True,
        }

    else:
        return {
            "assertion_id": assertion_id,
            "passed": True,
            "reason": f"check type '{check}': not evaluated in eval-health (advisory pass)",
            "description": description,
            "skipped": True,
        }


def check_capability(capability: str) -> dict:
    """Check a single capability's reference health. Returns a health record."""
    cap_dir = REFERENCES_DIR / capability
    ref_md = cap_dir / "reference.md"
    ref_meta_path = cap_dir / "reference.meta.json"
    tier = CAPABILITY_TIERS.get(capability, "standard")
    gated = tier in GATED_TIERS

    base = {
        "capability": capability,
        "tier": tier,
        "gated": gated,
        "checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    if not ref_md.exists():
        return {**base, "status": "missing", "reason": "no reference.md — promote a run first"}

    # Load meta
    meta = {}
    if ref_meta_path.exists():
        try:
            meta = json.loads(ref_meta_path.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    # Load assertions for this capability
    assertions_path = ASSERTIONS_DIR / f"{capability}.json"
    if not assertions_path.exists():
        return {
            **base,
            "status": "no_assertions",
            "reason": f"no assertion file at assertions/{capability}.json",
            "reference_promoted_on": meta.get("promoted_on"),
        }

    try:
        assertion_data = json.loads(assertions_path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        return {**base, "status": "error", "reason": f"could not load assertions: {e}"}

    assertions = assertion_data.get("assertions", [])
    if not assertions:
        return {
            **base,
            "status": "no_assertions",
            "reason": "assertions file exists but contains no assertions",
            "reference_promoted_on": meta.get("promoted_on"),
        }

    # Run assertions against the reference file
    results = [run_assertion(a, ref_md) for a in assertions]
    real_results = [r for r in results if not r.get("skipped")]
    skipped = [r for r in results if r.get("skipped")]

    passed = sum(1 for r in real_results if r["passed"])
    total = len(real_results)
    all_passed = (passed == total)

    assertions_at_promotion = meta.get("assertions_passed_at_promotion", "unknown")

    status = "healthy" if all_passed else "drifted"
    return {
        **base,
        "status": status,
        "assertions_now": f"{passed}/{total}",
        "assertions_at_promotion": assertions_at_promotion,
        "skipped_checks": len(skipped),
        "reference_promoted_on": meta.get("promoted_on"),
        "reference_source_eval": meta.get("source_eval_id"),
        "assertion_results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Check eval reference health for all gated capabilities")
    parser.add_argument("--capability", help="Check only this capability")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    parser.add_argument("--exit-code", action="store_true",
                        help="Exit 1 if any gated capability is unhealthy or drifted")
    args = parser.parse_args()
    indent = 2 if args.pretty else None

    if args.capability:
        capabilities = [args.capability]
    else:
        # Discover from references/ directories + known tiers
        known = set(CAPABILITY_TIERS.keys())
        existing = {d.name for d in REFERENCES_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")}
        capabilities = sorted(known | existing)

    results = [check_capability(cap) for cap in capabilities]

    gated_failures = [r for r in results if r.get("gated") and r["status"] in ("drifted", "missing", "error")]
    advisory_failures = [r for r in results if not r.get("gated") and r["status"] in ("drifted", "error")]

    summary = {
        "checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "total": len(results),
        "healthy": sum(1 for r in results if r["status"] == "healthy"),
        "drifted": sum(1 for r in results if r["status"] == "drifted"),
        "missing": sum(1 for r in results if r["status"] == "missing"),
        "no_assertions": sum(1 for r in results if r["status"] == "no_assertions"),
        "gated_failures": len(gated_failures),
        "advisory_failures": len(advisory_failures),
        "overall": "healthy" if not gated_failures else "DEGRADED",
    }

    output = {"summary": summary, "capabilities": results}

    if gated_failures:
        output["gated_failures"] = [r["capability"] for r in gated_failures]
        output["action_required"] = (
            "One or more gated capabilities have drifted references. "
            "The eval assertions are no longer correctly evaluating the reference. "
            "Review and update the assertion files or re-promote the reference."
        )

    print(json.dumps(output, indent=indent))

    if args.exit_code and gated_failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
