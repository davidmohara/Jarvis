#!/usr/bin/env python3
"""Coach: score Claude Code sessions for inefficient, coachable usage patterns.

Reads local transcripts (~/.claude/projects/*/*.jsonl), prices sessions using
attribute.py's rates, and flags six signals:

  1. re-read churn      high uncached-input share: same context re-sent repeatedly
  2. slow start         many small user turns before the first substantive answer
  3. session restart    same topic reopened in a new session within 24h
  4. fork storm         heavy sidechain/subagent volume relative to main work
  5. tool thrash        tool errors followed by immediate retries
  6. low convergence    huge input, tiny output: lots of reading, little shipped

Output: per-session scorecard (worst first) with the evidence behind each flag,
plus aggregate coaching themes. Review the flagged transcripts to coach the
operator on prompt quality and outcome definition.

Usage:
    python3 coach.py [--since 2026-10-01] [--until 2026-10-21] [--top 10] [--csv out.csv]
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import attribute  # noqa: E402  (price, rate_for, PROJECTS_DIR)

MIN_COST_FLAG = 1.0       # don't coach sessions under $1
SUBSTANTIVE_OUTPUT = 500  # output tokens marking a real answer
WORD_RE = re.compile(r"[a-z]{4,}")


def analyze(path):
    s = {
        "cost": 0.0, "in_uncached": 0, "in_cached": 0, "out": 0,
        "user_turns": 0, "first_substantive_at_turn": None,
        "sidechain_msgs": 0, "main_msgs": 0,
        "tool_errors": 0, "tool_calls": 0, "error_retry_pairs": 0,
        "first_user_text": "", "first_ts": None, "last_ts": None,
    }
    turn = 0
    last_was_error = False
    try:
        fh = open(path)
    except Exception:
        return None
    with fh:
        for line in fh:
            try:
                d = json.loads(line)
            except Exception:
                continue
            ts = d.get("timestamp")
            if ts:
                s["first_ts"] = s["first_ts"] or ts
                s["last_ts"] = ts
            t = d.get("type")
            msg = d.get("message") or {}
            if t == "user" and not d.get("isSidechain"):
                content = msg.get("content")
                text = content if isinstance(content, str) else " ".join(
                    c.get("text", "") for c in content if isinstance(c, dict))
                if text and not text.startswith("<"):
                    s["user_turns"] += 1
                    turn += 1
                    if not s["first_user_text"]:
                        s["first_user_text"] = text[:500]
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "tool_result":
                            is_err = c.get("is_error")
                            if is_err:
                                s["tool_errors"] += 1
                                if last_was_error:
                                    s["error_retry_pairs"] += 1
                            last_was_error = bool(is_err)
            elif t == "assistant":
                u = msg.get("usage")
                if u:
                    _, cost, itoks, otoks = attribute.price(msg.get("model", ""), u)
                    s["cost"] += cost
                    key, _ = attribute.rate_for(msg.get("model", ""))
                    _ = key
                    s["in_uncached"] += u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                    s["in_cached"] += u.get("cache_read_input_tokens", 0)
                    s["out"] += u.get("output_tokens", 0)
                    if s["first_substantive_at_turn"] is None and u.get("output_tokens", 0) >= SUBSTANTIVE_OUTPUT:
                        s["first_substantive_at_turn"] = max(turn, 1)
                if d.get("isSidechain"):
                    s["sidechain_msgs"] += 1
                else:
                    s["main_msgs"] += 1
                    for c in msg.get("content") or []:
                        if isinstance(c, dict) and c.get("type") == "tool_use":
                            s["tool_calls"] += 1
    return s


def topic_key(text):
    return frozenset(w for w in WORD_RE.findall(text.lower()) if w not in
                     {"please", "with", "from", "that", "this", "have", "what"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-10-01")
    ap.add_argument("--until", default="2026-10-21")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--csv")
    args = ap.parse_args()

    import datetime
    since_ts = datetime.datetime.fromisoformat(args.since).timestamp()

    sessions = []
    for proj in sorted(attribute.PROJECTS_DIR.iterdir()):
        if not proj.is_dir():
            continue
        for f in proj.glob("*.jsonl"):
            try:
                if f.stat().st_mtime < since_ts:
                    continue
            except Exception:
                continue
            s = analyze(f)
            if not s or s["cost"] < MIN_COST_FLAG:
                continue
            if not s["first_ts"] or s["first_ts"] < args.since or s["first_ts"] >= args.until:
                continue
            s["proj"] = proj.name
            s["sess"] = f.stem
            sessions.append(s)

    # restart detection: same topic, different session, within 24h
    sessions.sort(key=lambda s: s["first_ts"])
    restarts = set()
    for i, a in enumerate(sessions):
        ka = topic_key(a["first_user_text"])
        if len(ka) < 3:
            continue
        for b in sessions[i + 1:]:
            if b["first_ts"][:13] > a["first_ts"][:13] and \
               (datetime.datetime.fromisoformat(b["first_ts"].replace("Z", "+00:00")) -
                datetime.datetime.fromisoformat(a["first_ts"].replace("Z", "+00:00"))).days >= 1:
                break
            kb = topic_key(b["first_user_text"])
            if len(kb) >= 3 and len(ka & kb) / len(ka | kb) > 0.5:
                restarts.add(b["sess"])

    rows = []
    themes = defaultdict(lambda: [0, 0.0])  # signal -> [count, cost]
    for s in sessions:
        flags = []
        total_in = s["in_uncached"] + s["in_cached"]
        if total_in > 5e6 and s["in_uncached"] / total_in > 0.5:
            flags.append(f"re-read churn ({s['in_uncached']/1e6:.0f}M of {total_in/1e6:.0f}M input uncached)")
        if s["first_substantive_at_turn"] and s["first_substantive_at_turn"] >= 5:
            flags.append(f"slow start (first substantive answer at turn {s['first_substantive_at_turn']})")
        if s["sess"] in restarts:
            flags.append("session restart (same topic reopened within 24h)")
        total_msgs = s["sidechain_msgs"] + s["main_msgs"]
        if total_msgs > 20 and s["sidechain_msgs"] / total_msgs > 0.6:
            flags.append(f"fork storm ({s['sidechain_msgs']} sidechain vs {s['main_msgs']} main msgs)")
        if s["tool_calls"] > 5 and s["tool_errors"] / max(s["tool_calls"], 1) > 0.25:
            flags.append(f"tool thrash ({s['tool_errors']}/{s['tool_calls']} tool calls errored)")
        if total_in > 20e6 and s["out"] < total_in / 200:
            flags.append(f"low convergence ({total_in/1e6:.0f}M in, {s['out']/1e3:.0f}K out)")
        for fl in flags:
            themes[fl.split(" (")[0]][0] += 1
            themes[fl.split(" (")[0]][1] += s["cost"]
        rows.append((s, flags))

    rows.sort(key=lambda r: -r[0]["cost"] * (1 + len(r[1])))
    print(f"Sessions analyzed: {len(rows)} (>= ${MIN_COST_FLAG:.0f}, {args.since} .. {args.until})\n")
    print("== Coaching themes (signal -> sessions, est. cost touching it) ==")
    for name, (n, c) in sorted(themes.items(), key=lambda x: -x[1][1]):
        print(f"  {name:<16} {n:>3} sessions  ${c:>7.2f}")

    print(f"\n== Worst sessions (cost x flag count) ==")
    for s, flags in rows[: args.top]:
        print(f"\n  ${s['cost']:>7.2f}  {s['sess'][:8]}  ({s['first_ts'][:10]})  {s['first_user_text'][:70].strip()!r}")
        for fl in flags:
            print(f"      - {fl}")

    if args.csv:
        import csv
        with open(args.csv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["session", "project", "date", "est_cost_usd", "flags", "first_prompt_excerpt"])
            for s, flags in rows:
                w.writerow([s["sess"], s["proj"], s["first_ts"][:10], f"{s['cost']:.2f}",
                            "; ".join(flags), s["first_user_text"][:120].replace("\n", " ")])
        print(f"\nWrote {args.csv}")


if __name__ == "__main__":
    main()
