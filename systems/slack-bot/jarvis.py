#!/usr/bin/env python3
"""Jarvis Slack Bot — send and receive messages as Jarvis.

Usage:
    python3 jarvis.py send <channel_id> "<message>"
    python3 jarvis.py read <channel_id> [--limit N] [--since TIMESTAMP] [--from-user USER_ID] [--thread THREAD_TS]
    python3 jarvis.py reply <channel_id> <thread_ts> "<message>"
    python3 jarvis.py react <channel_id> <timestamp> <emoji_name>
    python3 jarvis.py threads <channel_id> [--limit N]

Commands:
    send      Post a message to a channel or DM
    read      Read recent messages from a channel (filters available)
    reply     Reply in a thread
    react     Add a reaction to a message
    threads   List recent threads with unread replies
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ── Config ──────────────────────────────────────────────────────────────────

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
BOT_USER_ID = os.environ.get("SLACK_BOT_USER_ID") or _env.get("SLACK_BOT_USER_ID", "")
DAVID_USER_ID = os.environ.get("SLACK_DAVID_USER_ID") or _env.get("SLACK_DAVID_USER_ID", "U0ANHV5UXEW")
DEFAULT_CHANNEL = _env.get("SLACK_DEFAULT_CHANNEL", "C0AN2PQNXBR")  # #jarvis

if not BOT_TOKEN:
    print(json.dumps({"ok": False, "error": "SLACK_BOT_TOKEN not found — add it to config/.env"}))
    sys.exit(1)


# ── API Helper ──────────────────────────────────────────────────────────────

def _slack_api(method, params=None, post_data=None):
    """Call a Slack API method. GET with params or POST with JSON body."""
    url = f"https://slack.com/api/{method}"
    headers = {"Authorization": f"Bearer {BOT_TOKEN}"}

    if post_data is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
        data = json.dumps(post_data).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers)
    else:
        if params:
            qs = "&".join(f"{k}={urllib.request.quote(str(v))}" for k, v in params.items())
            url = f"{url}?{qs}"
        req = urllib.request.Request(url, headers=headers)

    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read().decode())
    except urllib.error.URLError as e:
        return {"ok": False, "error": str(e)}


def _ts_to_human(ts):
    """Convert Slack timestamp to human-readable datetime."""
    try:
        dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, TypeError):
        return ts


# ── Commands ────────────────────────────────────────────────────────────────

def cmd_send(channel, text):
    """Post a message to a channel or DM."""
    result = _slack_api("chat.postMessage", post_data={"channel": channel, "text": text})
    if result.get("ok"):
        print(json.dumps({"ok": True, "channel": result["channel"], "ts": result["ts"]}))
    else:
        print(json.dumps({"ok": False, "error": result.get("error")}))


def cmd_reply(channel, thread_ts, text):
    """Reply in a thread."""
    result = _slack_api("chat.postMessage", post_data={
        "channel": channel,
        "text": text,
        "thread_ts": thread_ts,
    })
    if result.get("ok"):
        print(json.dumps({"ok": True, "channel": result["channel"], "ts": result["ts"], "thread_ts": thread_ts}))
    else:
        print(json.dumps({"ok": False, "error": result.get("error")}))


def cmd_react(channel, timestamp, emoji):
    """Add a reaction to a message."""
    result = _slack_api("reactions.add", post_data={
        "channel": channel,
        "timestamp": timestamp,
        "name": emoji,
    })
    if result.get("ok"):
        print(json.dumps({"ok": True, "emoji": emoji, "ts": timestamp}))
    else:
        print(json.dumps({"ok": False, "error": result.get("error")}))


def cmd_read(channel, limit=20, since=None, from_user=None, thread_ts=None):
    """Read messages from a channel, optionally filtering."""
    if thread_ts:
        # Read thread replies
        params = {"channel": channel, "ts": thread_ts, "limit": limit}
        result = _slack_api("conversations.replies", params=params)
        messages = result.get("messages", [])
    else:
        # Read channel history
        params = {"channel": channel, "limit": limit}
        if since:
            params["oldest"] = since
        result = _slack_api("conversations.history", params=params)
        messages = result.get("messages", [])

    if not result.get("ok"):
        print(json.dumps({"ok": False, "error": result.get("error")}))
        return

    # Resolve user IDs to display names (batch)
    user_ids = set(m.get("user", "") for m in messages if m.get("user"))
    user_map = {}
    for uid in user_ids:
        info = _slack_api("users.info", params={"user": uid})
        if info.get("ok"):
            u = info["user"]
            user_map[uid] = u.get("real_name") or u.get("profile", {}).get("display_name") or u.get("name", uid)
        else:
            user_map[uid] = uid

    # Filter by user if requested
    if from_user:
        # Accept user ID or name substring
        messages = [m for m in messages if
                    m.get("user") == from_user or
                    from_user.lower() in user_map.get(m.get("user", ""), "").lower()]

    # Format output
    formatted = []
    for m in messages:
        uid = m.get("user", "bot")
        sender = user_map.get(uid, m.get("bot_id", "unknown"))
        is_david = uid == DAVID_USER_ID
        is_bot = uid == BOT_USER_ID or "bot_id" in m
        ts = m.get("ts", "")
        text = m.get("text", "")
        thread = m.get("thread_ts", "")
        reply_count = m.get("reply_count", 0)

        formatted.append({
            "ts": ts,
            "time": _ts_to_human(ts),
            "sender": sender,
            "is_david": is_david,
            "is_bot": is_bot,
            "text": text,
            "thread_ts": thread if thread != ts else "",
            "reply_count": reply_count,
        })

    # Reverse so oldest first (channel history comes newest-first)
    if not thread_ts:
        formatted.reverse()

    print(json.dumps({"ok": True, "count": len(formatted), "messages": formatted}, indent=2))


def cmd_threads(channel, limit=10):
    """List recent messages that have thread replies — useful for finding David's responses."""
    params = {"channel": channel, "limit": 50}
    result = _slack_api("conversations.history", params=params)

    if not result.get("ok"):
        print(json.dumps({"ok": False, "error": result.get("error")}))
        return

    # Filter to messages with replies
    threaded = [m for m in result.get("messages", []) if m.get("reply_count", 0) > 0][:limit]

    formatted = []
    for m in threaded:
        formatted.append({
            "ts": m["ts"],
            "time": _ts_to_human(m["ts"]),
            "text": m.get("text", "")[:200],
            "reply_count": m.get("reply_count", 0),
            "latest_reply": _ts_to_human(m.get("latest_reply", "")),
        })

    print(json.dumps({"ok": True, "count": len(formatted), "threads": formatted}, indent=2))


