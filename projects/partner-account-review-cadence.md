# Partner & Account Review Cadence — Design Doc

**Owner:** David O'Hara | **Prepared by:** Chase | **Date:** 2026-07-30
**Trigger:** Austin Ledesma (Solace) lunch + recap email, 2026-07-29 — "Solace + Improving | Building the Partnership | Recap & Next Steps"
**Status:** Proposal — awaiting David's sign-off before instituting or replying to Austin

---

## 1. Bottom Line

Two things need a heartbeat that don't have one today: partner co-sell alignment (Solace now, Confluent and Microsoft/SME&C already exist informally) and named-account plan maintenance (CBRE, Constellation, Schwab, and the rest of `accounts/`). Neither needs a new meeting series bolted onto an already-full week. Both need to plug into rhythm that already exists — Rock 4 tracking, rock-review, and the quarterly review language already written into the account plans themselves.

**Recommendation in one line:** bi-weekly Solace sync (Confluent stays separate), a new monthly 30-minute partner-and-pursuit roll-up (data Chase already pulls, reviewed for decisions — not re-pulled), and a quarterly named-account deep-review rotation timed to rock-review week.

---

## 2. What Already Exists (don't duplicate this)

| Cadence | Meeting | Covers | Gap |
|---|---|---|---|
| Daily | Standup, Sales & Recruiting | Tactical | — |
| Weekly (Tu/Th/Fr) | Sales 2.0 | General sales motion | Not partner- or named-account-specific |
| Weekly (Mon 7am, automated) | `rock4-pipeline-weekly` | Pulls co-sell pipeline ($15M target) + 90-day weighted pipeline into Obsidian | Data collection only — no discussion, no decisions, no account-plan linkage |
| Monthly | One Texas Sales Update | Regional sales performance | Not partner-alignment or account-plan specific |
| Monthly | Dallas VP, Delivery VPs, SPARC/GRO Connect | Org management | Not this |
| Quarterly | `rock-review` | Grades all rocks (including Rock 4) against evidence | Grades the number — doesn't manage the relationships or the named-account plans that produce it |

**The gap:** nothing today reviews partner relationship health (Solace/Confluent/Microsoft) or walks the named-account plans on a fixed rhythm. Rock4-pipeline-weekly is a data pull, not a review. Rock-review is quarterly and rock-level, not account- or partner-level. Sales 2.0 and One Texas Sales Update are regional sales motion, not this.

---

## 3. Proposed Cadence

### Tier 1 — Bi-weekly: Solace Partner Sync (new, external)
- **30 minutes**, standing, per Austin's ask.
- Attendees: David + Austin (+ relevant Solace/Improving reps by topic).
- Agenda: joint-target movement (CBRE, Texas Stock Exchange, S&P Global, Caterpillar, Entergy, PepsiCo, Toyota), Schwab (joint-owned) check-in, any live intro asks.
- **Confluent and Microsoft/SME&C are NOT folded into this.** See Section 5 — different relationship stage, different contacts, folding them in dilutes the Solace-specific agenda Austin is asking for.

### Tier 2 — Monthly: Partner & Pursuit Roll-Up (new, internal, 30 min, David + Chase)
- Sits between the weekly Rock 4 data pull and the quarterly rock-review grade.
- Reviews (does not re-pull) the last 4 weeks of `Rock 4 - Pipeline Snapshots.md` for trend, plus a scan across all partner syncs (Solace bi-weekly, Confluent, Microsoft/SME&C, **SpaceXAI/Cole Estrate**) for movement on joint targets.
- Flags: partner accounts that have gone stale, named accounts that need to escalate to the quarterly deep-review early, any Rock 4 gap-trend risk before it hits rock-review.
- This is the "so what" layer on top of the automated weekly pull — not a new data source.

### Tier 2a — SpaceXAI (Cole Estrate): light-touch addition, added 2026-07-30
- David's interactions with Cole Estrate (xAI/SpaceXAI) have been happening organically — several already captured via Plaud ingest (e.g. Jun 22 recording, and at least one of the 2026-07-29 recordings appears to touch a "startup journey" topic that may be Cole). These have not been rolled into any partner tracking until now.
- **No new standing meeting** — Cole's cadence is relationship-driven, not calendar-driven like Solace's. Instead: every plaud-ingest run should tag Cole Estrate interactions distinctly (Knox — flag this speaker when identified), and the monthly roll-up (Tier 2) pulls those tagged interactions into the partner scan alongside Solace/Confluent/Microsoft.
- SpaceXAI/xAI is already on Improving's fixed 8-partner account-plan methodology list — this formalizes David's personal relationship with Cole as the active thread for that partner, the same way Nada/Lowell are the active threads for Microsoft.
- Escalate to a real standing sync only if/when a joint account play materializes — until then, tracking (not a new meeting) is the right weight.

