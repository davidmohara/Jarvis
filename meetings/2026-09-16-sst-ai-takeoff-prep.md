# Call Prep: AI Takeoff Weekly Touch — Improving & Simpson Strong-Tie (Recurring Client Leadership Sync)

**10:00–10:45 AM CDT (45 min) | Microsoft Teams | Ongoing engagement — weekly cadence; David is executive sponsor, not the day-to-day owner**

**Calibration note:** This is an active-client delivery sync — the recurring Wednesday Improving/Simpson Strong-Tie leadership touch — not a sales or discovery call. It is the meeting Devlin Liles asked you to cover while he steps back from go-to-market and travels. Do **not** pitch, do **not** commit to new dates in the room, and do **not** deep-dive model internals if the engineers aren't present. Your job is air cover and message discipline, not technical problem-solving. Everything in this document is drawn from this morning's internal huddle, the 2026-09-14 Devlin/O'Hara sync, and the account history — no live CRM or email thread was available at build time beyond the Devlin note cited below.

## Where the Engagement Stands

Simpson Strong-Tie (SST) is a confirmed Dallas **new-anchor** account for 2026 and one of the One Texas relationships you personally sponsor. The current body of work — internally called the **AI Takeoff** program — is a computer-vision and agentic system that reads construction plan sets and produces takeoffs automatically. This is the deepest AI delivery work Improving has in the account and it is under live schedule pressure.

