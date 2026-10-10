---
name: card-walkthrough
description: Guided monthly walkthrough of each card portal to capture current benefit details, update stored data, and discover new offers
agent: chase
model: sonnet
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
## STATE CHECK

Read and follow `reference/state-check-protocol.md` before any execution. Workflow: `card-walkthrough`; agent: `chase`.

## EXECUTION

Read and follow the step file. It walks each card portal in sequence, extracting credits, balances, offers, and category status, then syncing `card-registry.json`, `benefits-tracker.json`, and `optimization-guide.json`.

Read fully and follow: `steps/step-01-walkthrough.md` to begin.
<!-- system:end -->

---

<!-- system:start -->
## RULES — OFFER MANAGEMENT

### Rule 5: Offer Recommendations Must Be Filtered Against YNAB Spend

**Before recommending or adding any card-linked offer, pull 90 days of YNAB transaction data for that card and filter the offer list to vendors where David has actual spend.** Do not recommend offers for services David doesn't use.

**Process:**
1. Run `systems/credit-cards/scripts/ynab-card-pull.py` for the card being reviewed (requires YNAB_API_TOKEN — if unavailable, ask David before recommending)
2. Extract the top payees from YNAB output
3. Cross-reference against available offers — only surface offers where the vendor appears in David's actual spend history
4. For vendors with no YNAB history, do not recommend unless David explicitly asks

**What this prevents:** Recommending offers for DirectTV, Starlink, Tonal, Eight Sleep, or other services David doesn't subscribe to — which creates noise and wastes review time.

Rationale: A 35% offer on a service you don't use is worth $0. Filter first, then present.
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
