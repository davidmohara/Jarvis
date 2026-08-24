#!/usr/bin/env python3
"""
Shared helper: extract real token usage from a Claude Code session transcript
(JSONL) for a given time window, and price it.

Used by:
  - .claude/hooks/post-tool-use.py   (per-step slice of the main session transcript)
  - .claude/hooks/eval-agent-stop.py (whole-run slice of a subagent's transcript)

Transcript shape (one JSON object per line):
  {"type": "assistant", "isSidechain": false, "timestamp": "...", "message": {
      "id": "msg_...", "model": "claude-sonnet-5",
      "usage": {"input_tokens": N, "output_tokens": N,
                "cache_read_input_tokens": N,
                "cache_creation_input_tokens": N,
                "cache_creation": {"ephemeral_5m_input_tokens": N, "ephemeral_1h_input_tokens": N}}
  }, ...}

A single model turn is written as multiple JSONL lines (one per content block),
all sharing the same message.id and identical usage — dedupe by message.id or
the totals are inflated several-fold.
"""

import json
from pathlib import Path
from datetime import datetime, timezone

MODULE_DIR = Path(__file__).resolve().parent
PRICING_PATH = MODULE_DIR / "model-pricing.json"

# Model IDs seen in transcripts map to the pricing table's short keys.
MODEL_ALIASES = {
    "claude-sonnet-5": "sonnet",
    "claude-sonnet-4-6": "sonnet",
    "claude-sonnet-4-5": "sonnet",
    "claude-haiku-4-5": "haiku",
    "claude-haiku-4-5-20251001": "haiku",
}


def _load_pricing() -> dict:
    try:
        with open(PRICING_PATH, "r") as f:
            return json.load(f).get("models", {})
    except Exception:
        return {}


def _parse_ts(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except Exception:
        return None


def extract_assistant_turns(transcript_path: str, exclude_sidechain: bool = True) -> list[dict]:
    """Read a transcript JSONL and return one entry per unique assistant turn
    (deduped by message.id), each with timestamp/model/usage components."""
    turns = {}
    order = []
    try:
        with open(transcript_path, "r", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if obj.get("type") != "assistant":
                    continue
                if exclude_sidechain and obj.get("isSidechain"):
                    continue
                msg = obj.get("message", {})
                mid = msg.get("id")
                if not mid or mid in turns:
                    continue
                usage = msg.get("usage", {}) or {}
                cache_creation = usage.get("cache_creation", {}) or {}
                entry = {
                    "message_id": mid,
                    "timestamp": obj.get("timestamp"),
                    "model": msg.get("model"),
                    "input_tokens": usage.get("input_tokens", 0) or 0,
                    "output_tokens": usage.get("output_tokens", 0) or 0,
                    "cache_read_input_tokens": usage.get("cache_read_input_tokens", 0) or 0,
                    "cache_creation_5m": cache_creation.get("ephemeral_5m_input_tokens", 0) or 0,
                    "cache_creation_1h": cache_creation.get("ephemeral_1h_input_tokens", 0) or 0,
                }
                turns[mid] = entry
                order.append(mid)
    except Exception:
        return []
    return [turns[mid] for mid in order]


def usage_between(transcript_path: str, start_iso: str | None, end_iso: str | None,
                   exclude_sidechain: bool = True, lenient_fallback: bool = True) -> dict | None:
    """Aggregate real token usage for assistant turns whose timestamp falls in
    [start_iso, end_iso]. Returns None if the transcript can't be read or no
    turns fall in the window. Cost uses documented cache multipliers (cache
    read ~0.1x input rate, cache write 1.25x/2x for 5m/1h TTL) rather than a
    flat rate, since a real turn is mostly cache reads/writes, not fresh input.

    If lenient_fallback is True and strict time matching finds zero matches,
    returns all turns as a fallback (timestamps may not overlap step time)."""
    if not transcript_path:
        return None

    tp = Path(transcript_path)
    if not tp.exists():
        # Try to find a similarly-named transcript in the same session directory
        # (handles cases where subagent transcript path doesn't exist)
        parent = tp.parent
        if parent.exists():
            candidates = list(parent.glob("*.jsonl"))
            if candidates:
                # Use the most recent one if multiple exist
                transcript_path = str(max(candidates, key=lambda x: x.stat().st_mtime))
                tp = Path(transcript_path)
            else:
                return None
        else:
            return None

    start_dt = _parse_ts(start_iso)
    end_dt = _parse_ts(end_iso)

    turns = extract_assistant_turns(transcript_path, exclude_sidechain=exclude_sidechain)
    if not turns:
        return None

    matched = []
    for t in turns:
        ts = _parse_ts(t["timestamp"])
        if ts is None:
            continue
        if start_dt and ts < start_dt:
            continue
        if end_dt and ts > end_dt:
            continue
        matched.append(t)

    # Lenient fallback: if strict time matching found nothing, use all turns
    if not matched and lenient_fallback:
        matched = turns

    tokens_input = sum(t["input_tokens"] + t["cache_read_input_tokens"] + t["cache_creation_5m"] + t["cache_creation_1h"] for t in matched)
    tokens_output = sum(t["output_tokens"] for t in matched)

    # Dominant model across matched turns (usually just one)
    model_counts: dict[str, int] = {}
    for t in matched:
        m = t.get("model")
        if m:
            model_counts[m] = model_counts.get(m, 0) + 1
    model_raw = max(model_counts, key=model_counts.get) if model_counts else None
    model_short = MODEL_ALIASES.get(model_raw, model_raw)

    cost_usd = _compute_accurate_cost(model_short, matched)
    used_lenient_fallback = len(matched) == len(turns)

    return {
        "model": model_short,
        "model_raw": model_raw,
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "cost_usd": cost_usd,
        "turns_matched": len(matched),
        "used_lenient_fallback": used_lenient_fallback,
    }


def _compute_accurate_cost(model_short: str | None, turns: list[dict]) -> float | None:
    rates = _load_pricing().get((model_short or "").lower()) if model_short else None
    if not rates:
        return None
    input_rate = rates["input_per_mtok"] / 1_000_000
    output_rate = rates["output_per_mtok"] / 1_000_000

    cost = 0.0
    for t in turns:
        cost += t["input_tokens"] * input_rate
        cost += t["output_tokens"] * output_rate
        cost += t["cache_read_input_tokens"] * input_rate * 0.1
        cost += t["cache_creation_5m"] * input_rate * 1.25
        cost += t["cache_creation_1h"] * input_rate * 2.0
    return round(cost, 6)
