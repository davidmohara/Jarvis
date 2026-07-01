# Call Prep: Systemic Compliance
**Meeting:** Fractional Chief AI Officer Kickoff — Tuesday, July 1, 2026 @ 4:00 PM
**Attendees:** Robin Graham (rgraham@systemic-compliance.com), Kevin Graham (kgraham@systemic-compliance.com), Robyn Fuentes (Improving)
**Your Role:** Fractional Chief AI Officer
**Your Goal:** Establish trust, get clear on their current SC.IMS state, agree on the first 90-day focus areas, and set expectations for how you'll operate together.

---

## Account Snapshot

| Field | Value |
|---|---|
| **Company** | Systemic Compliance, LLC |
| **Founded** | Early 2025 (Kevin Graham + original Veriforce core team) |
| **HQ** | Texas, USA |
| **Industry** | Pipeline Safety & Regulatory Compliance (Oil & Gas) |
| **Focus** | OQ compliance, Pipeline Safety Management Systems (PSMS per API RP 1173), contractor alignment |
| **Products** | SC.ORB (contractor compliance platform), SC.IMS (AI-driven requirements & gap-analysis tool — the IP in question) |
| **Engagement** | Fractional advisory — 16 hours over 3 months, quarterly retainer model, SOW signed |
| **Sourced By** | Devlin Liles → Robyn Fuentes → Stephen Johnson → David O'Hara |

---

## Who You're Meeting

### Kevin Graham — Founder
- 30+ years in pipeline compliance, OQ, and management systems
- Founded Veriforce in 1998, sold 2009 — original inventor of the dominant OQ platform in this space
- Has since built and navigated PE exits multiple times (OQSG sold twice)
- Sat on API RP 1173, API RP 1161, and B31Q technical committees — he *wrote the standards*
- **What he cares about:** Getting the IP right, building something defensible, not repeating the PE-exit mistakes from his Veriforce/OQSG years
- **His lens:** He's the technical authority and founder; he'll probe whether you understand the regulatory space and whether you're going to add real value or just ask questions he already knows the answers to
- **Don't:** Come in soft. He's been around the block. Treat him as a peer who built something real.

### Robin Graham — appears to be co-founder/operator (rgraham@systemic-compliance.com)
- Referenced by Devlin as the person who should "get the timesheet" for R&D tax credit purposes — likely handles finance/operations side
- Devlin's email addressed the strategic and technical content to Kevin but looped Robin on commercials
- **Role in deal:** Likely business/ops decision-maker alongside Kevin; R&D tax credit mention suggests she manages the books
- **Talking point:** Devlin's R&D tax credit note — she should be capturing time against the SC.IMS build if profitable this year

### Robyn Fuentes — Improving, President South Texas
- Your internal sponsor; she closed the SOW and runs the commercial relationship
- She's hoping you can do this — treat it as her putting her neck out for you

---

## The SC.IMS Asset — What You're Being Brought In To Advise On

SC.IMS is an AI-driven requirements and gap-analysis tool built inside Claude Cowork. Here's what Devlin's diagnosis found:

