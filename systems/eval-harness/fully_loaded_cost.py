#!/usr/bin/env python3
"""Fully-loaded workflow cost: parent-window component + subagent components.

The problem (David, 2026-10-21): a workflow record's total_cost_usd summed
only steps[] and subagents[]. For the day's boot that was $0.68 — but the
boot ran inside a parent session whose own main-context turns during the
boot's execution window are billed too (that session metered ~34M glm-5p3
input tokens that day, ~$13). A workflow's recorded cost must correlate
across the WHOLE run, orchestration included.

Component model (no double counting):

  - parent_window   — the parent session's OWN non-sidechain assistant turns
                      in the main transcript within [started, completed].
                      Computed by token_usage.parent_window_usage. Inline
                      steps (token_source: windowed) are a SUBSET of this
                      window, so they are never added on top.
  - subagent work   — the record's subagents[] entries, plus steps carrying
                      executed_by_agent_id whose subagent rollup lost its
                      stop hook (same guard as eval-turn-stop.py finalize).
                      For type:"agent" records (a subagent's own record) this
                      is the record's own total_cost_usd instead.

  fully_loaded_cost_usd = parent_window.cost_usd + subagent-work cost

Record fields written:

  parent_window: {token_source, transcript_path, window_start, window_end,
                  model, tokens_input, tokens_output, cost_usd,
                  turns_matched, turns_with_usage, computed_at,
                  unpriced_models?}
  fully_loaded_cost_usd, fully_loaded_tokens_input,
  fully_loaded_tokens_output, fully_loaded_note?

Honest-null policy (same as the rest of the harness): a closed record whose
session transcript is missing (Cowork/VM-hosted runs store no transcript
under ~/.claude/projects) gets token_source "no-session-transcript" and null
tokens — never a fabricated zero — and fully_loaded falls back to the
subagent component with a note.

Writers: .claude/hooks/eval-turn-stop.py (workflow records, at finalize) and
.claude/hooks/eval-agent-stop.py (subagent records, at stop). This module is
also the backfill CLI:

    python3 fully_loaded_cost.py --date 2026-10-21 [--record eval-...] [--dry-run]
"""

import argparse
import fcntl
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MODULE_DIR))

import token_usage

EVAL_RUNS_DIR = MODULE_DIR / "runs"
PROJECTS_DIR = Path.home() / ".claude" / "projects"


def find_session_transcript(session_id: str, projects_dir: Path | None = None) -> str | None:
    """Locate the main session transcript <session_id>.jsonl under any
    ~/.claude/projects/<proj>/ directory. Newest mtime wins on duplicates
    (the same session id can appear under two project roots when a workflow
    re-points cwd)."""
    if not session_id:
        return None
    root = Path(projects_dir) if projects_dir else PROJECTS_DIR
    if not root.exists():
        return None
    matches = [p for p in root.glob(f"*/{session_id}.jsonl") if p.is_file()]
    if not matches:
        return None
    return str(max(matches, key=lambda p: p.stat().st_mtime))


def cost_components(record: dict) -> tuple[dict, dict]:
    """Split the record's recorded cost into (inline, subagent) components,
    mirroring eval-turn-stop.py finalize's double-count guard: a step stamped
    executed_by_agent_id is the SAME tokens as that subagent's subagents[]
    rollup, so it counts on the subagent side only when the rollup entry
    carries no tokens of its own (stop hook lost).

    A component's `cost` is None when nothing on that side carried a cost
    value at all (unknown), distinct from a summed 0.0 (known-zero)."""
    subs = [s for s in (record.get("subagents") or []) if isinstance(s, dict)]
    sub_ids_with_tokens = {s.get("agent_id") for s in subs
                           if s.get("tokens_input") is not None}
    inline = {"cost": None, "tokens_input": 0, "tokens_output": 0}
    sub = {"cost": None, "tokens_input": 0, "tokens_output": 0}

    def _add(bucket, cost, tin, tout):
        if cost is not None:
            bucket["cost"] = (bucket["cost"] or 0) + cost
        bucket["tokens_input"] += tin or 0
        bucket["tokens_output"] += tout or 0

    for s in subs:
        _add(sub, s.get("cost_usd"), s.get("tokens_input"), s.get("tokens_output"))
    for s in (record.get("steps") or []):
        if not isinstance(s, dict):
            continue
        ex = s.get("executed_by_agent_id")
        if ex and ex in sub_ids_with_tokens:
            continue  # already counted in the subagent rollup
        bucket = sub if ex else inline
        _add(bucket, s.get("cost_usd"), s.get("tokens_input"), s.get("tokens_output"))
    return inline, sub


