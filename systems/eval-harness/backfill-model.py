#!/usr/bin/env python3
"""Backfill `model` (and `model_source`) on eval records where it is derivable.

Created 2026-10-23 after David asked whether the harness captures the model
that executed each run/step — the answer was inconsistent: agent records got
a top-level model from eval-agent-stop.py's transcript slice, boot workflow
records got parent_window.model, but skill records, Cowork-path workflow
records, and most closed-without-transcript records carried nothing.

Derivation rules (verify-before-asserting: only real evidence, never a
default guess):

  Top-level record model, in priority order (first hit wins):
    1. workflow records: parent_window.model — already derived from the
       session transcript's own turns in the run window by
       fully_loaded_cost.py. Source: "parent-window-backfill".
    2. records with agent_transcript_path pointing at an existing file
       (type "agent"): dominant model of that subagent transcript's turns
       in [started, completed]. Source: "subagent-transcript-backfill".
    3. type "skill"/"workflow" records with a session_id whose session
       transcript exists under ~/.claude/projects: dominant model of the
       session's own (non-sidechain) turns in the run window; if the strict
       window is empty, the transcript's latest assistant-turn model.
       Sources: "session-transcript-window-backfill" /
       "session-transcript-latest-backfill".
       (NOT applied to type "agent" records: the session transcript there is
       the PARENT's, and stamping the parent's model on a subagent run would
       be a guess.)
    4. Otherwise: left absent.

  subagents[] entries: model copied from the child agent's own eval record
  (matched by agent_id) when the child carries one.
  Source: "child-record-backfill".

  steps[] entries: model copied from the executing subagent's own record
  when the step carries executed_by_agent_id and that child record has a
  model. Source: "child-record-backfill".

Existing model values are never overwritten. Only closed records
(completed != null) are processed — in-progress stubs get their model from
the live capture path at close.

Usage:
    python3 backfill-model.py --date 2026-10-23 [--dry-run]
    python3 backfill-model.py --since 2026-10-01 [--until 2026-10-24] [--dry-run]
    python3 backfill-model.py --record eval-... [--dry-run]
    python3 backfill-model.py --all [--dry-run]
"""

import argparse
import fcntl
import json
import sys
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MODULE_DIR))

from token_usage import usage_between, latest_turn_model  # noqa: E402
from fully_loaded_cost import find_session_transcript  # noqa: E402

EVAL_RUNS_DIR = MODULE_DIR / "runs"


def _atomic_write(path: Path, data: dict):
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        json.dump(data, f, indent=2)
        f.write("\n")
        fcntl.flock(f, fcntl.LOCK_UN)
    tmp.replace(path)


def derive_top_level_model(record: dict) -> tuple:
    """(model, model_source) for a record missing both, per the module
    docstring's priority order. (None, None) when not derivable."""
    rec_type = record.get("type")
    started = record.get("started")
    completed = record.get("completed")

    if rec_type == "workflow":
        pw_model = (record.get("parent_window") or {}).get("model")
        if pw_model:
            return pw_model, "parent-window-backfill"

    if rec_type == "agent":
        tp = record.get("agent_transcript_path")
        if tp and Path(tp).exists() and started and completed:
            try:
                u = usage_between(tp, started, completed,
                                  exclude_sidechain=False, lenient_fallback=False)
                if u and u.get("model"):
                    return u["model"], "subagent-transcript-backfill"
            except Exception:
                pass
        return None, None

    if rec_type in ("skill", "workflow"):
        session_id = record.get("session_id")
        if session_id:
            try:
                tp = find_session_transcript(session_id)
            except Exception:
                tp = None
            if tp:
                if started and completed:
                    try:
                        u = usage_between(tp, started, completed,
                                          exclude_sidechain=True, lenient_fallback=False)
                        if u and u.get("model"):
                            return u["model"], "session-transcript-window-backfill"
                    except Exception:
                        pass
                try:
                    m = latest_turn_model(tp)
                    if m:
                        return m, "session-transcript-latest-backfill"
                except Exception:
                    pass
    return None, None


def build_agent_model_index(runs_dir: Path) -> dict:
    """agent_id -> model for every record that carries both."""
    idx = {}
    for f in runs_dir.glob("eval-*.json"):
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        aid = d.get("agent_id")
        m = d.get("model")
        if aid and m:
            idx[aid] = m
    return idx


def backfill_record(record: dict, agent_models: dict) -> list:
    """Apply all backfill rules to one record (mutated in place).
    Returns a list of human-readable change descriptions."""
    changes = []
    if not record.get("model"):
        model, source = derive_top_level_model(record)
        if model:
            record["model"] = model
            record["model_source"] = source
            changes.append(f"model={model} ({source})")

    for entry in record.get("subagents") or []:
        if not isinstance(entry, dict) or entry.get("model"):
            continue
        m = agent_models.get(entry.get("agent_id"))
        if m:
            entry["model"] = m
            entry["model_source"] = "child-record-backfill"
            changes.append(f"subagents[{entry.get('agent_id')}].model={m}")

    for step in record.get("steps") or []:
        if not isinstance(step, dict) or step.get("model"):
            continue
        ex = step.get("executed_by_agent_id")
        if ex:
            m = agent_models.get(ex)
            if m:
                step["model"] = m
                step["model_source"] = "child-record-backfill"
                changes.append(f"steps[{step.get('name')}].model={m}")
    return changes


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", help="Records whose started date is YYYY-MM-DD")
    ap.add_argument("--record", help="A single eval record id")
    ap.add_argument("--since", help="started >= this ISO date")
    ap.add_argument("--until", help="started < this ISO date")
    ap.add_argument("--all", action="store_true", help="All closed records in runs/")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--runs-dir", default=str(EVAL_RUNS_DIR))
    args = ap.parse_args()

    runs_dir = Path(args.runs_dir)
    if args.record:
        candidates = [runs_dir / f"{args.record}.json"]
    else:
        if args.all:
            since, until = "", "9999"
        elif args.date:
            since, until = args.date, args.date + "T99"
        elif args.since:
            since, until = args.since, (args.until or "9999")
        else:
            ap.error("pass --date, --since/--until, --record, or --all")
        candidates = []
        for f in sorted(runs_dir.glob("eval-*.json")):
            try:
                d = json.loads(f.read_text())
            except Exception:
                continue
            started = d.get("started") or ""
            if started >= since and started < until:
                candidates.append(f)

    agent_models = build_agent_model_index(runs_dir)

    changed = skipped_open = unchanged = 0
    for f in candidates:
        if not f.exists():
            continue
        try:
            record = json.loads(f.read_text())
        except Exception:
            continue
        if not record.get("completed"):
            skipped_open += 1
            continue
        changes = backfill_record(record, agent_models)
        if not changes:
            unchanged += 1
            continue
        changed += 1
        print(f"{record.get('id')}  {str(record.get('name'))[:28]:<28} "
              f"{'; '.join(changes)}")
        if not args.dry_run:
            _atomic_write(f, record)
    print(f"\n{changed} record(s) backfilled, {unchanged} unchanged "
          f"(model already present or not derivable), {skipped_open} skipped "
          f"(still open){' — DRY RUN, nothing written' if args.dry_run else ''}")


if __name__ == "__main__":
    main()
