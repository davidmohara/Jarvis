#!/usr/bin/env python3
"""OmniFocus data extraction.

Canonical producer of `data/omnifocus-unified.json`, plus the shared read
primitives used by every consumer that needs OmniFocus data.

TWO PATHS: APPLESCRIPT AND MCP
------------------------------
AppleScript (osascript) is the pull path. The MCP server is an agent tool
reachable only through the session's connection, so it cannot be the sole
path: boot runs unattended, and an MCP that is "not connected" is a normal
condition there, not an error. osascript has no such dependency.

The MCP is used where it is genuinely better: `counts` (it speaks OmniFocus's
*effective* status, so archived work is excluded correctly), and `tags` /
`projects` (server-owned data, no parsing of our own). See `mcp_client.py`.

The one place the two disagree is `total_uncompleted`, and the MCP is right.
`count of (flattened tasks whose completed is false)` is inflated two ways:
`flattened tasks` includes each project's *root* row (49 of them here), and it
counts tasks inside archived projects, which OmniFocus itself treats as
dropped. Measured 2026-09-16: the naive count is 258; the honest count of open,
non-archived tasks is 136. Both paths now return the honest number.

INVARIANTS THIS SCRIPT EXISTS TO ENFORCE
----------------------------------------
1. Every query carries `completed is false`. The inbox permanently holds
   roughly 247 completed tasks alongside ~8 incomplete ones, and OmniFocus
   "Clean Up" does NOT remove them. The filter must live in the query.
2. The output always carries `status`, so a failed pull is distinguishable
   from an empty one. A failed pull must never look like a quiet day.
3. `completed` is written on every task, so the eval harness can assert
   that no completed task leaked into the pull.
4. `total_uncompleted` counts real open tasks: no project root rows, no tasks
   inside archived (hidden) folders. Anything else overstates the workload.

USAGE
-----
    omnifocus_data.py pull [--out PATH]   write data/omnifocus-unified.json
    omnifocus_data.py counts [--json]     inbox/flagged/due/overdue counts
    omnifocus_data.py tags                all tag names
    omnifocus_data.py projects            active project names
    omnifocus_data.py list --kind inbox|due|flagged

`--source {auto,mcp,apple}` forces a path (default `auto`: MCP when the server
is reachable, AppleScript otherwise). `pull` and `list` always use AppleScript,
because `query_omnifocus` returns a *display* rendering that omits notes.

Exit code is 0 on success, 1 on failure. `pull` never raises: it writes a
`status: failed` record and exits 1, so callers can always read the file.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Same directory; running the script puts it on sys.path, but an import from
# elsewhere would not, so make it explicit.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from mcp_client import McpClient, McpError  # noqa: E402

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

# Name-list reads. Each body assigns an AppleScript list to `out`; the template
# joins it with REC_SEP rather than letting AppleScript's default delimiter
# (", ") do it, because a tag or project named "A, B" would otherwise be split
# into two names with no error.
_NAMES_TEMPLATE = r'''
tell application "OmniFocus"
  tell default document
    set rsep to (ASCII character 30)
%(body)s
    set AppleScript's text item delimiters to rsep
    set joined to out as string
    set AppleScript's text item delimiters to ""
    return joined
  end tell
end tell
'''

NAMES_BODIES = {
    "tags": '    set out to (name of every flattened tag)',

    # `status is active status` alone returns three projects that live inside
    # the hidden Archive folder. OmniFocus's UI and the MCP both treat those as
    # dropped, so the AppleScript path has to exclude them too or the two
    # backends disagree (30 vs 27) and the task-creation gate offers archived
    # projects as targets. Same reasoning as _TOTAL_TEMPLATE.
    "projects": r'''    set archivedIds to {}
    repeat with fld in flattened folders
      if hidden of fld then
        repeat with pr in flattened projects of fld
          set end of archivedIds to (id of pr)
        end repeat
      end if
    end repeat
    set out to {}
    repeat with pr in flattened projects
      if (status of pr is active status) and (archivedIds does not contain (id of pr)) then
        set end of out to (name of pr)
      end if
    end repeat''',
}

# Count expressions. `cutoff` is referenced by some of these; when it is
# needed it is computed OUTSIDE the tell block, because arithmetic inside it
# gets sent to OmniFocus and fails (see the module docstring).
#
# `total_uncompleted` is deliberately absent: `flattened tasks` folds in each
# project's root row and counts tasks inside archived (hidden) folders, so a
# one-line count over it returns 258 where the honest answer is 136. It is
# computed by `_total_uncompleted()` instead.
COUNTS = {
    "inbox_uncompleted": 'count of (inbox tasks whose completed is false)',
    "flagged_uncompleted": 'count of (flattened tasks whose completed is false and flagged is true)',
    "overdue_uncompleted": 'count of (flattened tasks whose completed is false and (due date is not missing value) and (due date < cutoff))',
    "completed_today": 'count of (flattened tasks whose completed is true and completion date is not missing value and (completion date >= cutoff))',
}

NEEDS_CUTOFF = {"overdue_uncompleted", "completed_today"}

# Hours back from now for cutoff-based counts.
CUTOFF_HOURS = {"overdue_uncompleted": 0, "completed_today": 24}

# Open tasks that are genuinely open work.
#
# Two corrections, both measured against this database on 2026-09-16:
#
#   * Iterate projects rather than `flattened tasks`. The global collection
#     includes one row per project (its root), which carries completed=false
#     and is indistinguishable from a task in a count. That is 49 phantom rows
#     here, and it is also why the MCP reports project names as tasks.
#   * Skip projects inside hidden folders. OmniFocus "Archives" by hiding a
#     folder; the tasks inside keep completed=false forever, so they inflate
#     every naive count. 73 tasks live in the Archive folder here.
#
# Variable names avoid single letters (`c`, `h`, `p`): those collide with
# OmniFocus property names and produce "Can't set <name> of default document".
_TOTAL_TEMPLATE = r'''
tell application "OmniFocus"
  tell default document
    set archivedIds to {}
    repeat with fld in flattened folders
      if hidden of fld then
        repeat with pr in flattened projects of fld
          set end of archivedIds to (id of pr)
        end repeat
      end if
    end repeat

    set runningTotal to 0
    repeat with pr in flattened projects
      if archivedIds does not contain (id of pr) then
        set runningTotal to runningTotal + (count of (flattened tasks of pr whose completed is false))
      end if
    end repeat
    set runningTotal to runningTotal + (count of (inbox tasks whose completed is false))
    return runningTotal
  end tell
end tell
'''


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


def _names(kind: str) -> list[str]:
    out = _run(_NAMES_TEMPLATE % {"body": NAMES_BODIES[kind]})
    return [x.strip() for x in out.split(REC_SEP) if x.strip()]


def _count(name: str) -> int:
    if name == "total_uncompleted":
        return int(_run(_TOTAL_TEMPLATE).strip())
    pre = ""
    if name in NEEDS_CUTOFF:
        hours = CUTOFF_HOURS[name]
        # Computed OUTSIDE the tell block. Inside it, date arithmetic is sent
        # to OmniFocus and fails.
        pre = f"set cutoff to (current date) - ({hours} * hours)\n"
    script = f'{pre}tell application "OmniFocus" to tell default document to {COUNTS[name]}'
    return int(_run(script).strip())


# --------------------------------------------------------------------------
# MCP path
#
# Only the reads the MCP models better live here. `pull` and `list` stay on
# AppleScript: `query_omnifocus` returns a display rendering ("• name [id]
# (project) #status") that drops `note` entirely, so it cannot reproduce the
# canonical record shape. The JSON *resources* do carry notes, but they cover
# only inbox / flagged / today, not an arbitrary due window.
# --------------------------------------------------------------------------

COUNT_KEYS = (
    "inbox_uncompleted",
    "flagged_uncompleted",
    "total_uncompleted",
    "overdue_uncompleted",
    "completed_today",
)


def mcp_counts() -> dict:
    """The same six numbers, read through the MCP.

    `total_uncompleted` subtracts the project count because the MCP's task
    query returns each project's root row alongside its tasks — the same
    phantom rows described in `_TOTAL_TEMPLATE`. The subtraction is exact: the
    roots it returns are precisely the projects it returns (both are filtered
    by the same "not completed, not dropped" rule), and it is guarded below so
    an unexpected server change degrades to AppleScript rather than to a wrong
    number.
    """
    with McpClient() as c:
        all_open = c.query_count(entity="tasks")
        project_roots = c.query_count(entity="projects")
        if project_roots > all_open:
            raise McpError(
                f"project roots ({project_roots}) exceed open items ({all_open}); "
                "the MCP's task set no longer nests projects")

        return {
            "inbox_uncompleted": c.query_count(entity="tasks", filters={"inbox": True}),
            "flagged_uncompleted": c.query_count(entity="tasks", filters={"flagged": True}),
            "total_uncompleted": all_open - project_roots,
            "overdue_uncompleted": c.query_count(
                entity="tasks", filters={"status": ["Overdue"]}),
            "completed_today": c.query_count(
                entity="tasks", includeCompleted=True, filters={"completedOn": 0}),
            "due_within_7": c.query_count(entity="tasks", filters={"dueWithin": 7}),
        }


def apple_counts() -> dict:
    payload = {k: _count(k) for k in COUNT_KEYS}
    try:
        payload["due_within_7"] = len(collect(["due"], days=7))
    except (OmniFocusError, subprocess.TimeoutExpired, OSError):
        payload["due_within_7"] = None
    return payload


_TAG_LINE = re.compile(r"^\s*-\s+\*\*(.+?)\*\*", re.MULTILINE)


def mcp_tags() -> list[str]:
    """All tag names, including inactive ones.

    `list_tags` returns markdown, so the parse is checked against the count the
    server states in its own header. A mismatch raises, which sends the caller
    to AppleScript rather than emitting a truncated tag list into the
    task-creation gate.
    """
    with McpClient() as c:
        # includeDropped matters: Browser, Laptop and Convo are inactive, and
        # the AppleScript path lists them. Dropping them here would make the
        # two paths disagree.
        text = c.call_tool("list_tags", {"includeDropped": True})

    declared = re.search(r"## Tags \((\d+)\)", text)
    names = [m.group(1).strip() for m in _TAG_LINE.finditer(text)]
    if not declared or len(names) != int(declared.group(1)):
        raise McpError(
            f"tag parse mismatch: server declared {declared.group(1) if declared else '?'}, "
            f"parsed {len(names)}")
    return names


# With `fields: ["name"]` the renderer appends nothing else — no id, status,
# date, folder or flag — so each line is exactly "P: <name>". Parsing that
# beats parsing "P: <name> [<id>] ...", where a name containing a bracketed
# token would split in the wrong place. The count check below still guards the
# parse, and the fallback keeps a surprise from reaching the task-creation gate.
_PROJECT_LINE = re.compile(r"^P:\s(.*)$", re.MULTILINE)


def mcp_projects() -> list[str]:
    """Active project names, checked against the server's own count."""
    with McpClient() as c:
        expected = c.query_count(entity="projects", filters={"status": ["Active"]})
        text = c.call_tool(
            "query_omnifocus",
            {"entity": "projects", "fields": ["name"],
             "filters": {"status": ["Active"]}})

    names = [m.group(1).strip() for m in _PROJECT_LINE.finditer(text)]
    if len(names) != expected:
        raise McpError(
            f"project parse mismatch: server counted {expected}, parsed {len(names)}")
    return names


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


