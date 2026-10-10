---
status: not-started
started-at: ~
completed-at: ~
outputs:
  slow_update_written: false
  slow_update_content: null
  slow_update_validated: false
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` before any action
2. This step only runs at epoch boundaries — when `rounds_completed % epoch_size == 0`
3. Slow-update content goes into a PROTECTED region of SKILL.md — delimited by `<!-- SLOW_UPDATE_START -->` and `<!-- SLOW_UPDATE_END -->` markers
4. The written slow-update content must still pass through the gate (score the skill with the new protected region before committing)
5. Slow-update content must be instructions TO the executing agent, not meta-commentary
6. Write `status: complete` and `completed-at` after outputs stored

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Rigby |
| Input | `slow_update_history_path`, `accepted_edits_total`, round history, rejected-edits buffer |
| Output | Updated `<!-- SLOW_UPDATE_START/END -->` region in SKILL.md; updated slow-update history |

## CONTEXT BOUNDARIES

This step synthesizes cross-epoch lessons. It looks across all rounds in the completed epoch (not just the last one), identifies what consistently helped and what consistently failed, and writes durable strategic guidance into a protected region that step-level edits cannot touch.

## YOUR TASK

### 1. Load Epoch History

For the epoch just completed (rounds from `last_epoch_boundary + 1` to `rounds_completed`):

Read the reflect output file for each round: `skills/{skill_id}/candidates/round-{N}-edits.json`

For each round, extract:
- What failure patterns were identified
- What edits were proposed
- Whether the round was accepted or rejected (from the gate step)
- The delta (from `accumulated-context.last_round_delta` per round — stored in slow-update history)

Also read the rejected-edits buffer at `rejected_edits_path` — look for entries from this epoch's rounds.

### 2. Load Prior Slow-Update History

Read `slow_update_history_path` if it exists. This records what guidance was written at previous epoch boundaries and how well it performed.

Extract:
- Prior slow-update content (what was written)
- Whether that guidance appeared to help (look at subsequent round deltas — positive deltas after the slow update suggest it helped)

### 3. Synthesize Longitudinal Guidance

Think across the epoch. Ask:

**What worked?**
- Which edit types (append / insert_after / replace) had the best acceptance rate this epoch?
- Which failure patterns, once addressed by an accepted edit, stopped appearing in subsequent rounds?
- Are there behaviors the agent is doing correctly that haven't been fully codified yet?

**What didn't work?**
- Which proposed edits were rejected repeatedly without finding better alternatives?
- Are there failure patterns that persisted across every round despite edit attempts?
- Did the prior slow-update guidance (if any) help or create regressions?

**What's durable?**
- Identify 2-4 procedural principles that explain the epoch's learning — things the executing agent should internalize that are broader than any single edit.

### 4. Write Slow-Update Guidance Block

Compose a guidance block written as direct instructions to the executing agent. This is not commentary — it's operational guidance that will be inserted into the skill.

Format:

```markdown
<!-- SLOW_UPDATE_START -->
## Strategic Guidance (Epoch {N})

_Updated: {ISO-8601 date}. This section is managed by the optimization loop — do not edit manually._

{2-4 concise, actionable instructions derived from cross-epoch pattern analysis. Written as imperatives: "When X, always Y." "Before doing Z, first check W." Each instruction must address a pattern observed across multiple rounds.}
<!-- SLOW_UPDATE_END -->
```

**Constraints:**
- Maximum 300 tokens in this block
- Instructions must complement, not duplicate, the main skill body
- Do not reference specific eval record IDs or dates — keep it general
- Previous epoch guidance: retain any part that proved effective (positive subsequent delta), revise or remove parts that didn't

### 5. Gate the Slow-Update

The slow-update content must pass the same gate as regular edits.

**Apply to SKILL.md:**

If the SKILL.md already has a `<!-- SLOW_UPDATE_START/END -->` block: replace its content.
If not: append the block at the end of the main body (before `## SKILL COMPLETE` if present).

Write the updated SKILL.md to `skills/{skill_id}/candidates/epoch-{epoch_number}-slow-update.md` first (do not overwrite SKILL.md directly yet).

Score the epoch candidate against selection records (same formula as step-05). If score ≥ current `best_score`: commit to SKILL.md and update `best_score`. If score < `best_score`: discard the slow-update content and log the failure to `slow_update_history_path`.

### 6. Update Slow-Update History

Write or append to `slow_update_history_path`:

```json
{
  "epoch": <N>,
  "timestamp": "<ISO-8601>",
  "guidance_written": "<the slow-update content>",
  "score_before": <best_score before slow update>,
  "score_after": <score after slow update>,
  "accepted": <true|false>,
  "failure_patterns_addressed": ["<pattern 1>", "<pattern 2>"]
}
```

### 7. Write State

Update `state.yaml current-step: step-03-reflect` (continue to next round) or `step-08-report` if termination conditions are met.

Report:
> "[Rigby]: Epoch {N} complete. Slow update {'accepted (+{delta:.3f})' | 'rejected — no improvement'}. Continuing to round {next_round}."

## SUCCESS METRICS

- Guidance block written and gated
- Slow-update history updated
- SKILL.md contains valid `<!-- SLOW_UPDATE_START/END -->` markers after commit
- Protected region not contaminated by step-level edits in prior rounds

## FAILURE MODES

| Failure | Action |
|---------|--------|
| No completed rounds with accepted edits | Write minimal slow-update noting no improvement found yet. Gate it — if neutral, skip. |
| Slow-update makes score worse | Discard. Log to history. Report: "Slow update rejected — SKILL.md unchanged." |
| slow-update-history.json write fails | Log error, proceed. History is informational, not blocking. |

## NEXT STEP

Determined dynamically (next round or step-08-report).
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
