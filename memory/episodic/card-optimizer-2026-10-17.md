---
type: working-archive
task_id: "card-optimizer-2026-10-17-001"
session_id: "chase-card-optimizer-2026-10-17"
agent-source: chase
created: 2026-10-17
expires: 2026-10-19
status: archived
context: "Portfolio optimization run on captured data only. No portal access this run. Analyzes the three card data files, all last_updated 2026-10-16."
date: 2026-10-17
source_file: memory/working/card-optimizer-2026-10-17.md
tags:
  - chase
  - calendar
  - omnifocus
  - travel
  - flight
  - ypo
  - credit-cards
  - rewards
  - amex
  - citi
related_people:
salience:
  score: 10
  last-promoted-check: 2026-10-30
  promoted: true
---

# Card Portfolio Optimizer: 2026-10-17

**Run date:** 2026-10-17 | **Agent:** Chase | **Mode:** Portfolio Review (skill mode 8)

**Data sources (every figure below traces to one of these):**

- `systems/credit-cards/card-registry.json` — `last_updated` 2026-10-16
- `systems/credit-cards/benefits-tracker.json` — `last_updated` 2026-10-16
- `systems/credit-cards/optimization-guide.json` — `last_updated` 2026-10-16

**Freshness:** Amex, Citi, and Chase figures were captured live from the portals on 2026-10-16. **Discover is stale** (portal migrated to Capital One, unmapped) and is labelled STALE everywhere it appears. This run performed no portal access; it analyzes the captured data. No figure below claims what a portal currently shows.

**Portfolio:** 5 active cards (amex-bcp, amex-plat, citi-aa-exec, discover-it, chase-sapphire). Atlas Visa is closed (2026-07-01, `closed_cards` record only). There is **no Amex Business Platinum** in any card data file; verified absent by grep this run.

---

## At A Glance

1. **$992 of Amex Platinum credits reset on 2026-12-31 and sit unused.** CLEAR+ $219 and Uber Cash $200 are the two biggest, both at $0 all year. This is the single largest recoverable pool.
2. **$250 of Platinum credits already lost in 2026** (Q1 Resy $100, Q1 lululemon $75, Q3 lululemon $75). Source: `benefits-tracker.json` q1_2026_post_mortem + lululemon usage_log.
3. **BCP grocery 6% cap is REACHED** ($6,000 spent). Further grocery earns 1% on BCP, and the guide's runner-up (Discover) is stale, so there is no valid high-rate grocery card for the rest of 2026.
4. **Citi credit usage is entirely UNKNOWN.** The refreshed benefits hub shows no usage figures, and the Grubhub credit is no longer listed.
5. **Portfolio-level ROI is strongly positive on an out-of-pocket basis ($865 OOP fees vs $2,222 grounded value captured)**, carried by the Platinum (YPO reimburses its $1,285 gross fee).

---

## Portfolio ROI

### Fees

| Card | Fee OOP | Fee gross | Note |
|------|---------|-----------|------|
| amex-bcp | $95 | $95 | renewal 2026-04-21 |
| amex-plat | $0 | $1,285 | $895 primary + $390 auth users, all reimbursed by YPO Lone Star |
| citi-aa-exec | $770 | $770 | $595 primary + $175 auth user (Susie) |
| discover-it | $0 | $0 | no annual fee |
| chase-sapphire | $0 | $0 | no annual fee |
| **TOTAL** | **$865** | **$2,150** | gross matches registry `total_annual_fees` 2,150 |

Source: `card-registry.json` (annual_fee_out_of_pocket / annual_fee_with_auth_users / total_annual_fees).

### Value captured YTD vs fee

Basis: rewards/cashback earned in 2026 + credits actually used + card-linked offer savings. Components not tracked are marked UNKNOWN, not estimated.

