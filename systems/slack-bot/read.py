#!/usr/bin/env python3
"""Jarvis Slack Bot — read channels and threads via the Slack Web API."""

import argparse
import os
import sys
import json
import time
import urllib.request
import urllib.error
import urllib.parse

# Force stdout to flush immediately — prevents silent output loss via Desktop Commander
sys.stdout.reconfigure(line_buffering=True)

# Read bot token from config/.env (gitignored, never committed)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_ENV = os.path.join(_SCRIPT_DIR, "..", "..", "config", ".env")

def _load_env(path):
    env = {}
    if not os.path.exists(path):
        return env
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

_env = _load_env(_CONFIG_ENV)
BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN") or _env.get("SLACK_BOT_TOKEN")

if not BOT_TOKEN:
    print(json.dumps({"ok": False, "error": "SLACK_BOT_TOKEN not found — add it to config/.env"}))
    sys.exit(1)


def _api_get(endpoint, params):
    url = f"https://slack.com/api/{endpoint}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {BOT_TOKEN}"},
    )
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read().decode())
    except urllib.error.URLError as e:
        return {"ok": False, "error": str(e)}


def read_channel(channel, hours_ago=24, limit=100):
    """Read top-level messages from a channel posted in the last N hours.

    Sanity check: if the API returns ok=True but zero messages, we retry once
    with a 2x wider window before accepting the empty result. This guards against
    the silent-empty failure mode where the Slack API returns ok with no messages
    despite recent activity existing (observed 2026-05-29, err-20260529T200913-OZ7D7N).
    """
    oldest = str(time.time() - (hours_ago * 3600))
    result = _api_get("conversations.history", {
        "channel": channel,
        "oldest": oldest,
        "limit": limit,
        "inclusive": True,
    })
    if not result.get("ok"):
        print(json.dumps({"ok": False, "error": result.get("error")}))
        return
    messages = result.get("messages", [])

    # Sanity check: ok=True but empty — retry with 2x window before trusting it
    if not messages:
        retry_oldest = str(time.time() - (hours_ago * 2 * 3600))
        retry_result = _api_get("conversations.history", {
            "channel": channel,
            "oldest": retry_oldest,
            "limit": limit,
            "inclusive": True,
        })
        if retry_result.get("ok") and retry_result.get("messages"):
            messages = retry_result["messages"]
            # Surface a warning so the caller knows the window was widened
            sys.stderr.write(
                f"[read.py WARNING] Initial {hours_ago}h window returned 0 messages; "
                f"retry with {hours_ago * 2}h window found {len(messages)}. "
                f"Check bot permissions or channel activity timing.\n"
            )
        else:
            # Truly empty or API error on retry — emit warning in payload
            print(json.dumps({
                "ok": True,
                "messages": [],
                "warning": f"Zero messages returned for {hours_ago}h window and {hours_ago * 2}h retry. "
                           "Verify bot is a member of the channel and has conversations:history scope.",
            }))
            return

    # Top-level only — exclude threaded replies
    top_level = [m for m in messages if not m.get("thread_ts") or m.get("thread_ts") == m.get("ts")]
    print(json.dumps({"ok": True, "messages": top_level}))


def read_thread(channel, thread_ts):
    """Read all replies in a thread (excludes the original message)."""
    result = _api_get("conversations.replies", {
        "channel": channel,
        "ts": thread_ts,
        "limit": 100,
    })
    if not result.get("ok"):
        print(json.dumps({"ok": False, "error": result.get("error")}))
        return
    messages = result.get("messages", [])
    replies = messages[1:] if len(messages) > 1 else []
    print(json.dumps({"ok": True, "replies": replies}))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Read Slack messages as the Jarvis bot (JSON to stdout).",
        epilog="Examples:\n"
               "  python3 systems/slack-bot/read.py channel C0AN2PQNXBR 48\n"
               "  python3 systems/slack-bot/read.py thread C0AN2PQNXBR 1729.1234",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    p_ch = sub.add_parser("channel", help="read recent top-level messages")
    p_ch.add_argument("channel_id")
    p_ch.add_argument("hours_ago", nargs="?", type=int, default=24,
                      help="lookback window in hours (default: 24)")
    p_th = sub.add_parser("thread", help="read replies in a thread")
    p_th.add_argument("channel_id")
    p_th.add_argument("thread_ts")
    args = ap.parse_args()

    if args.command == "channel":
        read_channel(args.channel_id, args.hours_ago)

    elif args.command == "thread":
        read_thread(args.channel_id, args.thread_ts)