**Architecture (know this cold, don't recite it):** A plan set flows through two parallel pipelines — (1) models that detect and do geometry, and (2) semantic extraction that OCRs text into a graph-database semantic layer. An agent then syncs both pipelines and performs quantification, takeoffs, linear geometry, and material matching. The architecture and basics were stood up by **Josh** (former Improving consultant on the account, since resigned); the system is being integrated with the SST **headers and beams** models.

**Status:**
- Headers/beams models are at **90%+ F1**. Devlin's 2026-09-15 note to Chris Miller and the StrongTie team cited **first model results north of 95%** heading into an architecture review.
- **Hosting has flipped:** SST now hosts its own production infrastructure; Improving keeps only the **GPU training infrastructure**. Production sits inside Simpson's tenant. The team had been building integration patterns as if Improving stayed in the loop long-term — Devlin corrected that on 2026-09-14, and this is a source of confusion the team is still absorbing.
- **Planned move:** take the agentic system off the DGX cluster and into **Azure Foundry** so it can integrate on the **VNet side with Aaron's team** (SST), ideally without a large rework.
- **Still outstanding:** prompt tuning, agent definition, and a one-time semantic population of ground-truth data (industry truth tables, material availability, product lists). The list Josh was compiling for the semantic layer was lost to knowledge-transfer churn when he resigned.

**What was committed to Chris this morning (7:30 AM huddle — Fernando Pereira, Jose Maureira, Devlin Liles, Lyn Barrett):** Devlin defined four deliverables owed to Chris at SST —
1. A SharePoint location holding the **model checkpoint and the verification script** (headers and beams).
2. A **timeline** for when endpoints are UAT-ready and when the first-version API lands (Devlin floated **the 21st**).
3. A **generic step-by-step model-efficacy checklist** — usable on any model, run against non-trained, SME-labeled plan sets for official scores.
4. A **full-system UAT process** for the multi-agent system once semantic layers are stood up.
Lyn owns wordsmithing items 1 and 2 into the leadership sync; items 3 and 4 follow later.

## Who They Are

| | |
|---|---|
| **Company** | Simpson Strong-Tie (Simpson Manufacturing Co.) |
| **Industry** | Structural connectors, fasteners, and building products (wood construction) |
| **HQ** | Pleasanton, California |
| **Size** | Large national manufacturer (public parent, NYSE: SSD) — exact band not verified this run |
| **Known tech stack** | Strongside AI (internal AI platform), Azure Databricks, SAP (with an in-progress PDC migration to work around SAP's third-party AI restrictions) |
| **Email domain** | strongtie.com |

Note: the invite lists dual Improving/SST addresses for Lyn Barrett (`lyn.barrett@improving.com` and `lybarrett@strongtie.com`) and Lauren Clack (`lauren.clack@improving.com` and `lclack@strongtie.com`) — these are the same two Improving people with SST-side aliases, not separate attendees.

## Company Overview

Repeat-meeting — brief refresh only. Nothing material has changed in SST's business since the last touchpoint that bears on this call; the live issue is delivery-side, not client-side. What has changed inside the engagement: the hosting boundary moved to SST (see above), and the account is still assimilating the documentation gaps left by Josh's departure. If you need deeper company background, it isn't the point of this call.

## Who's in the Room

**Improving side:**
- **Devlin Liles** — delivery lead on SST. On the invite. May or may not be present — he asked you on 2026-09-14 to cover the Wednesday leadership sync in his place.
- **Lyn Barrett** — program/delivery. Owns the messaging into the SST leadership sync and the DGX helpdesk ticket. Has been reporting status without fully understanding the ML-vs-normal-project distinction (Devlin's read).
- **Lauren Clack** — Improving.
- **David O'Hara** — you. Regional Director, One Texas. Executive sponsor, optional attendee, dialing in from Little Rock.

**SST side (titles inferred from domain and context — confirm in the room, do not assert them):**
- **Gilbert Velasquez** (organizer) — SST. Per Lyn, Gilbert is **anxious about schedule changes** and tends to press on dates in the background.
- **Chris Miller** — SST. The executive the four committed actions are owed to.
- **John Tsiros** — SST. Senior presence; Lyn flagged John and Gilbert as the ones who "pop in" with pointed questions.
- **Aaron (A. Vo)** — SST infrastructure team; the VNet integration counterpart.
- **M. Shacklett, J. Holtz, S. Reddy, G. Koutsouros, S. Lambert** — additional SST attendees on the invite.

**"Read on them":** The SST attendees are the same leadership group Devlin is trying to satisfy with dates and verification tools. Expect the room to test whether Improving's commitments are real. The tone Lyn asked the team to hold — succinct answers, defer anything uncertain back to the team rather than risk bumping heads — is the right register for you too.

## Common Connections

LinkedIn mutual connections could not be pulled for this run (no LinkedIn access in this environment). Known relationship map, for context: **Diana Stevens** is the Improving Account Manager for SST; **Devlin Liles** is the delivery lead; **Lyn Barrett** owns program messaging; the Chile/Argentina delivery team (Fernando Pereira, Jose Maureira) and **Cesar Contreras** (DGX access) are on the delivery side.

## Reason for the Call

This is the recurring weekly AI Takeoff touch between Improving and SST leadership — the same Wednesday 45-minute leadership sync Devlin described on 2026-09-14. Evidence: Devlin asked you directly to cover this Wednesday's sync in his place; you confirmed you had it ("Is this the AI takeoff weekly touch? I already have it"). Devlin also sent an email **"Today's meeting"** on **2026-09-15** to **Chris Miller / StrongTie team + David**, noting an **architecture review and first model results north of 95%**. This is not a sales-sourced call — it is delivery governance. **Do not assume** it is a status-and-thank-you; the morning huddle shows four hard commitments were made hours before this call and a deadline is five days out.

## Suggested Talking Points / Questions

1. **Open on the committed actions, not on optimism.** Reference that Improving has four deliverables in motion for Chris, and that Lyn is driving the message and the timeline into the room. This is what relieves pressure — show it exists.
2. **Frame the checkpoint + verification script as the near-term proof point.** Be explicit that it covers headers and beams only, and that the generic efficacy checklist and full-system UAT process come next. Set scope expectations so "north of 95% F1" isn't over-read.
3. **Hold the line on dates.** The 21st was floated internally, not promised in the room. If pressed, the answer is: the delivery team owns the date and we won't move it again week over week — not a new number invented live.
4. **Position the Azure Foundry / VNet move as a joint integration with Aaron's team**, not an Improving-only gate. This is the honest framing and it defuses "Improving is late."
5. **Questions to ask:**
   - "What does SST need to see this week to feel the schedule is under control?"
   - "Is the 21st a hard acceptance date on your side, or an internal Improving target?"
   - "Who on Aaron's team owns the VNet integration, and what's the sequence from your end?"
   - "If we can get Fernando and Jose real GPU access, can the 200 labeled plan sets get into training sooner?"

## Landmines / Notes

- **Don't commit to a new date in the room.** Gilbert presses on schedule; the internal team explicitly does not want this call to generate fresh dates. Defer unknowns ("let us take that back").
- **Don't let it reframe as "Improving is late."** The VNet dependency sits with Aaron's team on the SST side; keep integration framed as shared.
- **Don't deep-dive model efficacy or architecture if Devlin/Fernando aren't on the call.** You don't own the technical detail; defer rather than improvise.
- **Don't let the semantic-layer gap read as negligence.** It traces to Josh's resignation and undocumented knowledge transfer — state it factually, don't apologize for it.
- **Do not raise the "Ty" recruiting idea.** Ty now works at Simpson Strong-Tie, and Devlin flagged that trying to hire him back mid-repair job is a landmine.
- **Stay succinct.** Lyn's guidance for this room: quick answers, and hand off anything uncertain.
- **You're an optional attendee on a travel day.** If the room is fully covered and running, you can listen and reinforce; you don't need to force participation.

## Open Questions Going In

- **Whether Devlin is actually on the call today.** He's on the invite; the 2026-09-14 arrangement was that you cover the Wednesday leadership sync. Confirm at the top whether you're covering solo or both of you are present.
- **Exact SST attendee titles.** Inferred from the invite and context only — not confirmed from a source.
- **Whether Lyn filed the DGX Spark helpdesk ticket with Jacob Sponitz** before 10:00, and whether access has been granted.
- **Whether the SharePoint checkpoint/script location is stood up.** The team's target was end of day today or early tomorrow — not by this meeting.
- **The true meaning of "the 21st."** First-version API existed internally already; unclear whether the 21st refers to a first *internal* API version or an SST-infrastructure-integrated endpoint. Don't assert either.
- **SST's expectation gap.** Jose was candid internally that SST expects roughly 95% of the project integrated within a week, which the team views as unrealistic, against a February finish target. Unclear how much of that expectation will surface in this room.
