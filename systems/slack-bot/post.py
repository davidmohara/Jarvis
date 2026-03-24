#!/usr/bin/env python3
"""Jarvis Slack Bot — posts messages as Jarvis to Slack."""

import os
import sys
import json
import urllib.request
import urllib.error

# Read bot token from config/.env (gitignored, never committed)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_CONFIG_ENV = os.path.join(_SCRIPT_DIR, "..", "..", "config", ".env")

def _load_env(path):
    """Load key=value pairs from a .env file into a dict."""
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
DEFAULT_CHANNEL = _env.get("SLACK_DEFAULT_CHANNEL", "C0AN2PQNXBR")  # #jarvis

if not BOT_TOKEN:
    print(json.dumps({"ok": False, "error": "SLACK_BOT_TOKEN not found — add it to config/.env"}))
    sys.exit(1)

def post_message(channel, text):
    data = json.dumps({"channel": channel, "text": text}).encode("utf-8")
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage",
        data=data,
        headers={
            "Authorization": f"Bearer {BOT_TOKEN}",
            "Content-Type": "application/json; charset=utf-8",
        },
    )
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read().decode())
        if result.get("ok"):
            ts = result["ts"]
            ch = result["channel"]
            print(json.dumps({"ok": True, "channel": ch, "ts": ts}))
        else:
            print(json.dumps({"ok": False, "error": result.get("error")}))
    except urllib.error.URLError as e:
        print(json.dumps({"ok": False, "error": str(e)}))

if __name__ == "__main__":
    channel = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CHANNEL
    text = sys.argv[2] if len(sys.argv) > 2 else "Jarvis online."
    post_message(channel, text)