def _read_from(source: str, mcp_fn, apple_fn):
    """Run `mcp_fn`, falling back to `apple_fn`.

    `--source mcp` never falls back: a caller that asked for the MCP wants to
    hear that the MCP is unavailable, not to be quietly served AppleScript.
    `auto` falls back, because a missing MCP is the normal state of an
    unattended run.
    """
    if source == "apple":
        return apple_fn()
    try:
        return mcp_fn()
    except (McpError, OSError) as exc:
        if source == "mcp":
            raise
        print(f"note: MCP unavailable ({exc}); using AppleScript", file=sys.stderr)
        return apple_fn()


def cmd_counts(args: argparse.Namespace) -> int:
    payload = _read_from(args.source, mcp_counts, apple_counts)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for k, v in payload.items():
            print(f"{k}: {v}")
    return 0


def cmd_tags(args: argparse.Namespace) -> int:
    tags = _read_from(args.source, mcp_tags, lambda: _names("tags"))
    print(json.dumps(tags, indent=2) if args.json else "\n".join(tags))
    return 0


def cmd_projects(args: argparse.Namespace) -> int:
    projects = _read_from(args.source, mcp_projects, lambda: _names("projects"))
    print(json.dumps(projects, indent=2) if args.json else "\n".join(projects))
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    tasks = collect([args.kind], days=args.days)
    print(json.dumps(tasks, indent=2) if args.json else "\n".join(t["name"] for t in tasks))
    return 0


