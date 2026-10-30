#!/usr/bin/env python3
"""Re-attach orphaned subagent records to their turn-level parent and
re-derive per-step attribution.

Background (2026-10-30 boot-token analysis): a turn-level record can lose its
subagents[] links without anyone noticing, because eval-agent-start.py writes
the link from a payload that carries no workflow and backs off whenever it
cannot identify exactly one live turn record. On 2026-10-30 the session-exit
sweep closed the live boot record seven minutes into the run, so the six
executors spawned afterwards (steps 02, 03, 04, 05-08 and the knox check) were
never linked. With no link, eval-agent-stop.py had no parent to roll the
tokens up into and no parent to partition step tokens across: the boot record
read `status: success` with total_tokens_input null while the executors' own
records held every step and every token.

The hooks now do this at stop time (eval-agent-stop.py's orphan re-attach).
This script is the repair path for records written before that fix, and the
audit path afterwards.

For each turn-level workflow record in the window it:
  1. attaches every same-session agent record whose `workflow` matches the
     parent's name and whose start falls inside the parent's [started,
     completed] window, and fills in tokens on entries that carry nulls;
  2. partitions each linked agent'transcript across ONLY the parent steps that
     agent recorded, filling tokens/model/cost/turns_matched and
     executed_by_agent_id (steps the parent already sliced inline are left
     alone);
  3. re-derives total_tokens_input / total_tokens_output / total_cost_usd with
     the same aggregation the closers use (hook_utils.aggregate_record_totals);
  4. computes parent_window / fully_loaded_* when absent, and clears
     monitoring.active on a record whose status is terminal.

Usage:
    python3 backfill-linkage.py --since 2026-10-30            # dry run
    python3 backfill-linkage.py --since 2026-10-30 --apply    # write
    python3 backfill-linkage.py --parent eval-20261030T140251-G668EK --apply
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS_DIR = HERE / "runs"

sys.path.insert(0, str(HERE))

from hook_utils import (  # noqa: E402
    _parse_iso_ts,
    aggregate_record_totals,
    is_turn_level_record,
)
from step_audit import step_key  # noqa: E402

try:
    from token_usage import partition_usage_by_steps  # noqa: E402
except Exception:  # pragma: no cover - defensive
    partition_usage_by_steps = None
try:
    import fully_loaded_cost as _flc  # noqa: E402
except Exception:  # pragma: no cover - defensive
    _flc = None

TERMINAL_STATUSES = ("success", "partial", "failure", "aborted", "no-op")


def load_records(runs_dir: Path) -> dict:
    out = {}
    for path in sorted(runs_dir.glob("eval-*.json")):
        try:
            out[path] = json.loads(path.read_bytes())
        except Exception:
            continue
    return out


def _in_window(child_start, parent_start, parent_end) -> bool:
    child = _parse_iso_ts(child_start)
    if child is None:
        return False
    start = _parse_iso_ts(parent_start)
    end = _parse_iso_ts(parent_end)
    if start is not None and child < start:
        return False
    if end is not None and child > end:
        return False
    return True


def _sub_entry(child: dict) -> dict:
    entry = {
        "agent_id": child.get("agent_id"),
        "agent_type": child.get("subagent_type") or child.get("name"),
        "started": child.get("started"),
        "completed": child.get("completed"),
        "model": child.get("model"),
        "tokens_input": child.get("total_tokens_input"),
        "tokens_output": child.get("total_tokens_output"),
        "cost_usd": child.get("total_cost_usd"),
        "duration_seconds": child.get("duration_seconds"),
    }
    for key in ("harness_tokens", "harness_tool_uses", "token_source", "workflow"):
        if child.get(key) is not None:
            entry[key] = child[key]
    return entry


def repair_parent(parent: dict, records: dict) -> tuple:
    """Attach + partition + total one parent record. Returns (report, changed)."""
    session = parent.get("session_id")
    workflow = parent.get("workflow") or parent.get("name")
    attached, refreshed, partitioned = [], [], []
    changed = False

    subs = parent.setdefault("subagents", [])
    by_id = {s.get("agent_id"): s for s in subs if isinstance(s, dict)}

    children = []
    for _path, rec in records.items():
        if rec.get("type") != "agent" or rec is parent:
            continue
        if rec.get("session_id") != session:
            continue
        if not rec.get("agent_id"):
            continue
        if rec.get("workflow") != workflow:
            continue
        if not _in_window(rec.get("started"), parent.get("started"), parent.get("completed")):
            continue
        children.append(rec)

    for child in children:
        aid = child["agent_id"]
        if aid not in by_id:
            subs.append(_sub_entry(child))
            by_id[aid] = subs[-1]
            attached.append(aid)
            changed = True
        else:
            entry = by_id[aid]
            if entry.get("tokens_input") is None and child.get("total_tokens_input") is not None:
                entry.update(_sub_entry(child))
                refreshed.append(aid)
                changed = True

    # Per-step attribution, same order of authority as eval-agent-stop.py:
    # adopt the child's own step entries first (step-complete.py sliced them
    # against the child's own transcript), then partition the child's
    # transcript across any step it ran without recording an entry. Adoption
    # is what makes this repair work at all for a parent closed by
    # close-eval-record.py: its step windows are synthetic equal slices of the
    # whole run and therefore predate every executor's real start, so a bare
    # partition classifies every step as stale-window and fills nothing.
    steps = [s for s in (parent.get("steps") or []) if isinstance(s, dict)]
    steps_by_key = {step_key(s.get("name")): s for s in steps}
    for child in children:
        own = {step_key(s.get("name")): s for s in (child.get("steps") or [])
               if isinstance(s, dict) and s.get("name")}
        for key, cs in own.items():
            ps = steps_by_key.get(key)
            if ps is None or ps.get("tokens_input") is not None:
                continue
            if cs.get("tokens_input") is None:
                continue
            for field in ("tokens_input", "tokens_output", "cost_usd", "model",
                          "turns_matched", "turns_with_usage", "token_source"):
                if cs.get(field) is not None:
                    ps[field] = cs[field]
            ps["executed_by_agent_id"] = child["agent_id"]
            partitioned.append(f"{ps.get('name')} <- {child['agent_id']}")
            changed = True

    # A child that ran exactly one step owns that step's whole run: attribute
    # its total there when neither the step entry nor the partition produced a
    # number (step-complete's strict window can match nothing — the 2026-10-30
    # step-04 executor recorded 603,606 tokens on the agent and none on the
    # step). Multi-step children with no step entries stay null rather than
    # guessing an order.
    for child in children:
        own = [s for s in (child.get("steps") or []) if isinstance(s, dict) and s.get("name")]
        if len(own) != 1 or child.get("total_tokens_input") is None:
            continue
        ps = steps_by_key.get(step_key(own[0]["name"]))
        if ps is None or ps.get("tokens_input") is not None:
            continue
        ps["tokens_input"] = child["total_tokens_input"]
        ps["tokens_output"] = child.get("total_tokens_output")
        ps["cost_usd"] = child.get("total_cost_usd")
        if child.get("model"):
            ps["model"] = child["model"]
        ps["executed_by_agent_id"] = child["agent_id"]
        ps["token_source"] = "subagent-transcript"
        partitioned.append(f"{ps.get('name')} <- {child['agent_id']} (whole run)")
        changed = True

    if partition_usage_by_steps:
        for child in children:
            tp = child.get("agent_transcript_path")
            if not tp or not Path(tp).exists():
                continue
            own_keys = {step_key(s.get("name")) for s in (child.get("steps") or [])
                        if isinstance(s, dict)}
            if not own_keys:
                continue
            needs = [s for s in steps
                     if step_key(s.get("name")) in own_keys and s.get("tokens_input") is None]
            if not needs:
                continue
            part = partition_usage_by_steps(
                tp, needs, child.get("started"), child.get("completed"))
            for s in steps:
                u = part.get(s.get("name"))
                if u is None or u.get("tokens_input") is None:
                    continue
                s["tokens_input"] = u["tokens_input"]
                s["tokens_output"] = u["tokens_output"]
                s["cost_usd"] = u["cost_usd"]
                if u.get("model"):
                    s["model"] = u["model"]
                s["turns_matched"] = u["turns_matched"]
                s["turns_with_usage"] = u["turns_with_usage"]
                s["executed_by_agent_id"] = child["agent_id"]
                if u.get("token_source"):
                    s["token_source"] = u["token_source"]
                partitioned.append(f"{s.get('name')} <- {child['agent_id']} (partition)")
                changed = True

    if not changed:
        return {"attached": [], "refreshed": [], "partitioned": [], "totals": None}, False

    aggregate_record_totals(parent)
    totals = (parent.get("total_tokens_input"), parent.get("total_tokens_output"),
              parent.get("total_cost_usd"))

    # Fully-loaded cost: a properly finalized record carries it. Only compute
    # when absent (never overwrite a hook-written value) and only for a record
    # with a closed window.
    if _flc is not None and not parent.get("parent_window") and parent.get("completed"):
        try:
            _flc.apply_to_record(parent)
        except Exception as e:  # pragma: no cover - environment dependent
            print(f"  (parent_window not computed: {e})")

    if parent.get("status") in TERMINAL_STATUSES and isinstance(parent.get("monitoring"), dict):
        parent["monitoring"]["active"] = False

    return {"attached": attached, "refreshed": refreshed,
            "partitioned": partitioned, "totals": totals}, True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", default=None,
                    help="only turn-level records whose started date (YYYY-MM-DD) is >= this")
    ap.add_argument("--parent", default=None,
                    help="repair only this eval record id")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--runs-dir", default=str(RUNS_DIR))
    args = ap.parse_args()

    runs_dir = Path(args.runs_dir)
    records = load_records(runs_dir)

    parents = []
    for path, rec in records.items():
        # Turn-level by construction: eval-turn-start.py stamps a monitoring
        # block; monitoring.active may already be false (a properly finalized
        # or repaired record), which is exactly the state this script leaves
        # behind, so it must still be selectable on a re-run.
        if rec.get("type") != "workflow" or not isinstance(rec.get("monitoring"), dict):
            continue
        if args.parent and rec.get("id") != args.parent:
            continue
        if args.since and str(rec.get("started") or "")[:10] < args.since:
            continue
        parents.append((path, rec))
    parents.sort(key=lambda x: x[1].get("started") or "")

    if not parents:
        print("No turn-level records matched.")
        return 0

    for path, rec in parents:
        report, changed = repair_parent(rec, records)
        if not changed:
            continue
        print(f"{rec.get('id')} ('{rec.get('name')}', {rec.get('status')})")
        if report["attached"]:
            print(f"  attached {len(report['attached'])} orphan(s): "
                  f"{', '.join(report['attached'])}")
        if report["refreshed"]:
            print(f"  filled tokens on {len(report['refreshed'])} existing link(s): "
                  f"{', '.join(report['refreshed'])}")
        if report["partitioned"]:
            print(f"  filled {len(report['partitioned'])} step(s) from subagent transcripts")
        tin, tout, tcost = report["totals"]
        print(f"  totals: in={tin} out={tout} cost={tcost}")
        if args.apply:
            with open(path, "w") as f:
                json.dump(rec, f, indent=2)
            print("  written")

    if not args.apply:
        print("\nDry run. Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
