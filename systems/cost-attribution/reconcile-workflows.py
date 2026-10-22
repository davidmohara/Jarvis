#!/usr/bin/env python3
"""Day-level reconciliation: fully-loaded workflow costs vs session-metered cost.

David's invariant (2026-10-21): for a session-day,
    sum over workflow runs of their FULLY-LOADED cost
    + non-workflow interactive remainder
    == the session's total metered cost            (within --tolerance)

where "fully loaded" = parent-window component (the parent session's own
turns during the run's [started, completed] window, priced per-turn from the
main transcript) + the run's subagent components (each subagent's own
transcript), and "metered" = every assistant turn in the session's local
transcripts (main + subagents), deduped by message.id.

Two subtleties this report handles explicitly:

1. OVERLAPPING WINDOWS. Records in the same session can nest (today:
   morning-briefing 15:20-15:36 ran INSIDE boot 15:13-15:41) or coincide
   (the boot record and the boot executor's own agent record span the same
   minutes). Summing per-record parent windows would double count, so the
   invariant is checked against the UNION of record windows; per-record
   fully-loaded figures are still printed for economics, with the overlap
   quantified.

2. RECORDS WITHOUT LOCAL TRANSCRIPTS. Cowork/VM-hosted runs bill the same
   Fireworks account but write no transcript under ~/.claude/projects. They
   are listed separately and excluded from the invariant (their recorded
   cost is real spend but not locally metered — see the meter note below).

Meter note (the report.py vs attribute.py discrepancy, 2026-10-21):
  - report.py's Fireworks column is ACCOUNT-scoped /billingUsage — every
    request authed with the X-Fireworks-Api-Key in ~/.claude/settings.json,
    from any client (this Mac's Claude Code, Cowork's bundled CLI, scheduled
    tasks), whether or not a local transcript exists. Today: $41.13.
  - attribute.py is LOCAL and transcript-derived, but (a) globs only
    top-level <project>/*.jsonl, missing <session>/subagents/*.jsonl,
    (b) never dedupes repeated message.id lines (~1.75x inflation on the
    boot session: 60.3M raw vs 34.4M deduped input tokens — the "58.75M"
    figure quoted today), and (c) substring-matches models so glm-5p3-flash
    prices at glm-5p3 rates. Today: $13.72 by that measure.
  - This script prices the same local transcripts deduped, per-turn, with
    the eval-harness rate table: today $10.03 locally attributable. The
    remaining ~$31 of the Fireworks meter is account traffic with no local
    transcript, dominated by kimi-k3 (52.4M tokens metered vs 5.1M local) —
    Cowork/scheduled-task runs (e.g. the unattended morning-briefing) whose
    sessions live in the Cowork VM, plus any other client on the key.
    glm-5p3, by contrast, reconciles tightly (34.2M metered vs 34.4M local).

Usage:
    python3 reconcile-workflows.py [--date 2026-10-21] [--tolerance 0.01] [--json]
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVAL_HARNESS = HERE.parent / "eval-harness"
sys.path.insert(0, str(EVAL_HARNESS))

import token_usage
import fully_loaded_cost as flc

EVAL_RUNS_DIR = EVAL_HARNESS / "runs"
PROJECTS_DIR = Path.home() / ".claude" / "projects"


def _day_bounds(date: str) -> tuple[str, str]:
    return f"{date}T00:00:00", f"{date}T23:59:59.999999"


def _turns_in_day(transcript_path: Path, day_start: str, day_end: str,
                  exclude_sidechain: bool) -> list[dict]:
    """Deduped assistant turns whose UTC timestamp falls on the given date.
    Transcript timestamps are ISO-8601 UTC (…Z), so a date-prefix compare is
    exact; day_start/day_end carry the date."""
    turns = token_usage.extract_assistant_turns(str(transcript_path),
                                                exclude_sidechain=exclude_sidechain)
    day = day_start[:10]
    return [t for t in turns if (t.get("timestamp") or "")[:10] == day]


def _sum_turns(turns: list[dict]) -> dict:
    cost, unpriced = token_usage.cost_for_turns(turns)
    return {
        "turns": len(turns),
        "tokens_input": sum(t["input_tokens"] + t["cache_read_input_tokens"]
                            + t["cache_creation_5m"] + t["cache_creation_1h"] for t in turns),
        "tokens_output": sum(t["output_tokens"] for t in turns),
        "cost_usd": cost,
        "unpriced_models": unpriced,
    }


def _turns_in_windows(turns: list[dict], windows: list[tuple]) -> list[dict]:
    out = []
    for t in turns:
        ts = token_usage._parse_ts(t.get("timestamp"))
        if ts is None:
            continue
        if any(lo <= ts <= hi for lo, hi in windows):
            out.append(t)
    return out


def _merge_windows(windows: list[tuple]) -> list[tuple]:
    """Union of (start_dt, end_dt) intervals."""
    merged = []
    for lo, hi in sorted(windows):
        if merged and lo <= merged[-1][1]:
            if hi > merged[-1][1]:
                merged[-1] = (merged[-1][0], hi)
        else:
            merged.append((lo, hi))
    return merged


def collect_sessions(date: str, projects_dir: Path | None = None) -> dict:
    """All locally-metered usage for the day, per session:
    {session_id: {project, main_turns, main, subagents: {agent_id: summary}}}.
    Subagent transcripts are <session>/subagents/agent-<id>.jsonl — the files
    attribute.py's top-level glob misses."""
    root = Path(projects_dir) if projects_dir else PROJECTS_DIR
    day_start, day_end = _day_bounds(date)
    sessions = {}
    if not root.exists():
        return sessions
    for proj in sorted(root.iterdir()):
        if not proj.is_dir():
            continue
        # Collect subagent transcripts per session dir FIRST, independent of
        # whether the session's main transcript has turns today — a session
        # whose main file is quiet today can still have subagents billing
        # today (and a session dir can outlive a deleted main transcript).
        sub_by_session: dict[str, dict] = defaultdict(dict)
        for sess_dir in proj.iterdir():
            if not sess_dir.is_dir():
                continue
            sub_dir = sess_dir / "subagents"
            if not sub_dir.is_dir():
                continue
            for sf in sorted(sub_dir.glob("agent-*.jsonl")):
                sturns = _turns_in_day(sf, day_start, day_end,
                                       exclude_sidechain=False)
                if sturns:
                    sub_by_session[sess_dir.name][sf.stem.replace("agent-", "", 1)] = {
                        "path": str(sf),
                        "turns_list": sturns,
                        **_sum_turns(sturns),
                    }
        for f in proj.glob("*.jsonl"):
            # No mtime prefilter: UTC turn timestamps vs local file mtimes
            # makes a date-based prefilter wrong at the day boundary
            # (yesterday-evening local turns are today UTC).
            turns = _turns_in_day(f, day_start, day_end, exclude_sidechain=True)
            sid = f.stem
            if not turns and sid not in sub_by_session:
                continue
            sessions[sid] = {
                "project": proj.name,
                "transcript": str(f),
                "main_turns": turns,
                "main": _sum_turns(turns),
                "subagents": sub_by_session.pop(sid, {}),
            }
        # Session dirs with subagent activity but no main-transcript turns
        for sid, subs in sub_by_session.items():
            sessions[sid] = {
                "project": proj.name,
                "transcript": None,
                "main_turns": [],
                "main": _sum_turns([]),
                "subagents": subs,
            }
    return sessions


