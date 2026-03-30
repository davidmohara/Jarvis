#!/usr/bin/env python3
"""
Jarvis Channel Poller

Monitors #jarvis Slack channel for messages from David. Routes each message to
a local headless Claude Code session (which boots Jarvis via CLAUDE.md), then
posts the response back as Jarvis bot.

The headless session runs in the Jarvis root directory so CLAUDE.md is picked
up automatically — Jarvis loads its identity files, agents, skills, etc. exactly
as it would in an interactive session. No separate API key needed.

Session continuity: the Claude Code session_id is persisted in data/state.json
so the conversation resumes across daemon restarts. If the session has expired,
a fresh one is started automatically.

Polling:
  Idle    → every 5 min
  Active  → 30s → 30s → 45s → 60s → 90s → 120s → 180s → 5min (backoff)
  Timeout → 5 min of David silence → back to idle

Auto-compact: sends /compact to the session every COMPACT_EVERY turns to keep
context from filling up, then continues the conversation.

Usage:
  python3 jarvis-channel.py          # run daemon
  python3 jarvis-channel.py --test   # single poll, no Claude calls or Slack posts
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).resolve().parent
JARVIS_ROOT = SCRIPT_DIR.parent.parent       # systems/jarvis-channel → systems → jarvis
CONFIG_ENV  = JARVIS_ROOT / "config" / ".env"
STATE_PATH  = SCRIPT_DIR / "data" / "state.json"
LOG_PATH    = SCRIPT_DIR / "data" / "jarvis-channel.log"
SLACK_BOT   = JARVIS_ROOT / "systems" / "slack-bot" / "post.py"
CLAUDE_BIN  = "/opt/homebrew/bin/claude"     # fallback: also checked on PATH


# ── Constants ─────────────────────────────────────────────────────────────────
# Read from env, with defaults for backward compatibility (David's values)
CHANNEL      = _env.get("JARVIS_CHANNEL_ID", "C0AN2PQNXBR")   # #jarvis
DAVID_ID     = _env.get("JARVIS_USER_ID", "U0ANHV5UXEW")      # Jarvis owner's Slack user ID

DEFAULT_INTERVAL = 300                           # 5 min idle
ACTIVE_INTERVALS = [30, 30, 45, 60, 90, 120, 180, 300]
CONVO_TIMEOUT    = 300                           # seconds of silence → back to idle
COMPACT_EVERY    = 10                            # send /compact every N turns

# ── Env Loading ───────────────────────────────────────────────────────────────
def load_env(path: Path) -> dict:
    env = {}
    if not path.exists():
        return env
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

_env      = load_env(CONFIG_ENV)
BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN") or _env.get("SLACK_BOT_TOKEN", "")

# ── Logging ───────────────────────────────────────────────────────────────────
def log(msg: str):
    ts   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass

# ── State ─────────────────────────────────────────────────────────────────────
def load_state() -> dict:
    if STATE_PATH.exists():
        try:
            with open(STATE_PATH) as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_ts": None, "session_id": None}

def save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


# ── Process Cleanup ───────────────────────────────────────────────────────────
def kill_existing_instances():
    """Kill any stale jarvis-channel.py processes before starting."""
    my_pid = str(os.getpid())
    try:
        result = subprocess.run(
            ["pgrep", "-f", "jarvis-channel.py"],
            capture_output=True, text=True
        )
        pids = [
            p.strip() for p in result.stdout.strip().split("\n")
            if p.strip() and p.strip() != my_pid
        ]
        if not pids:
            return
        log(f"Found {len(pids)} stale process(es) — killing: {', '.join(pids)}")
        for pid in pids:
            subprocess.run(["kill", pid], capture_output=True)
        time.sleep(2)
        result2 = subprocess.run(["pgrep", "-f", "jarvis-channel.py"], capture_output=True, text=True)
        survivors = [
            p.strip() for p in result2.stdout.strip().split("\n")
            if p.strip() and p.strip() != my_pid
        ]
        for pid in survivors:
            log(f"Force-killing PID {pid}")
            subprocess.run(["kill", "-9", pid], capture_output=True)
        log("Stale processes cleared.")
    except Exception as e:
        log(f"Process cleanup warning: {e}")

# ── Claude CLI ────────────────────────────────────────────────────────────────
def find_claude() -> str:
    """Locate the claude binary."""
    # Try PATH first
    result = subprocess.run(["which", "claude"], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    # Fallback to known Homebrew location
    if Path(CLAUDE_BIN).exists():
        return CLAUDE_BIN
    raise RuntimeError("claude binary not found — is Claude Code installed?")


# ── Jarvis Session ────────────────────────────────────────────────────────────
class JarvisSession:
    """
    Wraps a headless Claude Code session running in JARVIS_ROOT.
    CLAUDE.md bootstraps Jarvis on first turn — reads identity files, loads
    agent context, etc. Session is persisted via session_id for resumption.
    """

    def __init__(self, claude_bin: str, session_id: str | None = None):
        self.claude      = claude_bin
        self.session_id  = session_id    # None → fresh session on first send
        self.turn_count  = 0

    def send(self, message: str) -> tuple[str, str]:
        """
        Send a message to Jarvis. Returns (reply_text, session_id).
        Compacts the session every COMPACT_EVERY turns before sending.
        """
        # Proactive compact before sending if we're at the threshold
        if self.session_id and self.turn_count > 0 and self.turn_count % COMPACT_EVERY == 0:
            self._compact()

        reply, sid = self._invoke(message)
        if sid:
            self.session_id = sid
        self.turn_count += 1
        return reply, self.session_id

    def _invoke(self, message: str, timeout: int = 120) -> tuple[str, str | None]:
        """Run claude headlessly. Returns (response_text, session_id)."""
        cmd = [
            self.claude,
            "--print",
            "--output-format", "json",
            "--permission-mode", "bypassPermissions",
        ]
        if self.session_id:
            cmd.extend(["--resume", self.session_id])
        cmd.extend(["-p", message])

        log(f"Invoking claude {'(session: ' + self.session_id[:8] + '...)' if self.session_id else '(new session)'}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(JARVIS_ROOT),    # CLAUDE.md is picked up from here
            )
        except subprocess.TimeoutExpired:
            log(f"ERROR: claude timed out after {timeout}s")
            return "[Jarvis timed out]", self.session_id

        if result.returncode != 0:
            stderr = result.stderr.strip()[:300]
            log(f"claude exited {result.returncode}: {stderr}")
            # Session may have expired — signal caller to start fresh
            if "session" in stderr.lower() or "not found" in stderr.lower():
                self.session_id = None
            return f"[Jarvis error — see log]", None

        try:
            data       = json.loads(result.stdout)
            reply      = data.get("result", "").strip()
            session_id = data.get("session_id")
            num_turns  = data.get("num_turns", "?")
            cost       = data.get("cost_usd", 0)
            log(f"Response received (turns: {num_turns}, cost: ${cost:.4f})")
            return reply, session_id
        except json.JSONDecodeError:
            # Output-format json failed — fall back to raw stdout
            log("WARNING: JSON parse failed — using raw stdout")
            return result.stdout.strip(), None

    def _compact(self):
        """Send /compact to the session to summarize and free context."""
        log(f"Sending /compact at turn {self.turn_count}...")
        reply, sid = self._invoke("/compact", timeout=60)
        if sid:
            self.session_id = sid
        log(f"Compact result: {reply[:80] if reply else '(no output)'}")


# ── Slack API ─────────────────────────────────────────────────────────────────
def slack_api(method: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(
        f"https://slack.com/api/{method}",
        data=data,
        headers={
            "Authorization": f"Bearer {BOT_TOKEN}",
            "Content-Type":  "application/json; charset=utf-8",
        },
    )
    try:
        resp   = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read().decode())
        if not result.get("ok"):
            log(f"Slack API error ({method}): {result.get('error')}")
        return result
    except Exception as e:
        log(f"Slack API exception ({method}): {e}")
        return {"ok": False, "error": str(e)}

def fetch_new_messages(oldest_ts: str | None) -> list[dict]:
    """Fetch top-level #jarvis messages newer than oldest_ts, from David only."""
    payload = {"channel": CHANNEL, "limit": 20}
    if oldest_ts:
        payload["oldest"] = oldest_ts
    result = slack_api("conversations.history", payload)
    if not result.get("ok"):
        return []
    messages = result.get("messages", [])
    david_msgs = [
        m for m in messages
        if m.get("user") == DAVID_ID and not m.get("bot_id") and not m.get("subtype")
    ]
    return sorted(david_msgs, key=lambda m: float(m.get("ts", "0")))

