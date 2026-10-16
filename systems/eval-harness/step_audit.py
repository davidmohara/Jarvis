#!/usr/bin/env python3
"""
Shared helpers for the per-step audit trail (Stage 5 Phase 2).

An "instrumented" eval record carries, for every step of the run, the fields
Tim Rayburn's Stage 5 report asks for: step name, owning agent, model name,
input tokens, output tokens, and cost in USD. The canonical shape is a dict:

    {
      "name":             "step-05-synthesize-briefing",
      "agent":            "chief",          # owning agent
      "model":            "sonnet",
      "tokens_input":     12345,            # int >= 0, or null
      "tokens_output":    678,              # int >= 0, or null
      "cost_usd":         0.047,            # float >= 0, or null
      "status":           "complete",
      "started":          "2026-10-08T15:24:04Z",
      "completed":        "2026-10-08T15:44:04Z",
      "duration_seconds": 1200.0,
      "data_sources_used": [],
      "data_source_failures": []
    }

The harness has written step entries in this dict shape for a while, but two
older shapes still exist on disk and MUST keep loading:

  - `steps: []`                 -- no steps recorded yet (the common case)
  - `steps: ["step-auto", ...]` -- legacy records that stored bare name strings

Every writer and reader therefore goes through normalize_step()/upsert_step()
instead of touching `record["steps"]` directly. This is the backward-compat
contract: old records never crash a new reader, and new writers never crash on
an old record that still holds strings.

validate-token-audit-trail.py is the compliance check for this schema; this
module is the write-side counterpart that keeps the schema intact.
"""

import json
from pathlib import Path

IES_ROOT = Path(__file__).resolve().parents[2]
PRICING_PATH = IES_ROOT / "systems" / "eval-harness" / "model-pricing.json"
WORKFLOWS_DIR = IES_ROOT / "workflows"

# The full canonical field set, in display order. Kept in sync with
# validate-token-audit-trail.py's required_fields plus the audit-only extras
# the Stage 5 report asks for.
#
# `agent` vs `owning_agent`: the eval record's top-level `agent` field is
# frequently a Claude Code subagent type label ("general-purpose", "fork",
# "Explore") rather than the IES agent that owns the workflow, so it cannot be
# trusted for attribution. `owning_agent` is resolved independently from the
# workflow definition (workflows/<name>/workflow.md's `agent:` frontmatter)
# and is the field Stage 3/4 attribution should read. Both are kept: `agent`
# preserves whatever the harness wrote, `owning_agent` is the defensible one.
CANONICAL_STEP_FIELDS = (
    "name",
    "step_id",
    "agent",
    "owning_agent",
    "model",
    "tokens_input",
    "tokens_output",
    "cost_usd",
    "token_source",
    "status",
    "started",
    "completed",
    "duration_seconds",
    "data_sources_used",
    "data_source_failures",
)


def _load_yaml():
    """Import PyYAML from the vendored copy (same path the hooks use), falling
    back to any installed yaml. Returns None if unavailable."""
    import sys
    vendor = IES_ROOT / "systems" / "eval-harness" / "vendor"
    if str(vendor) not in sys.path:
        sys.path.insert(0, str(vendor))
    try:
        import yaml
        return yaml
    except Exception:
        return None


def _frontmatter(text: str) -> dict:
    """Parse a leading `--- ... ---` YAML frontmatter block. Returns {} on any
    failure (missing block, parse error, yaml unavailable)."""
    yaml = _load_yaml()
    if yaml is None or not text:
        return {}
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            try:
                return yaml.safe_load("\n".join(lines[1:i])) or {}
            except Exception:
                return {}
    return {}


def workflow_owner_agent(workflow_name: str) -> str | None:
    """The IES agent that owns a workflow, read from
    workflows/<name>/workflow.md's `agent:` frontmatter.

    This is the authoritative owner (e.g. plaud-ingest -> knox,
    boot-verification -> ralph) and is deliberately independent of the eval
    record's own `agent` field, which the hooks sometimes set to a Claude Code
    subagent type label instead. Returns None if the workflow or field can't be
    resolved.
    """
    if not workflow_name:
        return None
    path = WORKFLOWS_DIR / str(workflow_name) / "workflow.md"
    if not path.is_file():
        return None
    fm = _frontmatter(path.read_text(errors="replace"))
    agent = fm.get("agent")
    return str(agent) if agent else None


# --- Agent attribution mapping (Stage 3 Phase 0) --------------------------
#
# Eval records carry an `agent` field, but the hooks historically stamped it
# with the Claude Code subagent *type* ("general-purpose", "fork", "Explore",
# "claude") rather than the IES agent that actually did the work. The IES
# agent roster lives in agents/manifest.md; the mapping layer below resolves a
# raw label / spawn prompt / workflow owner back to a canonical manifest agent
# so attribution going forward lands on the right agent.

