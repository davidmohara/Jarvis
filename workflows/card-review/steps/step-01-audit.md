---
step: 1
name: audit
description: Read all card data and build the monthly status dashboard
next: step-02-actions.md
---

# Step 1: Benefits Audit

## Process

### 1. Read All Data Files

Load:
- `systems/credit-cards/card-registry.json`
- `systems/credit-cards/benefits-tracker.json`
- `systems/credit-cards/optimization-guide.json`

### 2. For Each Card, Report Credit Usage

Walk through `benefits_tracker.json` → `benefits_usage` for each card. For each credit/benefit:

| Credit | Total | Used | Remaining | Resets | Deadline |
|--------|-------|------|-----------|--------|----------|

Flag with ⚠️ any credit where:
- Remaining > 50% AND we're past the midpoint of the reset period
- $0 used year-to-date
- Expires within 30 days

### 3. Check Rotating Categories

Read `card-registry.json` → `discover-it.rotating_categories`:
- What is the current quarter's category? Is it activated?
- What is next quarter's category? Is it announced? Activation needed?
- How much of the $1,500 quarterly cap has been used?

### 4. Check Spend Thresholds

Read `benefits_tracker.json` → `spend_threshold_tracker`:
- Amex Plat $75K target: current spend, remaining, months left, required monthly pace
- Is David on track? If not, what's the gap and is it realistic?

### 5. Card-Linked Offer Summary

Read `benefits_tracker.json` → `card_linked_offers` for each card:
- Total savings to date across all cards
- Any offers expiring in the next 14 days
- Any high-value offers not yet added that match David's spending patterns

### 6. Annual Fee ROI Check

Read `benefits_tracker.json` → `annual_fee_roi`:
- For cards with fees: is the value extracted exceeding the fee?
- Flag any card where ROI is negative and the renewal is within 90 days

## Output Format

Present as a clean dashboard:

```
## Card Benefits Dashboard — [Month Year]

### Amex Platinum (Personal)
[credit table with status indicators]

### Citi AAdvantage Executive
[credit table]

### Amex Blue Cash Preferred
[category caps and usage]

### Discover it
[rotating category status + cap usage]

### Atlas Visa Infinite / Chase Sapphire
[any relevant updates]

---

### Spend Threshold Tracker
Amex Plat $75K: $X/$75,000 — [on/off pace] — need $X/mo remaining

### Card-Linked Offers
Total saved YTD: $X
Expiring soon: [list]

### Action Items
1. [specific action]
2. [specific action]
```

## Completion

Proceed to `step-02-actions.md`