def post_response(text: str) -> None:
    """Post Jarvis response to #jarvis via the bot script."""
    try:
        result = subprocess.run(
            [sys.executable, str(SLACK_BOT), CHANNEL, text],
            capture_output=True, text=True, timeout=15
        )
        log(f"Posted to Slack: {result.stdout.strip()}")
    except Exception as e:
        log(f"ERROR posting to Slack: {e}")

# ── Polling Controller ────────────────────────────────────────────────────────
class PollingController:
    def __init__(self):
        self.last_david_ts  = 0.0
        self.interval_index = 0
        self._active        = False

    @property
    def current_interval(self) -> int:
        if not self._active:
            return DEFAULT_INTERVAL
        return ACTIVE_INTERVALS[min(self.interval_index, len(ACTIVE_INTERVALS) - 1)]

    def on_message(self):
        self.last_david_ts  = time.time()
        self.interval_index = 0
        self._active        = True
        log(f"Active — next poll in {self.current_interval}s")

    def on_empty_poll(self):
        if not self._active:
            return
        if time.time() - self.last_david_ts >= CONVO_TIMEOUT:
            log(f"5min silence — returning to idle ({DEFAULT_INTERVAL}s)")
            self._active        = False
            self.interval_index = 0
        else:
            self.interval_index = min(self.interval_index + 1, len(ACTIVE_INTERVALS) - 1)
            log(f"No new messages — next poll in {self.current_interval}s")


