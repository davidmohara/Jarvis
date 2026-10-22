#!/usr/bin/env python3
"""
Shared helper: extract real token usage from a Claude Code session transcript
(JSONL) for a given time window, and price it.

Used by:
  - .claude/hooks/post-tool-use.py   (per-step slice of the main session transcript)
  - .claude/hooks/eval-agent-stop.py (whole-run slice of a subagent's transcript)
  - systems/eval-harness/fully_loaded_cost.py (parent_window_usage: the parent
    session's own turns inside a workflow run's window — the fully-loaded
    cost component David required after the 2026-10-21 boot record showed
    $0.68 of subagent work against a ~$13 parent-session day)

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
import re
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
    # Opus tier (added 2026-10-16, Stage 5 finding #4). These map to the
    # "opus" key now present in model-pricing.json. Only the Opus 4.6/4.7/4.8/5
    # first-party rate ($5/$25 per MTok) is modelled; claude-opus-5-5 has a
    # different rate ($4/$20) and is deliberately left unmapped so it prices
    # null rather than wrong if it ever appears.
    "claude-opus-5": "opus",
    "claude-opus-4-8": "opus",
    "claude-opus-4-7": "opus",
    "claude-opus-4-6": "opus",
    # Fireworks provider ids carry dated suffixes the pricing table omits
    # (deepseek-v4p1-flash-1017 left the 2026-10-21 morning-briefing subagent
    # unpriced). Map the dated variants onto the table's keys.
    "accounts/fireworks/models/deepseek-v4p1-flash-1017": "accounts/fireworks/models/deepseek-v4p1-flash",
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
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except Exception:
        return None
    # Assume UTC for naive stamps (historical step frontmatter carries both
    # forms); mixed naive/aware stamps otherwise crash on comparison.
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


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

    # Lenient fallback: if strict time matching found nothing, use all turns.
    # Track it explicitly -- the old "len(matched) == len(turns)" test also
    # fired when a strict window happened to contain every turn, mislabeling
    # a real per-step slice as a fallback and corrupting token_source.
    used_lenient_fallback = False
    if not matched and lenient_fallback:
        matched = turns
        used_lenient_fallback = True

    # Honor the documented contract: no matched turns (strict path, or an
    # empty transcript) returns None rather than a zero-sum dict. A zero dict
    # is indistinguishable from a genuine zero-usage match and let the
    # backfill write fabricated zeros into records (caught by the coverage
    # scan, 2026-10-09).
    if not matched:
        return None

    tokens_input = sum(t["input_tokens"] + t["cache_read_input_tokens"] + t["cache_creation_5m"] + t["cache_creation_1h"] for t in matched)
    tokens_output = sum(t["output_tokens"] for t in matched)
    # Thinking-only assistant entries carry all-zero usage; counting them as
    # "turns matched" made a window look populated when it held no billable
    # work (boot step-01.2 on 2026-10-21: 5 "turns", 0 tokens).
    turns_with_usage = sum(
        1 for t in matched
        if (t["input_tokens"] or t["output_tokens"] or t["cache_read_input_tokens"]
            or t["cache_creation_5m"] or t["cache_creation_1h"])
    )

    # Dominant model across matched turns (usually just one)
    model_counts: dict[str, int] = {}
    for t in matched:
        m = t.get("model")
        if m:
            model_counts[m] = model_counts.get(m, 0) + 1
    model_raw = max(model_counts, key=model_counts.get) if model_counts else None
    model_short = MODEL_ALIASES.get(model_raw, model_raw)

    cost_usd = _compute_accurate_cost(model_short, matched)

    return {
        "model": model_short,
        "model_raw": model_raw,
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "cost_usd": cost_usd,
        "turns_matched": len(matched),
        "turns_with_usage": turns_with_usage,
        "used_lenient_fallback": used_lenient_fallback,
    }


def partition_usage_by_steps(transcript_path: str, steps: list[dict],
                             run_start: str | None, run_end: str | None,
                             exclude_sidechain: bool = False) -> dict[str, dict]:
    """Attribute EVERY billable turn of a single agent's transcript to exactly
    one step, using the steps' started-at ordering as the partition.

    Why this exists: step frontmatter started-at/completed-at are written by
    the executing model and are provably unreliable — stale from prior runs
    (status: complete persists across runs), round-numbered projections
    (2026-10-21 boot steps 06-08 carry 15:47-15:50 windows for a subagent
    that ended at 15:41:15), and mutually overlapping (steps 01.5 and 02 both
    claim 15:18:30 starts). Independent per-step window queries against such
    data either match nothing (the old lenient_fallback then stamped the
    WHOLE transcript onto each step — six plaud-ingest steps each "cost"
    1,654,697 tokens on 2026-10-21) or attribute concurrent unrelated turns.

    The partition instead trusts only the ORDER of the steps and the real
    transcript: boundaries are the sorted started-at values clamped to
    [run_start, run_end]; turns before the first step's start are attributed
    to the first step (spawn/setup work), turns after the last step's start
    to the last step. Integrity invariant: sum over steps of tokens_input ==
    whole-transcript tokens_input (callers can and should verify).

    `steps` entries need {name, started, completed} (None tolerated).
    Returns {step_name: usage-dict | None}. A step with unusable timestamps
    (no started-at) maps to None — honest null, not a guess.
    """
    if not transcript_path or not Path(transcript_path).exists():
        return {}
    turns = extract_assistant_turns(transcript_path, exclude_sidechain=exclude_sidechain)
    if not turns:
        return {}

    run_start_dt = _parse_ts(run_start)
    run_end_dt = _parse_ts(run_end)

    timed = []   # (start_dt, name)
    untimed = [] # names with no usable started-at
    stale = []   # names whose started-at predates this run (frontmatter never rewritten)
    for s in steps:
        name = s.get("name")
        sd = _parse_ts(s.get("started"))
        if not name:
            continue
        if sd is None:
            untimed.append(name)
        elif run_start_dt is not None and sd < run_start_dt:
            # Stale frontmatter from a prior run (status: complete persists).
            # Admitting it to the partition would hand it every turn from
            # run_start up to the next step's claimed start — the same class
            # of fabrication as the retired lenient fallback, quieter.
            stale.append(name)
        else:
            timed.append((sd, name))
    timed.sort(key=lambda x: x[0])

    result: dict[str, dict | None] = {name: None for name in untimed}
    for name in stale:
        result[name] = {
            "model": None, "model_raw": None,
            "tokens_input": None, "tokens_output": None, "cost_usd": None,
            "turns_matched": 0, "turns_with_usage": 0,
            "token_source": "stale-window",
        }
    if not timed:
        return result

    # Partition boundaries: [run_start, start_1) -> step_1, ..., [start_n, run_end] -> step_n
    bounds = []
    first_start = timed[0][0]
    bounds.append(run_start_dt if (run_start_dt and run_start_dt < first_start) else first_start)
    for sd, _ in timed[1:]:
        # Clamp pathological ordering inversions (a later step claiming an
        # earlier start than its predecessor) to the running boundary so
        # windows never go negative.
        bounds.append(max(sd, bounds[-1]))
    bounds.append(run_end_dt if (run_end_dt and run_end_dt > bounds[-1]) else None)
    # bounds has len(timed)+1 entries: window for step i is [bounds[i], bounds[i+1])
    # with bounds[-1] == None meaning "no upper bound".

    per_step_turns: dict[str, list] = {name: [] for _, name in timed}
    idx = 0
    for t in turns:
        ts = _parse_ts(t["timestamp"])
        if ts is None:
            continue
        while idx < len(timed) - 1 and bounds[idx + 1] is not None and ts >= bounds[idx + 1]:
            idx += 1
        if bounds[idx] is not None and ts < bounds[idx]:
            continue  # before this partition's start (only possible for pre-run turns)
        per_step_turns[timed[idx][1]].append(t)

    for _, name in timed:
        matched = per_step_turns[name]
        tokens_input = sum(t["input_tokens"] + t["cache_read_input_tokens"] + t["cache_creation_5m"] + t["cache_creation_1h"] for t in matched)
        tokens_output = sum(t["output_tokens"] for t in matched)
        turns_with_usage = sum(
            1 for t in matched
            if (t["input_tokens"] or t["output_tokens"] or t["cache_read_input_tokens"]
                or t["cache_creation_5m"] or t["cache_creation_1h"])
        )
        model_counts: dict[str, int] = {}
        for t in matched:
            m = t.get("model")
            if m:
                model_counts[m] = model_counts.get(m, 0) + 1
        model_raw = max(model_counts, key=model_counts.get) if model_counts else None
        model_short = MODEL_ALIASES.get(model_raw, model_raw)
        result[name] = {
            "model": model_short,
            "model_raw": model_raw,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            "cost_usd": _compute_accurate_cost(model_short, matched),
            "turns_matched": len(matched),
            "turns_with_usage": turns_with_usage,
            "token_source": "windowed-partition",
        }
    return result


_TASK_NOTIFICATION_RE = re.compile(
    r"<task-notification>.*?</task-notification>", re.DOTALL)


def extract_task_notifications(main_transcript_path: str) -> list[dict]:
    """Parse <task-notification> blocks from the MAIN session transcript.

    When a background/async subagent completes, the harness enqueues a
    task-notification into the main session transcript whose <usage> block
    carries the harness's own authoritative totals for that subagent run:
        <task-id>a548027b586ba0f14</task-id>
        <status>completed</status>
        <usage><subagent_tokens>143307</subagent_tokens>
              <tool_uses>77</tool_uses><duration_ms>1621653</duration_ms></usage>

    This is the same number the harness reports to the user at task
    completion — the figure David quoted for the 2026-10-21 boot executor —
    and it survives even when the subagent's own transcript is missing,
    unflushed, or never linked to an eval record (five "No eval record found
    for agent" SubagentStop failures that same day). subagent_tokens is a
    single aggregate (no input/output split), so consumers must store it as
    `harness_tokens`, never as tokens_input/tokens_output.

    Returns one dict per notification: {task_id, status, timestamp,
    harness_tokens, harness_tool_uses, harness_duration_ms}. Multiple
    notifications for the same task-id are all returned (resumable
    background agents notify more than once); callers should take the last
    with status == "completed".
    """
    out = []
    if not main_transcript_path or not Path(main_transcript_path).exists():
        return out
    try:
        with open(main_transcript_path, "r", errors="replace") as f:
            for line in f:
                if "task-notification" not in line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                ts = obj.get("timestamp")
                content = (obj.get("message") or {}).get("content")
                texts = []
                if isinstance(content, str):
                    texts.append(content)
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and isinstance(item.get("text"), str):
                            texts.append(item["text"])
                for text in texts:
                    for m in _TASK_NOTIFICATION_RE.finditer(text):
                        block = m.group(0)

                        def _tag(name):
                            mm = re.search(rf"<{name}>(.*?)</{name}>", block, re.DOTALL)
                            return mm.group(1).strip() if mm else None

                        def _int(name):
                            v = _tag(name)
                            try:
                                return int(v) if v is not None else None
                            except ValueError:
                                return None

                        out.append({
                            "task_id": _tag("task-id"),
                            "status": _tag("status"),
                            "timestamp": ts,
                            "harness_tokens": _int("subagent_tokens"),
                            "harness_tool_uses": _int("tool_uses"),
                            "harness_duration_ms": _int("duration_ms"),
                        })
    except Exception:
        pass
    return out


def latest_task_usage(main_transcript_path: str, task_id: str) -> dict | None:
    """The final completed-status usage block for one task-id, or None."""
    if not task_id:
        return None
    best = None
    for n in extract_task_notifications(main_transcript_path):
        if n.get("task_id") != task_id:
            continue
        if n.get("harness_tokens") is None:
            continue
        best = n  # transcript order is chronological; last wins
        if n.get("status") == "completed":
            # a later completed notification supersedes; keep scanning but
            # remember this as the floor
            pass
    return best


def rates_for_model(model_raw: str | None) -> dict | None:
    """Pricing-table entry for a transcript model id: exact key, then the
    MODEL_ALIASES mapping, then the bare id after a provider prefix
    ('accounts/fireworks/models/glm-5p3' -> 'glm-5p3'). None when unpriced —
    callers must treat that as 'unpriced model', never as zero cost."""
    if not model_raw:
        return None
    pricing = _load_pricing()
    candidates = [
        model_raw,
        MODEL_ALIASES.get(model_raw),
        str(model_raw).rsplit("/", 1)[-1],
    ]
    for cand in candidates:
        if cand and cand.lower() in pricing:
            return pricing[cand.lower()]
    return None


def cost_for_turns(turns: list[dict]) -> tuple[float | None, list[str]]:
    """Price a turn list PER-TURN by each turn's own model.

    usage_between/_compute_accurate_cost price the whole matched set at the
    dominant model's rates — fine inside a single agent's transcript, wrong
    for a parent-session window that mixes models (2026-10-21 boot session:
    glm-5p3 at $1.4/$4.4 alongside glm-5p3-flash at $0.15/$0.5 — dominant-rate
    pricing would 9x the flash component).

    Returns (cost, unpriced_models): cost is None when NO turn with usage had
    a priced model; unpriced_models lists models that carried usage but had
    no rate (their tokens are in the token sums but not in cost — partial,
    labeled, never silently zero)."""
    total = 0.0
    any_priced = False
    unpriced: dict[str, None] = {}
    for t in turns:
        has_usage = (t["input_tokens"] or t["output_tokens"]
                     or t["cache_read_input_tokens"]
                     or t["cache_creation_5m"] or t["cache_creation_1h"])
        rates = rates_for_model(t.get("model"))
        if not rates:
            if has_usage and t.get("model"):
                unpriced[t["model"]] = None
            continue
        input_rate = rates["input_per_mtok"] / 1_000_000
        output_rate = rates["output_per_mtok"] / 1_000_000
        total += t["input_tokens"] * input_rate
        total += t["output_tokens"] * output_rate
        total += t["cache_read_input_tokens"] * input_rate * 0.1
        total += t["cache_creation_5m"] * input_rate * 1.25
        total += t["cache_creation_1h"] * input_rate * 2.0
        if has_usage:
            any_priced = True
    return (round(total, 6) if any_priced else None), sorted(unpriced)


def parent_window_usage(main_transcript_path: str, start_iso: str | None,
                        end_iso: str | None) -> dict | None:
    """The PARENT session's own token usage inside a workflow run's execution
    window: non-sidechain assistant turns of the main session transcript in
    [start_iso, end_iso].

    Why this exists: a workflow record's steps[]/subagents[] capture only the
    delegated and step-sliced work. The orchestrating parent session's own
    full-context turns during the run — spawn prompts, result handling, user
    interaction — are often the expensive part (2026-10-21: the boot record's
    subagent components totaled $0.68 while the parent session's main
    transcript burned ~34M glm-5p3 input tokens across the same day). David's
    ruling: a workflow's recorded cost must be fully loaded with this
    component, labeled separately as `parent_window`.

    Subagent turns never appear in the main transcript (verified 2026-10-21:
    zero isSidechain assistant turns in the boot session's main transcript;
    subagents live in <session>/subagents/agent-<id>.jsonl), so this sum
    cannot double count a record's subagents[] entries. Inline steps
    (token_source: windowed) ARE a subset of this window — consumers must
    combine parent_window + subagent components, never parent_window + steps
    + subagents.

    Strict window, no lenient fallback: a transcript that exists but has no
    parent turns in the window returns an honest zero-valued dict, and only a
    missing/unreadable transcript returns None. Priced per-turn (mixed-model
    windows)."""
    if not main_transcript_path:
        return None
    tp = Path(main_transcript_path)
    if not tp.exists():
        return None
    turns = extract_assistant_turns(str(tp), exclude_sidechain=True)

    start_dt = _parse_ts(start_iso)
    end_dt = _parse_ts(end_iso)
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

    tokens_input = sum(t["input_tokens"] + t["cache_read_input_tokens"]
                       + t["cache_creation_5m"] + t["cache_creation_1h"] for t in matched)
    tokens_output = sum(t["output_tokens"] for t in matched)
    turns_with_usage = sum(
        1 for t in matched
        if (t["input_tokens"] or t["output_tokens"] or t["cache_read_input_tokens"]
            or t["cache_creation_5m"] or t["cache_creation_1h"])
    )
    model_counts: dict[str, int] = {}
    for t in matched:
        m = t.get("model")
        if m:
            model_counts[m] = model_counts.get(m, 0) + 1
    model_raw = max(model_counts, key=model_counts.get) if model_counts else None
    cost_usd, unpriced = cost_for_turns(matched)
    if not matched:
        # The transcript exists and is readable; the window genuinely
        # contains no parent turns. That is a true $0.00, not an unknown —
        # distinct from "matched turns on an unpriced model" (None below).
        cost_usd = 0.0

    result = {
        "token_source": "parent-window",
        "model": MODEL_ALIASES.get(model_raw, model_raw),
        "model_raw": model_raw,
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "cost_usd": cost_usd,
        "turns_matched": len(matched),
        "turns_with_usage": turns_with_usage,
    }
    if unpriced:
        result["unpriced_models"] = unpriced
    return result


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
