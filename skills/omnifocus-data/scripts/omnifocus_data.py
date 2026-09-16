#!/usr/bin/env python3
"""OmniFocus data extraction.

Canonical producer of `data/omnifocus-unified.json`, plus the shared read
primitives used by every consumer that needs OmniFocus data.

WHY APPLESCRIPT AND NOT THE MCP
-------------------------------
The OmniFocus MCP server is the preferred path for *ad-hoc interactive
reads* by an agent (`query_omnifocus`, `list_tags`). It returns structured
data with IDs and supports server-side filtering.

This script uses AppleScript instead, and that is deliberate. The MCP
path depends on session state: the server must be built, running, and
connected before the session starts. osascript has none of those
dependencies. Boot runs unattended, so the canonical pull must not depend
on MCP availability. Agents should use the MCP when it is present and
fall back to this script; the reverse is not required.

INVARIANTS THIS SCRIPT EXISTS TO ENFORCE
----------------------------------------
1. Every query carries `completed is false`. The inbox permanently holds
   roughly 247 completed tasks alongside ~8 incomplete ones, and OmniFocus
   "Clean Up" does NOT remove them. The filter must live in the query.
2. The output always carries `status`, so a failed pull is distinguishable
   from an empty one. A failed pull must never look like a quiet day.
3. `completed` is written on every task, so the eval harness can assert
   that no completed task leaked into the pull.

USAGE
-----
    omnifocus_data.py pull [--out PATH]   write data/omnifocus-unified.json
    omnifocus_data.py counts [--json]     inbox/flagged/due/overdue counts
    omnifocus_data.py tags                all tag names
    omnifocus_data.py projects            active project names
    omnifocus_data.py list --kind inbox|due|flagged

Exit code is 0 on success, 1 on failure. `pull` never raises: it writes a
`status: failed` record and exits 1, so callers can always read the file.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

FIELD_SEP = "\x1f"
REC_SEP = "\x1e"

# Repo root: this file lives at <root>/skills/omnifocus-data/scripts/
IES_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUT = IES_ROOT / "data" / "omnifocus-unified.json"

# Records are joined with ASCII 30 and fields with ASCII 31 so that commas
# and newlines inside names/notes cannot corrupt parsing. osascript would
# otherwise flatten a returned list with ", ".
#
# `ASCII character` is required: AppleScript's `character 31` is invalid
# and fails with "Can't get character 31. (-1728)".
_TASK_TEMPLATE = r'''
set cutoff to (current date) + (%(days)d * days)
set fsep to (ASCII character 31)
set rsep to (ASCII character 30)

tell application "OmniFocus"
  tell default document
    set collected to {}
%(collect)s
    set out to {}
    set seenIds to {}
    repeat with t in collected
      set tid to id of t
      if seenIds does not contain tid then
        set end of seenIds to tid

        set tname to name of t

        set tnote to ""
        try
          set tnote to note of t
        end try
        if tnote is missing value then set tnote to ""

        set tdue to ""
        if due date of t is not missing value then set tdue to (due date of t as string)

        set tproj to ""
        if containing project of t is not missing value then set tproj to (name of containing project of t)

        set ttags to ""
        try
          set ttags to (name of tags of t) as string
        end try

        set tflag to (flagged of t) as string

        set end of out to tid & fsep & tname & fsep & tdue & fsep & tproj & fsep & ttags & fsep & tflag & fsep & tnote
      end if
    end repeat

    set AppleScript's text item delimiters to rsep
    set joined to out as string
    set AppleScript's text item delimiters to ""
    return joined
  end tell
end tell
'''

COLLECTORS = {
    "inbox": '    repeat with t in (inbox tasks whose completed is false)\n      set end of collected to t\n    end repeat',
    "due": '    repeat with t in (flattened tasks whose completed is false and (due date is not missing value) and (due date < cutoff))\n      set end of collected to t\n    end repeat',
    "flagged": '    repeat with t in (flattened tasks whose completed is false and flagged is true)\n      set end of collected to t\n    end repeat',
}

# Simple scalar expressions, evaluated inside a single `tell default document`.
SIMPLE = {
    "tags": 'name of every flattened tag',
    "projects": 'name of every flattened project whose status is active status',
}

# Count expressions. `cutoff` is referenced by some of these; when it is
# needed it is computed OUTSIDE the tell block, because arithmetic inside it
# gets sent to OmniFocus and fails (see the module docstring).
COUNTS = {
    "inbox_uncompleted": 'count of (inbox tasks whose completed is false)',
    "flagged_uncompleted": 'count of (flattened tasks whose completed is false and flagged is true)',
    "total_uncompleted": 'count of (flattened tasks whose completed is false)',
    "overdue_uncompleted": 'count of (flattened tasks whose completed is false and (due date is not missing value) and (due date < cutoff))',
    "completed_today": 'count of (flattened tasks whose completed is true and completion date is not missing value and (completion date >= cutoff))',
}

NEEDS_CUTOFF = {"overdue_uncompleted", "completed_today"}

# Hours back from now for cutoff-based counts.
CUTOFF_HOURS = {"overdue_uncompleted": 0, "completed_today": 24}


class OmniFocusError(RuntimeError):
    """osascript failed. Carries stderr so callers can surface the reason."""


def _run(script: str, timeout: int = 180) -> str:
    proc = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True, timeout=timeout,
    )
    if proc.returncode != 0:
        raise OmniFocusError(collapse(proc.stderr) or "osascript exited nonzero")
    return proc.stdout


def collapse(s: str) -> str:
    """Collapse whitespace, including newlines, into single spaces."""
    return " ".join((s or "").replace(FIELD_SEP, " ").split())


def _simple(name: str) -> list[str]:
    out = _run(f'tell application "OmniFocus" to tell default document to {SIMPLE[name]}')
    return [x.strip() for x in out.strip().split(",") if x.strip()]


def _count(name: str) -> int:
    pre = ""
    if name in NEEDS_CUTOFF:
        hours = CUTOFF_HOURS[name]
        # Computed OUTSIDE the tell block. Inside it, date arithmetic is sent
        # to OmniFocus and fails.
        pre = f"set cutoff to (current date) - ({hours} * hours)\n"
    script = f'{pre}tell application "OmniFocus" to tell default document to {COUNTS[name]}'
    return int(_run(script).strip())


def collect(kinds: list[str], days: int = 7) -> list[dict]:
    """Run one AppleScript per kind and merge, deduping by task id."""
    merged: dict[str, dict] = {}
    for kind in kinds:
        script = _TASK_TEMPLATE % {"days": days, "collect": COLLECTORS[kind]}
        for rec in _run(script).split(REC_SEP):
            if not rec.strip():
                continue
            parts = rec.split(FIELD_SEP)
            if len(parts) < 7:
                continue
            tid, name, due, proj, tags, flagged, note = parts[:7]
            tid = tid.strip()
            if tid in merged:
                continue
            merged[tid] = {
                "id": tid,
                "name": collapse(name),
                "completed": False,
                "due_date": collapse(due) or None,
                "project": collapse(proj) or None,
                "tags": collapse(tags) or None,
                "is_flagged": flagged.strip().lower() == "true",
                "note": collapse(note),
            }
    return list(merged.values())


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def cmd_pull(args: argparse.Namespace) -> int:
    out = Path(args.out).resolve()
    try:
        tasks = collect(["inbox", "due", "flagged"], days=args.days)
    except (OmniFocusError, subprocess.TimeoutExpired, OSError) as exc:
        # OSError covers osascript being absent or unrunnable, which is the
        # exact condition that degraded this source for five consecutive
        # boots. It must produce a status:failed record, not a traceback.
        write(out, {
            "pulled_at": now_iso(),
            "status": "failed",
            "task_count": 0,
            "tasks": [],
            "error": str(exc),
        })
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1

    write(out, {
        "pulled_at": now_iso(),
        "status": "available",
        "task_count": len(tasks),
        "tasks": tasks,
    })
    if not args.quiet:
        print(f"OK: wrote {len(tasks)} tasks to {out}")
    return 0


def cmd_counts(args: argparse.Namespace) -> int:
    payload = {
        k: _count(k)
        for k in (
            "inbox_uncompleted",
            "flagged_uncompleted",
            "total_uncompleted",
            "overdue_uncompleted",
            "completed_today",
        )
    }
    try:
        payload["due_within_7"] = len(collect(["due"], days=7))
    except (OmniFocusError, subprocess.TimeoutExpired, OSError):
        payload["due_within_7"] = None
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for k, v in payload.items():
            print(f"{k}: {v}")
    return 0


def cmd_tags(args: argparse.Namespace) -> int:
    tags = _simple("tags")
    print(json.dumps(tags, indent=2) if args.json else "\n".join(tags))
    return 0


def cmd_projects(args: argparse.Namespace) -> int:
    projects = _simple("projects")
    print(json.dumps(projects, indent=2) if args.json else "\n".join(projects))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    tasks = collect([args.kind], days=args.days)
    print(json.dumps(tasks, indent=2) if args.json else "\n".join(t["name"] for t in tasks))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="OmniFocus data extraction")
    p.add_argument("--days", type=int, default=7, help="lookahead window for due/overdue (default 7)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("pull", help="write the canonical data file")
    s.add_argument("--out", default=str(DEFAULT_OUT))
    s.add_argument("--quiet", action="store_true")
    s.set_defaults(func=cmd_pull)

    s = sub.add_parser("counts", help="inbox/flagged/due counts")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_counts)

    s = sub.add_parser("tags", help="all tag names")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_tags)

    s = sub.add_parser("projects", help="active project names")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_projects)

    s = sub.add_parser("list", help="list tasks of one kind")
    s.add_argument("--kind", choices=sorted(COLLECTORS), required=True)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_list)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (OmniFocusError, subprocess.TimeoutExpired, OSError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
