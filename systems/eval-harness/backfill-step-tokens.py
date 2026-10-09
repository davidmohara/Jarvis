#!/usr/bin/env python3
"""Backfill per-step token data onto historical eval records.

Fills ONLY null token fields on step entries that carry a [started,
completed] window, by slicing the run's transcript with the same
usage_between machinery the live capture uses (strict window matching only:
no lenient fallback for backfill, a retro slice that matches nothing is
skipped, not approximated). Never rewrites captured data, never touches
non-token fields, never touches live (in-progress) records. Every filled
entry is stamped token_source="backfilled-windowed" so live-captured
("windowed") and retro-computed data stay distinguishable in exports and
submissions.

Preceded by backfill-all-eval-costs.py (top-level costs); this is the
per-step layer.

Usage:
  python3 backfill-step-tokens.py            # dry-run (default): report only
  python3 backfill-step-tokens.py --apply    # fill and write
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from token_usage import usage_between  # noqa: E402

RUNS_DIR = HERE / "runs"
PROJECT_DIR = Path.home() / ".claude" / "projects" / "-Users-davidohara-Library-CloudStorage-OneDrive-Improving-IES"


def transcript_candidates(rec):
    """Ordered transcript candidates for a record: its own agent transcript,
    then the project-dir transcript for its session_id, then its subagents'."""
    cands = []
    atp = rec.get("agent_transcript_path")
    if atp:
        cands.append(Path(atp))
    sid = rec.get("session_id")
    if sid and len(str(sid)) >= 30:  # uuid-shaped session ids only
        cands.append(PROJECT_DIR / f"{sid}.jsonl")
    for sub in rec.get("subagents") or []:
        aid = sub.get("agent_id") if isinstance(sub, dict) else None
        if aid:
            cands.append(PROJECT_DIR / f"{aid}.jsonl")
    cands = [c for c in cands if c and c.exists()]
    if cands:
        return cands
    # Fallback for records with an empty or non-uuid session_id (a harness
    # gap): map by time overlap — any project transcript whose turns span
    # the record's [started, completed] window is a plausible owner. Honest
    # limit: with several overlapping sessions this can pick a sibling;
    # strict per-step window matching (no lenient fallback) keeps the data
    # itself honest even if the transcript owner is ambiguous.
    started, completed = rec.get("started"), rec.get("completed")
    if not (started and completed):
        return []
    spans = _transcript_spans()
    if spans is None:
        return []
    return [tp for tp, lo, hi in spans if lo <= completed and started <= hi]


_SPAN_CACHE = None


def _transcript_spans():
    """One pass over the project's transcripts: {path: (min_ts, max_ts)}."""
    global _SPAN_CACHE
    if _SPAN_CACHE is not None:
        return _SPAN_CACHE
    from token_usage import extract_assistant_turns
    spans = []
    for tp in sorted(PROJECT_DIR.glob("*.jsonl")):
        try:
            turns = extract_assistant_turns(str(tp), exclude_sidechain=True)
        except Exception:
            continue
        stamps = [t.get("timestamp") or "" for t in turns]
        stamps = [s for s in stamps if s]
        if stamps:
            spans.append((tp, min(stamps), max(stamps)))
    _SPAN_CACHE = spans
    return spans


def backfill(rec):
    """Fill null per-step token fields on one record. Returns (filled, skipped)
    counts and mutates rec['steps'] in place."""
    filled = 0
    skipped = {"no-window": 0, "already-filled": 0, "no-transcript": 0, "no-strict-match": 0, "not-a-dict": 0}
    cands = transcript_candidates(rec)
    steps = rec.get("steps")
    if not isinstance(steps, list):
        return 0, skipped
    for s in steps:
        if not isinstance(s, dict):
            skipped["not-a-dict"] += 1
            continue
        has_tokens = s.get("tokens_input") is not None or s.get("tokens_output") is not None
        if has_tokens:
            skipped["already-filled"] += 1
            continue
        if not (s.get("started") and s.get("completed")):
            skipped["no-window"] += 1
            continue
        if not cands:
            skipped["no-transcript"] += 1
            continue
        result = None
        for tp in cands:
            r = usage_between(str(tp), s.get("started"), s.get("completed"),
                              exclude_sidechain=True, lenient_fallback=False)
            if r and r.get("turns_matched"):
                result = r
                break
        if not result:
            skipped["no-strict-match"] += 1
            continue
        s["model"] = result["model"]
        s["tokens_input"] = result["tokens_input"]
        s["tokens_output"] = result["tokens_output"]
        s["cost_usd"] = result["cost_usd"]
        s["turns_matched"] = result["turns_matched"]
        s["token_source"] = "backfilled-windowed"
        filled += 1
    return filled, skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write the filled records (default: dry-run)")
    args = ap.parse_args()

    total_filled = 0
    totals = {}
    per_record = []
    for f in sorted(RUNS_DIR.glob("eval-*.json")):
        try:
            rec = json.loads(f.read_text())
        except Exception as e:
            print(f"skip unreadable {f.name}: {e}", file=sys.stderr)
            continue
        if rec.get("status") == "in-progress":
            continue  # live record; never touch
        steps = rec.get("steps")
        if not isinstance(steps, list) or not any(isinstance(s, dict) for s in steps):
            continue
        filled, skipped = backfill(rec)
        for k, v in skipped.items():
            totals[k] = totals.get(k, 0) + v
        total_filled += filled
        if filled or skipped.get("no-strict-match") or skipped.get("no-transcript"):
            wf = rec.get("workflow") or rec.get("name") or "?"
            per_record.append((f.name, wf, filled, skipped))
        if filled and args.apply:
            tmp = f.with_suffix(".tmp")
            tmp.write_text(json.dumps(rec, indent=2))
            tmp.replace(f)

    mode = "APPLIED" if args.apply else "DRY-RUN (use --apply to write)"
    print(f"backfill-step-tokens: {mode}")
    print(f"  step entries filled: {total_filled}")
    print(f"  skips: {totals}")
    for name, wf, filled, skipped in per_record:
        relevant = {k: v for k, v in skipped.items() if v and k in ("no-strict-match", "no-transcript")}
        print(f"  {name} | {wf} | filled {filled} | {relevant or ''}")


if __name__ == "__main__":
    main()
