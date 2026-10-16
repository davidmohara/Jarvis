---
type: working
task_id: "card-review-2026-10-16-001"
session_id: "chase-card-review-2026-10-16"
agent-source: chase
created: 2026-10-16T15:35:54
expires: 2026-10-18T15:35:54
status: active
context: "First-ever card-review workflow run (overdue by months). Audit-only: no portal access, all figures computed from stored data files (107 to 244 days stale). Dashboard + action items + walkthrough capture list."
---

# Card Benefits Dashboard: October 2026

> **SUPERSEDED:** this run predates the freshness gate added to the workflow (2026-10-16). It should never have run on data this stale. The usage section is void; only the structural findings about the files themselves and the walkthrough capture list remain useful. Re-run this review after a card-walkthrough refreshes the data.
>
> **Correction 2026-10-16:** this run performed NO portal access. It analyzed stored JSON (benefits-tracker 107 days old; card-registry and optimization-guide 244 days old). Every usage claim below is an unverified inference from those files unless marked otherwise. Q3 Resy, Q3 lululemon, and the Atlas points were corrected by David against actual records. Only a card-walkthrough (live portal, David present) can confirm recorded activity. Logged err-20261016T203925-XMT2U0.


**Run date:** 2026-10-16
**Agent:** Chase
**Mode:** Audit-only (stored data, no live portal access)
**Status:** COMPLETE (step-01 audit + step-02 action items). Step-03 write-back BLOCKED, see below.

## Data Freshness (read this first)

| File | last_updated | Age | Verdict |
|------|-------------|-----|---------|
| `systems/credit-cards/benefits-tracker.json` | 2026-07-01 | 107 days | STALE, walkthrough required |
| `systems/credit-cards/card-registry.json` | 2026-02-14 | 244 days | STALE, walkthrough required |
| `systems/credit-cards/optimization-guide.json` | 2026-02-14 | 244 days | STALE, walkthrough required |

**This is the first time this workflow has ever run.** The monthly cadence was documented but never registered as a scheduled task (logged as `err-20261016T203341-4J8Y63`, category process-skip, unscheduled-cadence). Result: no reminder ever fired and the data aged unchecked. Everything below that depends on live portal state is flagged UNKNOWN rather than presented as current.

---

## Amex Platinum (Personal) ••••21001

Annual credits $2,484. Annual fee $0 out-of-pocket (YPO Lone Star reimburses all $1,085). Credits are pure upside.

| Credit | Annual | Used (as of) | Remaining | Resets | Deadline | Status |
|--------|--------|-------------|-----------|--------|----------|--------|
| Resy | $400 | $0 tracked | $100 (Q4) | quarterly $100 | 12/31 | Q1 $100 LOST, Q2 $100 LOST 6/30, Q3 USED (confirmed by David 2026-10-16). Q4 $100 open |
| Digital Entertainment | $300 | $30.32 (May 1) | $269.68 tracked | monthly $25 | monthly | ⚠️ Only WSJ used. ~$120 uncaptured Jan-Jun. Jul-Oct UNKNOWN |
| Hotel FHR/THC | $600 | $0 | $300 (H2) | semi-annual $300 | 12/31 | ⚠️ H1 $300 LOST 6/30. H2 $300 open, 76 days left |
| lululemon | $300 | $0 | $75 (Q4) | quarterly $75 | 12/31 | Q1 $75 LOST, Q2 $75 LOST 6/30, Q3 NOT used (forfeited, confirmed by David 2026-10-16). Q4 $75 open |
| Uber Cash | $200 | $0 | $200 | annual | 12/31 | ⚠️ $0 tracked, enrollment UNKNOWN |
| Airline Incidental (AA) | $200 | $85 (May 1) | $115 | annual | 12/31 | STALE, $115 remaining as of May 1 |
| CLEAR+ | $209 | $0 | $209 | annual | 12/31 | ⚠️ $0 used. Claim if David holds CLEAR |
| Walmart+ | $155 | $0 | $155 | monthly $12.95 | monthly | ⚠️ $0 used, enrollment UNKNOWN |
| Uber One | $120 | $0 | $120 | annual | 12/31 | ⚠️ Tracker says $0, but offers log records auto-credit of $96. INCONSISTENT |

**Known credit losses to date:** Q1 Resy $100 + Q1 lululemon $75 + Q2 Resy $100 + Q2 lululemon $75 + H1 hotel $300 = **$650 lost through 6/30**. Q3 Resy was USED; Q3 lululemon was NOT used (forfeited). Confirmed by David 2026-10-16. Corrected total loss through 9/30 = **$725 (29% of $2,484)**.

**Note:** tracker row for Resy is internally inconsistent (total $400, used $0, remaining $300), which itself signals the $100 Q1 loss was folded into remaining rather than used.

## Citi AAdvantage Executive ••••9598

Annual fee $770 out-of-pocket (includes $175 authorized-user fee for Susie). Main justification is Admirals Club access.

