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
| Discover it Cash Back | YNAB + Capital One portal | David logs in | capitalone.com (Discover is serviced by Capital One after the acquisition; the card's navigation flow on that site is not yet mapped) |
| Chase Sapphire | YNAB + portal | David logs in | chase.com |

<!-- system:end -->

---

<!-- system:start -->
## STATE CHECK

Read and follow `reference/state-check-protocol.md` before any execution. Workflow: `card-walkthrough`; agent: `chase`.

## EXECUTION

Read and follow each step file in order. The step files own the detailed process.

| Step | File | What It Does |
|------|------|-------------|
| 1 | `steps/step-01-walkthrough.md` | Walk each card portal in sequence, extracting credits, balances, offers, and category status; sync `card-registry.json`, `benefits-tracker.json`, and `optimization-guide.json` |
| 2 | `steps/step-02-offers.md` | Enroll card-linked offers per card, filtered against 12 months of YNAB spend; update the tracker |

Run step-02 in the same session as step-01, while the portals are still logged in. Capture and enrollment are one job, not two.

Read fully and follow: `steps/step-01-walkthrough.md` to begin.
<!-- system:end -->

---

<!-- system:start -->
## RULES — OFFER MANAGEMENT

### Rule 5: Offer Recommendations Must Be Filtered Against YNAB Spend

**Before recommending or adding any card-linked offer, pull 12 months of YNAB transaction data for that card and filter the offer list to vendors where David has actual spend.** Do not recommend offers for services David doesn't use.

**Process:**
1. Pull the card's YNAB transactions with a 12-month window (the inline `curl` pattern documented in `skills/chase-card-offers-*/SKILL.md`, using `YNAB_API_TOKEN` from `config/.env`; requires YNAB_API_TOKEN — if unavailable, ask David before recommending). NOTE: the previously referenced `systems/credit-cards/scripts/ynab-card-pull.py` does not exist; the offer skills' inline curl is the working method.
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

- Amex BCP grocery cap hit — switch grocery spend to Discover or Citi
- Discover quarterly category not activated — losing 5% on qualifying spend
- Any credit with <7 days remaining and significant balance unused
- New high-value card-linked offer for a vendor David uses frequently
- Any card benefit eliminated or significantly reduced
<!-- system:end -->
