---
type: working-archive
task_id: "card-review-2026-10-16-002"
session_id: "chase-card-review-2026-10-16"
agent-source: chase
created: 2026-10-16T19:00:00
expires: 2026-10-18T19:00:00
status: archived
context: "card-review run on FRESH data. All three card files were refreshed today (2026-10-16) by a full live portal walkthrough, so the freshness gate passes. Analysis of captured data only, no portal access in this run."
date: 2026-10-16
source_file: memory/working/card-review-2026-10-16.md
tags:
  - chase
  - briefing
  - morning-briefing
  - omnifocus
  - flight
  - ypo
  - credit-cards
  - rewards
  - amex
  - citi
related_people:
salience:
  score: 10
  last-promoted-check: 2026-10-26
  promoted: true
---

# Card Benefits Dashboard: October 2026

**Run date:** 2026-10-16 | **Agent:** Chase | **Status:** COMPLETE (step-01 audit, step-02 actions, step-03 write-back and routing)

**Data source:** `systems/credit-cards/benefits-tracker.json` and `card-registry.json`, both `last_updated: 2026-10-16` (0 days old). Every figure below is taken from those files, which were refreshed today by a live portal walkthrough with David present. This run performed no portal access itself; it analyzes the captured data. The source date for all usage figures is 2026-10-16 unless stated otherwise. Discover is the one exception (see its section).

**Supersedes:** the earlier `card-review-2026-10-16` run, which was blocked on stale data and whose loss figures were wrong. This file replaces it.

---

## At A Glance (most urgent first)

1. **$992 of Amex Platinum credits sit unused as of 2026-10-16, all resetting 2026-12-31.** That is Resy Q4 $100, lululemon Q4 $75, hotel H2 $300, airline incidental $74, CLEAR+ $219, Uber Cash $200, Uber One $24. The Q4 Resy and lululemon are the same two credits David lost in Q1, so they are the repeat-offender risk.
2. **$250 of Amex Platinum credits already lost in 2026** (Q1 Resy $100, Q1 lululemon $75, Q3 lululemon $75). Note: the earlier run claimed $650 to $725 lost; today's portal-confirmed data contradicts that. See Flags.
3. **Discover data is 137 days stale and its Q4 category is unknown.** The card migrated to Capital One, the portal is unmapped, and the review cannot see it. Its figures below are from 2026-06-01 and are labelled stale, not current.
4. **Citi credit usage is entirely unverifiable.** The refreshed Citi benefits hub shows no usage figures for any credit, and the Grubhub credit is no longer listed at all.
5. **Amex Platinum annual fee ROI review is due ~2026-11-28** (renewal 2026-12-28).

---

## Amex Platinum (Personal) ••••21001

Annual credits $2,484. Annual fee $0 out-of-pocket (YPO Lone Star reimburses the full $1,085). All credits are pure upside. Source: benefits-tracker.json, 2026-10-16.

| Credit | Annual | Used (2026-10-16) | Remaining | Resets | Deadline | Status |
|--------|--------|-------------------|-----------|--------|----------|--------|
| Resy | $400 ($100/qtr) | $200 (Q2 + Q3) | $100 (Q4) | quarterly | 12/31 | Q1 $100 LOST. Q2 + Q3 used. Q4 $100 open |
| Digital Entertainment | $300 ($25/mo) | $87.90 YTD | $25 this month | monthly | monthly | WSJ is the only known sub. 3 of 9 months tracked |
| Hotel FHR/THC | $600 ($300 semi) | $300 (H1 USED) | $300 (H2) | semi-annual | 12/31 | H1 used. H2 $300 open |
| lululemon | $300 ($75/qtr) | $75 (Q2) | $75 (Q4) | quarterly | 12/31 | Q1 $75 LOST, Q3 $75 LOST. Q4 $75 open |
| Uber Cash | $200 | $0 | $200 | annual | 12/31 | zero usage YTD |
| Airline Incidental (AA) | $200 | $126 | $74 | annual | 12/31 | on pace |
| CLEAR+ | $219 | $0 | $219 | annual | 12/31 | zero usage YTD |
| Walmart+ | $155 ($12.95/mo) | $0 | $155 | monthly | monthly | zero usage YTD |
| Uber One | $120 | $96 | $24 | annual | 12/31 | nearly captured |

**Zero-usage flags:** Uber Cash $0, CLEAR+ $0, Walmart+ $0. **Past-midpoint flags:** hotel H2 $300 remaining (H2 is 3.5 months in), lululemon Q4 $75 and Resy Q4 $100 (Q4 just opened, watch them).

**Confirmed losses to date: $250** (Q1 Resy $100, Q1 lululemon $75, Q3 lululemon $75). H1 hotel was used, not lost.

