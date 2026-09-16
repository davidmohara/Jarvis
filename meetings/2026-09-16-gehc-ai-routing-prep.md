# Call Prep: GE HealthCare — AI-Driven Routing Weekly Sync

**10:30–11:00 AM CDT (15:30–16:00 UTC, verified against Mac local time Wed Sep 16 2026 09:43 CDT) (30 min) | Microsoft Teams — organizer is on the GE HealthCare tenant; David attends as a guest | Ongoing engagement — repeat meeting, you joined this account on 2026-09-11 as Tim Rayburn's replacement**

**Calibration note:** This is an existing-engagement recurring sync, not a sales call. You are the incoming Improving technical lead (ML Architect, ~5 hrs/week) on a fixed-price, $27K, 12-week AI-Driven Routing PoV for GE HealthCare's Imaging division. Do not pitch Improving services, do not horizon-expand the SOW, and do not answer architecture questions with more confidence than your onboarding supports — you have not yet been in the code, the repo, or the GEHC environment. Your job today is presence, listening, and one or two well-chosen technical questions. Also: **confirm at the top whether this meeting is even still on** (see Open Questions).

## Who They Are

| | |
|---|---|
| **Company** | GE HealthCare (contracting entity: GE Precision Healthcare, LLC) |
| **Division** | Imaging — Core Routing Validation workstream |
| **Industry** | Medical technology / medical imaging (MRI, CT, and related modalities) |
| **HQ** | Chicago, IL (GE HealthCare); this engagement's GEHC site is WSO, 3000 N Grandview |
| **Founded** | GE HealthCare spun out of GE in January 2023 |
| **Size** | Large-cap public medtech (not researched in depth for this run — this is a repeat meeting) |
| **Known tech stack** | GEHC Clinical Data Hub (primary data source per SOW); STO AI Fabric (Improving's SLM hosting layer); AWS; DICOMweb / DICOM-RS; MCP destination integration; PRISMA (with a known copy/paste limitation); GEHC-approved Git |
| **Email domain** | gehealthcare.com (external tenant — see transcript gap below) |
| **Improving side** | Improving Chicago is the contracting entity (222 S Riverside Plaza, Chicago). Patrick Emmons signed as President, Improving Chicago |

**Disambiguation note:** "GEHC" here is GE HealthCare — specifically the Imaging division of GE Precision Healthcare, LLC, contracted through Improving Chicago under SOW #22633 / PSBC02846. This is not "GE" at large and not the GE Aerospace or GE Vernova entities. The POC is scoped to one machine type within Imaging.

## Company Overview

**Depth: brief refresh (repeat meeting).** Nothing found in this run indicates a material change at GE HealthCare as a company since the engagement started on 8/31. The relevant movement is all inside the engagement itself, covered under "Reason for the Call" below. No web research was performed for this prep — the first-party artifacts (SOW, internal hand-off doc, weekly topics deck, Teams chat history) were richer and more current than anything a web search would return, and were prioritized per the client-meeting-prep ordering.

- **CRM history:** An active Dynamics opportunity exists — "GE Healthcare – AI PoC" under the GE Healthcare account (opportunity path confirmed in SharePoint metadata). Prior Improving-created assets for this pursuit include a Capabilities Overview deck, a Business & Cost deck, a Technical Proposal (v1), and a PoV Scope Comparison (v2), dating back to at least May 2026.
- **Competitive/market pressure:** None identified in the artifacts reviewed. The engagement is budget-constrained on GEHC's side rather than competitive.

## Who He Is

**Justin Holder — PM, Imaging (Project Lead), GE HealthCare.** Named GEHC Project Manager in the SOW (phone 262-309-5185, justin.holder@gehealthcare.com). Organizer of the weekly sync and the Tuesday technical deeper dive. Tone in the Teams chats is casual, collegial, and low-ego — "my head hurts" over UTC math, "point is, let's meet for a bit, but somehow I doubt we need the full hour scheduled." He has stated his top priority plainly: *"making sure Vlad is happy and efficient and no big short term questions or blockers."* He also shared on 2026-09-15 that he was having a "death-by-thousand-meetings" day and dropped off the technical call early for food.

**"Read on him":** He is a protective, pragmatic delivery lead, not a technical architect. He will care about Vlad's unblocked-ness and momentum far more than about architectural elegance. Bring him problems solved, not problems discovered.

**The other attendees on this invite:**

| Name | Role | Notes |
|---|---|---|
| **Vladimir "Vlad" Avila** | AI Engineer (Improving consultant, GEHC email) | The single engineer building the POC. Based in **Argentina** (near-shore), 40 hrs/week. Lisa Kimbrel: he is "super responsive," "detailed in his written updates," and "has mastered the use of AI to communicate effectively" in writing — **but verbally it's not as good.** His unblocked-ness is Justin's stated priority. |
| **Sandeep Kaushik** | Architect, GEHC | Lisa Barnes describes him as "their chief data guy" — and that the Clinical Data Hub is "one of his products." Senior, technically strong. He was flexible on rescheduling today ("I'm good with anything that works"). |
| **Michael Braunstein** | Architect, GEHC | On both the weekly sync and the technical deeper dive. |
| **Anthony Pezet** | Architect (Tech Lead), GEHC | **Based in France — the hand-off doc explicitly says meetings should be before noon CT.** Marked optional on the Tuesday deep dive. Did not appear in the chat traffic reviewed. |
| **Lisa Barnes** | Delivery Lead / PM, Improving | Organizer of the internal twice-weekly check-in. Your primary internal channel. |
| **Tim Rayburn** | Improving | Former Technical Lead / AI Architect on GEHC — **you are his replacement.** Still on the invite. |
| **Lisa Kimbrel** | Account Manager / Supplier PM, Improving | The SOW's named Supplier PM. She is the person who recruited you onto this account (1:1 on 2026-09-11). Not on the weekly sync invite — she is the commercial owner. |

## Common Connections

**Unavailable for this run** — no LinkedIn profile URL was surfaced in the first-party artifacts, and no browser session was invoked to pull mutual connections. Nothing is known here; treat as blank rather than as zero.

## Reason for the Call

**Meeting classification: internal-review / existing engagement (recurring cadence). Repeat meeting — first-touch depth not applicable.**

This is the standing Wednesday weekly sync on the GE HealthCare engagement *"LLM on Cloud for Imaging — Core Routing Validation."* It has run weekly since the 8/28/2026 GEHC kickoff. It is a client-facing status and demo cadence, not a sales motion — there is already a signed SOW and an active Dynamics opportunity.

Evidence cited — all first-party, from David's own mail, calendar, Teams, and SharePoint:

| Source | Evidence |
|---|---|
| **SOW (SharePoint)** | `IMPROVING CHICAGO_SOW_2026_LLM ON CLOUD FOR IMAGING.pdf` — SOW #22633 / PSBC02846, dated 17 Aug 2026 (executed 11-Aug-2026), between GE Precision Healthcare, LLC and Improving Chicago. Fixed fee, **$27,000 total** (list $54,000, halved), invoiced Oct 2026 $9,000 / Nov 2026 $18,000. Term ends **31 December 2026**. Justin Holder named GEHC PM. |
| **Internal hand-off doc (SharePoint)** | `Internal Project Hand Off GEHC.docx`, dated 8/20/2026 — names the GEHC stakeholders, the Improving team, the resource plan (ML Architect 5 hrs/wk), and the stated goal: *"Win POC > MVP work for next year. Positive impression on broader GEHC that allows us to expand outside of this team."* |
| **Teams chat — Tim Rayburn, 2026-09-08** | *"I'm going to have to step aside from the architect role here on GEHC, but I've got you an capable replacement. David O'Hara will be stepping in to pick this up."* (Cause: an NRG trainer resignation pulling Tim into NRG training and McKesson.) |
| **Teams chat — Lisa Barnes, 2026-09-08** | *"…it'd be great if you could eek out one more session with GEHC — and then we transition to David... i'm reluctant to add David to the GEHC meeting tomorrow without internal transition."* |
| **Teams meeting transcript — "Lisa & David quick chat on GE," 2026-09-11** | Lisa Kimbrel recruiting you: the POC is small (*"not even $100,000... just based on the budget they had left for this year"*), Vlad needs *"a little bit of babysitting," "a few code reviews,"* and — critically — *"we are going to need someone US-based that has really strong communication that can demo what he's doing to larger groups at GE."* Two larger demos planned: **one ~6 weeks in, one at the end.** |
| **Teams meeting recap — 2026-09-11** | Facilitator summary of the same conversation: *"David can support the US-based presence and demos, with larger demonstrations planned around week six and at the end of the POC."* |
| **Teams recap — 2026-09-15 technical deeper dive** | Facilitator notes from a meeting where the transcript is inaccessible (see gap below) — architecture locked in the direction of Clinical Data Hub → SLM inference → app adapter. |
| **Calendar** | Recurring installer from justin.holder@gehealthcare.com; original invite forwarded to the group 2026-08-28. Reference Box folder: `https://gehealthcare.ent.box.com/folder/409725693470`. |

**do_not_assume list:**

- **Do not assume you understand the architecture well enough to defend it.** You have read a Facilitator's recap, not the code, and you have no repo access yet.
- **Do not assume the meeting is happening at 10:30.** It was actively being rescheduled this morning (see Open Questions).
- **Do not pitch Improving services or expand scope.** This is a discounted, fixed-price, already-undersized engagement.
- **Do not assume the transcript gap means you missed nothing — it means you missed everything that was said.**
- **Do not assume Vlad's verbal summaries match the quality of his written updates.** Lisa flagged this specifically.
- **Do not volunteer for more than 5 hrs/week** without a conversation with Lisa Barnes and Lisa Kimbrel first; your calendar is already carrying an October boot camp, Alberta Blue Cross, and the Arkansas YPO travel block.

## Suggested Talking Points / Questions

**Where the engagement actually stands (as of the last artifacts available):**

- 12-week Proof of Value, Phase 1. Timeline: D1 Discover (Wk 1, 8/31) → D2 Design (Wk 2, 9/7) → **D3 Develop (Wks 3–6, 9/14 – 10/5) → D4 Deploy (Wks 7–8, 10/12 — the deck also renders "11/9 – 11/23" for D4 and "Phase 2 roadmap delivered" at 12/18); PoV completes 12/18.** Note the deck itself carries two inconsistent D4 renderings — the version you may be walking into has drifted.
- **SOW gating criteria:** C1 working routing agent in GEHC infra invoking the SLM and routing DICOM series; C2 evaluation harness with 50–100 labelled routing test cases; C3 MCP discovery against one real destination; C4 audit log of routing decisions; C5 add-a-destination scalability demo; C6 ReadMe + light runbook; C7 source code in a GEHC-approved Git repo; C8 detailed estimate for MVP.
- **Vlad's status (from the 2026-09-14 internal check-in):** 2–3 weeks in. The LLM routing engine and the MCP for dynamic destination routing are built. Architecture is on AWS with infrastructure-as-code, using a small language model. This week: mocking the production destination service for end-to-end testing, then prompt-engineering refinement.
- **Architecture direction (from the 2026-09-15 deep dive recap):** router receives an event when a DICOM series is available → queries the **Clinical Data Hub** for the metadata needed for inference → SLM infers a destination → the downstream **app adapter** retrieves and sends the DICOM series. The current bucket-and-queue implementation is an accepted mock; the prototype is not expected to decompose or optimize DICOM storage yet.
- **Two open design points left on the table on 9/15 — these are the sharpest questions you can ask:**
  1. **Orchestration boundary:** does the router only *select a destination*, or does it also *trigger and coordinate* the app adapter? What is the interface between them?
  2. **Data contracts:** which metadata fields does the model actually receive, and what is the application-capability data model and trigger payload for sending a study to an adapter?
- **Improvement goals stated in the deck:** better e2e performance, lower latency using a GPU, higher routing accuracy with more real examples — including experiments across different model brands (llama, Mistral, qwen).
- **Metrics/NFRs:** Accuracy, Precision, Recall, F1; latency at P50 (baseline experience), P90 (most users' worst case), P99 (tail).
- **Cadence context:** Tuesday technical deeper dive 11:00 AM–12:00 PM CDT (moved from Wednesdays); Wednesday weekly sync 10:30–11:00 AM CDT; internal Improving check-in Mondays and Wednesdays 3:30 PM CDT.

**Questions worth asking — pick two or three, not ten:**

1. *"Justin — before we start, is this slot still right, or did we land on moving today's session to Thursday?"*
2. *"On the two open design points from Tuesday — has the orchestration boundary been settled, or is that still open? I want to know whether we're converging or circling."*
3. *"Vlad — what's the one thing blocking you this week that I can actually help clear?"* (This is Justin's stated top priority; asking it in the room earns immediate credibility with him.)
4. *"What does the week-6 demo need to look like for the broader GEHC audience to take the MVP conversation seriously? I own that room."*
5. *"Sandeep — how much of the Clinical Data Hub's metadata surface are we realistically able to use for inference, versus what's governed or off-limits?"*
6. *"Where are we on PRISMA access and the repo? I'd like to be reading Vlad's code, not just hearing about it."*

**Framing for your own role:** the 2026-09-11 recruiting conversation was explicit that this is two things — technical oversight/code review of a near-shore engineer, and **executive presence in front of GEHC technical leadership at the two larger demos.** Lisa Kimbrel: *"they'll probably get the directors and VPs from those areas involved in the larger demos."* Nothing you say today needs to win the work. Everything you say today should signal that the demo room is in good hands.

## Landmines / Notes

- **Do not let the Wintrust reference reach the client.** The weekly topics deck (`GEHC_Improving AI Routing Weekly Meeting Topics 0909.pptx`, last modified 2026-09-11, posted to the meeting chat 2026-09-14) carries a header reading **"GOVERNANCE Wintrust DevSecOps Status Report – Week ending 9"** — apparently template residue from another client's deck. If this deck is being shown on the call, someone should catch it. Flag it privately to Lisa Barnes; do not raise it in front of GEHC unless it appears on screen.
- **Do not overstate your knowledge of the codebase.** You have not been in the repo. You have no VPN or PRISMA access as of the last evidence. If you are asked a question you cannot answer, say so and name who can — that reads as competent here, not weak. GEHC's team is described as laid-back, technically strong, and highly invested in the POC's success.
- **Do not confuse "5 hours a week" with "small."** You are now the technical lead of record on a fixed-price engagement with a $27K ceiling, a 12/18 completion date, a 50%-discounted rate, and explicit risk-register entries for timeline overrun and GEHC engineering bandwidth being thin. Overrun on a fixed fee is Improving's loss, and the mitigation named in the deck is literally "weekly burn tracking; scope gates."
- **Do not underestimate Vlad's communication asymmetry.** Written: excellent. Verbal: weaker. Do not put him on the spot for an unrehearsed verbal walkthrough in front of the broader GEHC audience — that is exactly the gap you were recruited to fill.
- **Do not schedule anything with Anthony Pezet after noon CT.** He is based in France; the hand-off doc calls this out explicitly. If a working session needs him, it has to be a morning-CT slot.
- **Do not treat GEHC's internal tooling rules as soft.** Risk register item #1: *"Improving should only use GEHC tools and processes approved by GEHC."* PRISMA blocks copy/paste; the Git repo must be GEHC-approved. Do not introduce tooling or workflows the client hasn't blessed — including AI tooling.
- **Do not assume the calendar time is reliable.** The whole team is churning on scheduling.
- **Regulatory sensitivity is live.** The deck contemplates a human-in-the-loop queue and an FDA-aligned audit ledger as the mitigation for regulatory pathway shifts. Do not discuss the routing output as if it operates autonomously in production.

## Follow-On Block: GEHC Twice Weekly Internal Check-In — 3:30 PM CDT today

**Organizer:** Lisa Barnes (Improving). **Attendees:** Lisa Barnes, Vlad Avila, Tim Rayburn, Lisa Kimbrel, David O'Hara. **Format:** Teams, 30 min. Not client-facing — this is the Improving-side team sync.

**Purpose:** Lisa Barnes set these up for *"internal alignment meetings to discuss plans, progress, internal issues, etc."* It is the informal roundtable where the team gets on the same page before facing GEHC. You attended the 2026-09-14 instance (your intro to the team).

**What you owe this room:**

- **The onboarding status.** As of 2026-09-14, Lisa Barnes was to (a) reach out to Justin to get you repository/VPN access, (b) submit your network access request through **GE's SAP FieldGlass process** — only she can submit it, and (c) add you to both the Tuesday deep dive and the Wednesday GE cadence. Confirm where each of these actually landed. You cannot do code review without them, and your entire value proposition on this account depends on getting into the code.
- **The transition handoff from Tim.** Tim stepped aside on 2026-09-08; Lisa Barnes asked at the time whether a transition discussion was needed. There is no evidence in this run that a formal Tim → David handoff ever happened — you may still be holding a handoff gap.
- **Your own capacity guardrail.** You are carrying ~5 hrs/week on GEHC against a fixed calendar, with an October boot camp, Alberta Blue Cross, and a travel day today. If fielding the GE calls is going to run over five hours, say so here, not later.
- **The demo plan.** Two larger demos (week 6 and end of POC) are yours. The week-6 demo lands roughly in the first half of October — inside the same window as the boot camp and the Houston work. This conflict is real and should be named now.

**Landmine for this block:** this is the room where internal friction is supposed to be surfaced, not the client room. Do not carry a scheduling or access problem into the Wednesday sync with GEHC without first raising it here.

## Data Gaps — What You Are Walking In Blind On

Called out explicitly, because this prep sheet is thinner on last week's substance than it should be:

1. **No transcript for the 2026-09-15 "AI Routing technical deeper dive."** This is the meeting you most needed. Microsoft Graph returns HTTP 403 on GEHC-tenant meeting transcripts — the external tenant restricts transcript access to the organizer (Justin Holder). Confirmed by retry in this run against the meeting's transcript endpoint, on both v1.0 and beta. What you have instead is the **Facilitator chat recaps** posted during the call, which is a useful but partial secondhand account, not a record.
2. **No transcript for today's weekly sync (yet)** — same tenant restriction, expected to recur. Assume you will never get transcripts off this account.
3. **No attendee bios or LinkedIn research on any GEHC attendee.** No mutual connections were pulled. Titles come from the Improving internal hand-off doc and the Teams chat, not from LinkedIn or the GEHC website.
4. **No CRM record pulled.** An opportunity ("GE Healthcare – AI PoC") is known to exist in Dynamics, but its stage, value, close date, and owner were not read for this run.
5. **No GE HealthCare company research.** Deliberately brief-refresh depth for a repeat meeting; treated as stable background.
6. **Revenue/billability context unresolved.** The engagement is $27K fixed-fee against three named Improving resources. Whether hours are tracking to the fixed-fee ceiling was not determinable from the artifacts available.

## Open Questions Going In

- **Is this meeting still at 10:30 AM CDT today?** A live Teams conversation this morning (07:46–08:43 AM CDT, in the technical-deeper-dive meeting chat) has Vlad asking to move today's session for a medical appointment, Justin replying *"I almost think maybe pushing to Thursday could make more sense just cause we have already spoken Friday + Tuesday,"* Lisa Barnes replying *"i agree...,"* and the thread ending unresolved on UTC/day math. A separate invite titled **"GEHC Improving – AI Routing weekly sync (2)"** already sits on your calendar for **Thursday 2026-09-17, 10:00–10:30 AM CDT**, and Justin created it because he believed the original invite's Copilot/Facilitator thread "was corrupted." **Confirm before dialing.**
- **Do you actually have repo/VPN/PRISMA access yet?** As of 2026-09-14 the SAP FieldGlass request had not been confirmed as submitted or granted. Without it, "code review" is notional.
- **Is Tim Rayburn still on this account at all, or fully out?** He remains on every invite. No evidence of a formal handoff conversation.
- **Who is the actual technical lead on the GEHC side?** The hand-off doc names **Anthony Pezet** as "Architect (Tech Lead)," but Pezet is optional on the deeper dive and absent from all chat traffic reviewed. Justin, Michael Braunstein, and Sandeep Kaushik are the ones showing up.
- **Which build of the timeline is live?** The kickoff deck renders D4 as "Wks 7–8 · 10/12" and also as "11/9 – 11/23." These cannot both be true. Worth clarifying, since your week-6 demo commitment hangs off it.
- **What is the week-6 demo's actual date and audience?** Lisa Kimbrel said *"about six weeks in,"* which lands mid-October; the deck's D3 window ends 10/5. No exact date is on record.
- **Two open architecture decisions were left unresolved on 9/15** (orchestration boundary; data contracts). Whether they were settled off-line is unknown.
- **Has the PO been issued?** The hand-off doc (8/20) says *"SOW signed but awaiting PO & all access."* An unissued PO on a GEHC SOW means the contract is not yet binding on GEHC — worth knowing before you invest hours.
- **Unconfirmed business context:** whether GEHC's budget for a 2027 MVP has actually been reserved, or whether "MVP next year" is still aspiration. Lisa Kimbrel framed the expansion as a possibility, not a commitment.
