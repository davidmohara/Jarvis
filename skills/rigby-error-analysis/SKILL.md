---
name: rigby-error-analysis
description: Analyze the IES error log for recurring patterns, propose systemic fixes (rules, skill updates, workflow changes), and report improvement opportunities. Tiered response — auto-proposes clear-cut fixes, surfaces data-only for ambiguous patterns.
evolution: system
model: sonnet
---

<!-- system:start -->
## Trigger Phrases

- "error analysis", "error review", "what mistakes am I making", "how can we improve"
- "error patterns", "correction log", "show me the error log"
- Automatically invoked by Chief during daily review (count only) and Quinn during weekly review (full analysis)
- Proactively triggered when Master detects a threshold breach (3+ occurrences of same pattern)

## Workflow

### Step 1: Load Error Data

Read `systems/error-tracking/error-log.json`. If the file is empty or has no entries, report: "Clean log — no corrections recorded yet." and exit.

### Step 2: Compute Statistics

- **Total entries** since last analysis (`patterns.last_analyzed`)
- **By category** — count per error category
- **By failure mode** — count per root cause
- **By agent** — which agents are generating the most corrections
- **By source** — explicit vs. self-detected ratio
- **By severity** — minor/moderate/major distribution
- **Trend** — are errors increasing, stable, or decreasing over time?

### Step 3: Identify Patterns

A pattern is **3+ entries** sharing the same `category` + `failure_mode` combination.

For each pattern:
1. Pull all matching entries
2. Identify the common thread — what keeps going wrong and why
3. Classify the fix type:
   - `rule` — add a rule to SYSTEM.md or an agent file
   - `skill-update` — modify an existing skill's protocol
   - `workflow-update` — add a step or check to a workflow
   - `agent-update` — modify an agent's behavior, routing, or data requirements
   - `training-module` — create or update a training module

### Step 4: Propose Fixes (Tiered)

**Tier 1: Auto-Propose (clear-cut fixes)**

These have obvious, low-risk solutions. Rigby drafts the specific fix and presents it for approval:

| Condition | Auto-Proposal |
|-----------|---------------|
| Same `tool-misuse` error 3+ times | Draft a rule addition to the relevant agent file specifying the correct tool |
| Same `format-violation` 3+ times | Draft a convention rule for SYSTEM.md |
| Same `missed-context` 3+ times | Add the missed source to the agent's Data Requirements table |
| Same `process-skip` 3+ times | Add a checkpoint to the relevant workflow step |
| Same `assumption-error` 3+ times | Draft a "verify before assuming" rule for the specific scenario |

**Tier 2: Data-Only (ambiguous patterns)**

These need executive judgment. Rigby presents the data and asks for direction:

| Condition | Presentation |
|-----------|-------------|
| `routing-error` patterns | Show the misroutes, suggest routing table changes, ask for confirmation |
| `hallucination` patterns | Flag the sources that are unreliable or gaps in knowledge, ask how to address |
| `over-engineering` or `under-delivery` patterns | Surface the pattern, ask about calibration preferences |
| Mixed-category patterns | Present the correlation, ask what systemic change would address the root cause |

### Step 5: Update Pattern Log

Write identified patterns to `patterns.recurring` in the error log. Update `patterns.last_analyzed` timestamp.

### Step 6: Present Results

**Daily review integration (Chief calls this):**
Brief — one line only.
```
Error tracking: [N] corrections since last review ([X] explicit, [Y] self-detected). [Any threshold alerts.]
```

**Weekly review integration (Quinn calls this):**
Full analysis:
```
## System Improvement Opportunities

**Period:** [date range]
**Corrections logged:** [N] ([X] explicit, [Y] self-detected)
**Severity:** [major: N] [moderate: N] [minor: N]

### Recurring Patterns

[For each pattern:]
**[Category] → [Failure Mode]** — [N] occurrences
- What keeps happening: [description]
- Proposed fix: [fix description]
- Fix type: [rule | skill-update | etc.]
- Recommendation: [Apply now | Needs your call]

### Agent Performance

| Agent | Corrections | Top Issue |
|-------|------------|-----------|
| [agent] | [N] | [most common category] |

### Trend
[Improving / Stable / Degrading] — [one sentence context]
```

**On-demand invocation:**
Full analysis (same as weekly) with additional detail — show individual entries if requested.

## Error Handling

| Failure | Action |
|---------|--------|
| Error log file missing or corrupt | Create a fresh one. Report: "Error log was missing — initialized a new one." |
| No new entries since last analysis | Report: "No new corrections since last analysis on [date]." |
| Pattern fix requires file the agent can't modify | Surface the fix proposal and flag it for Rigby's capability build |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
