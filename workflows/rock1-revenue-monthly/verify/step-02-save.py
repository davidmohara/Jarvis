#!/usr/bin/env python3
"""Ground-truth verifier for rock1-revenue-monthly/step-02-save.

This workflow is a single workflow.md file with no steps/ directory — the
literal current-step value it writes is "step-02-save", taken directly from
the state.yaml examples in workflow.md and from a real completed run, not
inferred.

The Obsidian vault is readable directly from the filesystem (iCloud-synced
folder). When reachable, this verifier parses Mind/One Texas/Rock 1 -
Revenue Snapshots.md directly and confirms a dated snapshot section for the
run's expected month actually exists with real revenue figures — closing
the gap where a workflow could write a garbage state.yaml claiming success
without ever calling the Obsidian MCP tool. If the vault path is ever
unreachable, this degrades to the original state.yaml-only proxy logic.
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

MIN_REVENUE_CONTENT_LENGTH = 40
SKIP_MARKERS = ("already", "skip", "cache hit")

VAULT_FILE = Path("/Users/davidohara/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian/Mind/One Texas/Rock 1 - Revenue Snapshots.md")

HEADER_RE = re.compile(r"^##\s+(?:CORRECTED\s*—\s*)?(.+?)\s*—\s*Revenue Snapshot(?:\s*\(.*\))?\s*$", re.MULTILINE)
PULLED_RE = re.compile(r"\*Pulled:\s*(\d{4}-\d{2}-\d{2})")
AMOUNT_RE = re.compile(r"\$[\d,.]+\s*[MK]?")
PLACEHOLDER_RE = re.compile(r"\b(n/a|tbd|null|none|pending)\b", re.IGNORECASE)
MONTH_YEAR_RE = re.compile(r"^([A-Za-z]+)\s+(\d{4})$")
MONTH_DAY_YEAR_RE = re.compile(r"^([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})$")

STALE_THRESHOLD_DAYS = 62


def parse_header_date(text):
    text = text.strip()
    m = MONTH_DAY_YEAR_RE.match(text)
    if m:
        month_name, day, year = m.groups()
        try:
            return datetime.strptime(f"{month_name} {day} {year}", "%B %d %Y").date()
        except ValueError:
            return None
    m = MONTH_YEAR_RE.match(text)
    if m:
        month_name, year = m.groups()
        try:
            return datetime.strptime(f"{month_name} 1 {year}", "%B %d %Y").date()
        except ValueError:
            return None
    return None


def parse_vault_entries(vault_text):
    headers = list(HEADER_RE.finditer(vault_text))
    entries = []
    for i, h in enumerate(headers):
        section_end = headers[i + 1].start() if i + 1 < len(headers) else len(vault_text)
        section = vault_text[h.start():section_end]
        header_date = parse_header_date(h.group(1))
        pulled_match = PULLED_RE.search(section)
        pulled_date = None
        if pulled_match:
            try:
                pulled_date = datetime.strptime(pulled_match.group(1), "%Y-%m-%d").date()
            except ValueError:
                pulled_date = None
        row_match = re.search(r"\|\s*Monthly Revenue\s*\|[^\n]*", section)
        row_text = row_match.group(0) if row_match else ""
        has_real_figures = bool(AMOUNT_RE.search(row_text)) and not PLACEHOLDER_RE.search(row_text)
        entries.append({
            "header_date": header_date,
            "pulled_date": pulled_date,
            "has_real_figures": has_real_figures,
        })
    return entries


def check_vault(expected_year_month):
    if not VAULT_FILE.exists():
        return None

    try:
        vault_text = VAULT_FILE.read_text()
    except Exception:
        return None

    entries = parse_vault_entries(vault_text)

    dated_entries = [e for e in entries if e["header_date"] or e["pulled_date"]]
    latest_snapshot_date = None
    for e in dated_entries:
        candidate = e["pulled_date"] or e["header_date"]
        if candidate and (latest_snapshot_date is None or candidate > latest_snapshot_date):
            latest_snapshot_date = candidate

    matching = [
        e for e in entries
        if (e["header_date"] and (e["header_date"].year, e["header_date"].month) == expected_year_month)
        or (e["pulled_date"] and (e["pulled_date"].year, e["pulled_date"].month) == expected_year_month)
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

    state_path = ies_root / "workflows" / "rock1-revenue-monthly" / "state.yaml"

    if yaml is None or not state_path.is_file():
        print(json.dumps({
            "result": "retry",
            "reason": "workflows/rock1-revenue-monthly/state.yaml not found or YAML parser unavailable",
            "fields": {"save_outcome": "undocumented"},
            "validation_errors": ["state_file_missing"],
            "retry_instruction": "Confirm workflows/rock1-revenue-monthly/state.yaml exists after running workflow.md step 2.",
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
            "retry_instruction": "Re-execute step 2 — state.yaml is corrupted or malformed.",
        }))
        return

    status = state.get("status")
    accumulated_context = state.get("accumulated-context") or {}
    revenue = str(accumulated_context.get("revenue") or "")
    context_str = json.dumps(accumulated_context).lower()

    fields = {
        "status": status,
        "revenue_content_length": len(revenue),
    }

    if status != "complete":
        fields["save_outcome"] = "incomplete"
        print(json.dumps({
            "result": "retry",
            "reason": f"state.yaml status is '{status}', expected 'complete'",
            "fields": fields,
            "validation_errors": ["status_not_complete"],
            "retry_instruction": "Finish workflow.md step 2 and set status: complete in state.yaml.",
        }))
        return

    session_started_str = state.get("session-started")
    reference_date = date.today()
    expected_year_month = (reference_date.year, reference_date.month)
    if session_started_str:
        try:
            reference_date = datetime.strptime(str(session_started_str), "%Y-%m-%d").date()
            expected_year_month = (reference_date.year, reference_date.month)
        except ValueError:
            pass

    validation_errors = []
    vault_info = check_vault(expected_year_month)
    if vault_info is None:
        vault_info = {
            "vault_reachable": False,
            "latest_snapshot_date": None,
            "snapshot_confirmed_in_vault": None,
            "matching_entries_found": 0,
        }
        validation_errors.append("vault_unreachable")

    fields.update(vault_info)

    documented_skip = any(marker in context_str for marker in SKIP_MARKERS)

    if documented_skip:
        fields["save_outcome"] = "documented-skip"
        if vault_info["vault_reachable"]:
            if vault_info["snapshot_confirmed_in_vault"]:
                print(json.dumps({
                    "result": "pass",
                    "reason": "Recency gate correctly skipped the append — vault confirms a snapshot for this month already exists with real revenue figures",
                    "fields": fields,
                    "validation_errors": [],
                }))
                return
            days_stale = stale_days(vault_info["latest_snapshot_date"], reference_date)
            outcome = "fail" if days_stale is not None and days_stale > STALE_THRESHOLD_DAYS else "retry"
            print(json.dumps({
                "result": outcome,
                "reason": "state.yaml claims a recency-gate skip, but the vault has no confirmed snapshot for the expected month — this is exactly the silent-failure case that a state.yaml-only check would have missed",
                "fields": fields,
                "validation_errors": ["skip_claimed_but_vault_unconfirmed"],
                "retry_instruction": "Confirm Mind/One Texas/Rock 1 - Revenue Snapshots.md actually contains a dated section for the expected month with real Dallas/South Texas figures, or re-run the append.",
            }))
            return
        print(json.dumps({
            "result": "pass",
            "reason": "Recency gate correctly skipped the append — a snapshot for this month already exists (vault unreachable, falling back to state.yaml-only check)",
            "fields": fields,
            "validation_errors": validation_errors,
        }))
        return

    if len(revenue) >= MIN_REVENUE_CONTENT_LENGTH:
        fields["save_outcome"] = "fresh-write"
        if vault_info["vault_reachable"]:
            if vault_info["snapshot_confirmed_in_vault"]:
                print(json.dumps({
                    "result": "pass",
                    "reason": "Revenue data collected, status complete, and vault confirms a fresh snapshot section for the expected month with real revenue figures",
                    "fields": fields,
                    "validation_errors": [],
                }))
                return
            days_stale = stale_days(vault_info["latest_snapshot_date"], reference_date)
            outcome = "fail" if days_stale is not None and days_stale > STALE_THRESHOLD_DAYS else "retry"
            print(json.dumps({
                "result": outcome,
                "reason": "state.yaml claims a fresh write with real revenue data, but the vault file has no matching dated section for the expected month — the Obsidian append likely never happened",
                "fields": fields,
                "validation_errors": ["fresh_write_claimed_but_vault_unconfirmed"],
                "retry_instruction": "Re-append the current month's snapshot to Mind/One Texas/Rock 1 - Revenue Snapshots.md with the header format '## <Month> <Year> — Revenue Snapshot'.",
            }))
            return
        print(json.dumps({
            "result": "pass",
            "reason": "Revenue data collected and status complete with no recency-skip note — treated as a fresh Obsidian append (vault unreachable, falling back to state.yaml-only check)",
            "fields": fields,
            "validation_errors": validation_errors,
        }))
        return

    fields["save_outcome"] = "undocumented"
    print(json.dumps({
        "result": "retry",
        "reason": "status is complete but accumulated-context has neither a documented recency-skip nor substantive revenue data — cannot confirm the snapshot was ever produced",
        "fields": fields,
        "validation_errors": ["no_revenue_data_no_skip_note"] + validation_errors,
        "retry_instruction": "Re-run skills/revenue-tracker/SKILL.md and populate accumulated-context.revenue with the formatted output, or document the recency-gate skip explicitly in accumulated-context.",
    }))


if __name__ == "__main__":
    main()
