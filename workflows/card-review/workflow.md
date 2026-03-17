---
name: card-review
description: Monthly benefits audit — credit usage, expiring deadlines, spend threshold pace, card-linked offer savings
agent: chase
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
<!-- system:end -->

---

<!-- system:start -->
## EXECUTION

### Step 1 — Credits Dashboard (Per Card)

For each card with active credits, produce a table:

| Benefit | Total | Used | Remaining | Resets | Status |
|---------|-------|------|-----------|--------|--------|
| Resy credit | $100/qtr | $X | $X | Quarterly | 🟢 / 🟡 / 🔴 |

Status codes:
- 🟢 On track / sufficient time remaining
- 🟡 Expiring this month or next — action needed
- 🔴 Expiring within 7 days or already expired with balance remaining

Cards to cover: Amex Platinum, Citi AAdvantage Executive, Atlas Visa Infinite.

### Step 2 — Zero-Usage Flag

Flag any credit with $0 used year-to-date where the reset period means value has already been lost or is about to be lost. These are the leaks.

### Step 3 — Discover Rotating Category Check

From `card-registry.json → rotating_categories`:
- What is the current quarter's category?
- Is it activated? (requires manual activation each quarter)
- What is the next quarter's category (if known)?
- If unactivated: surface as urgent action item

### Step 4 — Amex Plat $75K Spend Threshold

From `benefits-tracker.json → spend_threshold_tracker.amex_plat_75k`:
- Current spend vs. $75K target
- Remaining needed
- Deadline: December 31
- Pace assessment: on track / at risk / not achievable without change
- Unlocks: Centurion Lounge guest access + unlimited Delta Sky Club through Jan 2028

### Step 5 — Card-Linked Offer Savings

From `benefits-tracker.json → card_linked_offers`:
- Total saved to date (all cards combined)
- Any offers expiring this month — flag for immediate use or evaluation
- Any recommended-to-add offers still sitting unacted on — surface with priority

### Step 6 — Upcoming Deadlines

From `benefits-tracker.json → upcoming_deadlines`:
- List all deadlines within the next 60 days
- Sort by urgency
- Call out any that require action before end of month

### Step 7 — Action Item Summary

Produce a prioritized action list:

**URGENT (this week):**
- [Item]

**THIS MONTH:**
- [Item]

**NEXT MONTH:**
- [Item]

**ONGOING:**
- [Item]

### Step 8 — Data Freshness Check

Check `last_updated` in benefits-tracker.json. If more than 30 days old:
> "⚠️ Benefits data is X days old. A site walkthrough is needed to refresh Amex Platinum and Atlas portal data. Trigger `card walkthrough` when you have 20 minutes."

### Step 9 — Route to Chief

After completing the review, pass any 🔴 or 🟡 flagged items to Chief for inclusion in the morning briefing cadence. Chief should surface expiring credits in the daily briefing until resolved.
<!-- system:end -->

---

<!-- system:start -->
## OUTPUT FORMAT

Dashboard-style. Use tables for the credit status section. Use bullet lists for action items. Keep it scannable — David should be able to read this in 60 seconds and know exactly what to do.

Lead with the most urgent item, not the most comprehensive one.
<!-- system:end -->
