#!/usr/bin/env python3
"""Ground-truth verifier for rock4-pipeline-weekly/step-03-save.

This workflow is a single workflow.md file with no steps/ directory. The
literal current-step value it writes is "step-03-save" — taken directly
from a real completed state.yaml, not inferred (workflow.md's final example
block drifts and shows "step-03" instead, but the actual write instruction
in step 3 and the live state.yaml both use "step-03-save").

The Obsidian vault is readable directly from the filesystem (iCloud-synced
folder). When reachable, this verifier parses Mind/One Texas/Rock 4 -
Pipeline Snapshots.md directly and confirms a dated "Week of" section for
the run's expected week actually exists with real gap figures — closing
the gap where state.yaml's last-completed/last-written-obsidian dates could
claim a write happened without the Obsidian MCP tool ever being called. If
the vault path is ever unreachable, this degrades to the original
state.yaml-only proxy logic (last-completed vs last-written-obsidian).
"""

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "systems" / "eval-harness" / "vendor"))
try:
    import yaml
except Exception:
    yaml = None

MIN_SECTION_CONTENT_LENGTH = 20
SKIP_MARKERS = ("already", "skip", "cache hit", "no obsidian write")

VAULT_FILE = Path("/Users/davidohara/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian/Mind/One Texas/Rock 4 - Pipeline Snapshots.md")

HEADER_RE = re.compile(r"^##\s+Week of (\d{4}-\d{2}-\d{2})\s*—\s*Pipeline Snapshot(?:\s*\(.*\))?\s*$", re.MULTILINE)
PULLED_RE = re.compile(r"\*Pulled:\s*(\d{4}-\d{2}-\d{2})")
AMOUNT_RE = re.compile(r"\$[\d,.]+\s*[MK]?")
PLACEHOLDER_RE = re.compile(r"\b(n/a|tbd|null|none|pending)\b", re.IGNORECASE)

WEEKLY_WINDOW_DAYS = 7
STALE_THRESHOLD_DAYS = 14


def parse_vault_entries(vault_text):
    headers = list(HEADER_RE.finditer(vault_text))
    entries = []
    for i, h in enumerate(headers):
        section_end = headers[i + 1].start() if i + 1 < len(headers) else len(vault_text)
        section = vault_text[h.start():section_end]
        try:
            week_date = datetime.strptime(h.group(1), "%Y-%m-%d").date()
        except ValueError:
            week_date = None
        pulled_match = PULLED_RE.search(section)
        pulled_date = None
        if pulled_match:
            try:
                pulled_date = datetime.strptime(pulled_match.group(1), "%Y-%m-%d").date()
            except ValueError:
                pulled_date = None
        gap_match = re.search(r"#### Rock 4 Gap[^\n]*\n(?:.*\n){0,10}?[^\n]*Remaining Gap[^\n]*", section)
        gap_text = gap_match.group(0) if gap_match else section
        has_real_figures = bool(AMOUNT_RE.search(gap_text)) and not PLACEHOLDER_RE.search(gap_text)
        entries.append({
            "week_date": week_date,
            "pulled_date": pulled_date,
            "has_real_figures": has_real_figures,
        })
    return entries


def check_vault(reference_date):
    if not VAULT_FILE.exists():
        return None

    try:
        vault_text = VAULT_FILE.read_text()
    except Exception:
        return None

    entries = parse_vault_entries(vault_text)

    dated = [e for e in entries if e["week_date"] or e["pulled_date"]]
    latest_snapshot_date = None
    for e in dated:
        candidate = e["pulled_date"] or e["week_date"]
        if candidate and (latest_snapshot_date is None or candidate > latest_snapshot_date):
            latest_snapshot_date = candidate

    matching = [
        e for e in entries
        if e["week_date"] and abs((e["week_date"] - reference_date).days) <= WEEKLY_WINDOW_DAYS
    ]
    confirmed = any(e["has_real_figures"] for e in matching)

    return {
        "vault_reachable": True,
        "latest_snapshot_date": latest_snapshot_date.isoformat() if latest_snapshot_date else None,
        "snapshot_confirmed_in_vault": confirmed,
        "matching_entries_found": len(matching),
    }


def stale_days(latest_snapshot_date_str, reference_date):
    if not latest_snapshot_date_str:
        return None
    try:
        latest = datetime.strptime(latest_snapshot_date_str, "%Y-%m-%d").date()
    except ValueError:
        return None
    return (reference_date - latest).days