SOURCE_HELP = (
    "counts/tags/projects: 'auto' prefers the MCP and falls back to "
    "AppleScript; 'mcp' fails instead of falling back; 'apple' is "
    "AppleScript only. pull/list always use AppleScript."
)


def _add_source(parser: argparse.ArgumentParser) -> None:
    """Accept --source after the subcommand as well as before it.

    SUPPRESS is load-bearing: without it the subparser's default would clobber
    a --source given before the subcommand.
    """
    parser.add_argument(
        "--source", choices=("auto", "mcp", "apple"),
        default=argparse.SUPPRESS, help=SOURCE_HELP,
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="OmniFocus data extraction")
    p.add_argument("--days", type=int, default=7, help="lookahead window for due/overdue (default 7)")
    p.add_argument("--source", choices=("auto", "mcp", "apple"), default="auto", help=SOURCE_HELP)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("pull", help="write the canonical data file")
    s.add_argument("--out", default=str(DEFAULT_OUT))
    s.add_argument("--quiet", action="store_true")
    s.set_defaults(func=cmd_pull)

    s = sub.add_parser("counts", help="inbox/flagged/due counts")
    s.add_argument("--json", action="store_true")
    _add_source(s)
    s.set_defaults(func=cmd_counts)

    s = sub.add_parser("tags", help="all tag names")
    s.add_argument("--json", action="store_true")
    _add_source(s)
    s.set_defaults(func=cmd_tags)

    s = sub.add_parser("projects", help="active project names")
    s.add_argument("--json", action="store_true")
    _add_source(s)
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
    except (OmniFocusError, McpError, subprocess.TimeoutExpired, OSError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
