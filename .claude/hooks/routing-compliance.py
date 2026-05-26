#!/usr/bin/env python3
"""
Stop Hook: Routing Compliance Enforcement
Fires after every Master turn. Blocks the response if Master handled
domain-specialist work directly instead of spawning a subagent via the Agent tool.

Problem it solves: Master's routing rules require any domain-specialist request
to be routed via Agent tool spawn. When Master answers directly, the entire
hook chain is bypassed (no SubagentStart/SubagentStop, no eval stub, no working
memory written). This hook catches and blocks those violations.

Exit codes:
  0 = allow (pass through)
  2 = block (re-feed turn to model with reason)
"""

import json
import sys
from pathlib import Path
from datetime import datetime

LOG_FILE = Path("/tmp/ies-hook-errors.log")


# ---------------------------------------------------------------------------
# Domain routing table — derived from agents/routing.md
# Each entry: (agent_name, agent_title, signals)
# Signals are lowercased substrings. All matching is case-insensitive.
# Only include signals that are unambiguous domain indicators — not general words.
# ---------------------------------------------------------------------------
DOMAIN_AGENTS = [
    (
        "Galen",
        "Longevity Advisor",
        [
            "whoop", "bloodwork", "labs", "lab results", "recovery score",
            "health review", "health report", "health status", "health protocol",
            "peptide", "supplement stack", "supplement protocol", "body comp",
            "body composition", "doctor visit", "biometrics", "hrv", "strain score",
            "sleep performance", "health check",
        ],
    ),
    (
        "Chase",
        "Closer",
        [
            "pipeline review", "pipeline report", "pipeline health",
            "deal review", "deal status", "opportunity review",
            "sales forecast", "revenue forecast", "crm update",
            "account review", "post-mortem", "deal post mortem",
            "client meeting prep", "lost deal", "win/loss",
        ],
    ),
    (
        "Quinn",
        "Strategist",
        [
            "quarterly rocks", "q1 rocks", "q2 rocks", "q3 rocks", "q4 rocks",
            "okr review", "strategic plan", "strategy review",
            "goal review", "initiative alignment", "roadmap review",
            "quarterly planning", "annual planning",
        ],
    ),
    (
        "Harper",
        "Storyteller",
        [
            "draft email", "write email", "draft a message", "draft message",
            "build deck", "build a deck", "build presentation",
            "write a blog", "blog post", "talking points",
            "podcast prep", "speech draft", "write the content",
            "draft the content", "draft the announcement",
        ],
    ),
    (
        "Shep",
        "Coach",
        [
            "1:1 prep", "1-on-1 prep", "delegation review", "direct report review",
            "team review", "coaching session", "overdue delegations",
            "people review", "performance review", "development plan",
        ],
    ),
    (
        "Rigby",
        "System Operator",
        [
            "new workflow", "new skill", "new agent", "new script",
            "create capability", "build system", "system change",
            "grade evals", "eval analysis", "eval dashboard", "eval trends",
            "deploy workflow", "deploy skill", "install connector",
            "build a hook", "new hook", "create a hook",
        ],
    ),
    (
        "Knox",
        "Knowledge Manager",
        [
            "search my notes", "search the vault", "what do i know about",
            "ingest transcript", "plaud ingest", "remarkable ingest",
            "vault search", "knowledge search", "find in my notes",
        ],
    ),
    (
        "Sterling",
        "Concierge",
        [
            "book a flight", "book flight", "hotel reservation", "dinner reservation",
            "make a reservation", "wine recommendation", "buy a gift",
            "personal errand", "travel itinerary", "flight options",
        ],
    ),
    (
        "Chief",
        "Chief of Staff",
        [
            "morning briefing", "run the briefing", "daily briefing",
            "shutdown briefing", "end of day briefing", "calendar prep",
            "inbox review", "triage my inbox", "what's on my calendar",
            "prepare my day",
        ],
    ),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(level: str, msg: str) -> None:
    """Append a line to the shared Jarvis hooks log."""
    try:
        ts = datetime.now().isoformat(timespec="seconds")
        with open(LOG_FILE, "a") as f:
            f.write(f"[{ts}] [routing-compliance] [{level}] {msg}\n")
    except Exception:
        pass


def read_stdin() -> dict:
    try:
        return json.load(sys.stdin)
    except Exception as e:
        log("ERROR", f"Failed to parse stdin JSON: {e}")
        return {}


def read_transcript_lines(transcript_path: str) -> list[dict]:
    """Read the transcript JSONL and return all parsed lines."""
    lines = []
    try:
        p = Path(transcript_path)
        if not p.exists():
            log("WARN", f"Transcript not found: {transcript_path}")
            return lines
        for raw in p.read_text(errors="replace").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                lines.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
    except Exception as e:
        log("ERROR", f"Failed to read transcript {transcript_path}: {e}")
    return lines

def get_current_turn_messages(lines: list[dict]) -> tuple[str, bool]:
    """
    Extract the last human message text and whether an Agent tool call
    appeared in the assistant's most recent turn.

    Returns: (last_human_text, agent_tool_used)

    Strategy: Walk lines in reverse. Collect the last assistant turn's
    tool uses, then find the human message immediately preceding it.
    """
    last_human_text = ""
    agent_tool_used = False

    # Find the last human message
    for line in reversed(lines):
        msg = line.get("message", {})
        role = msg.get("role", "")
        content = msg.get("content", "")

        if role == "human" or role == "user":
            if isinstance(content, str):
                last_human_text = content
                break
            elif isinstance(content, list):
                # Content blocks — extract text parts
                parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        parts.append(block.get("text", ""))
                last_human_text = " ".join(parts)
                break

    # Scan the entire last assistant response for Agent tool calls.
    # Claude transcripts record tool uses as assistant content blocks
    # with type="tool_use" and name="Agent" (or "Task" in some versions).
    # We look at all lines since the last human turn.
    in_assistant_turn = False
    last_human_idx = -1

    for i, line in enumerate(lines):
        msg = line.get("message", {})
        role = msg.get("role", "")
        if role in ("human", "user"):
            last_human_idx = i

    # Check all lines after the last human message for Agent tool calls
    if last_human_idx >= 0:
        for line in lines[last_human_idx + 1:]:
            msg = line.get("message", {})
            role = msg.get("role", "")
            content = msg.get("content", "")

            if role == "assistant":
                in_assistant_turn = True
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict):
                            block_type = block.get("type", "")
                            tool_name = block.get("name", "")
                            # Agent tool shows up as type=tool_use, name=Agent
                            # Also check for "Task" as an alias used by some versions
                            if block_type == "tool_use" and tool_name in ("Agent", "Task"):
                                agent_tool_used = True
                                log("INFO", f"Agent tool call detected: {tool_name}")

            # Also catch tool use records at the top level (some transcript formats)
            tool_uses = line.get("tool_uses", [])
            if isinstance(tool_uses, list):
                for tu in tool_uses:
                    if isinstance(tu, dict) and tu.get("name") in ("Agent", "Task"):
                        agent_tool_used = True
                        log("INFO", "Agent tool call detected via top-level tool_uses")

    return last_human_text, agent_tool_used


