---
name: card-which
description: Full-optimization credit card selection for a purchase — category match, rotating categories, caps, thresholds, stacking opportunities
agent: chase
---

# Card Optimizer — Which Card?

**Goal:** Never leave rewards on the table. Every purchase hits the card with the highest return, factoring in every variable — not just the base category rate.

**Agent:** Chase — Revenue & Pipeline (personal finance domain)

**Architecture:** Single-step decision engine. No user interaction beyond the initial ask. Reads data files, runs the logic, returns the answer.

---

## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Card Registry | All cards, reward structures, benefits | `systems/credit-cards/card-registry.json` |
| Optimization Guide | Category → best card mappings, portfolio gaps | `systems/credit-cards/optimization-guide.json` |
| Benefits Tracker | Credit usage, spend thresholds, card-linked offers | `systems/credit-cards/benefits-tracker.json` |

### Input

Any of:
- "Which card for [purchase]?"
- "Buying [item] at [vendor]"
- "Card for [category]?"
- "What should I use at [store]?"

---

## EXECUTION

Read fully and follow: `steps/step-01-recommend.md`