### Tier 3 — Quarterly: Named-Account Deep-Review Rotation (new, internal, timed to rock-review week)
- Matches the cadence the account plans already call for. Constellation's own 30/60/90 plan recommends "a quarterly account review" as a Day-90 milestone; CBRE's plan structures itself the same way (phased Access → Prove → Expand → Partner path checked at intervals).
- Rotate through the full named-account list each quarter (CBRE, Constellation Energy, Schwab, Systemic Compliance, Santa's Wonderland, Nexben, LiftNet, Builders FirstSource, Tenet Healthcare, and the rest of `accounts/`) — prioritize by 9-box classification (SIGNIFICANT accounts first: CBRE, Constellation) and by partner-overlap accounts (CBRE, Schwab, Builders FirstSource — all touch Solace).
- Update each `account-plan.md`'s "Immediate Next Actions" and re-run the CRM-status check where the plan flags staleness.
- Schedule this the week before or same week as `rock-review` so account-level evidence feeds the Rock 4 grade rather than the two running on separate, disconnected clocks.

**Net new meeting load: one bi-weekly external sync + one monthly internal 30-min roll-up.** The quarterly piece is a work rotation, not a new meeting — it's folded into existing quarterly rock-review week.

---

## 4. Ties to Rock 4 and Account Plan Maintenance

This is an execution mechanism for Rock 4 (Partner Co-Sell Pipeline, $15M target), not a competing initiative:

- **Rock4-pipeline-weekly** keeps pulling the number (automated, unchanged).
- **Monthly roll-up** is where David actually looks at the number with context — is it moving because of the Solace thread, stalling because a named account went cold, etc.
- **Quarterly named-account rotation** is what keeps the account plans (the actual pursuit logic behind the pipeline number) from going stale between the deep-research sessions that produced CBRE's and Constellation's plans. Right now those plans have "Immediate Next Actions" sections that nobody has a forcing function to revisit.
- **Rock-review** (quarterly, Quinn) grades the rock using evidence — this cadence is what generates that evidence on a rhythm, instead of a scramble the week rock-review runs.

---

## 5. Recommended Reply to Austin

**Cadence: bi-weekly, not monthly.** Monthly is too slow for joint-target accounts that are moving fast (see CBRE below) and for the American Airlines opening, which is time-sensitive. Bi-weekly, 30 minutes, matches what Austin proposed as the lighter option and gives enough frequency to track joint-target movement without becoming a standing tax on the calendar.

**First-meeting agenda, in order:**
1. **American Airlines / Diana introduction** — timely, given Tuesday's ground stop and Solace's United case study. Confirm with Diana Stevens first, then bring a yes/no (or a timeline) to the first sync rather than committing Diana's relationship on Austin's timeline.
2. **CBRE** — flag this as priority topic #2, not an afterthought. See Section 6 — Improving's internal CBRE work is materially ahead of a "joint target" framing and this needs to be reconciled before Solace and Improving start co-selling into the same account from different starting points.
3. Remaining joint targets (Texas Stock Exchange, S&P Global, Caterpillar, Entergy, PepsiCo, Toyota) — quick status round-robin.
4. Schwab — confirm what "joint-owned" means operationally today (see Section 6 — this isn't yet reflected on Improving's side).

**Confluent: keep separate, do not fold under one partner-sync umbrella.** Confluent is a different relationship (different Improving contacts, different account list, different maturity — Confluent is already a named partner in Improving's account-plan methodology; Solace isn't yet). Merging them into one recurring meeting either dilutes the Solace-specific relationship Austin is trying to build or turns a 30-minute sync into an hour covering two unrelated partner motions. Keep them on separate syncs; the monthly internal roll-up (Tier 2) is where David sees both side-by-side.

---

## 6. Flags — Read Before the First Solace Sync

**Schwab — joint-owned per Austin, not yet reflected in Improving's own tracking.** A search of `accounts/Schwab/account-plan-pursuit-map-draft.md` and `accounts/CBRE/account-plan.md` turns up zero mentions of Solace. Improving's own account-plan methodology tracks a fixed 8-partner list per account (AWS, Microsoft, GCP, Confluent, Databricks, SpaceX/xAI, Snowflake, SAP) — **Solace isn't even on that list.** Before telling Austin "yes, we're aligned on Schwab," confirm internally: who owns the Schwab relationship on Improving's side, does that person know Solace is a co-sell partner there today, and does the account plan need a Solace row added to its partner-network section. This is a data-hygiene gap, not just a scheduling one — worth fixing before the first sync so David isn't discovering it live with Austin.

**CBRE — listed as a joint TARGET, but Improving is already far down the field.** Austin's list has CBRE as a target still to be pursued jointly. Improving's own `accounts/CBRE/account-plan.md` (July 2026, extensively researched) shows: a 9-year relationship, an active PSA since 2017, a live inbound Confluent referral thread (Rob Ogbah) already naming CBRE as his "key Confluent Cloud customer," a named CRM account owner (David), a fully mapped leadership org, and a phased entry plan already underway (Option A: Confluent Cloud Services Partner, already the lead play). This is not a cold joint target — Improving has an open door via Confluent already. Flag this to Austin directly as the first substantive topic: Improving isn't starting from zero on CBRE, and the co-sell motion should be built around the referral thread that already exists, not a fresh joint-pursuit plan. Getting this reconciled early avoids Solace and Improving showing up to CBRE with two different stories.

---

## 7. What This Doc Does Not Do

No new workflow, skill, or agent file created — this is a planning/cadence proposal for David to approve. If approved, the monthly roll-up and quarterly rotation should be formalized as workflow files by Rigby, not Chase.