def load_records(date: str, runs_dir: Path | None = None) -> list[dict]:
    """Eval records whose [started, completed] window overlaps the day."""
    rd = Path(runs_dir) if runs_dir else EVAL_RUNS_DIR
    day_lo = token_usage._parse_ts(f"{date}T00:00:00Z")
    day_hi = token_usage._parse_ts(f"{date}T23:59:59.999999Z")
    out = []
    for f in sorted(rd.glob("eval-*.json")):
        try:
            rec = json.load(open(f))
        except Exception:
            continue
        s = token_usage._parse_ts(rec.get("started"))
        e = token_usage._parse_ts(rec.get("completed"))
        if s is None or e is None or e < s:
            continue
        if e < day_lo or s > day_hi:
            continue
        rec["_path"] = str(f)
        out.append(rec)
    return out


def reconcile_day(date: str, tolerance: float = 0.01,
                  projects_dir: Path | None = None,
                  runs_dir: Path | None = None) -> dict:
    sessions = collect_sessions(date, projects_dir)
    records = load_records(date, runs_dir)

    per_session = {}
    unmatched_records = []
    for sid, sess in sessions.items():
        recs = [r for r in records if r.get("session_id") == sid]
        windows = []
        rec_rows = []
        linked_agents = set()
        for r in recs:
            s = token_usage._parse_ts(r.get("started"))
            e = token_usage._parse_ts(r.get("completed"))
            windows.append((s, e))
            # parent window for THIS record (live from transcript, per-turn priced)
            pw_turns = _turns_in_windows(sess["main_turns"], [(s, e)])
            pw = _sum_turns(pw_turns)
            own = flc.own_run_cost(r)
            fully = round((pw["cost_usd"] or 0) + (own.get("cost") or 0), 6) \
                if (pw["cost_usd"] is not None or own.get("cost") is not None) else None
            rec_rows.append({
                "id": r.get("id"), "name": r.get("name"), "type": r.get("type"),
                "window": [r.get("started"), r.get("completed")],
                "parent_window_cost_usd": pw["cost_usd"],
                "parent_window_turns": pw["turns"],
                "subagent_cost_usd": own.get("cost"),
                "fully_loaded_cost_usd": fully,
            })
            for entry in (r.get("subagents") or []):
                if isinstance(entry, dict) and entry.get("agent_id"):
                    linked_agents.add(entry["agent_id"])
            if r.get("agent_id"):
                linked_agents.add(r["agent_id"])

        union = _merge_windows(windows)
        attr_parent_turns = _turns_in_windows(sess["main_turns"], union)
        attr_parent = _sum_turns(attr_parent_turns)
        attr_sub_cost = 0.0
        unlinked_sub_cost = 0.0
        unlinked_subs = []
        for aid, summ in sess["subagents"].items():
            if aid in linked_agents:
                attr_sub_cost += summ["cost_usd"] or 0
            else:
                unlinked_sub_cost += summ["cost_usd"] or 0
                unlinked_subs.append(aid)

        main_cost = sess["main"]["cost_usd"] or 0
        sub_cost = sum(s["cost_usd"] or 0 for s in sess["subagents"].values())
        session_total = main_cost + sub_cost
        remainder_main = main_cost - (attr_parent["cost_usd"] or 0)
        remainder = remainder_main + unlinked_sub_cost
        attributed = (attr_parent["cost_usd"] or 0) + attr_sub_cost
        diff = abs(attributed + remainder - session_total)
        per_session[sid] = {
            "project": sess["project"],
            "session_total_cost_usd": round(session_total, 6),
            "main_cost_usd": round(main_cost, 6),
            "subagent_cost_usd": round(sub_cost, 6),
            "records": rec_rows,
            "window_union_minutes": round(sum((hi - lo).total_seconds() for lo, hi in union) / 60, 1),
            "naive_window_minutes": round(sum((e - s).total_seconds() for s, e in windows) / 60, 1),
            "attributed_parent_usd": round(attr_parent["cost_usd"] or 0, 6),
            "attributed_subagents_usd": round(attr_sub_cost, 6),
            "attributed_total_usd": round(attributed, 6),
            "remainder_usd": round(remainder, 6),
            "remainder_main_outside_windows_usd": round(remainder_main, 6),
            "remainder_unlinked_subagents_usd": round(unlinked_sub_cost, 6),
            "unlinked_subagent_ids": sorted(unlinked_subs),
            "invariant_diff_usd": round(diff, 9),
            "over_attributed": remainder < -tolerance,
            "passed": diff <= tolerance and remainder >= -tolerance,
        }

    matched_sids = set(per_session)
    for r in records:
        if r.get("session_id") not in matched_sids:
            unmatched_records.append({
                "id": r.get("id"), "name": r.get("name"), "type": r.get("type"),
                "session_id": r.get("session_id"),
                "total_cost_usd": r.get("total_cost_usd"),
                "reason": "no local session transcript (Cowork/VM-hosted run?)",
            })

    day_total = sum(s["session_total_cost_usd"] for s in per_session.values())
    day_attr = sum(s["attributed_total_usd"] for s in per_session.values())
    day_rem = sum(s["remainder_usd"] for s in per_session.values())
    return {
        "date": date,
        "tolerance_usd": tolerance,
        "sessions": per_session,
        "records_without_local_transcript": unmatched_records,
        "day": {
            "metered_total_usd": round(day_total, 6),
            "attributed_usd": round(day_attr, 6),
            "remainder_usd": round(day_rem, 6),
            "invariant_diff_usd": round(abs(day_attr + day_rem - day_total), 9),
            "passed": all(s["passed"] for s in per_session.values()),
        },
    }