def own_run_cost(record: dict) -> dict:
    """The subagent-work component to add alongside the parent window.

    workflow records: the subagent component (inline steps live inside the
    parent window). agent/skill records: the record's own whole-run totals
    (the record IS the subagent run)."""
    if record.get("type") == "workflow" and (record.get("steps") or record.get("subagents")):
        _inline, sub = cost_components(record)
        return sub
    cost = record.get("total_cost_usd")
    tin = record.get("total_tokens_input")
    tout = record.get("total_tokens_output")
    if cost is None and (record.get("steps") or []):
        # fallback: sum whatever the steps carry (None when they carry nothing)
        _inline, sub = cost_components({"steps": record["steps"], "subagents": []})
        cost = (sub.get("cost") or 0) + (_inline.get("cost") or 0)
        if sub.get("cost") is None and _inline.get("cost") is None:
            cost = None
        tin = tin if tin is not None else sub["tokens_input"] + _inline["tokens_input"]
        tout = tout if tout is not None else sub["tokens_output"] + _inline["tokens_output"]
    return {"cost": cost, "tokens_input": tin, "tokens_output": tout}


def apply_to_record(record: dict, transcript_path: str | None = None,
                    projects_dir: Path | None = None,
                    now: str | None = None) -> dict | None:
    """Compute and stamp the parent_window block + fully_loaded_* fields onto
    a record (mutated in place). Returns the parent_window block, or None when
    the record has no usable execution window (nothing written then — an
    open/in-progress run's window is still growing)."""
    start = record.get("started")
    end = record.get("completed")
    if not start or not end:
        return None
    if token_usage._parse_ts(end) and token_usage._parse_ts(start) \
            and token_usage._parse_ts(end) < token_usage._parse_ts(start):
        # corrupted window (e.g. eval-20261021T151813-348IAN, completed
        # predates started) — no honest slice exists
        record["parent_window"] = {
            "token_source": "invalid-window",
            "window_start": start, "window_end": end,
            "model": None, "tokens_input": None, "tokens_output": None,
            "cost_usd": None, "turns_matched": 0, "turns_with_usage": 0,
            "computed_at": now or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        own = own_run_cost(record)
        record["fully_loaded_cost_usd"] = own.get("cost")
        record["fully_loaded_tokens_input"] = own.get("tokens_input")
        record["fully_loaded_tokens_output"] = own.get("tokens_output")
        record["fully_loaded_note"] = (
            "invalid execution window (completed predates started); "
            "fully_loaded covers the subagent component only")
        return record["parent_window"]

    tp = transcript_path or find_session_transcript(record.get("session_id"), projects_dir)
    own = own_run_cost(record)
    note = None

    if not tp:
        block = {
            "token_source": "no-session-transcript",
            "transcript_path": None,
            "window_start": start, "window_end": end,
            "model": None, "tokens_input": None, "tokens_output": None,
            "cost_usd": None, "turns_matched": 0, "turns_with_usage": 0,
            "computed_at": now or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        note = ("parent window not computable locally (no session transcript "
                "under ~/.claude/projects — Cowork/VM-hosted run?); "
                "fully_loaded covers the subagent component only")
    else:
        pw = token_usage.parent_window_usage(tp, start, end)
        if pw is None:
            block = {
                "token_source": "transcript-unreadable",
                "transcript_path": tp,
                "window_start": start, "window_end": end,
                "model": None, "tokens_input": None, "tokens_output": None,
                "cost_usd": None, "turns_matched": 0, "turns_with_usage": 0,
                "computed_at": now or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            }
            note = "parent transcript unreadable; fully_loaded covers the subagent component only"
        else:
            block = {
                "token_source": pw["token_source"],
                "transcript_path": tp,
                "window_start": start, "window_end": end,
                "model": pw.get("model"),
                "tokens_input": pw.get("tokens_input"),
                "tokens_output": pw.get("tokens_output"),
                "cost_usd": pw.get("cost_usd"),
                "turns_matched": pw.get("turns_matched"),
                "turns_with_usage": pw.get("turns_with_usage"),
                "computed_at": now or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            }
            if pw.get("unpriced_models"):
                block["unpriced_models"] = pw["unpriced_models"]
                note = (f"parent window contains unpriced model(s) "
                        f"{pw['unpriced_models']}; their tokens are in the "
                        f"token sums but not in cost_usd")

    record["parent_window"] = block

    pw_cost = block.get("cost_usd")
    pw_in = block.get("tokens_input")
    pw_out = block.get("tokens_output")
    if pw_cost is not None or own.get("cost") is not None:
        record["fully_loaded_cost_usd"] = round((pw_cost or 0) + (own.get("cost") or 0), 6)
        record["fully_loaded_tokens_input"] = (pw_in or 0) + (own.get("tokens_input") or 0)
        record["fully_loaded_tokens_output"] = (pw_out or 0) + (own.get("tokens_output") or 0)
    else:
        record["fully_loaded_cost_usd"] = None
        record["fully_loaded_tokens_input"] = None
        record["fully_loaded_tokens_output"] = None
    if note:
        record["fully_loaded_note"] = note
    elif "fully_loaded_note" in record:
        del record["fully_loaded_note"]
    return block


def _atomic_write(path: Path, data: dict):
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        json.dump(data, f, indent=2)
        fcntl.flock(f, fcntl.LOCK_UN)
    tmp.replace(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", help="Backfill records whose started date is YYYY-MM-DD")
    ap.add_argument("--record", help="Backfill a single eval record id")
    ap.add_argument("--since", help="Started >= this ISO date (alternative to --date)")
    ap.add_argument("--until", help="Started < this ISO date (alternative to --date)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--runs-dir", default=str(EVAL_RUNS_DIR))
    ap.add_argument("--projects-dir", default=None)
    args = ap.parse_args()

    runs_dir = Path(args.runs_dir)
    if args.record:
        candidates = [runs_dir / f"{args.record}.json"]
    else:
        if not (args.date or args.since):
            ap.error("pass --date, --since/--until, or --record")
        since = args.since or args.date
        until = args.until or (args.date + "T99" if args.date else "9999")
        candidates = []
        for f in sorted(runs_dir.glob("eval-*.json")):
            try:
                d = json.load(open(f))
            except Exception:
                continue
            started = d.get("started") or ""
            if started >= since and started < until:
                candidates.append(f)

    changed = skipped = 0
    for f in candidates:
        if not f.exists():
            continue
        try:
            record = json.load(open(f))
        except Exception:
            continue
        if not record.get("completed"):
            skipped += 1
            continue
        block = apply_to_record(record, projects_dir=args.projects_dir)
        if block is None:
            skipped += 1
            continue
        changed += 1
        fl = record.get("fully_loaded_cost_usd")
        print(f"{record.get('id')}  {str(record.get('name'))[:24]:<24} "
              f"pw={block.get('token_source')} "
              f"pw_cost={block.get('cost_usd')} "
              f"fully_loaded={fl}")
        if not args.dry_run:
            _atomic_write(f, record)
    print(f"\n{changed} record(s) updated, {skipped} skipped "
          f"(open or no window){' — DRY RUN, nothing written' if args.dry_run else ''}")


if __name__ == "__main__":
    main()
