---
date: 2026-08-25
tags:
  - context/client
  - context/ai-workshop
  - meeting-prep
  - presentation-plan
---

# Remington Hotels AI Executive Workshop — 2-Hour Presentation Plan

**Session:** 2:00–4:00 PM CT, August 25, 2026. Condensed from Improving's standard 4-hour Executive AI Workshop.
**Built from:** Existing slides only, pulled from `/Presentations/AI/` and subfolders. No new content invented — narrative gaps are flagged explicitly where the library doesn't have what the story needs.
**Companion doc:** `meetings/2026-08-25-remington-hotels-workshop-context.md` (attendee/relationship prep — read that first if you haven't).

---

## Source decks used

| Short name | File | Role in this plan |
|---|---|---|
| **CEO** | `Workshop/CEO AI Workshop v6.pptx` | Fundamentals, maturity mapping exercise, agentic fundamentals (dev), governance intro |
| **Shift** | `Workshop/The Enterprise Shift.pptx` | 8-stage maturity model, waves/walls, Intelligence OS, Agentic Landing Zone, adoption path |
| **F&T** | `Workshop/Practical AI - Finance & Treasury.pptx` | FP&A/Accounting concrete use cases (AP, cash forecasting, close) |
| **Acct** | `AI in Accounting/Innovations and Implications of AI in Accounting.pptx` | Governance framework (NIST/Microsoft/IBM/OECD), demand-limit precedent |
| **Advantage** | `AI Advantage Workshop.pptx` | Common SMB mistakes (tool proliferation/shadow AI — cost governance anchor), 60-day action plan, adoption stages |
| **LSD** | `Workshop/AI Workshop - LSD.pptx` | Cross-functional tool landscape reference (recruiting, workforce mgmt tools) |

v6 of CEO Workshop is used, not v4 — v6 is the version with the current Intelligence OS/governance material layered in; v4 wasn't opened since v6 supersedes it for this purpose. Topgolf Executive Briefing and Wendy's QBR were reviewed and confirmed to be recombinations of CEO+Shift content already covered above — not separately cited.

---

## The story arc in one paragraph

Everyone in the room is somewhere on the same 8-stage trust ladder — Ben isn't behind, he's just earlier on a path Jason Pool and Randy are already walking, and naming that up front defuses status anxiety before it forms. From there we build one shared framework (the maturity model, then a simple lens for mapping AI onto any role) and apply it three times — accounting/FP&A, development, HR — so the framework does the work, not three unrelated topic dumps. Governance and cost show up as the natural adult conversation that comes with getting serious about this, not a lecture bolted onto the end. We close on the fact that frameworks are necessary but not sufficient — Remington needs its own roadmap, which is exactly what Innovation Labs builds.

---

## Full agenda with timing

| # | Section | Time | Cumulative |
|---|---|---|---|
| 1 | Welcome & Maturity-Spread Framing | 12 min | 0:12 |
| 2 | AI Fundamentals (compressed) | 12 min | 0:24 |
| 3 | The 8-Stage Maturity Model | 15 min | 0:39 |
| 4 | Mapping AI's Impact on Your Business | 8 min | 0:47 |
| 5 | Department Deep Dive: FP&A & Accounting | 15 min | 1:02 |
| 6 | Department Deep Dive: Software Development | 8 min | 1:10 |
| 7 | Department Discussion: HR | 8 min | 1:18 |
| 8 | Responsible AI: Governance & Security | 10 min | 1:28 |
| 9 | Cost Governance (Ashford → Remington) | 10 min | 1:38 |
| 10 | Build vs. Buy & Your Adoption Path | 8 min | 1:46 |
| 11 | Close: Innovation Labs Handoff | 6 min | 1:52 |
| — | Slack / live Q&A absorption | 8 min | 2:00 |

The 8 minutes of slack isn't a separate block — distribute it as needed wherever Ben's questions run long, since the brief specifically says answer him but don't let the room rabbit-hole for his benefit. If the room is moving fast, spend the slack on Section 3 (maturity model) since that's the one every attendee needs to fully land.

---

## Section 1 — Welcome & Maturity-Spread Framing (12 min)

**Slides:**
- CEO Slide 2 — "Who am I?" (Technologist / President / Entrepreneur / Early Adopter)
- CEO Slide 10 — "Fill in the blank: Good _____, Bob." (icebreaker)
- Shift Slide 17–18 — The Trust Evolution: 8 Stages of AI Maturity (show early, don't teach yet)

**Read from slide:** Just the "Who am I" bullets and the fill-in-the-blank prompt.
**Ad-lib:** Everything else. This is where you name the maturity spread directly and out loud — not as a slide, as a spoken framing move.

**Talking points:**
- Open with the icebreaker (slide 10) — it's fast, low-stakes, and gets Ben answering something before the "real" content starts, which matters given he'll be the one asking the most questions all session.
- State plainly: "Everyone in this room is somewhere on a maturity curve. Some of you are further along than others — that's not a judgment, that's just where your part of the business happens to be right now. This isn't a room where anyone should feel like they're behind." Name Jason Pool and Randy specifically as already operating ahead on this curve (per the brief, their teams already use AI for reports/analysis and accounting expects a lot) — this does two things: it makes Ben feel safe, and it makes Jason Pool/Randy feel seen rather than bored.
- Put the 8-stage ladder (Shift 17) up early as a preview — "you'll see exactly where you sit on this by the end of the next section" — but don't explain the stages yet. This is a teaser, not the teaching moment (that's Section 3).
- Confirm logistics live if not already done: final attendee list, whether Ayotunde's use-case catalog and Ben's AI pitch deck arrived, whether Nick Clark/ops joined.

**Transition to Section 2:** "Before we can talk about where AI takes Remington, we need one shared vocabulary for what AI actually is and isn't — because half the confusion in every room I run this in comes from people using the word 'AI' to mean five different things."

---

## Section 2 — AI Fundamentals, compressed (12 min)

**Slides:**
- CEO Slide 4 — Common perceptions of AI (skip the deep script; use as a 60-second "here's the two myths" beat)
- CEO Slide 28 — AI and ML at the simplest (Data/Rules/Results diagram)
- Shift Slide 10 — Three Waves of Enterprise GenAI (Chatbots → Insights → Agentic)
- CEO Slide 6 — "Where are we today?" (one slide only — the $750M training / $5B datacenter cost point)

**Skip for time (flag, don't cut silently):** CEO/Shift slides 5, 7, 8 (compute/data/latency deep dive, subscription cost curve, data plateau) — too technical for a condensed exec session; the single "where we are today" cost slide (CEO 6) carries enough of the "this is genuinely expensive infrastructure, you're a renter not an owner" point without the full Epoch AI data walkthrough. Also skip CEO 19–20 (Diffusion of Innovations, "Not that GPT") — good material, not essential at this length.

**Read from slide:** The AI/ML diagram (28) speaks for itself, read it as shown.
**Ad-lib:** The "hasn't changed in 70 years" framing, the CapEx/OpEx point on slide 6, and the bridge into three waves.

**Talking points:**
- AI/ML at the simplest (slide 28): data + rules → results, or in ML's case, data + results → rules. This one visual kills a lot of mystique in the room fast.
- The one cost slide (CEO 6): the best model on the planet cost roughly $750M to train and its datacenter $5B to house. You are never going to be one of the labs building this — you're a renter, not a builder, and that's the correct strategic posture, not a limitation. This sets up the "stay close to off-the-shelf" investment rule later.
- Three Waves of Enterprise GenAI (Shift 10): Chatbots (2022–23, stages 1-2, human does the work) → Insights (2024–26, stages 3-4, human reviews) → Agentic (2027+, stages 5-8, human directs). This is the bridge slide into the full maturity model — it's the same ladder, viewed as an industry timeline instead of an individual/team position.

**Transition to Section 3:** "That timeline is the industry's clock. Now let's get specific about where any one person, team, or department sits on it — because that's the framework you're going to use for the rest of this session, and honestly, after you leave the room."

---

## Section 3 — The 8-Stage Maturity Model (15 min) — the anchor framework

**Slides:**
- Shift Slide 17–18 — The Trust Evolution: 8 Stages (full walkthrough now)
- Shift Slide 19 — Wave 1: Tools (Stages 1-2, with examples)
- Shift Slide 20 — The Tool Wall (Identity/Trust/Process barriers)
- Shift Slide 21 — Wave 2: Process (Stages 3-4, with examples)
- Shift Slide 22 — The Process Wall (what changes, what it requires)
- Shift Slide 23 — Wave 3: Agentic Operations (Stages 5-8, with examples)
- Shift Slide 25 — The Role Evolution: Contributor → Operator (Doer/Reviewer/Director/Operator)

**Ad-lib, don't read bullets:** This is David's strongest framework material — speak from it, use the room. Cold-call is fair game here ("Jason, where would you put your team on this?").
**Read from slide:** The stage labels themselves (Zero AI / Off the Shelf / Task / Workflow / Delegate / Coordinate / Supervise / Orchestrate) — these are the vocabulary the room needs to leave with, say them clearly.

**Talking points:**
- This is domain-specific, not company-wide — "your accounting team may sit at a different stage than your development team, and that's normal, not a problem to fix."
- The Identity Barrier from the Tool Wall slide (20) is worth landing deliberately for this room: "I AM a controller" vs. "I do controlling." Randy's team lives this tension directly. Reframing identity away from the activity is what unlocks people actually trying stage 3+.
- The Trust Barrier ("it hallucinated once, so I can't trust it") is a direct, softened way to invite Ben's likely skepticism into the open without singling him out — normalize it as the most common reason people stall, not a personal failing.
- Contributor → Operator (slide 25) is the single best slide for this specific room: it explicitly plots low-trust/high-trust against Doer → Reviewer → Director → Operator. This is where Jason Pool and Randy can see themselves near "Director," and Ben can see a credible path from "Doer" without shame.
- Skip the Skill Leveling Effect slide (Shift 15, "junior workers gain 35%, experts gain 3%") unless there's time — good stat, not essential to the core arc, and it risks reading as a headcount-reduction message this early, before governance/trust framing has landed.

**Transition to Section 4:** "So now you have the ladder. The next question is the one every executive actually wants answered: how do I know which tasks in my business are worth climbing that ladder for?"

---

## Section 4 — Mapping AI's Impact on Your Business (8 min)

**Slides:**
- CEO Slide 22 — AI impact on tasks that are demand limited (the economics primer)
- CEO Slide 23 — AI impact on tasks that are collapsable (software dev / sales example)
- CEO Slide 24–25 — Demand Limit × Time Impact matrix (Accounting Clerk / Software Developer / Sales plotted, with the "Wait / Do More / Reduce or Grow" quadrant labels)
- CEO Slide 26 — "What's 1 task in your organization that could benefit the most?" (discussion prompt)

**Ad-lib:** The economics framing (slide 22) — this is a live Socratic bit ("if payroll got 5x faster and 100% accurate, would you pay people 5x more often? No — demand is limited there. If sales closed 5x more deals, would you cut 80% of the sales team to hold revenue flat? No — demand is nearly infinite there."). Don't read this off a slide, it lands as a conversation.
**Read from slide:** The quadrant labels on slide 25 (Wait / Do More / Reduce headcount or grow the role / Scale by headcount + incremental improvement) — these are the four decision buckets the room needs to walk away holding.

**Talking points:**
- The core question isn't "can AI do this task" — it's "is demand for this task limited or unlimited." That's what determines whether AI adoption there means doing the same work with fewer people, or doing dramatically more work with the same people.
- Use the pre-built Accounting Clerk / Software Developer / Sales plot (slide 24-25) as the worked example, then immediately pivot to the live discussion prompt (slide 26): "Where would Remington's own roles land on this?" This is the moment to let Randy, Jason Pool, and Keith name one task each out loud — it makes the framework theirs, not just David's.
- This slide set is the scaffold for all three department deep-dives that follow — call that out explicitly: "We're about to apply exactly this lens three times: accounting, development, HR."

**Transition to Section 5:** "Let's start where the sharpest questions in this room are probably going to come from — accounting and FP&A."

---

## Section 5 — Department Deep Dive: FP&A & Accounting (15 min)

This is Remington's flagged priority topic and Randy's home turf — give it the most department time and the most concrete material. This section is built almost entirely from the **F&T deck**, which is the strongest, most concrete source in the whole library — use it directly, largely as designed.

**Slides (in order):**
- F&T Slide 14 — AP Invoice Processing (framing: "500 invoices a week = 500 data entry events, 500 coding decisions, 500 routing steps")
- F&T Slide 15 — AP: What AI Can Do (Automate fully / Use AI for / Watch-outs / Keep humans here — 4-box)
- F&T Slide 16 — AP: Key Takeaways (Start here / Training period / Set policy first / Expected outcomes: 70-80% reduction in manual entry)
- F&T Slide 17 — Cash Flow Forecasting (framing: "How confident are you in your cash position 13 weeks out?")
- F&T Slide 18 — Cash Flow: What AI Can Do (4-box)
- F&T Slide 19 — Cash Flow: Key Takeaways (accuracy improves ~70% → 90%+ in 6 months)
- F&T Slide 20 — Month-End Close (framing: "3 days instead of 10")
- F&T Slide 21 — Month-End Close: What AI Can Do (4-box — note the SOX/human-sign-off line, this is a natural governance touchpoint, see below)
- F&T Slide 22 — Month-End Close: Key Takeaways (10 days → 5-6 days year one)
- F&T Slide 23 — The AI Tooling Landscape for Finance (vendor landscape — AP, FP&A, Close, ERP-embedded copilots)

**Read from slide:** The 4-box "Automate fully / Use AI for / Watch-outs / Keep humans here" grids — these are dense and precise, read them rather than paraphrase. The "Expected outcomes" stats too — those are the credibility anchors Randy will want exact.
**Ad-lib:** The framing questions ("how confident are you in your 13-week cash position?") — deliver those live to the room, ideally aimed loosely at Randy, before revealing the slide.

**Talking points:**
- Pick one of the three (AP, cash forecasting, close) to go deep on live if time is short in the room — probably **month-end close**, since "3 days instead of 10" is the most viscerally compelling number and ties best to a CAO's actual pain.
- The **"Keep humans here"** box on every one of these three slides is your governance sprinkle for this section, entirely in Randy's own language — final approval above payment threshold, vendor disputes, SOX sign-off, complex judgment calls. You don't need a separate governance slide here; it's built into the framework already.
- The tooling landscape slide (23) directly answers "what do we actually go buy" without Improving pitching a specific product — useful credibility move, and a natural bridge into the build-vs-buy section later.
- Skip nothing from this sub-section unless time-constrained — this is the deck's strongest, most client-ready material and matches exactly what Remington asked for.

**Transition to Section 6:** "That's the finance side. Now let's talk about how this same lens applies to how software actually gets built — because some of you already have a foot in this door."

---

## Section 6 — Department Deep Dive: Software Development (8 min)

Keep this section tight and conceptual — the room's development-maturity anchor is Nick Clark (SVP Ops, already using Claude in agentic mode), not a broad audience need. Use this section as validation of what he's already doing, not a technical tutorial.

**Slides:**
- CEO Slide 54 — Agentic Fundamentals: RAG (one slide, concept only — "your AI grounded in your own data, not just its training data")
- CEO Slide 63–64 — Agent Design / Agentic Patterns: Multiple Tools (concept only)
- CEO Slide 66 — Agentic Patterns: Supervisor ("the Supervisor knows the Experts available and routes work to them")
- CEO Slide 68 — Agentic Workflows: Overview (combining patterns into a complex agent)

**Ad-lib:** Nearly all of it. This section should feel like a conversation, not a slide-read — the content is technical enough that reading bullets will lose the room. Use the "Staff & Project Planner" example baked into CEO slides 55-60 only if you want one worked example; otherwise stay at the pattern level (Supervisor, Router, multi-tool).
**Read from slide:** Nothing verbatim here — these slides are visual/diagrammatic, not bulleted prose.

**Talking points:**
- If Nick Clark is in the room (confirm at Section 1), invite him directly here: "Nick, you're already running Claude in agentic mode operationally — tell the room what that actually looks like day to day." This is more credible coming from inside Remington than from David.
- Frame this as: development is usually the furthest-along department in any org, because engineers are naturally early adopters and the tooling (Copilot, Claude Code, Cursor) is mature. That's consistent with Jason Pool's team already using AI for reports/analysis — the pattern repeats.
- The Supervisor/Router pattern (slide 66) is worth one clean explanation because it's the conceptual bridge to governance: "a supervisor agent deciding which expert to route to" is structurally identical to the approval-gates conversation you're about to have in Section 8. Flag that connection out loud so it lands twice.
- Do not go deep on RAG mechanics, vector databases, or embeddings (CEO slides 56-60) — those are practitioner-level and will lose the room. One sentence on RAG ("grounding AI in your own documents instead of its general training data, so it doesn't make things up about your business") is enough.

**Transition to Section 7:** "Let's bring it back to the department that touches every single person in this building — HR."

---

## Section 7 — Department Discussion: HR (8 min)

**⚠️ Narrative gap.** Unlike FP&A/Accounting (which has the full, purpose-built F&T deck) or Development (which has the agentic-fundamentals material), **David's library has no dedicated HR practical-use-case deck** — no AP-invoice-processing-equivalent walkthrough for recruiting, onboarding, benefits admin, or performance review drafting. What exists instead:

- **CEO/Shift Slides 24-25** (Demand Limit matrix) references payroll directly in the speaker notes ("cross-train payroll to do AP/AR" is the given example for the "reduce headcount or grow the role" quadrant) — usable as a worked example, but it's one line, not a full section.
- **Culture over Code deck** (`Culture over Code.pptx`) — not detailed above since it wasn't part of the core reading, but scanned for HR content: it addresses the *people/ethics* side of AI-driven workforce change (reskilling vs. replacing, Amazon's HR/marketing/ops cuts, Conscious Capitalism framing, cost of replacing an employee running 1.5-2x salary) — this is a values/culture lens, not a "here's how AI does HR tasks" lens.
- **LSD Workshop Slide 38** — a cross-functional tool-landscape table that name-checks two HR-adjacent tools (Teamtailor for recruiting, Eightfold for workforce management) alongside tools for every other function — useful as a single reference point, not a narrative.

**Recommendation for this section, given the gap:** Don't manufacture a fake HR case-study slide. Instead, run this section as a **live application of the Section 4 framework to HR**, the same way you'll have just done for accounting and development — but treat it as a facilitated discussion rather than a slide-driven walkthrough.

**Slides to use:**
- CEO Slide 24-25 (Demand Limit matrix) — re-display, point specifically at the payroll/cross-train note
- LSD Slide 38 (tool landscape table) — show briefly as "here's what's already out there" (Teamtailor, Eightfold) without endorsing either
- CEO Slide 26 — "What's 1 task in your organization that could benefit the most?" (reuse the discussion prompt, aimed at HR this time)

**Ad-lib — this whole section is a facilitated conversation, not a deck read:**
- Ask the room directly: "Where does HR sit on the maturity ladder today at Remington? Screening resumes, drafting job descriptions, benefits Q&A, onboarding checklists, policy documents — which of these are demand-limited, and which aren't?"
- Use the payroll example from slide 25 as the one concrete anchor: payroll accuracy/speed is classically demand-limited — nobody wants payroll run 5x more often, so AI there means the same output with less headcount or a broadened role (e.g., cross-trained into AP/AR), not "do more."
- If Ayotunde's 100+ item use-case catalog arrived before the session (confirm at the top, per the context brief), this is the natural moment to reference it live — "some of you already have 100+ ideas cataloged; let's test a few of them against this framework right now" — without projecting content Improving hasn't verified.
- If the culture/workforce-trust angle comes up naturally (likely, given Ben's team will be sensitive to "will this cut jobs"), the Culture over Code framing is available as an ad-lib resource: reskilling costs less than replacement (1.5-2x salary to replace a role), and treating talent as a stakeholder rather than a cost line is consistent with a hospitality-management company's culture. This is optional color, not a scripted slide.

**Flag for David:** if HR keeps coming up as a priority account (not just for Remington), this is worth building as a proper fourth deck alongside F&T — an "AI in HR: Recruiting, Onboarding, Benefits Admin" concrete-use-case deck, mirroring the F&T structure (Automate fully / Use AI for / Watch-outs / Keep humans here / Expected outcomes). Consider raising with Rigby as a capability-build candidate after this session.

**Transition to Section 8:** "We've now applied this framework three times. Every time, one box kept showing up in the corner of the slide — 'keep humans here.' Let's talk about why that box exists, and what it takes to make it real instead of decorative."

---

## Section 8 — Responsible AI: Governance & Security (10 min)

This is Ayotunde's ask, and per the prep brief she's the one internal governance champion — the goal is to make this land for the room generally, without it reading as "David is here to validate Ayotunde's internal argument." Keep it business-relevant, not compliance-lecture.

**Slides:**
- CEO Slide 33 / Shift Slide 9 — "Picking the right problem is crucial" (the Boeing Wingman story — AI is your wingman, not your lead pilot)
- Acct Slide 24 — Principles of AI Governance Framework (Explainability, Accountability, Safety, Security, Transparency, Reproducibility, Robustness)
- Acct Slide 26 — AI Governance Frameworks (NIST AI RMF, Microsoft Responsible AI, IBM AI Ethics, OECD AI Principles — one line each)
- CEO Slide 42 — Governance as the Engine of Trust (governance = coding standards/access controls/audits, the mechanism that builds trust)

**Ad-lib:** The Wingman story (slide 33/9) — this is David's best governance story and it's a narrative, not bullets. Tell it as a story: fully autonomous weapons vehicle at Lackland, no cockpit, the wingman's job is to fly, protect, obey orders — and if the lead pilot gives an order that turns out to be a war crime, the lead pilot goes to jail for what the wingman did. Land the punchline live: "If you let 'the AI made a mistake' become an acceptable excuse in your business, you've just given away 100% of your accountability. AI is your wingman. It is never your lead pilot."
**Read from slide:** The seven governance principles (Acct 24) and the four-framework names (Acct 26) — these are reference vocabulary, read them cleanly so the room has the right terms if they go looking afterward.

**Talking points:**
- This is where "keep humans here" from every department section gets its teeth: accountability doesn't evaporate because AI did the work. Someone at Remington owns every AI-touched decision, the same way a lead pilot owns everything their wingman does.
- Improving's own posture here is worth a light mention if natural: Improving operates under a SOC 2 Type II program (with NIST CSF/CIS Controls alignment where relevant) — the same discipline being described is one Improving holds itself to, not just prescribes to clients. Keep this to one sentence; it's a credibility anchor, not a subject to dwell on.
- Acknowledge Ayotunde directly and warmly, without making it about her: "Someone in this room has been the one asking the security/governance questions before anyone else was ready to hear them — that's exactly the right instinct, and it's the instinct this whole framework is built to support." This validates her without making the room feel like it's being scolded for not caring yet.
- Skip the "AI for Good / AI for Bad" slides (present in CEO, appears 2x, also in LSD) — long generic ethics essays, not sharp enough for this room's time budget, and the Wingman story + governance framework slides do this job better and faster.

**Transition to Section 9:** "Governance is what makes AI safe to trust. There's a second kind of governance most companies don't think about until it's already a problem — and for Remington, that clock just started ticking. Let's talk about cost."

---

## Section 9 — Cost Governance: Ashford → Remington Transition (10 min)

This is the section the prep brief flagged as a genuinely timely, forward-looking opening — not a tangential aside. Land it as practical foresight, not a warning.

**Slides:**
- Advantage Slide 23 — Common SMB Mistakes (Tool Proliferation, Shadow AI, Skipping Security Review, No Training Plan, Expecting Perfection)
- CEO Slide 32 — Rules of Thumb for AI Investment Today (stay close to off-the-shelf / look for 5-10x returns / define the problem before starting)
- Shift Slide 51 — Where to Focus Investment (Company Density × Excellence Required matrix — General AI Platforms / Industry Platforms / Unified SaaS / Domain-Specific Advantage)
- Shift Slide 54 — Agentic Landing Zone: Six Components (specifically Tool Registry and Governance, as the infrastructure answer to sprawl)

**Ad-lib:** Open this section with the direct, named context: "Right now, Ashford pays for your Claude seats. Starting next month, that bill is yours. This is the exact moment every company that's ever scaled up a cloud platform hits — and it usually goes one of two ways." Use the cloud-cost-shock analogy the brief notes resonated on the planning call: per-user costs that seemed trivial as line items on someone else's budget become a real number fast, once you own it, plus the classic pattern of duplicate tools nobody tracked (Shadow AI) piling on top.
**Read from slide:** The five "Common SMB Mistakes" (Advantage 23) — Tool Proliferation and Shadow AI specifically are exactly the failure modes a cost transition surfaces; read these cleanly, they're short and punchy as-is.

**Talking points:**
- Tool Proliferation and Shadow AI (Advantage 23) are the two mistakes most directly caused by *not* having a single point of cost/tool ownership — which is precisely the gap opening up as this bill moves from Ashford to Remington. Frame this as: "this transition is actually your best chance to get ahead of tool sprawl, because right now you get to design the governance before the sprawl happens, not clean it up after."
- Rules of Thumb (CEO 32) doubles as a cost-discipline framework: stay close to off-the-shelf rather than custom-building, target 5-10x return minimum when picking problems to invest in, and define the problem well before spending anything. This is the practical filter for "should we buy this new AI tool someone's asking for."
- The Landing Zone's Tool Registry component (Shift 54) is the direct structural answer: an approved-integrations catalog is what prevents the same capability from being bought three times under three different tool names across departments — which is exactly the kind of visibility problem a newly-cost-owning org needs.
- Keep this practical and forward-looking, not alarmist — this is "here's how to do this well from day one," not "here's the mistake you're about to make."

**Transition to Section 10:** "So — you now have a framework for maturity, a lens for mapping impact, a governance posture, and a cost discipline. The last question is the practical one: how do you actually start, and where do you go to buy versus build?"

---

## Section 10 — Build vs. Buy & Your Adoption Path (8 min)

**Slides:**
- Shift Slide 47 — Enterprise AI Maturity (Mapped to Evolution): Ad-Hoc → Experimental → Strategic → Operational
- Shift Slide 48 — Your Path Up the Trust Ladder (Week 1: Identify 3 tasks / Month 1: Pilot with governance / Quarter 1: Scale beyond stage 6)
- Advantage Slide 25 — 60-Day Action Plan (Collect & Focus → Practice & Document → Sharing & Expansion)
- Shift Slide 57 — Three Questions to Answer Now (What stage are you at? What's your path to autonomy safely? Who operates your agent factory?)

**Read from slide:** The Week 1 / Month 1 / Quarter 1 structure (Shift 48) and the Three Questions (Shift 57) — these are meant to be taken away verbatim, as a checklist.
**Ad-lib:** The framing that ties it together — "don't skip steps" is the one line worth saying out loud and meaning it, since a room this maturity-spread will have some people (Ben) tempted to leapfrog and others (Jason Pool, Randy) tempted to move faster than governance supports.

**Talking points:**
- This section deliberately compresses two build-vs-buy-adjacent slide sets from earlier decks (Shift 51 "Where to Focus Investment" was already used in Section 9) rather than repeating it — don't re-show it here, just reference it: "remember the density/excellence matrix from a few minutes ago — that's your build-vs-buy filter."
- Week 1 / Month 1 / Quarter 1 (Shift 48) is the single most actionable slide in the whole session — this is what people photograph with their phones. Give it a beat of silence after you put it up.
- Close this section with the Three Questions (Shift 57) read straight, one at a time, with a pause after each: What stage are you at today? What's your path to autonomy safely? Who will operate your agent factory? These are the three questions Innovation Labs is built to help answer — say that explicitly, since it's the bridge to the close.

**Transition to Section 11:** "Those three questions are exactly what a focused follow-on engagement answers — and that's exactly what Diana's going to walk you through."

---

## Section 11 — Close: Innovation Labs Handoff (6 min)

**Slides:**
- Shift Slide 55 — Improving's Agentic Landing Zone Offering (Assess 2-4 weeks / Build 6-12 weeks / Scale ongoing)
- Shift Slide 58 — "The future isn't about working with AI. It's about orchestrating it." (closing line, David's exit)

David reads the closing line (Shift 58) as his true exit line, then explicitly hands the floor to Diana. Do not attempt to describe Innovation Labs' actual scope, pricing, or delivery mechanics — that's Diana's material and wasn't part of the source decks reviewed for this plan.

**What Diana should have ready (setup notes, not scripted content — confirm directly with her, this plan doesn't presume to know her materials):**
- A clear, concrete description of what Innovation Labs actually delivers (per the prep brief: "discovery workshop + AI project plan for top 3 use cases") and how it differs from the Assess/Build/Scale offering shown on Shift Slide 55 — these may be the same offering under two names, or two different things; worth Diana clarifying which framing she's using before she stands up, so it doesn't contradict the slide David just showed.
- A plan for how to use Ayotunde's existing 100+ item use-case catalog as the *input* to Innovation Labs, if it exists and arrived — this was flagged as the natural on-ramp in the Aug 10 planning call and is Remington's cheapest path to a fast, credible follow-on (the catalog work is already done, it just needs prioritization and a delivery plan).
- Reference points from comparable engagements already run or in flight (FP&A/accounting team workshops completed elsewhere; marketing and HR team workshops upcoming) — these lend credibility that this isn't a first-of-its-kind pitch.
- A light answer ready in case Ben (as the BD-minded CEO building his own "AI pitch deck" to win hotels into the portfolio) asks whether Innovation Labs' output could double as external-facing collateral — worth Diana having a view on this before she's asked, since it's a plausible tangent given what's known about Ben's motivations.

**Talking points for David's handoff line:**
- "You've now got the framework. What you don't have yet is your roadmap — the specific answer, for Remington, to those three questions. That's what Diana's team builds next."

---

## Slides explicitly recommended to skip (with reasons)

| Slide(s) | Deck | Why skip |
|---|---|---|
| Understanding Demand, cost-per-month, data-plateau (5, 7, 8) | CEO/Shift | Too technical/data-dense for a 2-hour condensed session; one cost slide (CEO 6) carries the needed point |
| Diffusion of Innovations (19), "Not that GPT" (20) | CEO | Good material, not load-bearing for this specific narrative at this length |
| AI for Good / AI for Bad (both appear 2x across decks, also in LSD) | CEO/LSD | Long generic ethics essays; the Wingman story + governance framework slides do this job faster and more specifically |
| RAG/vector database mechanics (CEO 56-60) | CEO | Practitioner-level detail, will lose a mixed exec room; one sentence on the concept is sufficient |
| Skill Leveling Effect (Shift 15) | Shift | Good stat, but risks reading as a headcount-reduction message before governance/trust framing has landed — safer to leave out |
| Full construction/manufacturing industry deep dives (Shift 33-45) | Shift | Interesting benchmarking, not essential; if time allows, one line referencing JPMorgan/Goldman stats during the FP&A section is enough external validation |
| AI Resources slide (appears in every deck) | All | Nice-to-have follow-up reading list; hand out or email afterward rather than spend room time on it |

---

## Narrative gaps flagged (things the library doesn't have)

1. **No dedicated HR practical-use-case deck.** This is the one place Section 7 has to run as live facilitation rather than slide-driven teaching, unlike FP&A/Accounting and Development which both have purpose-built source material. See Section 7 above for the workaround and a recommendation to build this as a proper fourth deck if HR becomes a recurring ask across clients.
2. **No AI cost-governance / FinOps-for-AI deck.** Section 9 stitches this together from adjacent material (Common SMB Mistakes, Investment Rules of Thumb, Landing Zone's Tool Registry) because no single deck addresses "managing AI subscription/tool cost as you scale" directly. This worked well enough for this session, but if cost governance keeps coming up as a client topic, it's worth its own dedicated slide set.
3. **Ben's AI pitch deck and Ayotunde's 100+ item use-case catalog** — external to Improving's library, not reviewed here, referenced only because the prep brief flagged them as possibly-not-yet-delivered. Confirm on arrival; if they did arrive, they may offer additional real Remington-specific examples worth weaving into Sections 5/6/7 live, but that's a same-day judgment call, not something to pre-build into this plan.

---

## Quick reference: what to read vs. ad-lib, by section

| Section | Read from slide | Ad-lib |
|---|---|---|
| 1. Welcome | Icebreaker prompt, "Who am I" bullets | Maturity-spread framing, naming Jason Pool/Randy |
| 2. Fundamentals | AI/ML diagram | Cost point, three-waves bridge |
| 3. Maturity Model | Stage labels | Identity/Trust barrier framing, cold-calls to room |
| 4. Mapping Impact | Quadrant labels | Payroll/sales economics Socratic bit |
| 5. FP&A/Accounting | 4-box grids, expected-outcome stats | Framing questions to Randy |
| 6. Development | (diagrams only, minimal reading) | Nearly everything; invite Nick Clark |
| 7. HR | Discussion prompt only | Nearly everything — this is a facilitated conversation |
| 8. Governance | 7 principles, 4 framework names | Wingman story, Ayotunde acknowledgment |
| 9. Cost Governance | 5 SMB mistakes | Ashford→Remington framing, cloud-cost-shock analogy |
| 10. Adoption Path | Week1/Month1/Quarter1, Three Questions | "Don't skip steps" framing |
| 11. Close | Closing line | Handoff to Diana |
