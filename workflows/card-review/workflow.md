---
name: card-review
description: Monthly credit card benefits audit — usage tracking, expiring credits, rotating categories, spend thresholds, optimization opportunities
agent: chase
---

# Card Optimizer — Monthly Benefits Review

**Goal:** Never leave money on the table. Every credit gets used. Every rotating category gets activated. Every benefit gets extracted before it expires.

**Agent:** Chase — Revenue & Pipeline (personal finance domain)

**Architecture:** Sequential 3-step workflow. Audit current state, surface action items, update tracker files.

**Cadence:** 1st of every month at 9 AM (scheduled task: `credit-card-monthly-review`)

---

## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Card Registry | All cards, reward structures, benefits, credits | `systems/credit-cards/card-registry.json` |
| Benefits Tracker | Credit usage, spend thresholds, card-linked offers, deadlines | `systems/credit-cards/benefits-tracker.json` |
| Optimization Guide | Category mappings, portfolio gaps | `systems/credit-cards/optimization-guide.json` |
| YNAB (4 cards) | Recent transaction data for spend tracking | YNAB MCP (if available) |

### Input

Triggered automatically on the 1st of each month, or manually via:
- "Card review"
- "How are my card benefits looking?"
- "What credits am I leaving on the table?"

---

## EXECUTION

Read fully and follow: `steps/step-01-audit.md`