# ── Main Daemon ───────────────────────────────────────────────────────────────
def run_daemon(dry_run: bool = False):
    log("=" * 60)
    log(f"Jarvis Channel Poller starting (PID {os.getpid()})")

    # 1. Kill stale instances
    kill_existing_instances()

    # 2. Validate config
    if not BOT_TOKEN:
        log("ERROR: SLACK_BOT_TOKEN not found — check config/.env")
        sys.exit(1)

    # 3. Locate claude binary
    try:
        claude_bin = find_claude()
        log(f"claude binary: {claude_bin}")
    except RuntimeError as e:
        log(f"ERROR: {e}")
        sys.exit(1)

    # 4. Load persisted state (last Slack ts + Claude session_id)
    state      = load_state()
    last_ts    = state.get("last_ts")
    session_id = state.get("session_id")

    if not last_ts:
        last_ts = f"{time.time():.6f}"
        state["last_ts"] = last_ts
        save_state(state)
        log("First run — cursor set to now (skipping backlog)")
    else:
        log(f"Resuming from Slack ts: {last_ts}")

    if session_id:
        log(f"Resuming Claude session: {session_id[:8]}...")
    else:
        log("No prior session — will start fresh on first message")

    # 5. Init session and poller
    session = JarvisSession(claude_bin, session_id=session_id)
    poller  = PollingController()

    log(f"Idle: {DEFAULT_INTERVAL}s | Active: {ACTIVE_INTERVALS} | Compact every: {COMPACT_EVERY} turns")
    log(f"Watching #jarvis for David ({DAVID_ID})")
    log("=" * 60)

    while True:
        try:
            messages = fetch_new_messages(last_ts)

            if messages:
                for msg in messages:
                    ts   = msg.get("ts", "")
                    text = msg.get("text", "").strip()
                    if not text:
                        continue

                    log(f"David [{ts}]: {text[:80]}{'...' if len(text) > 80 else ''}")

                    if dry_run:
                        log(f"[DRY RUN] Would invoke Jarvis: {text}")
                    else:
                        reply, new_sid = session.send(text)
                        log(f"Jarvis: {reply[:100]}{'...' if len(reply) > 100 else ''}")
                        post_response(reply)
                        # Persist updated session_id
                        state["session_id"] = new_sid
                        save_state(state)

                    last_ts          = ts
                    state["last_ts"] = last_ts
                    save_state(state)
                    poller.on_message()

                if dry_run:
                    log("[DRY RUN] Done — exiting")
                    break

            else:
                poller.on_empty_poll()
                if dry_run:
                    log("[DRY RUN] No new messages — exiting")
                    break

        except KeyboardInterrupt:
            log("Interrupted — shutting down")
            break
        except Exception as e:
            log(f"Poll error: {e}")

        time.sleep(poller.current_interval)


def main():
    dry_run = "--test" in sys.argv
    if dry_run:
        log("Test mode — Slack reads only, no Claude invocations or posts")
    run_daemon(dry_run=dry_run)


if __name__ == "__main__":
    main()