# ── CLI Router ──────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "send":
        channel = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CHANNEL
        text = sys.argv[3] if len(sys.argv) > 3 else "Jarvis online."
        cmd_send(channel, text)

    elif command == "read":
        channel = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CHANNEL
        # Parse optional flags
        limit = 20
        since = None
        from_user = None
        thread_ts = None
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--limit" and i + 1 < len(sys.argv):
                limit = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--since" and i + 1 < len(sys.argv):
                since = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--from-user" and i + 1 < len(sys.argv):
                from_user = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--thread" and i + 1 < len(sys.argv):
                thread_ts = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        cmd_read(channel, limit=limit, since=since, from_user=from_user, thread_ts=thread_ts)

    elif command == "reply":
        if len(sys.argv) < 5:
            print(json.dumps({"ok": False, "error": "Usage: jarvis.py reply <channel> <thread_ts> <message>"}))
            sys.exit(1)
        cmd_reply(sys.argv[2], sys.argv[3], sys.argv[4])

    elif command == "react":
        if len(sys.argv) < 5:
            print(json.dumps({"ok": False, "error": "Usage: jarvis.py react <channel> <timestamp> <emoji>"}))
            sys.exit(1)
        cmd_react(sys.argv[2], sys.argv[3], sys.argv[4])

    elif command == "threads":
        channel = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CHANNEL
        limit = 10
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--limit" and i + 1 < len(sys.argv):
                limit = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        cmd_threads(channel, limit=limit)

    else:
        print(json.dumps({"ok": False, "error": f"Unknown command: {command}. Use send|read|reply|react|threads"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