| Credit | Annual | Used | Remaining | Resets | Status |
|--------|--------|------|-----------|--------|--------|
| Grubhub | $120 | $0 | $120 | monthly $10 | ⚠️ $0 used. Up to ~$100 uncaptured Jan-Oct |
| Lyft | $120 | $0 | $120 | monthly $10 after 3 rides | ⚠️ $0 used, conditional on 3 rides/mo |
| Avis/Budget | $120 | $0 | $120 | annual | ⚠️ $0 used |
| Global Entry/TSA | $120 / 4yr | UNKNOWN | n/a | 4yr | UNKNOWN |

**All three tracked credits sit at $0.** $360/yr of credits are not offsetting the $770 fee. Card ROI is negative on credits alone, carried by Admirals Club. Miles balance 774,255 (5/1), balance $14,654, FICO 847.

## Amex Blue Cash Preferred ••••73008

Annual fee $95 (renewed 2026-04-21). Category-bonus card, no statement credits.

| Category | Rate | Cap | Usage |
|----------|------|-----|-------|
| Grocery (US supermarkets) | 6% | $6K/yr then 1% | ⚠️ NOT TRACKED at all |
| Streaming | 6% | none | Not tracked |
| Gas | 3% | none | Not tracked |
| Transit/rideshare | 3% | none | Not tracked |

**Critical gap:** BCP grocery cap usage ($6K/yr) has no entry anywhere in the tracker. July analysis estimated ~$20K/yr grocery spend, so the $6K cap is likely hit mid-year and everything after earns 1%. This needs portal confirmation. Offers: $90 saved, 96 offers added.

## Discover it ••••8369

Rotating 5% categories, $1,500/quarter cap, activation required.

| Quarter | Categories | Status | Result |
|---------|-----------|--------|--------|
| Q1 2026 | Grocery, Wholesale Clubs, Select Streaming | Completed | n/a |
| Q2 2026 | Restaurants + Home Improvement | Completed 6/30 | ⚠️ Only $75.80 spend, $3.79 earned of $75 potential. MAJOR MISS |
| Q3 2026 | Gas Stations, Transportation, Drug Stores | Ended 9/30 | ⚠️ Activated. Actual usage UNKNOWN, no data since 7/1 |
| Q4 2026 | **TBA (unknown)** | **UNKNOWN** | ⚠️ Q4 is 16 days old. Current category and activation status both UNKNOWN |

**Critical:** the current quarter's (Q4) category is not known and activation is unverified. If not activated, David earns 1% through the window. YTD earnings were $218.28 as of 6/23. Balance $834.48, cashback available $100.24.

## Chase Sapphire ••••0209

No fee, no credits. 2x dining, 1x everything else. This is now the designated Q4 dining card after the Atlas closure. UR balance 2,933 (as of 2/14, stale). Offers: $6.39 saved, 122 available (7/1). Thin value proposition.

## Atlas Visa Infinite (CLOSED 2026-07-01)

Final points: 11,255 available + 3,289 pending = 14,544 total. Benefits forfeited on closure.

**Resolved:** the points were used to pay the card down (confirmed by David 2026-10-16). No redemption at risk.

---

## Spend Threshold Tracker

**Amex Plat $75K: ACHIEVED.** Confirmed on portal 2026-05-01. Centurion Lounge guest access + unlimited Delta Sky Club both unlocked through Jan 2028. No pace concern. This item is done.

## Card-Linked Offers

| Card | Saved to Date | Offers Added | Notes |
|------|--------------|--------------|-------|
| Amex Platinum | $350.00 | 75 + 5 | MR balance conflict: 619,381 (3/19) vs 415,951 (5/1), needs reconciliation |
| Amex BCP | $90.00 | 96 | New adds 6/1 |
| Citi AA Exec | $34.72 | ~12 | |
| Chase Sapphire | $6.39 | 2 | |
| Discover it | $218.28 (earnings) | n/a | |
| **Portfolio total (per 7/1 log)** | **$263.11** | | |

**Expiring in the next 14 days:** NONE known from stored data. All stored offer expiration dates are already in the past. Any current offers are UNKNOWN because the data is 107+ days stale.

## Upcoming Deadlines (from 2026-10-16)

**Still ahead:**
- ~2026-11-28: Amex Plat annual fee ROI review (30 days before 12/28 renewal)
- 2026-12-28: Amex Plat annual fee renewal ($695)
- 2026-12-31: Amex Plat ALL credits reset (Q4 Resy $100, H2 hotel $300, airline $115, CLEAR $209, Uber Cash/One, Walmart+): use or lose
- 2026-12-31: Citi Avis/Budget credit resets ($120)
- 2026-12-31: Discover Q4 category ends
- 2027-01-28: Citi annual fee renewal ($770)

