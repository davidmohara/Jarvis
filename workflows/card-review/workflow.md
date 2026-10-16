---
name: card-review
description: Monthly benefits audit — credit usage, expiring deadlines, spend threshold pace, card-linked offer savings
agent: chase
model: sonnet
---

<!-- system:start -->
# Card Optimizer — Monthly Benefits Review

**Goal:** Full audit of benefit extraction across all cards. Surface unused credits, expiring deadlines, spend pace, and card-linked offer savings. Produce a dashboard with prioritized action items.

**Agent:** Chase

**Cadence:** 1st of each month (scheduled) or on-demand via "card review."

**Routing:** Expiring-credit alerts → route data to Chief for integration into morning briefing.
<!-- system:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | File |
|--------|-------------|------|
| Benefits tracker | Credit usage, card-linked offers, spend threshold, deadlines | `systems/credit-cards/benefits-tracker.json` |
| Card registry | Full credit/benefit structure, caps, reset cadences | `systems/credit-cards/card-registry.json` |

Read both files fully before building the review. Check `last_updated` in benefits-tracker — if >30 days old, flag that a site walkthrough is needed to refresh data.

### FRESHNESS GATE (hard rule, runs FIRST)

Before building any dashboard, read `last_updated` in `systems/credit-cards/benefits-tracker.json`.

- **If it is more than 30 days old: STOP.** Do not produce a dashboard, do not compute usage, do not guess. Output exactly one thing: "Card data is N days stale. Run `card-walkthrough` first to refresh it, then re-run this review." Mark the run complete with `outcome: blocked-stale-data` and stop.
- Only proceed when the data is under 30 days old.

Rationale: an analysis of stale data produces confident wrong answers. The review's value is entirely dependent on the walkthrough having run first. Order matters: walkthrough refreshes, review analyzes. Never the reverse. See err-20261016T203925-XMT2U0.

### VERIFICATION BOUNDARY (hard rule)

This workflow performs **no portal access**. It reads stored JSON only. Therefore:

- **Never state or imply what usage has been recorded.** No "used", "lost", "forfeited", "at risk", or "remaining" claim may be presented as fact unless it comes from a stored file AND that file's `last_updated` is stated next to it.
- Every usage statement must be labelled as an **unverified inference from a file of age N days**, or omitted entirely.
- Write `UNKNOWN (needs walkthrough)` rather than a guess. A wrong "you lost $175" is worse than "unknown".
- The only workflow that can assert recorded activity is `card-walkthrough`, which logs into the portals with David present.
- Structural facts about the files themselves (a field never tracked, a stale `best_card` pointer, an internal contradiction) ARE reliable and may be stated plainly.

This rule exists because the 2026-10-16 run presented stale-data inferences as findings and got them wrong (Q3 Resy, Q3 lululemon, Atlas points). See err-20261016T203925-XMT2U0.
<!-- system:end -->

---

<!-- system:start -->
## STATE CHECK

Read and follow `reference/state-check-protocol.md` before any execution. Workflow: `card-review`; agent: `chase`.

## EXECUTION

Read and follow each step file in order. The step files own the detailed process.

| Step | File | What It Does |
|------|------|-------------|
| 1 | `steps/step-01-audit.md` | Read all card data files and build the monthly dashboard: per-card credit usage, zero-usage flags, Discover rotating category, Amex Plat $75K threshold, card-linked offer savings, upcoming deadlines, annual fee ROI |
| 2 | `steps/step-02-actions.md` | Present action items grouped by urgency and get David's decisions; check data freshness |
| 3 | `steps/step-03-update.md` | Write new information back to the tracker files; route time-sensitive alerts to Chief |

Read fully and follow: `steps/step-01-audit.md` to begin.
<!-- system:end -->

---

<!-- system:start -->
## OUTPUT FORMAT

Dashboard-style. Use tables for the credit status section. Use bullet lists for action items. Keep it scannable — David should be able to read this in 60 seconds and know exactly what to do.

Lead with the most urgent item, not the most comprehensive one.
<!-- system:end -->