**Unused and at risk of a 12/31 reset (not yet lost): $992** = Resy Q4 100 + lululemon Q4 75 + hotel H2 300 + airline 74 + CLEAR+ 219 + Uber Cash 200 + Uber One 24.

## Citi AAdvantage Executive ••••9598

Annual fee $770 out-of-pocket (includes $175 authorized-user fee for Susie). Value is carried by Admirals Club access, not credits. Source: benefits-tracker.json + card-registry.json, 2026-10-16.

| Credit | Annual | Used | Remaining | Resets | Status |
|--------|--------|------|-----------|--------|--------|
| Grubhub | $120 | UNKNOWN | UNKNOWN | monthly $10 | NOT LISTED on the refreshed benefits hub (2026-10-16). Status unclear |
| Lyft | $180 ($15/mo) | UNKNOWN | UNKNOWN | monthly | Enhanced to $180/yr (was $120). No usage figure on portal |
| Avis/Budget | $120 | UNKNOWN | UNKNOWN | annual | Confirmed still active. No usage figure on portal |
| Inflight / Admirals | $100 | UNKNOWN | UNKNOWN | annual | NEW benefit. No usage figure on portal |
| AA Vacations | $500 ($250 semi) | UNKNOWN | UNKNOWN | semi-annual | NEW benefit. No usage figure on portal |
| Global Entry / TSA | $120 / 4yr | UNKNOWN | n/a | 4yr | UNKNOWN |

**Every credit usage figure is UNKNOWN. The portal does not display them.** $900 of credits (Lyft 180 + Avis 120 + inflight 100 + AA Vacations 500) are tracked but unverified. Grubhub ($120) is no longer listed, so treat it as at risk of having been removed.

**Account:** miles 851,936; Loyalty Points 232,718 (AAdvantage Executive Platinum, highest tier); balance $21,625.49; available credit $14,310.15; limit $40,000; payment due **2026-10-24**; remaining statement $14,591.02; minimum due $148; FICO Bankcard 832 (as of 2026-09-22).

**Card refresh 2026-10-16:** NEW $100 inflight/Admirals credit, $500 AA Vacations credit, Omni Champion Status (enrollment required), Omni Free Night Award; ENHANCED Lyft to $180/yr, 12X hotels and rental cars on AA.com (was 10X), up to 40,000 bonus Loyalty Points (was 20,000).

## Amex Blue Cash Preferred ••••73008

Annual fee $95 (renewed 2026-04-21). Category-bonus card. Source: benefits-tracker.json + card-registry.json, 2026-10-16.

| Category | Rate | Cap | 2026 spend (implied) | Cashback earned | Status |
|----------|------|-----|----------------------|-----------------|--------|
| US supermarkets | 6% | $6,000/yr then 1% | $6,000 | $360.00 | **CAP REACHED**. Further grocery earns 1% |
| Streaming | 6% | none | $1,755.67 | $105.34 | active |
| Gas stations | 3% | none | $584.67 | $17.54 | active |
| Transit | 3% | none | $0 | $0.00 | no usage |
| Everything else | 1% | none | $18,458 | $184.58 | |

**Reward Dollars:** balance $188.94; earned 2026 $637.87; used $536.03; pending $64.18.

**New benefit:** $120/yr Disney Streaming Credit ($10/mo on Disney+, Hulu, ESPN), enrollment shows "Enrolled". No usage figure displayed on the portal, so usage is UNKNOWN. Venue Collection ($250/yr, 10% on concessions) also has no usage figure.

**Change flag:** the $6K grocery cap is reached. Route further grocery spend to Discover (if grocery is its rotating category) or Citi.

## Discover it ••••8369  [STALE, DO NOT TREAT AS CURRENT]

**This card was SKIPPED in the 2026-10-16 walkthrough** (migrated to Capital One, portal unmapped). Everything below is from the last read on **2026-06-01, 137 days old**, and is labelled stale. It is not current.

| Quarter | Categories | Status (as of 2026-06-01) |
|---------|-----------|---------------------------|
| Q1 2026 | Grocery, Wholesale Clubs, Select Streaming | Completed |
| Q2 2026 | Restaurants + Home Improvement | Completed 6/30. Only $75.80 spend, $3.79 earned |
| Q3 2026 | Gas, Transportation, Drug Stores | Activated, ended 9/30. Actual usage UNKNOWN |
| Q4 2026 | **TBA** | **UNKNOWN. Current category and activation both unknown** |

Stale balances (2026-06-01): balance $834.48, available credit $21,798, cashback available $100.24. **The current quarter's category is unknown and activation is unverified.** Until the portal is re-mapped, this card cannot be optimized.

