#!/usr/bin/env python3
"""Jarvis Slack Bot — read channels and threads via the Slack Web API."""

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
    """Read top-level messages from a channel posted in the last N hours."""
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
    if len(sys.argv) < 3:
        print("Usage:")
        print("  channel  <channel_id> [hours_ago]   — read recent top-level messages")
        print("  thread   <channel_id> <thread_ts>   — read replies in a thread")
        sys.exit(1)

    command = sys.argv[1]

    if command == "channel":
        channel = sys.argv[2]
        hours_ago = int(sys.argv[3]) if len(sys.argv) > 3 else 24
        read_channel(channel, hours_ago)

    elif command == "thread":
        channel = sys.argv[2]
        thread_ts = sys.argv[3] if len(sys.argv) > 3 else None
        if not thread_ts:
            print(json.dumps({"ok": False, "error": "thread_ts required"}))
            sys.exit(1)
        read_thread(channel, thread_ts)

    else:
        print(json.dumps({"ok": False, "error": f"Unknown command '{command}'. Use: channel, thread"}))
        sys.exit(1)
