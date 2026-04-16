---
name: win-loss-analysis
description: Win/loss analysis — post-decision debrief with pattern recognition and lessons applied to active pursuits
agent: chase
model: sonnet
---

<!-- system:start -->
# Win/Loss Analysis Workflow

**Goal:** Extract actionable lessons from every closed deal and apply them to active pursuits. Lost deals are more valuable than won deals — if you learn from them. Every post-mortem adds to the institution's competitive intelligence.

**Agent:** Chase — Revenue & Pipeline

**Architecture:** Sequential 3-step workflow. Pull deal data and engagement history, identify patterns across multiple deals, apply lessons to active pipeline and write permanent records to knowledge layer. No user interaction required until the analysis is delivered.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| CRM (CRM) | Closed deal details, timeline, outcome, competitive data, client feedback | CRM via Chrome/M365 auth |
| Knowledge layer | Engagement history, meeting notes, relationship context, past win/loss records | Knowledge base API |
| Active pipeline | Current open opportunities for lesson application | From CRM (same session) |

### Input

This workflow requires a deal identifier to begin. One of:
- A specific deal name or CRM opportunity ID
- A company name with a recently closed deal
- A direct request: "Win/loss on [deal/company]"

If no deal is specified, surface recently closed deals that have no post-mortem on record.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-deal-data.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
