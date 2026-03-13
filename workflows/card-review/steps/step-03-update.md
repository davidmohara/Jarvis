---
step: 3
name: update
description: Update tracker files with any new information from the review
---

# Step 3: Update Tracker Files

## Process

### 1. Update Benefits Tracker

Write any changes to `systems/credit-cards/benefits-tracker.json`:
- New usage entries from David's input
- Updated card-linked offers (added/removed/expired)
- Updated spend threshold progress
- Set `last_updated` to today's date

### 2. Update Optimization Guide (if needed)

If any category recommendations changed due to:
- Discover rotating category shift
- Atlas dynamic category change
- Cap being hit (e.g., BCP grocery $6K)
- New card added/removed from portfolio

Update `systems/credit-cards/optimization-guide.json`.

### 3. Update Card Registry (if needed)

If David provided new information about:
- Benefit changes
- Fee changes
- New cards or closed cards

Update `systems/credit-cards/card-registry.json`.

### 4. Route Alerts to Chief

For any time-sensitive action items (expiring credits, deadlines):
- Create OmniFocus tasks with due dates
- Flag for inclusion in tomorrow's morning briefing

### 5. Confirm Completion

Report to David:
- What was updated
- What alerts were created
- When the next review is scheduled
- Whether a site walkthrough is recommended

## Completion

Workflow complete. Next scheduled run: 1st of next month.
