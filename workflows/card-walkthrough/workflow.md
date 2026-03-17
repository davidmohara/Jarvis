---
name: card-walkthrough
description: Guided monthly walkthrough of each card portal to capture current benefit details, update stored data, and discover new offers
agent: chase
---

<!-- system:start -->
# Card Optimizer — Site Walkthrough

**Goal:** Read live data from each card's portal, compare against stored values, capture changes, and update all three data files. Produces a fresh, accurate benefits tracker.

**Agent:** Chase

**Cadence:** Monthly — triggered after the monthly benefits review when data is >30 days stale.

**Time required:** ~20 minutes with David present for login steps.

**Chrome access:** Chase reads pages via Chrome automation (AppleScript JS execution). Setup already enabled: Chrome → View → Developer → Allow JavaScript from Apple Events.
<!-- system:end -->

---

<!-- system:start -->
## INITIALIZATION

### Prerequisites

- David must be available to log into card portals on his Mac
- Chrome must be open
- All three data files must be read before starting:
  - `systems/credit-cards/card-registry.json`
  - `systems/credit-cards/benefits-tracker.json`
  - `systems/credit-cards/optimization-guide.json`
- Note `last_updated` date in each file — this establishes the baseline for "what changed"

### Card Inventory

| Card | Data Source | Login Required | Portal URL |
|------|-------------|----------------|------------|
| Amex Blue Cash Preferred | YNAB + portal | David logs in | americanexpress.com |
| Amex Platinum (Personal) | Portal (statement parsing) | David logs in | americanexpress.com |
| Citi AAdvantage Executive | YNAB + portal | David logs in | citi.com |
| Discover it Cash Back | YNAB + portal | David logs in | discover.com |
| Chase Sapphire | YNAB + portal | David logs in | chase.com |
| Atlas Visa Infinite | Portal (statement parsing) | David logs in | atlasmoney.com |
<!-- system:end -->

---

<!-- system:start -->
## EXECUTION

Work through cards in this order. For each card, follow the same extract → compare → update pattern.

---

### Card 1: Amex Platinum

**Why first:** Most credits, most complexity, highest value card.

**Ask David to:** Navigate to americanexpress.com → Benefits tab

**Extract from portal:**
- All active credits: current balance used vs. remaining for each (Resy, digital entertainment, hotel FHR/THC, lululemon, Uber Cash, airline incidental, CLEAR+, Walmart+, Uber One)
- Membership Rewards point balance
- $75K spend threshold progress (check "Spend & Save" or similar section)
- Any new card-linked offers (navigate to Offers tab — look for new, high-value, or expiring offers)
- Any benefit changes or new benefits added since last visit

**Compare to stored values in `benefits-tracker.json`**

**Update:**
- `benefits_usage.amex-plat.*` — used/remaining for each credit
- `mr_balance` and `mr_balance_as_of` in card-registry
- `spend_threshold_tracker.amex_plat_75k.current` and recalculate remaining
- `card_linked_offers.amex-plat` — add new offers, remove expired ones
- Flag any benefit that changed (amount, reset period, eligibility)

---

### Card 2: Citi AAdvantage Executive

**Ask David to:** Navigate to citi.com → card account → Benefits

**Extract from portal:**
- AAdvantage miles balance
- Monthly credits status: Grubhub ($10/mo), Lyft ($10/mo after 3 rides), Avis/Budget ($120/yr)
- Card-linked offers: navigate to "Shop with Points" or offers section
  - Note: 283+ shopping offers — scan for new high-value or expiring relevant ones
  - Confirm enrolled offers are still active
- Any changes to benefits structure

**Update:**
- `benefits_usage.citi-aa-exec.*` — all credit usage
- `card_linked_offers.citi-aa-exec` — refresh enrolled list, add recommendations
- Flag any enrolled offers expiring within 30 days

---

### Card 3: Amex Blue Cash Preferred

**Ask David to:** Navigate to americanexpress.com → BCP account → Benefits & Offers

**Extract from portal:**
- YTD cashback earned
- Any card-linked offers (check Offers tab)
- Confirm $6K grocery cap progress (check YTD grocery spend)
- Renewal date confirmation

**Update:**
- `card_linked_offers.amex-bcp` — refresh
- Note if grocery cap is approaching (flag when within $1K of $6K)

---

### Card 4: Discover it Cash Back

**Ask David to:** Navigate to discover.com → Cashback Bonus

**Extract from portal:**
- Q1 (or current quarter) 5% category activation status — is it activated?
- Upcoming quarter category announcement (if posted)
- YTD cashback earned
- $1,500 quarterly cap progress for current rotating category

**Update:**
- `rotating_categories` in card-registry — add next quarter if announced
- `activated` status for current quarter
- Flag immediately if current quarter is NOT activated

---

### Card 5: Chase Sapphire

**Ask David to:** Navigate to chase.com → Sapphire account → Offers for You

**Extract from portal:**
- Active card-linked offers (check all categories)
- Confirm previously enrolled offers are still active / not expired
- Ultimate Rewards balance
- Note any new relevant offers (dining, travel, shopping David uses)

**Update:**
- `card_linked_offers.chase-sapphire` — refresh enrolled list
- `ur_balance` and `ur_balance_as_of` in card-registry
- Remove expired offers from active list

---

### Card 6: Atlas Visa Infinite

**Ask David to:** Navigate to atlasmoney.com → account dashboard

**Extract from portal:**
- Points balance (available + pending)
- Current top category assignment — confirm dining is still 2x (watch for changes)
- FUTURE fitness credit status ($300/yr) — used/remaining
- Any new benefits or credit changes
- Recent statement data if visible

**Update:**
- `points_balance`, `points_pending`, `points_balance_as_of` in card-registry
- `dining_current` rate — update immediately if it changed from 2x
- `benefits_usage.atlas-visa.future_fitness` — used/remaining
- If top category changed: update `optimization-guide.json → dining` recommendation

---

### Final Step — Sync All Files

After completing all cards:

1. Update `last_updated` in `benefits-tracker.json`, `card-registry.json`, and `optimization-guide.json` to today's date
2. Write a brief change log at the top of benefits-tracker:

```
## Last Walkthrough: [DATE]
Changes:
- [Card]: [What changed]
- [Card]: [What changed]
No changes: [Cards with no updates]
```

3. If any optimization guide recommendations changed (e.g., Atlas top category shifted), update `optimization-guide.json` accordingly and notify David

4. Surface a summary: "Walkthrough complete. X changes captured. [Any urgent flags]."
<!-- system:end -->

---

<!-- system:start -->
## CHANGE FLAGS — ESCALATE IMMEDIATELY

These changes require immediate action or notification to David:

- Atlas top category dropped from dining (affects every restaurant meal)
- Amex BCP grocery cap hit — switch grocery spend to Discover or Citi
- Discover quarterly category not activated — losing 5% on qualifying spend
- Any credit with <7 days remaining and significant balance unused
- New high-value card-linked offer for a vendor David uses frequently
- Any card benefit eliminated or significantly reduced
<!-- system:end -->
