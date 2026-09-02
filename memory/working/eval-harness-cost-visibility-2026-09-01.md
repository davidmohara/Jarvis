---
date: 2026-09-01
session_focus: eval-harness cost visibility and reporting fixes
---

# Eval-Harness Cost Visibility & Token Reporting — Session Summary

## Problem Statement
Today's spend hit $10.87 with 26M input tokens across 5 general-purpose agent runs. Initial investigation seemed to point toward "context bloat," but actual cause was misidentified: the eval-harness had a status-derivation bug mislabeling completed runs with mid-run tool retries as "aborted," and token reporting lacked per-turn context (10M "input tokens" looked like one bloated context, but was actually 68 turns × ~153K tokens/turn with cache overhead).

## Changes Implemented

### 1. Fixed Status Derivation Bug (eval-agent-stop.py)
- **Issue**: Skill runs with tool_failures > 0 were marked "aborted" even when successfully completing
- **Root cause**: Fallback logic assumed tool_failures == non-completion
- **Fix**: Changed to check for `last_assistant_message` as completion signal; tool failures alone now only downgrade to "partial"
- **Impact**: Prevents false negatives in reliability metrics and future gate scoring

### 2. Added Daily Cost Check (daily-cost-check.py + budget.json)
- New script that flags daily spend spikes above configurable threshold ($15 default)
- Reports top 3 most expensive runs and flags wasted spend (aborted/failed)
- Silent no-op if under threshold (follows exit-behavior pattern)
- Integrated into Exit Behavior checklist (step 5)

### 3. Per-Turn Token Breakdown (--verbose flag)
- Extended daily-cost-check.py with `--verbose` flag
- Shows per-turn token analysis: turn count, avg tokens/turn, separating cache overhead from actual context size
- Example: "10.3M input tokens = 68 turns × 152K/turn" makes it clear this is multi-connector workflow, not context bloat
- Prevents misinterpretation going forward

### 4. Correction Mode Guidance (podcast-prep workflow)
- Added subsection explaining how to fix completed episodes without re-running expensive step-02 data-gather
- Skip multi-connector step (SharePoint + Clay + Outlook + WebSearch) on single-field corrections
- Reuse cached data from previous run, start at affected downstream step
- Avoids 3-4M token waste per fix-and-retry cycle

## Results
- **Status**: All 5 general-purpose runs now correctly categorized (none actually "aborted"; 3 marked "partial" for mid-run retries)
- **Cost visibility**: Daily threshold monitoring now active; running costs will surface immediately on next spike
- **Token clarity**: Per-turn breakdown prevents future "context bloat" misreadings
- **Workflow efficiency**: Correction Mode documented; next single-field fix on podcast-prep will skip expensive data-gather

## Remaining Optimization Opportunities
- **Clay guest cache in accumulated-context**: Skip re-lookup on session retries (est. save 100K tokens per retry)
- **Batch SharePoint searches**: Combine questions + guide lookup into single API call (est. save 200-400K tokens)
- **Conditional WebSearch fallback**: Skip if Clay data sufficient (est. save 50-100K tokens per run)

All three are viable follow-ups but require workflow/skill changes. Status derivation and reporting fixes are foundational and complete.

## Commits
1. `fix(eval-harness): correct status derivation for skill runs with tool retries`
2. `feat(eval-harness): add per-turn token breakdown to daily-cost-check`
3. `docs(eval): clarify per-turn token reporting in daily cost check exit step`
