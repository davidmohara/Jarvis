#!/usr/bin/env python3
"""Search across all Claude Code session transcripts.

Usage:
  python3 scripts/search-sessions.py "search terms"
  python3 scripts/search-sessions.py "search terms" --date 2026-02-10
  python3 scripts/search-sessions.py "search terms" --after 2026-02-09
  python3 scripts/search-sessions.py "search terms" --before 2026-02-12
  python3 scripts/search-sessions.py --list
  python3 scripts/search-sessions.py --session <uuid> "search terms"
  python3 scripts/search-sessions.py --full <uuid>
"""

import json
import os
import sys
import re
import glob
import argparse
from datetime import datetime

SESSION_DIR = os.path.expanduser(
    "~/.claude/projects/-Users-davidohara-develop-my-os/"
)


def parse_messages(filepath):
    """Extract human-readable messages from a JSONL session file."""
    messages = []
    session_date = None

    with open(filepath) as f:
        for line in f:
            try:
                obj = json.loads(line, strict=False)
            except json.JSONDecodeError:
                continue

            ts = obj.get("timestamp")
            if ts and not session_date:
                session_date = ts[:10]

            msg = obj.get("message", {})
            role = msg.get("role", "")
            content = msg.get("content", "")

            if role == "user" and isinstance(content, str):
                if content.startswith(("<local-command", "<command")):
                    continue
                clean = re.sub(
                    r"<system-reminder>.*?</system-reminder>",
                    "",
                    content,
                    flags=re.DOTALL,
                ).strip()
                if clean:
                    messages.append(
                        {"role": "user", "text": clean, "timestamp": ts}
                    )

            elif role == "assistant" and isinstance(content, list):
                texts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        texts.append(block.get("text", ""))
                if texts:
                    combined = "\n".join(texts).strip()
                    if combined:
                        messages.append(
                            {"role": "assistant", "text": combined, "timestamp": ts}
                        )

    return session_date, messages


def search_sessions(query, date=None, after=None, before=None, session_id=None):
    """Search all sessions for matching content. Returns relevant excerpts."""
    files = sorted(glob.glob(os.path.join(SESSION_DIR, "*.jsonl")))
    query_lower = query.lower()
    results = []

    for filepath in files:
        fname = os.path.basename(filepath)
        uid = fname.replace(".jsonl", "")

        if session_id and uid != session_id:
            continue

        session_date, messages = parse_messages(filepath)
        if not session_date or not messages:
            continue

        # Date filters
        if date and session_date != date:
            continue
        if after and session_date < after:
            continue
        if before and session_date > before:
            continue

        # Search for matches
        hits = []
        for i, msg in enumerate(messages):
            if query_lower in msg["text"].lower():
                # Include surrounding context (previous and next message)
                context = []
                if i > 0:
                    prev = messages[i - 1]
                    context.append(
                        f"  [{prev['role'].upper()}]: {prev['text'][:200]}"
                    )
                context.append(
                    f"  >>> [{msg['role'].upper()}]: {msg['text'][:500]}"
                )
                if i + 1 < len(messages):
                    nxt = messages[i + 1]
                    context.append(
                        f"  [{nxt['role'].upper()}]: {nxt['text'][:200]}"
                    )
                hits.append("\n".join(context))

        if hits:
            results.append(
                {
                    "session_id": uid,
                    "date": session_date,
                    "hits": hits,
                    "hit_count": len(hits),
                }
            )

    return results


def list_sessions():
    """List all sessions with dates and message counts."""
    files = sorted(glob.glob(os.path.join(SESSION_DIR, "*.jsonl")))
    sessions = []

    for filepath in files:
        fname = os.path.basename(filepath)
        uid = fname.replace(".jsonl", "")
        session_date, messages = parse_messages(filepath)
        if not session_date or not messages:
            continue

        user_msgs = [m for m in messages if m["role"] == "user"]
        first_msg = user_msgs[0]["text"][:80] if user_msgs else "(empty)"
        sessions.append((session_date, uid, len(user_msgs), first_msg))

    sessions.sort(key=lambda x: (x[0], x[2]))

    print(f"{'Date':<12} {'Messages':>8}  {'First Request':<60}  {'Session ID'}")
    print("-" * 120)
    for date, uid, count, first in sessions:
        print(f"{date:<12} {count:>8}  {first:<60}  {uid[:12]}...")


def full_transcript(session_id):
    """Print the full human-readable transcript of a session."""
    filepath = os.path.join(SESSION_DIR, f"{session_id}.jsonl")
    if not os.path.exists(filepath):
        # Try partial match
        files = glob.glob(os.path.join(SESSION_DIR, f"{session_id}*.jsonl"))
        if files:
            filepath = files[0]
        else:
            print(f"Session not found: {session_id}")
            return

    session_date, messages = parse_messages(filepath)
    print(f"# Session: {session_date} ({os.path.basename(filepath)})\n")

    for msg in messages:
        role = "DAVID" if msg["role"] == "user" else "JARVIS"
        print(f"[{role}]:")
        print(msg["text"][:2000])
        if len(msg["text"]) > 2000:
            print("\n[...truncated...]")
        print("\n---\n")


def main():
    parser = argparse.ArgumentParser(description="Search Claude Code session history")
    parser.add_argument("query", nargs="?", default=None, help="Search terms")
    parser.add_argument("--date", help="Filter to exact date (YYYY-MM-DD)")
    parser.add_argument("--after", help="Filter sessions after date (YYYY-MM-DD)")
    parser.add_argument("--before", help="Filter sessions before date (YYYY-MM-DD)")
    parser.add_argument("--session", help="Search within a specific session UUID")
    parser.add_argument("--list", action="store_true", help="List all sessions")
    parser.add_argument("--full", help="Print full transcript of a session UUID")
    parser.add_argument(
        "--context", type=int, default=500, help="Max chars per match (default 500)"
    )

    args = parser.parse_args()

    if args.list:
        list_sessions()
        return

    if args.full:
        full_transcript(args.full)
        return

    if not args.query:
        parser.print_help()
        return

    results = search_sessions(
        args.query,
        date=args.date,
        after=args.after,
        before=args.before,
        session_id=args.session,
    )

    if not results:
        print(f'No matches for "{args.query}"')
        return

    total_hits = sum(r["hit_count"] for r in results)
    print(f'Found {total_hits} matches across {len(results)} sessions for "{args.query}"\n')

    for r in results:
        print(f"=== {r['date']} (session {r['session_id'][:12]}...) — {r['hit_count']} hits ===")
        for hit in r["hits"][:5]:  # Cap at 5 hits per session
            print(hit)
            print()
        if r["hit_count"] > 5:
            print(f"  ... and {r['hit_count'] - 5} more matches in this session\n")


if __name__ == "__main__":
    main()