| Card | Fee OOP | Value captured YTD | Basis / caveats |
|------|---------|--------------------|-----------------|
| amex-bcp | $95 | **$727.87** | $637.87 Reward Dollars earned 2026 + $90 offer savings. Disney and Venue credits used = UNKNOWN |
| amex-plat | $0 | **$1,234.90** | $884.90 credits used YTD + $350 offer savings. Excludes 204,810 MR points earned (point value not grounded) |
| citi-aa-exec | $770 | **$34.72** | offer savings only. Credits used = UNKNOWN. Miles balance 851,936 is not YTD earnings |
| discover-it | $0 | **$218.28 STALE** | YTD earnings as of 2026-06-23. Card stale since 2026-06-01 |
| chase-sapphire | $0 | **$6.39** | offer savings only. UR 8,920 is a balance, not YTD earnings |
| **TOTAL** | **$865** | **$2,222.16** | understates: excludes all MR value, all Citi miles, and Citi/BCP credit usage |

Net on an OOP basis: **$2,222.16 captured minus $865 fees = +$1,357.16**, and this omits MR points and Citi miles entirely, so the true figure is higher. Sources: `benefits-tracker.json` annual_fee_roi + benefits_usage + card_linked_offers; `card-registry.json` reward_dollars_2026, mr_points_earned_2026.

### Recorded annual_fee_roi block (for reference, inconsistent basis)

`benefits-tracker.json` stores a per-card `value_extracted` that uses different bases per card and should not be summed as-is:

| Card | fee_oop | value_extracted (recorded) | roi_positive | Inconsistency |
|------|---------|----------------------------|--------------|---------------|
| amex-bcp | $95 | $637.87 | true | reward dollars earned, consistent basis |
| amex-plat | $0 | $7.58 | true | only David's own Jan statement charges; ignores the $884.90 credits used and $2,494 credit pool |
| citi-aa-exec | $770 | $0 | false | credits UNKNOWN, so 0 is a placeholder not a measurement |
| discover-it | $0 | $0 | true | STALE |
| chase-sapphire | $0 | $6.39 | true | offers only |

**Flag:** the Plat `value_extracted` of $7.58 materially misrepresents the card. The tracker's own note says "$2,494 in credits = pure upside. ROI is infinite." The card is not a $7.58-value card.

---

## Unused / At-Risk Credits

### Amex Platinum (source: `benefits-tracker.json` benefits_usage.amex-plat, 2026-10-16)

Total credit pool $2,494 (`card-registry.json` total_credit_value). Captured YTD $884.90. Lost $250. Remaining $1,359.10.

| Credit | Annual | Used | Remaining | Resets | At risk at 12/31? |
|--------|--------|------|-----------|--------|-------------------|
| Resy | $400 ($100/qtr) | $200 | $100 (Q4) | quarterly | YES |
| lululemon | $300 ($75/qtr) | $75 | $75 (Q4) | quarterly | YES |
| Hotel FHR/THC | $600 ($300 semi) | $300 (H1) | $300 (H2) | semi-annual | YES |
| Airline incidental (AA) | $200 | $126 | $74 | calendar year | YES |
| CLEAR+ | $219 | $0 | $219 | calendar year | YES |
| Uber Cash | $200 | $0 | $200 | calendar year | YES |
| Uber One | $120 | $96 | $24 | calendar year | YES |
| Digital Entertainment | $300 ($25/mo) | $87.90 | $212.10 annual | monthly | no, monthly ($25/mo) |
| Walmart+ | $155 ($12.95/mo) | $0 | $155 annual | monthly | no, monthly |
| **Sum of 12/31-reset at risk** | | | **$992.00** | | |
| **Sum of all remaining** | | | **$1,359.10** | | |

The $992 matches the figure established in the 2026-10-16 review (Resy 100 + lululemon 75 + hotel 300 + airline 74 + CLEAR+ 219 + Uber Cash 200 + Uber One 24). The monthly-reset pair (Digital Entertainment $212.10 remaining annual, Walmart+ $155) is a separate $367.10 that leaks month by month, not at year end.

**Zero-usage all year:** CLEAR+ ($0 of $219), Uber Cash ($0 of $200), Walmart+ ($0 of $155). Combined $574 fully unused.

### Amex BCP (source: `benefits-tracker.json` benefits_usage.amex-bcp, 2026-10-16)

