---
status: not-started
started-at: ~
completed-at: ~
model: sonnet
---

---
step: 1
name: walkthrough
description: Walk through each card portal with David, extract data, update files
---

# Step 1: Portal Walkthrough

## EXECUTION PROTOCOL

**Agent:** Chase, spawned by the coordinator, never executed inline


## Process

Walk through each card portal in sequence. For each card:

1. **Ask David to log in** — "Pull up [issuer] in Chrome and log in. Let me know when you're on the dashboard."
2. **Read the page** — Use Claude in Chrome (`mcp__Claude_in_Chrome__read_page` or `get_page_text`) to extract visible data.
3. **Navigate to key pages** — Guide David or use Chrome automation to visit:
   - Benefits/credits page
   - Offers page
   - Rewards/points balance page
   - Recent transactions (last 30 days)
4. **Extract and compare** — Read current data, compare against stored values in `card-registry.json` and `benefits-tracker.json`.
5. **Flag changes** — Call out anything that differs from stored data.
6. **Update files** — Write new values immediately after each card.

---

## Card-by-Card Walkthrough

### 1. Amex Platinum (amextravel.com → amex.com)

**Pages to visit:**
- Dashboard → Membership Rewards balance
- Benefits → credit usage (Resy, digital entertainment, hotel, lululemon, Uber, airline incidental, CLEAR, Walmart+, Uber One)
- Offers → scan for new high-value Amex Offers
- Centurion lounge / Sky Club spend progress ($75K tracker)

**Extract:**
- MR balance (compare to stored `mr_balance`)
- Each credit: used/remaining this period
- Spend YTD for $75K threshold
- Any new Amex Offers worth adding

### 2. Amex Blue Cash Preferred

**Pages to visit:**
- Dashboard → cashback balance
- Rewards → category breakdown (grocery YTD spend — tracking $6K cap)
- Offers → scan for Amex Offers

**Extract:**
- Cashback balance
- Grocery spend YTD (for $6K cap tracking)
- Any new offers

### 3. Citi AAdvantage Executive (citi.com)

**Pages to visit:**
- Dashboard → AAdvantage miles balance
- Benefits → credit usage (Grubhub, Lyft, Avis/Budget)
- Offers → Citi Merchant Offers (283+ shopping offers — may need scrolling)

**Extract:**
- Miles balance
- Each credit: used/remaining
- New high-value offers to enroll
- Expiring enrolled offers

**Note:** Citi's offer page lazy-loads. David may need to scroll to load all offers, or Chase can filter by category using Chrome JS execution.

### 4. Chase Sapphire (chase.com)

**Pages to visit:**
- Dashboard → UR balance, payment due
- Offers → Chase Offers (card-linked)

**Extract:**
- UR balance
- New Chase Offers to add
- Expiring offers

### 5. Discover it (myaccounts.capitalone.com)

Discover is serviced by Capital One. Sign-in is at `verified.capitalone.com/auth/signin`; credentials live in 1Password item "Capital One" (fields `txtUserID`, `txtPassword`), inject in memory via osascript, never write to disk or print.

**Navigation (verified live 2026-10-17):**
- After sign-in you land on `/accountSummary`.
- Find the button whose text is exactly `View rewards`. It is a BUTTON element, not a link: the surrounding "Explore rewards and benefits" container is a DIV with no href.
- Dispatching mousedown/mouseup/click with `bubbles:true` on that button navigates to `/Card/<opaque-token>/rewards`.

**Pages to visit:**
- `/accountSummary` → current balance
- `/Card/<opaque-token>/rewards` → rewards cash balance, rotating category status, and per-quarter earned amounts

**Extract:**
- Current balance
- Rewards cash balance
- Each quarter's rotating categories, activation status, and earned amount (of the $75 max earned per quarter)
- Any portal notice (e.g. a replacement card being issued)

**Note:** the card-linked offers page on Capital One is NOT yet mapped (only the rewards/rotating-category path is verified). Leave offer enrollment to step-02 and its current skip.

### 6. (Removed) Atlas Visa Infinite

Closed 2026-07-01 and removed from the card set (David, 2026-10-16). No walkthrough step.

---

## After All Cards

### Update Files

1. Update `card-registry.json`:
   - Points/miles balances
   - Any benefit or policy changes
   - Rotating category details

2. Update `benefits-tracker.json`:
   - All credit usage figures
   - Card-linked offers (new, expired, savings)
   - Spend threshold progress
   - Set `last_updated` to today

3. Update `optimization-guide.json`:
   - If any category recommendations changed
   - If any new portfolio gaps or closures identified

### Report

Present a change summary:
```
## Walkthrough Complete — [Date]

### Changes Detected
- [Card]: [what changed]
- [Card]: [what changed]

### New Offers Added
- [Card]: [offer details]

### Files Updated
- card-registry.json ✓
- benefits-tracker.json ✓
- optimization-guide.json ✓ (if changed)

### Next Review: [1st of next month]
```

## Completion

Workflow complete. All data files refreshed.