# Canonical manifest agent names (agents/manifest.md), lowercase.
MANIFEST_AGENTS = (
    "master", "chief", "chase", "knox", "shep", "quinn",
    "harper", "rigby", "sterling", "galen", "ralph",
)

# Raw labels that map onto a canonical manifest agent. Master is the agent
# (agents/master.md; frontmatter name `Master`); "Jarvis" is the name of the
# whole system, not an agent — David 2026-10-16, err-20261016T123345-KNNL1T.
# Eval records carry both `master` and `jarvis` labels; both canonicalize to
# `master` for reporting, records themselves are never rewritten.
AGENT_LABEL_ALIASES = {
    "jarvis": "master",
    "master": "master",
}

# Reporting display for the merged identity: the agent's canonical name.
MASTER_MERGED_LABEL = "master"

# Step statuses that count as a step having finished its work. Both spellings
# are live in the workflow library (boot "complete", plaud-ingest "completed").
TERMINAL_STEP_STATUSES = ("complete", "completed", "success")


def normalize_agent_label(agent) -> str | None:
    """Canonical manifest agent name for a raw label, or None if the label is
    not an IES agent at all (e.g. Claude Code subagent types: general-purpose,
    fork, Explore, claude, unknown)."""
    if not agent:
        return None
    a = str(agent).strip().lower()
    if a in AGENT_LABEL_ALIASES:
        return AGENT_LABEL_ALIASES[a]
    if a in MANIFEST_AGENTS:
        return a
    return None


def merge_reporting_agent(agent) -> str:
    """Reporting-level merge: records carry both `master` and `jarvis` labels
    for the one coordinator agent. The canonical agent name is `master`
    ("Jarvis" is the system name, not an agent), so rollups report both as
    `master`. Every other label — including non-agent labels such as
    `general-purpose` — passes through unchanged. Applied to the reporting
    output only; the underlying records are never rewritten."""
    if not agent:
        return agent
    if str(agent).strip().lower() in ("master", "jarvis"):
        return MASTER_MERGED_LABEL
    return agent


def resolve_record_agent(record: dict) -> str | None:
    """Best-effort canonical IES agent that owns an eval record.

    Priority (most authoritative first):
      1. an explicit top-level `owning_agent` (already canonical)
      2. the workflow's own owner — workflows/<name>/workflow.md's `agent:`
         frontmatter — read from the record's `workflow` field, then its `name`
      3. a canonical mapping of the record's raw `agent` label
      4. reporting-time recovery for unattributable records: mine the record's
         own `agent_transcript_path` (a subagent transcript whose first user
         message is the spawn prompt, "You are Shep ...") or, failing that, its
         `agent_id` (locate the transcript/.meta.json under ~/.claude/projects)
         for a manifest agent name.

    Step 4 exists because the SubagentStart hook payload carries no prompt text
    (see hook_utils.resolve_spawn_text), so spawned specialists historically
    landed as `agent: general-purpose` with `workflow`/`owning_agent` null —
    e.g. the six 2026-10-16 runs. It is a read-side-only recovery: the record
    on disk is never rewritten. Best-effort — an unresolvable path is None, no
    crash.

    Returns a canonical manifest agent name (e.g. "ralph", "knox", "master"),
    or None when nothing resolves.
    """
    if not isinstance(record, dict):
        return None
    canon = normalize_agent_label(record.get("owning_agent"))
    if canon:
        return canon
    for wf in (record.get("workflow"), record.get("name")):
        canon = normalize_agent_label(workflow_owner_agent(wf))
        if canon:
            return canon
    canon = normalize_agent_label(record.get("agent"))
    if canon:
        return canon
    # Reporting-time recovery from the record's own spawn evidence. Imported
    # lazily: hook_utils imports THIS module at load time (for the roster), so
    # a top-level import here would be circular.
    try:
        from hook_utils import agent_from_transcript, agent_from_meta
    except Exception:
        return None
    canon = agent_from_transcript(record.get("agent_transcript_path"))
    if canon:
        return canon
    return agent_from_meta(record.get("agent_id"))


def apply_record_attribution(record: dict) -> str | None:
    """Stamp an eval record's attribution from the best available evidence.

    Always sets `owning_agent` to the resolved canonical owner. Additionally
    upgrades the top-level `agent` label to that owner *only* when the current
    label is not itself a manifest agent — so a real Claude Code subagent-type
    label ("general-purpose") is replaced with the owning IES agent, while an
    already-canonical `agent` (e.g. "chief") is left untouched. Returns the
    resolved owner, or None.
    """
    if not isinstance(record, dict):
        return None
    owner = resolve_record_agent(record)
    if owner:
        record["owning_agent"] = owner
        if normalize_agent_label(record.get("agent")) is None:
            record["agent"] = owner
    return owner