**Already passed unnoticed (this run's catch):**
- 2026-09-30: Q3 Resy $100, USED (confirmed)
- 2026-09-30: Q3 lululemon $75, FORFEITED (confirmed)
- 2026-09-30: Discover Q3 category ended, usage unknown
- April-May 2026: numerous offers and TurboTax expired unused (already logged in Q1 post-mortem)

## Annual Fee ROI

| Card | Fee (out-of-pocket) | Value Extracted (tracked) | Verdict |
|------|--------------------|--------------------------|---------|
| Amex Platinum | $0 (YPO reimbursed) | $7.58 (stale) | Positive / infinite. $2,484 credits are pure upside |
| Amex BCP | $95 | $0 (stale, unpopulated) | Likely positive via offers + category bonuses, unverified |
| Citi AA Exec | $770 | $0 | NEGATIVE on credits. Justified only by Admirals Club |
| Discover it | $0 | $218.28 | Positive |
| Chase Sapphire | $0 | $6.39 | Positive but thin |
| Atlas Visa | $0 | closed | n/a |

---

## Action Items

### 🔴 Expiring This Year (use or lose by 12/31)
1. **Amex Plat H2 hotel credit $300** (FHR/THC) expires 12/31. Book a prepaid Amex Travel hotel stay before then.
2. **Amex Plat Q4 Resy $100** expires 12/31. Do not repeat Q1/Q2. Use at a Resy restaurant now.
3. **Amex Plat Q4 lululemon $75** expires 12/31. Buy something at lululemon now.
4. **Amex Plat airline incidental $115** (AA, as of May) expires 12/31.
5. **Amex Plat CLEAR+ $209** if David holds CLEAR, claim before 12/31.
6. **Amex Plat Uber Cash $200 / Uber One $120 / Walmart+ $155**: verify enrollment, these are monthly/auto and may be silently wasting.
7. **Citi Avis/Budget $120** expires 12/31.
8. ~~Atlas Visa points redemption~~ RESOLVED: points were used to pay the card down (David, 2026-10-16).
9. **Discover Q4 category**: identify and activate immediately. 16 days already gone.

### 🟡 Attention Needed
1. **Discover Q4 activation** is the single most time-sensitive unknown.
2. **Citi credits all at $0**: Grubhub $10/mo and Lyft $10/mo are being left on the table every month.
3. **Amex Plat Q3** resolved by David 2026-10-16: Resy used, lululemon forfeited ($75).
4. **BCP grocery cap**: no tracking exists. Confirm whether the $6K cap was hit.
5. **Citi annual fee renewal 2027-01-28** ($770), just past the 90-day flag window. ROI decision needed.
6. **Amex Plat annual fee renewal 2026-12-28** ($695), ROI review due ~11/28.

### 🟢 Optimization Opportunities
1. **Discover Q2 was a $75-potential miss ($3.79 earned).** Route dining/gas to the active rotating category aggressively.
2. **Portfolio gap**: no 2% flat-rate card for insurance ($24K+/yr earning 1x). ~$240/yr opportunity.
3. **Chase Sapphire** has a thin value proposition. Consider product change to Sapphire Preferred.
4. **Amex Plat MR balance conflict** (619,381 vs 415,951) needs reconciliation.
5. **YNAB-first offer selection** was never integrated (`workflow_improvements.ynab_first` still PENDING_INTEGRATION).

---

## Step-03 Write-Back: BLOCKED

Step-03 calls for writing updates back to `systems/credit-cards/benefits-tracker.json`, `optimization-guide.json`, and `card-registry.json`, plus routing alerts to Chief via OmniFocus.

**Blocked for two independent reasons:**
1. **No fresh portal data exists.** This run had no portal access, so there are no "new usage entries," refreshed offers, or updated spend progress to write. Writing anything would mean inventing data.
2. **The authorized vault write path is unreachable.** These files live under `systems/`, which is Obsidian-vault-resident. Per the agent data-requirements rule, vault files must be written with the Obsidian MCP write tools, never the Write tool. The Obsidian MCP server failed to connect this session (ECONNREFUSED), and the OmniFocus MCP also failed (needed for the step-03 Chief alert tasks).

**Precise pending write-backs for when the walkthrough produces fresh data:**
- `benefits-tracker.json`: refresh all `benefits_usage` for Amex Plat (Resy Q3/Q4, lululemon Q3/Q4, H2 hotel, digital entertainment, airline, CLEAR, Uber Cash/One, Walmart+), Citi (Grubhub/Lyft/Avis monthly), Discover Q3 actual + Q4 category; add a `monthly_review_log` entry for 2026-10-16; reconcile the MR balance conflict; resolve the Uber One $0 vs $96 contradiction; add the BCP grocery-cap usage field (currently absent).
- `optimization-guide.json`: dining `best_card` still points to the CLOSED Atlas Visa. Must be reassigned (Chase Sapphire 2x for Q4, Discover when rotating). All Atlas references are dead.
- `card-registry.json`: Discover `rotating_categories` Q4 is still "TBA". Update once known. Registry already reflects the Atlas closure.
- Do NOT bump `last_updated` on any file until a real portal walkthrough occurs. Bumping it now would falsely clear the staleness flag.

**Next run:** the walkthrough (`card-walkthrough` workflow) is required to clear the staleness. `card-review` is also not registered as a scheduled task and should be, so this never silently ages again.