def match_domain(human_text: str) -> tuple[str, str] | None:
    """
    Return (agent_name, agent_title) if the human message clearly matches
    a domain-specialist's trigger signals. Returns None if no match or ambiguous.
    """
    normalized = human_text.lower()

    for agent_name, agent_title, signals in DOMAIN_AGENTS:
        for signal in signals:
            if signal in normalized:
                log("INFO", f"Domain match: '{signal}' → {agent_name} ({agent_title})")
                return agent_name, agent_title

    return None


def block_response(reason: str) -> None:
    """Write block decision to stdout and exit with code 2."""
    output = json.dumps({"decision": "block", "reason": reason})
    sys.stdout.write(output)
    sys.stdout.flush()
    log("WARN", f"BLOCKED: {reason}")
    sys.exit(2)


def allow_response(reason: str = "no violation") -> None:
    """Exit 0 to allow the response through."""
    log("INFO", f"ALLOWED: {reason}")
    sys.exit(0)


def main() -> None:
    payload = read_stdin()

    # Guard: if stop_hook_active, we're already in a re-feed loop — pass through
    if payload.get("stop_hook_active", False):
        allow_response("stop_hook_active=true, skipping to prevent loop")

    session_id = payload.get("session_id", "unknown")
    transcript_path = payload.get("transcript_path", "")

    log("INFO", f"Routing compliance check — session={session_id}")

    if not transcript_path:
        log("WARN", "No transcript_path in payload — cannot inspect turn, allowing")
        allow_response("no transcript_path")

    # Read and parse the transcript
    lines = read_transcript_lines(transcript_path)
    if not lines:
        allow_response("empty or unreadable transcript")

    # Extract the last human message and whether Agent was called this turn
    human_text, agent_tool_used = get_current_turn_messages(lines)

    if not human_text:
        allow_response("no human message found in transcript")

    log("INFO", f"Last human message (first 120 chars): {human_text[:120]!r}")
    log("INFO", f"Agent tool used this turn: {agent_tool_used}")

    # If Master already spawned a subagent, routing was correct — allow
    if agent_tool_used:
        allow_response("Agent tool was called — routing compliant")

    # Check whether the message targets a specialist domain
    match = match_domain(human_text)
    if match is None:
        allow_response("no domain-specialist match detected")

    agent_name, agent_title = match

    # Violation: domain-specialist request handled directly without Agent spawn
    reason = (
        f"ROUTING VIOLATION: This request belongs to {agent_name} ({agent_title}) "
        f"and must be routed via the Agent tool — not handled directly by Master. "
        f"You answered the prompt directly instead of spawning {agent_name} as a subagent. "
        f"Read agents/routing.md and agents/master.md, then re-respond by spawning "
        f"{agent_name} using the Agent tool and passing the full original request plus "
        f"relevant context. Do not answer the domain question yourself."
    )
    block_response(reason)


if __name__ == "__main__":
    main()