def steps_all_terminal(record: dict) -> bool:
    """True when the record has at least one step and every recorded step is in
    a terminal status (complete/completed/success).

    This is the step-evidence derivation of `mechanical.completed` introduced in
    eval-agent-stop.py (2026-10-15): a run whose steps all finished counts as
    mechanically complete even when no state.yaml completion was captured.
    Returns False for a record with no steps (nothing to derive from)."""
    steps = record.get("steps") or []
    if not steps:
        return False
    return all(
        normalize_step(s).get("status") in TERMINAL_STEP_STATUSES
        for s in steps
    )


def load_pricing() -> dict:
    """Load the per-million-token pricing table. Returns {} on failure."""
    try:
        with open(PRICING_PATH, "r") as f:
            return json.load(f).get("models", {})
    except Exception:
        return {}


def compute_cost(model, tokens_in, tokens_out):
    """Flat-rate cost in USD from token counts. Returns None if inputs are
    incomplete or the model isn't in the pricing table.

    This is the simple flat-rate math used by record-step.py (no cache
    multipliers). token_usage.py's _compute_accurate_cost is the cache-aware
    variant used when pricing a whole transcript slice; both are valid for
    different inputs, so this stays independent rather than unifying them.
    """
    if not model or tokens_in is None or tokens_out is None:
        return None
    rates = load_pricing().get(str(model).lower())
    if not rates:
        return None
    cost = (tokens_in / 1_000_000) * rates["input_per_mtok"] + \
           (tokens_out / 1_000_000) * rates["output_per_mtok"]
    return round(cost, 6)


def normalize_step(step) -> dict:
    """Coerce any historical step shape into a canonical dict.

    - dict            -> returned as-is (already canonical)
    - str             -> {"name": <str>} with null audit fields
    - anything else   -> {"name": str(step)}
    """
    if isinstance(step, dict):
        return step
    if isinstance(step, str):
        return {"name": step}
    return {"name": str(step)}


def normalize_steps(record) -> list:
    """Return the record's steps as a list of canonical dicts, never raising
    on the legacy string shape. Non-destructive: does not write back."""
    return [normalize_step(s) for s in (record.get("steps") or [])]


def step_name(step) -> str:
    """Name of a step in any historical shape ('' if unnameable)."""
    if isinstance(step, dict):
        return step.get("name", "") or ""
    if isinstance(step, str):
        return step
    return str(step)


def step_key(name) -> str:
    """Canonical identity for a step name: a trailing '.md' is ignored.

    Two writers name the same step differently: post-tool-use.py keys
    skeletons as Path(file).name ('step-01-x.md') while record-step.py and
    close-eval-record.py name steps without the suffix ('step-01-x'). Without
    a shared identity, a writer using one spelling appends a duplicate entry
    alongside the other's, and a captured (token-bearing) entry can be
    shadowed by a null skeleton. This is comparison only -- stored names are
    never rewritten.
    """
    if not isinstance(name, str):
        name = "" if name is None else str(name)
    return name[:-3] if name.endswith(".md") else name


def upsert_step(record: dict, step_entry: dict) -> dict:
    """Insert or replace a step entry in record["steps"] by name, tolerating
    legacy string entries in the existing list.

    Replaces ALL existing entries with the same canonical name (dedup,
    ignoring a trailing '.md') and appends the new entry last, so ordering
    reflects completion. Returns the record.
    """
    entry = normalize_step(step_entry)
    name = step_key(entry.get("name"))
    existing = record.get("steps") or []
    kept = [s for s in existing if step_key(step_name(s)) != name]
    kept.append(entry)
    record["steps"] = kept
    return record


def step_totals(record: dict) -> dict:
    """Sum tokens/cost across steps[] and subagents[] for a record.

    Mirrors the aggregation in eval-turn-stop.py's finalize() so a consumer
    can compute the same totals the harness writes into total_tokens_*/
    total_cost_usd. Returns None-valued totals when nothing was recorded.
    """
    tokens_in = tokens_out = 0
    cost = 0.0
    found = False

    for group in ("steps", "subagents"):
        for entry in (record.get(group) or []):
            if not isinstance(entry, dict):
                continue
            ti = entry.get("tokens_input")
            to = entry.get("tokens_output")
            c = entry.get("cost_usd")
            if ti is None and to is None and c is None:
                continue
            found = True
            tokens_in += ti or 0
            tokens_out += to or 0
            cost += c or 0

    if not found:
        return {"tokens_input": None, "tokens_output": None, "cost_usd": None}
    return {
        "tokens_input": tokens_in,
        "tokens_output": tokens_out,
        "cost_usd": round(cost, 6),
    }