| Credit | Annual | Used | Remaining | Note |
|--------|--------|------|-----------|------|
| Disney Streaming | $120 ($10/mo) | UNKNOWN | UNKNOWN | enrolled; portal shows no usage figure |
| Venue Collection | $250 | UNKNOWN | UNKNOWN | 10% on concessions, enrollment required; no usage_log |

**Routing flag (not a credit):** grocery 6% cap REACHED. Supermarket cashback $360.00 = exactly $6,000 spend. Further grocery earns 1%.

### Citi AAdvantage Executive (source: `benefits-tracker.json` benefits_usage.citi-aa-exec, 2026-10-16)

All usage figures are UNKNOWN. The portal shows none.

| Credit | Annual | Used | Resets | At risk at 12/31? |
|--------|--------|------|--------|-------------------|
| Grubhub | $120 | UNKNOWN | monthly $10 | status: NOT LISTED on refreshed hub |
| Lyft | $180 | UNKNOWN | monthly $15 | active |
| Avis/Budget | $120 | UNKNOWN | calendar year | YES |
| Inflight/Admirals | $100 | UNKNOWN | calendar year | YES (new) |
| AA Vacations | $500 | UNKNOWN | semi-annual | YES, $250 Jul-Dec half |
| Global Entry/TSA | $120 | UNKNOWN | every 4 years | n/a |

Citi `total_credit_value` = $900 (registry), excluding Grubhub and Global Entry. Up to $570 of calendar-year/semi-annual Citi credits reset on 12/31 (Avis $120 + inflight $100 + AA Vacations $250 Jul-Dec + Lyft monthly remainder) and none is confirmed used.

### Discover it and Chase Sapphire

- Discover it: no credits defined (`card-registry.json` credits = {}). STALE.
- Chase Sapphire: no credits defined (`card-registry.json` credits = {}).

---

## Category Routing Gaps

Source: `optimization-guide.json` card_selection_guide.categories + portfolio_gaps.

**Where the guide's best card is weak (all cards earn base rate):**

| Category | Guide's best | Rate | Gap |
|----------|--------------|------|-----|
| insurance | citi-aa-exec | 1x AA miles | $24K+/yr at ~1%. A 2% card would save $240+/yr. Guide calls this the biggest opportunity |
| wine_spirits | citi-aa-exec | 1x AA miles | $3,600+/yr, no bonus category anywhere |
| business_purchases_5k_plus | citi-aa-exec | 1x AA miles | no large-purchase bonus on any held card |
| dell_technology | citi-aa-exec | 1x AA miles | uncategorized spend |
| wireless_phone | citi-aa-exec | 1x AA miles | no wireless credit in portfolio |
| everything_else | citi-aa-exec | 1x AA miles | base rate only |
| dining | chase-sapphire | 2x UR | thin; CSP would be 3x |

**Where the guide routes to a card that is stale or out of scope:**

| Category | Guide's card | Problem |
|----------|--------------|---------|
| groceries_us (runner-up) | discover-it | after BCP cap reached, guide says "switch to Discover if in-season" but Discover is stale/unmapped, so no valid runner-up exists |
| wholesale_clubs | discover-it | best card is stale/out of scope |
| online_shopping | discover-it | best card is stale/out of scope |
| gas_stations_us (runner-up) | discover-it | runner-up stale/out of scope |

**Where the guide routes to a card not in the registry:** none. Every `best_card` and `runner_up` in `optimization-guide.json` resolves to one of the 5 active cards (verified this run). The two 2026-10-17 corrections (flights_non_aa, hotels) now point to amex-plat. No fabricated card remains.

**International:** guide routes to citi-aa-exec (no FTX). Chase Sapphire FTX is `unknown` in the registry, so the guide correctly does not treat it as a safe international card. Amex BCP must never be used abroad (2.7% FTX).

---

## Recommendations (ranked by dollar impact)