def main():
    payload = json.loads(sys.stdin.read() or "{}")
    ies_root = Path(payload.get("ies_root", "."))

    state_path = ies_root / "workflows" / "rock4-pipeline-weekly" / "state.yaml"

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/rock4-pipeline-weekly/state.yaml not found or YAML parser unavailable",
            "fields": {"save_outcome": "undocumented"},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Confirm workflows/rock4-pipeline-weekly/state.yaml exists after running workflow.md step 3.",
        }))
        return

    try:
        state = yaml.safe_load(state_path.read_text()) or {}
    except Exception as e:
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml invalid YAML: {e}",
            "fields": {"save_outcome": "undocumented"},
            "validation_errors": ["invalid_yaml"],
            "retry_instruction": "Re-execute step 3 — state.yaml is corrupted or malformed.",
        }))
        return

    status = state.get("status")
    accumulated_context = state.get("accumulated-context") or {}
    cosell = str(accumulated_context.get("cosell") or "")
    pipeline = str(accumulated_context.get("pipeline") or "")
    last_completed = state.get("last-completed")
    last_written = state.get("last-written-obsidian")
    context_str = json.dumps(accumulated_context).lower()

    fields = {
        "status": status,
        "cosell_content_length": len(cosell),
        "pipeline_content_length": len(pipeline),
        "last_completed": last_completed,
        "last_written_obsidian": last_written,
    }

    if status != "complete":
        fields["save_outcome"] = "incomplete"
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml status is '{status}', expected 'complete'",
            "fields": fields,
            "validation_errors": ["status_not_complete"],
            "retry_instruction": "Finish workflow.md step 3 and set status: complete in state.yaml.",
        }))
        return

    validation_errors = []
    if len(cosell) < MIN_SECTION_CONTENT_LENGTH:
        validation_errors.append("cosell_data_missing_or_thin")
    if len(pipeline) < MIN_SECTION_CONTENT_LENGTH:
        validation_errors.append("pipeline_data_missing_or_thin")

    if validation_errors:
        fields["save_outcome"] = "undocumented"
        print(json.dumps({
            "result": "retry",
            "reason": f"status is complete but source data is missing or too thin to represent a real pull: {validation_errors}",
            "fields": fields,
            "validation_errors": validation_errors,
            "retry_instruction": "Re-run skills/co-sell-pipeline/SKILL.md and skills/pipeline-snapshot/SKILL.md and populate accumulated-context.cosell and accumulated-context.pipeline with the formatted output.",
        }))
        return

    reference_date = date.today()
    if last_completed:
        try:
            reference_date = datetime.strptime(str(last_completed), "%Y-%m-%d").date()
        except ValueError:
            pass

    vault_info = check_vault(reference_date)
    if vault_info is None:
        vault_info = {
            "vault_reachable": False,
            "latest_snapshot_date": None,
            "snapshot_confirmed_in_vault": None,
            "matching_entries_found": 0,
        }
        validation_errors_vault = ["vault_unreachable"]
    else:
        validation_errors_vault = []

    fields.update(vault_info)

    documented_skip = any(marker in context_str for marker in SKIP_MARKERS)
    dates_match = bool(last_completed) and last_completed == last_written

    if dates_match:
        fields["save_outcome"] = "fresh-write"
        if vault_info["vault_reachable"]:
            if vault_info["snapshot_confirmed_in_vault"]:
                print(json.dumps({
                    "result": "pass",
                    "reason": "last-completed matches last-written-obsidian and the vault confirms a matching 'Week of' section with real gap figures within the expected weekly window",
                    "fields": fields,
                    "validation_errors": [],
                }))
                return
            days_stale = stale_days(vault_info["latest_snapshot_date"], reference_date)
            outcome = "fail" if days_stale is not None and days_stale > STALE_THRESHOLD_DAYS else "retry"
            print(json.dumps({
                "result": outcome,
                "reason": "state.yaml claims a fresh write (last-completed == last-written-obsidian), but the vault has no confirmed 'Week of' entry within the expected weekly window — the Obsidian append likely never happened",
                "fields": fields,
                "validation_errors": ["fresh_write_claimed_but_vault_unconfirmed"],
                "retry_instruction": "Re-append the current week's snapshot to Mind/One Texas/Rock 4 - Pipeline Snapshots.md with the header format '## Week of <YYYY-MM-DD> — Pipeline Snapshot'.",
            }))
            return
        print(json.dumps({
            "result": "pass",
            "reason": "last-completed matches last-written-obsidian — treated as a fresh append this run (vault unreachable, falling back to state.yaml-only check)",
            "fields": fields,
            "validation_errors": validation_errors_vault,
        }))
        return

    if documented_skip:
        fields["save_outcome"] = "documented-skip"
        if vault_info["vault_reachable"]:
            if vault_info["snapshot_confirmed_in_vault"]:
                print(json.dumps({
                    "result": "pass",
                    "reason": "Recency gate correctly skipped the append — vault confirms a 'Week of' entry within the expected window already exists with real gap figures",
                    "fields": fields,
                    "validation_errors": [],
                }))
                return
            days_stale = stale_days(vault_info["latest_snapshot_date"], reference_date)
            outcome = "fail" if days_stale is not None and days_stale > STALE_THRESHOLD_DAYS else "retry"
            print(json.dumps({
                "result": outcome,
                "reason": "state.yaml claims a documented recency-gate skip, but the vault has no confirmed 'Week of' entry within the expected weekly window — this is exactly the silent-failure case that a state.yaml-only check would have missed",
                "fields": fields,
                "validation_errors": ["skip_claimed_but_vault_unconfirmed"],
                "retry_instruction": "Confirm Mind/One Texas/Rock 4 - Pipeline Snapshots.md actually contains a recent-enough 'Week of' section with real gap figures, or re-run the append.",
            }))
            return
        print(json.dumps({
            "result": "pass",
            "reason": "Recency gate correctly skipped the append — last-written-obsidian predates last-completed but the skip is documented in accumulated-context (vault unreachable, falling back to state.yaml-only check)",
            "fields": fields,
            "validation_errors": validation_errors_vault,
        }))
        return

    fields["save_outcome"] = "undocumented"
    print(json.dumps({
        "result": "retry",
        "reason": "last-written-obsidian does not match last-completed and no recency-gate skip is documented in accumulated-context — cannot confirm whether a write happened or was silently dropped",
        "fields": fields,
        "validation_errors": ["write_status_undocumented"] + validation_errors_vault,
        "retry_instruction": "Either confirm the Obsidian append and set last-written-obsidian to today's date, or explicitly document the recency-gate skip reason in accumulated-context.",
    }))


if __name__ == "__main__":
    main()