## Chase Sapphire ••••0209

No fee, no credits. 2x dining, 1x everything else. Source: benefits-tracker.json, 2026-10-16.

- UR balance **8,920** (carried from a prior read; the Ultimate Rewards portal redirected to chase.com home on 2026-10-16, so it was NOT re-read live).
- Balance $370.21; available credit $100,027.79; limit $100,398; payment due 2026-11-07.
- VantageScore 801 (as of 2026-10-13).
- Chase Offers: 106 available, $6.39 saved to date, 0 added, 0 expiring. Zero offers matched the 14 Sapphire YNAB payees, so nothing was added.

## Closed: Atlas Visa Infinite

Closed 2026-07-01. Final points (11,255 available + 3,289 pending) were used to pay the card down, confirmed by David. No redemption at risk. No longer an active card.

---

## Spend Threshold Tracker

- **Amex Platinum $75K: ACHIEVED.** Confirmed on the portal 2026-05-01. Centurion Lounge guest access and unlimited Delta Sky Club are both unlocked through 2028-01-31. No pace concern.
- **Citi $150K spend threshold (unlocks 5x on AA purchases): NOT TRACKED anywhere.** No current-spend or pace figure exists for it. UNKNOWN.

## Card-Linked Offers

| Card | Saved to date | Currently added | Available | Notes |
|------|---------------|-----------------|-----------|-------|
| Amex Platinum | $350.00 | 9 (75+ historically) | n/a | 3 hotels added 2026-10-16 |
| Amex BCP | $90.00 | 6 | 99 | 23andMe + Hollywood Feed added 2026-10-16 |
| Citi AA Exec | $34.72 | 0 enrolled | 34 | Walmart + Home Depot added 2026-10-16 |
| Chase Sapphire | $6.39 | 0 | 106 | nothing matched the payee list |
| **Portfolio total** | **$481.11** | | | |

**Expiring within ~2 weeks (by 2026-10-31):**
- Amex BCP: 23andMe $10 back on $10+ (10/31), plus Cracker Barrel, CVS, Dollar General 10% up to $5 to $6 (all 10/31).
- Amex Platinum: Wyndham Hotels $20 back on $100+ (10/31).
- Citi: Walmart $5 back (10/31), The Home Depot $5 back (10/31).
- Citi merchant offers at ~15 days: BP $5, Avis $30, Macy's $5, Sunoco 3%, Burger King $5, Splendid Spoon, Fulton Fish Market $20.
- Amex Platinum: NFL Sunday Ticket offer expired today (2026-10-16).

## Upcoming Deadlines

- **2026-10-24:** Citi payment due ($148 minimum; $14,591.02 statement balance outstanding).
- **2026-10-31:** offer cluster above.
- **2026-11-30:** Citi Sixt $30 offer expires. Enrollment failed twice on 2026-10-16 (Citi backend error); retry if still wanted.
- **2026-12-28:** Amex Platinum annual fee renewal. ROI review due ~2026-11-28.
- **2026-12-31:** Amex Platinum credits reset (Resy Q4 $100, lululemon Q4 $75, hotel H2 $300, airline $74, CLEAR+ $219, Uber Cash $200, Uber One $24). Citi Avis/Budget resets.
- **2027-01-15:** Amex Platinum Hotels.com offer ($125) expires.
- **2027-01-28:** Citi annual fee renewal ($770). ROI review due.

## Annual Fee ROI

| Card | Fee (out-of-pocket) | Value extracted (tracked) | Verdict |
|------|---------------------|---------------------------|---------|
| Amex Platinum | $0 (YPO reimbursed) | $7.58 (stale, from January) | Positive. $2,484 credits are upside |
| Amex BCP | $95 | tracker says $0, but 2026 Reward Dollars earned = $637.87 | Positive in reality; the tracker field is stale. See Flags |
| Citi AA Exec | $770 | tracker says $0 (credits unverifiable) | Negative on credits; carried by Admirals Club |
| Discover it | $0 | $218.28 (stale, 2026-06-23) | Positive |
| Chase Sapphire | $0 | $6.39 | Positive but thin |

Renewal inside 90 days (by 2027-01-14): **Amex Platinum (2026-12-28)**. Citi (2027-01-28) is just outside.

---

## Action Items

### Expiring This Month (by 2026-10-31)
1. Amex BCP 23andMe $10 back on $10+ offer expires 10/31 (added today). Use it if a 23andMe purchase is planned.
2. Amex Platinum Wyndham Hotels $20 back on $100+ expires 10/31.
3. Citi Walmart $5 and The Home Depot $5 offers expire 10/31.
4. Amex BCP Cracker Barrel / CVS / Dollar General 10% (up to $5 to $6 each) expire 10/31, not added.
5. Citi payment due 10/24 ($148 minimum).

