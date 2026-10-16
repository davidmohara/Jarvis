---
status: not-started
started-at: ~
completed-at: ~
model: sonnet
---

---
step: 2
name: offers
description: Enroll card-linked offers across each card, filtered against YNAB spend
next: ~
---

# Step 2: Offer Enrollment

## EXECUTION PROTOCOL

**Agent:** Chase, spawned by the coordinator, never executed inline.

Run this step immediately after step-01, in the same session, while the card portals are still logged in. Data capture and offer enrollment are two halves of one job: the walkthrough knows what David actually spends on, and that is exactly the filter the offers need.

## Why this step exists

The offer skills (`chase-card-offers-*`) used to run separately and went dark (last run 2026-06-01). Tying them to the walkthrough means they run monthly, with fresh YNAB data and live sessions, instead of being forgotten.

## Process

For each card with a live session, in this order:

1. **Amex (Platinum ••••21001 and Blue Cash Preferred ••••73008)** — follow `skills/chase-card-offers-amex/SKILL.md`.
2. **Citi AAdvantage Executive ••••9598** — follow `skills/chase-card-offers-citi/SKILL.md`.
3. **Chase Sapphire ••••0209** — follow `skills/chase-card-offers-chase/SKILL.md`.
4. **Discover** — SKIP. Discover is serviced by Capital One now and the portal is not mapped (err-20261016T210131-BI38IK). Do not run the discover offer skill.

For each card:

1. **Read every available offer** on the portal's offers page, noting which are already enrolled and which are new.
2. **Pull YNAB spend for that card through the YNAB MCP connector** (`get_accounts` then `get_transactions_by_account`) with a **12-month lookback** (not 90 days). A merchant bought from at any point this year is a legitimate target. If the MCP is unavailable, fall back to inline curl with `YNAB_API_TOKEN` from the repo's `config/.env`.
3. **Filter**: only add offers where the vendor appears in YNAB spend history, or where spend is highly probable from known patterns (e.g. hotels and travel on the Platinum). Do not add offers for services David does not use.
4. **Add the qualifying offers** via the skill's enrollment flow.
5. **Confirm each enrollment on the page** ("Added to Card") before moving on. Do not report an offer as added unless the page confirms it.

## Single-Enrollment Offers

Some offers can only be added to one card. Default: **BCP for everyday spend** (grocery, streaming, fuel), **Platinum for hotel, travel, and luxury**. Pick the card David is more likely to trigger the offer on.

## Update After Enrollment

Update `systems/credit-cards/benefits-tracker.json`:

- `card_linked_offers.<card>.last_reviewed` to today
- `card_linked_offers.<card>.offers_added` with the count added this run
- Add newly enrolled offers to `newly_added_[DATE]` arrays
- Add urgent expirations to `upcoming_deadlines`

## Report

```
## Offer Enrollment — [Date]

### Added
- [Card]: [merchant] — [offer terms], expires [date]
- ...

### Skipped (no YNAB spend)
- [Card]: [merchant] — no matching spend in 12 months

### Skipped (portal not mapped)
- Discover — Capital One migration
```

## Completion

Workflow complete when every mappable card has had its offers reviewed and enrolled, and the tracker is updated.