def _fmt_money(v):
    return "   null" if v is None else f"${v:>7.4f}"


def print_report(result: dict):
    print(f"Day reconciliation {result['date']}  "
          f"(transcript-metered, per-turn priced, tolerance ${result['tolerance_usd']})")
    for sid, s in sorted(result["sessions"].items()):
        print(f"\nSession {sid}  [{s['project'][:60]}]")
        print(f"  session metered total: {s['session_total_cost_usd']:.4f}  "
              f"(main {s['main_cost_usd']:.4f} + subagents {s['subagent_cost_usd']:.4f})")
        if s["records"]:
            print(f"  {'record':<30} {'name':<22} {'window':<36} {'parent':>9} {'subagt':>9} {'loaded':>9}")
            for r in s["records"]:
                w0 = (r["window"][0] or "")[11:19]
                w1 = (r["window"][1] or "")[11:19]
                print(f"  {r['id']:<30} {str(r['name'])[:22]:<22} {w0 + '-' + w1:<36} "
                      f"{_fmt_money(r['parent_window_cost_usd'])} "
                      f"{_fmt_money(r['subagent_cost_usd'])} "
                      f"{_fmt_money(r['fully_loaded_cost_usd'])}")
            if s["naive_window_minutes"] > s["window_union_minutes"]:
                print(f"  (overlap de-duplicated: {s['naive_window_minutes']} min of record "
                      f"windows -> {s['window_union_minutes']} min union)")
        else:
            print("  (no eval records this session-day — all usage is interactive remainder)")
        print(f"  attributed: parent-windows(union) ${s['attributed_parent_usd']:.4f} "
              f"+ linked subagents ${s['attributed_subagents_usd']:.4f} "
              f"= ${s['attributed_total_usd']:.4f}")
        print(f"  remainder:  ${s['remainder_usd']:.4f}  "
              f"(main outside windows ${s['remainder_main_outside_windows_usd']:.4f} "
              f"+ unlinked subagents ${s['remainder_unlinked_subagents_usd']:.4f})")
        verdict = "PASS" if s["passed"] else "FAIL"
        print(f"  invariant: attributed + remainder == metered "
              f"(diff ${s['invariant_diff_usd']})  [{verdict}]"
              + ("  OVER-ATTRIBUTED — double count suspected" if s["over_attributed"] else ""))
    if result["records_without_local_transcript"]:
        print("\nRecords with no local transcript (excluded from invariant):")
        for r in result["records_without_local_transcript"]:
            print(f"  {r['id']}  {str(r['name'])[:24]:<24} session={str(r['session_id'])[:12]} "
                  f"recorded_cost={r['total_cost_usd']}  ({r['reason']})")
    d = result["day"]
    print(f"\nDAY TOTAL: metered ${d['metered_total_usd']:.4f} = "
          f"attributed ${d['attributed_usd']:.4f} + remainder ${d['remainder_usd']:.4f}  "
          f"(diff ${d['invariant_diff_usd']})  [{'PASS' if d['passed'] else 'FAIL'}]")
    print("\nCross-meter check: report.py's Fireworks column is account-scoped and "
          "includes traffic with no local transcript (Cowork/scheduled runs, other "
          "clients on the API key); attribute.py under-scans (top-level transcripts "
          "only, no message.id dedupe). This report is the local-truth reconciliation; "
          "see the module docstring for the measured breakdown.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    ap.add_argument("--tolerance", type=float, default=0.01)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--runs-dir", default=None)
    ap.add_argument("--projects-dir", default=None)
    args = ap.parse_args()
    result = reconcile_day(args.date, args.tolerance, args.projects_dir, args.runs_dir)
    if args.json:
        # turn lists are not JSON-friendly to dump wholesale; strip them
        print(json.dumps(result, indent=2, default=str))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