**What they have:**
- Real IP — an AI capability for pipeline safety requirements crosswalk and gap analysis
- A "contractor equivalency engine" and peer benchmarking capability across operators
- The moat is the interconnectivity, not just the prompts — prompts are replaceable, but the network effects from multi-operator data are hard to copy
- Currently running on Anthropic Claude Team seats inside Cowork (30-day retention, no training, data-private — they're safe but need to graduate)

**The structural problem Devlin identified (your starting brief):**
1. **Trapped IP** — everything lives inside an Anthropic account. Needs to be extracted, owned, and made portable before it can be sold or audited
2. **Spreadsheet-based requirements store** — the crosswalk is a giant spreadsheet; this creates semantic saturation risk (Claude merging similar requirements like 192.31.4.b and .c)
3. **No evaluation harness** — AI checking its own work fails ~91% of the time; they need external graders, datasets, and edge-case tests
4. **Cognitive surrender risk** — as SMEs see the AI get things right repeatedly, they stop catching the times it doesn't; need to track reviewer kickback rates
5. **Passive governance** — output is currently a report; PSMS is Plan-Do-Check-Act, so the value is in intervention *before* the compliance mistake, with trended KPIs

**The two strategic paths Devlin laid out:**
- **Path A: Keep & Scale** — build SC.IMS into value-priced software + consulting. Moat holds because of the network effects. Best if they want a 10+ year annuity.
- **Path B: Sell the IP** — harden it, sell into 10-20 large midstream operators, harvest in ~4 years before knockoffs appear.

**Both paths require the same first move:** get the asset out of Cowork, into a deployable framework they own.

---

## Technical Architecture Context (Devlin's KSTG Framework)

As the corpus grows, you need four search methods running in parallel:
- **K** — Keyword: exact citation/clause matches (the literal 49 CFR 192 reference)
- **S** — Semantic: meaning and intent (passages that satisfy a requirement without quoting it)
- **T** — Temporal: what applied *when* — handles grandfathering and effective dates
- **G** — Graph: connective tissue — links, equivalencies, peer relationships (powers benchmarking and contractor equivalency)

Running only K+S causes semantic saturation. Adding T+G lets the system distinguish similar requirements and reason across them.

---

## Your First-Call Agenda (Suggested)

1. **Open (5 min)** — Brief intro of your background, acknowledge Devlin's intro, set the tone: you're here to be a working partner, not a consultant who asks questions and writes memos.

2. **Understand the current state of SC.IMS (15 min)**
   - Where does it live today? (Cowork, API, other?)
   - Who uses it and how? (Internal only, client-facing, demos?)
   - What does the output look like right now — report, dashboard, raw text?
   - How are SMEs reviewing outputs today? Any quality tracking?

3. **Clarify the strategic intent (10 min)**
   - Are they leaning Path A (build and scale) or Path B (sell)? Or still open?
   - Do they have any customer pilots running on SC.IMS yet, or is it still internal?
   - Timeline pressure: any investor conversations, partnerships, or competitive threats moving the clock?

4. **Align on the first 90 days (10 min)**
   - Of the six roadmap items Devlin outlined, where do they want to start?
   - Your recommendation: prioritize the evaluation harness first — it's the easiest to see ROI on and de-risks everything else
   - What does "done" look like for month 1? Month 3?

5. **Operating model (5 min)**
   - How do they want to use your time? (Async advising, working sessions, architecture review, stakeholder calls?)
   - Preferred comms cadence
   - Who else on their side needs to be looped in (engineering, legal for IP, tax for R&D credit)?

---

## Discovery Questions

1. What does the current SC.IMS workflow look like end-to-end — from a client loading a document to getting an output?
2. Have you had any near-misses where SC.IMS returned something that looked right but wasn't? How was it caught?
3. Are clients currently paying for SC.IMS outputs, or is this still pre-commercial?
4. What's your read on the moat — are you seeing competitors starting to approach what you've built?
5. On the IP question: have you engaged IP counsel yet, or is that still ahead of you?
6. What does your dev capacity look like? Is this Kevin building it, or do you have engineers?

---

## Potential Friction Points & How to Handle Them

| Risk | Response |
|---|---|
| Kevin tests your domain knowledge | You don't need to know 49 CFR cold — but know that 192 covers natural gas pipelines, 195 covers hazardous liquids, and API RP 1173 is the PSMS voluntary standard. Know the KSTG framework. |
| They expect you to prescribe a stack immediately | Don't. Your job in round one is to understand the current state deeply, not to land on a solution. Say so explicitly — "I'd rather understand what you've built before I tell you what to change." |
| They want to move faster than 16 hours allows | Good problem. Frame it: "Let's make sure the first 16 hours are the most leveraged 16 hours — that means starting where the risk is highest." |
| Scope creep into SC.ORB (their other product) | Keep scope on SC.IMS. SC.ORB is a different product (contractor compliance platform, already in market). They're related but separate. |
| Robin asks about R&D tax credit documentation | Validate it's real — it is. Devlin flagged that if work is capitalizable R&D, Kevin's time and development costs feed the credit. Recommend they get a tax attorney involved if they haven't. |

---

## What Improving Needs From This Call

- Confirm you're the right fit for the fractional CAIO role (Robyn is counting on yes)
- Leave Kevin and Robin with confidence you can add real, specific value — not general AI consulting
- Establish a working cadence for the retainer
- Identify the first concrete deliverable within hours 1-4

---

## Quick Reference: Key Contacts

| Person | Role | Email |
|---|---|---|
| Kevin Graham | Founder, SC | kgraham@systemic-compliance.com |
| Robin Graham | Co-founder/Ops, SC | rgraham@systemic-compliance.com |
| Robyn Fuentes | President South Texas, Improving | robyn.fuentes@improving.com |
| Stephen Johnson | Improving (deal originator) | stephen.johnson@improving.com |
| Devlin Liles | Chief AI & Consulting Officer, Improving (original advisor) | devlin.liles@improving.com |

---

## Context You Should Read Before the Call

- Devlin's full roadmap email (FW: Follow up / Introduction, June 17 2026) — you've read it, but re-skim the 6-step roadmap and KSTG section
- [Systemic Compliance Services Page](https://systemic-compliance.com/services/) — especially the SC.ORB platform description; understand the difference between SC.ORB and SC.IMS
- [About page](https://systemic-compliance.com/about/) — Kevin's background and the Veriforce origin story
- Devlin's hallucination benchmark post: https://www.devlinliles.com/lies-lies-and-statistics-the-five-ways-ai-gets-things-wrong/ — know the five failure modes cold, you'll likely reference them

---

*Prep assembled June 30, 2026 — sources: Stephen Johnson email thread, Devlin Liles roadmap email, systemic-compliance.com*
