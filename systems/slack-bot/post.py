#!/usr/bin/env python3
"""Jarvis Slack Bot — posts messages as Jarvis to Slack."""

import argparse
import os
import sys
import json
import urllib.request
import urllib.error

# Force stdout to flush immediately — prevents silent output loss via Desktop Commander
sys.stdout.reconfigure(line_buffering=True)

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

def post_message(channel, text, thread_ts=None):
    payload = {"channel": channel, "text": text}
    if thread_ts:
        payload["thread_ts"] = thread_ts
    data = json.dumps(payload).encode("utf-8")
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
            print(json.dumps({"ok": True, "channel": result["channel"], "ts": result["ts"]}))
        else:
            print(json.dumps({"ok": False, "error": result.get("error")}))
    except urllib.error.URLError as e:
        print(json.dumps({"ok": False, "error": str(e)}))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Post a message to Slack as the Jarvis bot (JSON result to stdout).",
        epilog="Example:\n"
               "  python3 systems/slack-bot/post.py C0AN2PQNXBR \"Daily briefing ready.\"",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("channel", nargs="?", default=DEFAULT_CHANNEL,
                    help="Slack channel ID (default: SLACK_DEFAULT_CHANNEL from config/.env)")
    ap.add_argument("text", nargs="?", default="Jarvis online.",
                    help="message text; literal \\n becomes a newline")
    ap.add_argument("thread_ts", nargs="?", default=None,
                    help="thread timestamp to reply in-thread")
    args = ap.parse_args()
    # Replace literal \n strings with actual newlines
    text = args.text.replace('\\n', '\n')
    post_message(args.channel, text, args.thread_ts)