### Attention Needed
1. Amex Platinum Uber Cash $200, CLEAR+ $219, and Walmart+ $155 show $0 usage. Verify enrollment and use them; they reset 12/31 (Walmart+ monthly).
2. Amex Platinum hotel H2 $300, Resy Q4 $100, lululemon Q4 $75, airline $74 all reset 12/31.
3. Amex BCP grocery 6% cap reached. Move grocery spend off BCP to Discover or Citi.
4. Discover Q4 category is unknown and the portal is unmapped. This is the biggest blind spot in the portfolio.
5. Citi credit usage is entirely unverified. Confirm Grubhub, Lyft, and Avis status on the next walkthrough.
6. Amex Platinum annual fee renewal 12/28; ROI review due ~11/28.

### Optimization Opportunities
1. Enroll Omni Champion Status and use the new Citi AA Vacations $500 and inflight $100 credits.
2. Citi has 34 merchant offers and 0 enrolled. Enrolling Lyft 10% stacks with the $15/mo Lyft credit.
3. Chase Sapphire matches none of the payees; its value is thin. Consider a product change to Sapphire Preferred.
4. Portfolio gap: no 2% flat-rate card for large uncategorized spend (insurance is $24K+/yr at 1x, about $240/yr missed).
5. Add a spend-pace tracker for the Citi $150K threshold.

---

## Data Contradictions and Flags (structural facts about the files)

1. **Prior loss figure was wrong.** The earlier run said $650 to $725 of Amex Platinum credits were lost. Today's portal-confirmed data shows H1 hotel USED and Q2 Resy + Q2 lululemon USED. Actual confirmed losses are **$250** (Q1 Resy, Q1 lululemon, Q3 lululemon). This is exactly the stale-data error the freshness gate was added to prevent.
2. **CLEAR+ amount disagrees between files.** card-registry.json says $209; benefits-tracker.json says $219. Registry `total_credit_value` ($2,484) is built on $209. Needs one source of truth.
3. **BCP ROI field is stale.** benefits-tracker.json marks amex-bcp `roi_positive: false` with `value_extracted: 0`, but the card earned $637.87 in Reward Dollars in 2026. The field was never populated.
4. **Citi enrolled-offer contradiction.** `currently_enrolled_offers: 0` but the `enrolled` array lists 14 entries (including Walmart and Home Depot added today).
5. **Amex Platinum annual fee conflict.** card-registry.json says the fee is $695; an existing OmniFocus task says "fee jumping to $895 on Dec 28". One is wrong; cannot verify without a portal read.
6. **Grubhub is orphaned.** The credit is not listed on the refreshed Citi benefits hub, yet optimization-guide.json still routes Grubhub to Citi and an OmniFocus task still says to use it. Status unclear.
7. **optimization-guide.json references a card not in the registry.** Flights and hotels route to "amex-biz-plat", which is not in card-registry.json's card list.
8. **Discover is stale by definition** (portal unmapped) and its Q4 category is still "TBA".
9. Minor: Chase Offers count reads 107 in one field and 106 in another; optimization-guide "american_airlines" note still says 10x while the card is now 12x.

## What I Could Not Ground (UNKNOWN)

- Any Citi credit usage figure (portal shows none).
- Discover current category, activation, balance, and earnings (stale since 2026-06-01).
- Amex BCP Disney Streaming Credit and Venue Collection usage (no figures on portal).
- Chase Sapphire UR balance for today (UR portal redirected; 8,920 is carried from a prior read).
- Amex Platinum annual fee amount ($695 vs $895 conflict).
- Citi $150K threshold pace (no tracker field).
- Whether David holds CLEAR (determines if the $219 is usable).

---

## Step-03 Write-Back and Routing

- **Dashboard:** this file, `memory/working/card-review-2026-10-16.md`.
- **Workflow state:** `workflows/card-review/state.yaml` updated to complete.
- **Benefits tracker:** a `monthly_review_log` entry for 2026-10-16 was appended recording this run. No usage figures were written back (the walkthrough already refreshed them today; this run has no new portal data to add).
- **OmniFocus tasks:** created in the "Credit Cards" project for the Amex Platinum credits that have no existing task (Resy Q4, lululemon Q4, CLEAR+). The hotel H2, airline, annual-fee-review, and Uber Cash items already had open tasks and were not duplicated.
- **Chief routing:** the time-sensitive items above are flagged here for the morning briefing. See the run report for the routing detail.

**Next:** the monthly cadence is walkthrough on the 1st, review on the 2nd. A walkthrough is recommended to re-map the Discover portal (Capital One) and to confirm the Citi credit usage figures.