1. **Recover the $992 Platinum pool before 12/31.** Highest single item: CLEAR+ $219 (enroll/renew). Then Uber Cash $200 (add Platinum to the Uber account), hotel H2 $300 (book prepaid FHR/THC via Amex Travel), Resy Q4 $100, lululemon Q4 $75, airline incidental $74, Uber One $24. Impact: up to $992.
2. **Stop the monthly Platinum leak.** Walmart+ $155 and Digital Entertainment $212.10 remaining are monthly-reset. Enroll Walmart+ and route a $25/mo eligible subscription. Impact: up to $367.10, but only the current month is recoverable at any time.
3. **Prevent the repeat loss.** The $250 lost in 2026 was Q1/Q3 Resy and Q1/Q3 lululemon, exactly the two credits now at risk again in Q4. Add calendar reminders 2 weeks before each quarter end (the q1 post-mortem lesson).
4. **Fix the Citi blind spot.** All $900 of Citi credit value is UNKNOWN. Confirm whether Grubhub still exists (currently not listed), and whether Lyft/Avis/inflight are being used. Up to $570 resets 12/31. Retry the failed Sixt $30 offer (expires 2026-11-30).
5. **Resolve the grocery gap.** BCP cap is reached. With Discover stale, the only options are BCP at 1% or Citi at 1x miles. Re-map the Discover portal (Capital One) or accept the gap for the rest of 2026.
6. **Close the 2% flat-rate gap.** Insurance alone is $24K+/yr at ~1%. A Citi Double Cash or Wells Fargo Active Cash (2%) would add $240+/yr (guide estimate). Impact: $240+/yr.
7. **Product-change the Chase Sapphire.** Base Sapphire is 2x dining / 1x everything, no transfer partners. CSP ($95/yr) adds 3x dining, 2x travel, and transfers. Impact: modest but positive.

---

## Recommended Actions (OmniFocus offline this session)

OmniFocus MCP is disconnected; these are listed for task creation on next connect.

- [ ] Amex Plat: enroll/renew CLEAR+ to capture $219 (due 12/31)
- [ ] Amex Plat: add card to Uber account for Uber Cash $200 (due 12/31)
- [ ] Amex Plat: book prepaid FHR/THC hotel for H2 $300 (due 12/31)
- [ ] Amex Plat: use Resy Q4 $100 (due 12/31)
- [ ] Amex Plat: use lululemon Q4 $75 (due 12/31)
- [ ] Amex Plat: use AA airline incidental $74 (due 12/31)
- [ ] Amex Plat: enroll Walmart+ for $155 monthly credit
- [ ] Amex Plat: route a $25/mo subscription to Digital Entertainment
- [ ] Citi: retry Sixt $30 offer (expires 2026-11-30)
- [ ] Citi: confirm Grubhub credit status and Lyft/Avis/inflight usage
- [ ] Discover: re-map Capital One portal, capture Q4 rotating category
- [ ] Portfolio: evaluate a 2% flat-rate card for insurance

---

## Could Not Ground (UNKNOWN)

- Citi credit usage: no figures on the refreshed hub. Every Citi credit remaining is UNKNOWN.
- BCP Disney and Venue Collection credit usage: portal shows no figure.
- Discover figures: STALE since 2026-06-01. Q4 rotating category UNKNOWN.
- MR point value: 204,810 earned YTD is grounded; its dollar value is not (depends on redemption, not in the data).
- Citi AAdvantage miles earned YTD: not tracked in the registry (only the 851,936 balance).
- Chase UR earned YTD: not tracked (only the 8,920 balance).
- Chase Sapphire foreign transaction fee: `unknown` in the registry.

---

## Flags

- Plat `annual_fee_roi.value_extracted` = $7.58 materially understates the card (its own note says ROI is infinite; credits used YTD are $884.90). Recommend the field be recomputed on the same basis as the other cards.
- The 2026-10-16 card-review header cited the Plat fee as $1,085 and credits as $2,484. The registry now holds $1,285 gross fee and $2,494 credits. This run uses the registry values.
- No phantom card references found in the card data files this run (grep for "business platinum" and cross-check of all guide card IDs returned clean).
