# Fractional Chief AI Officer - Execution Playbook

**A repeatable model for delivering Fractional CAIO engagements to clients who lack the function internally.**

| | |
|---|---|
| **Owner** | David O'Hara - Improving |
| **Status** | Living document - `v0.5 SKELETON` |
| **Last updated** | 2026-07-10 |
| **Origin** | Templated from the Springline Advisory engagement (PE-backed CPA/advisory roll-up). Generalized for reuse. Second live engagement (Systemic Compliance, a regulated/compliance-vertical client) added 2026-07-10 - see §13A for the vertical-specific pattern it surfaced. |
| **Audience** | Improving advisory + delivery leads running or scoping a Fractional CAIO engagement. |

> **How to use this file.** This is the operating manual, not the strategy deck. Sections marked `[TEMPLATE]` contain reusable scaffolding (questions, criteria, structures). Sections marked `[PATTERN]` describe judgment that recurs across engagements. Replace every `<placeholder>` with client specifics when standing up a new engagement. Update this file as engagements teach us what works - see the Changelog at the bottom.

---

## 0. Document Map

1. What This Engagement Is (and Is Not)
2. Engagement Qualification - Is This a Fit?
3. The Operating Model (Two Tracks, One Rhythm)
4. The Deliverable Catalog
5. The First 90 Days - Reusable Phase Plan
6. Cadence & Rhythm (Weekly / Monthly / Quarterly)
7. Time & Staffing Model
8. Stakeholder Map - Roles We Always Need
8A. The Engagement Compact - What We Need From the Client `[TEMPLATE]`
9. Discovery Toolkit `[TEMPLATE]`
10. Decision Gates & Funding Model
11. Governance Baseline `[TEMPLATE]`
12. Measurement & KPIs
13. Risk Register `[PATTERN]`
13A. Vertical Pattern - Regulated / Compliance-Heavy Clients `[PATTERN]`
14. Commercials
15. Reusable Artifacts & Templates Index
16. Lessons Learned Log
17. Changelog

---

## 1. What This Engagement Is (and Is Not)

`[PATTERN]`

The Fractional CAIO engagement gives a client **senior AI leadership without a full-time executive hire**. We own the strategy, the sequencing, the governance spine, and the investor/board narrative. We do not own the building - execution runs as a separate, bid-per-program track.

**The one-line positioning:**
> "I am not here to sell you AI. I am the officer accountable for making sure every dollar you put toward AI produces evidence, drives the roadmap, and builds a story your board and stakeholders can hold."

**Is:**
- A named officer accountable across quarters - continuity, not a deliver-and-leave consult.
- Strategy, roadmap, sequencing, architecture/governance direction, and the board narrative.
- An operating rhythm with decision gates that tie spend to evidence.

**Is Not:**
- Pilot construction, tool procurement, vendor management, or platform rollout (those are execution bids).
- A full-time seat. If hours balloon, scope is bleeding - re-bid it.
- A replacement for an internal AI owner. We augment and accelerate one, or flag the gap.

---

## 2. Engagement Qualification - Is This a Fit?

`[TEMPLATE]`

Score a prospect against these. The model is strongest when most are true.

- [ ] **No internal CAIO / AI function** (or one that is understaffed and over-tasked).
- [ ] **A forcing event** that makes AI strategy time-sensitive (capital event, integration window, competitive pressure, regulatory deadline).
- [ ] **Leadership that thinks in operating systems** - values rigor, measurement, and gates over enthusiasm.
- [ ] **Capital discipline** - wants evidence before scale; allergic to "AI theater."
- [ ] **A stakeholder who must be convinced** the story is real (board, PE sponsor, acquirer).
- [ ] **Enterprise stack we can anchor on** (e.g., Microsoft 365 / Azure / Snowflake) rather than greenfield chaos.
- [ ] **Distributed or federated structure** where a modular, evidence-gated approach beats a monolithic plan.

**Anti-signals:** wants a body to do the work, not direct it; expects a one-time deck; no budget authority in the room; treats AI as a tooling purchase.

---

## 3. The Operating Model (Two Tracks, One Rhythm)

`[PATTERN]`

```
STRATEGY → SEQUENCING → PILOTS (capped, fail-fast) → EVIDENCE GATE → SCALE/KILL → NARRATIVE → (loop, sharper)
```

| Track | What it is | Who owns it | Funding |
|---|---|---|---|
| **Advisory** | Strategy, architecture/governance decisions, sequencing, gates, board narrative | Fractional CAIO (us) | Flat quarterly retainer |
| **Execution** | Stand up initiatives, instrument them, report hard numbers | Purpose-built delivery pod (AI lead + embedded engineers) | Bid per program, with stated ROI hypothesis |

**Core principle - decoupling.** Advisory is never bottlenecked by delivery; delivery is never unmoored from strategy. They share one rhythm and one decision gate.

**Inherited operating principles (carry into every engagement):**
- Model-agnostic; route to the right model, avoid lock-in.
- Two parallel portfolios: efficiency (hard ROI) and innovation (upside).
- Budget to fail fast; cap every pilot.
- Governance gates the move into composed/workflow automation - non-negotiable.
- Enterprise-secured tools trail frontier capability by ~2.5–3 months; sequence around it.

---

## 4. The Deliverable Catalog

`[TEMPLATE]` - Standard quarter-one foundation set. Adapt names; keep the spine.

| ID | Deliverable | Purpose | Acceptance criteria (definition of done) |
|---|---|---|---|
| **D1** | Multi-year AI Strategy | Vision everything is measured against; container for the board narrative | Approved by principal; framed in client's ROI language; tied to the forcing event; not date-locked |
| **D2** | 3-Year Roadmap | Translate strategy to sequenced, unit-by-unit execution | Each initiative mapped to a horizon + target unit; first pilots in cleanest-data / lightest-change area; re-sequenceable at each gate |
| **D3** | Prioritized Pilot List + ROI Hypotheses | Capital-allocation tool for the first gate | Every pilot: named owner, metric baseline, budget cap, gate date, falsifiable hypothesis; surfaced from discovery |
| **D4** | Board & Investor Narrative | Position the program for diligence / board comms | Readable in ~30 min; classifies portfolio by realization state; matches the reality being lived |
| **D5** | Governance Baseline | Precondition for workflow automation at scale | Signed off by security/legal/HR; defines approvals + audit trails; sufficient that no scaled workflow ships without it |
| **D6** | Reference Architecture v1 *(companion)* | Set architectural direction | Preserves enterprise controls + data residency; keeps model access open; we set direction, pod owns depth |

**Recurring quarterly set (post-Q1):**

| Quarter | Deliverables | Outcome |
|---|---|---|
| Q1 | D1–D6; first pilots started | Strategy set, pilots running, board story drafted |
| Q2 | Pilot evidence + gate decisions; scaled-work scoping; governance hardened; narrative refresh | Validated ROI, first scale decisions |
| Q3 | Scaled rollout; next wave designed; architecture/model-routing updates; diligence pack updated | Gains compounding, roadmap extended |
| Q4 / ongoing | Program review vs. KPIs; strategy refresh; investor-readiness pack | Investor-ready position with a track record |

---

## 5. The First 90 Days - Reusable Phase Plan

`[TEMPLATE]`

**Goal by day 90:** strategy set, governance baseline in place, first pilots running against hypotheses, board narrative drafted, operating rhythm run at least once.

### Phase 1 - Mobilize & Discover (Weeks 1–3)
- Charter & access: confirm scope, gate cadence, independence statement; secure admin + security/legal/HR access; set the weekly working session.
- Discovery workshops with unit/department leaders (see §9 toolkit).
- Maturity map: place each unit on the maturity model; pick the lead unit for the first pilot; identify resisters to sequence around.
- Lock the principal's 12-month definition of success and the metric under pressure.

### Phase 2 - Strategy & Sequencing (Weeks 4–6)
- Draft D1 (strategy), D2 (roadmap), D3 (scored pilot list).
- Strategy review with principal; secure go-ahead to fund the first tranche.

### Phase 3 - Govern & Launch (Weeks 7–10)
- D5 governance baseline with security/legal/HR - **leads the launches, does not trail them.**
- D6 reference architecture v1.
- Pilot kickoff with the pod; instrumentation from day one.
- First monthly initiative gate - practice the ritual.

### Phase 4 - Narrate & Set Cadence (Weeks 11–13)
- D4 board/investor narrative draft.
- First quarterly portfolio gate.
- Q1 readout; confirm Q2 plan and standing cadence.

**90-day exit criteria:**
- [ ] Strategy + roadmap approved.
- [ ] Governance baseline signed off.
- [ ] ≥2 pilots live, instrumented, running against hypotheses.
- [ ] Board narrative v1 delivered.
- [ ] Monthly + quarterly gates each run once.

---

## 6. Cadence & Rhythm

`[PATTERN]`

| Rhythm | Frequency | Purpose | Output |
|---|---|---|---|
| Working session | Weekly | Progress, blockers, decisions with day-to-day counterpart | Action log |
| Delivery-pod sync | Weekly (when a build cycle is active) | Coordinate the execution pod you pull in; you direct, they build | Architecture + delivery decisions |
| Initiative gate | Monthly | Release tranche against evidence | Fund / scale / pause / kill |
| Portfolio gate | Quarterly | Reset horizon envelopes, refresh roadmap | Continue / scale / stop |
| Principal 1:1 | Monthly | Alignment, narrative, escalations | - |
| Standing update comms | Ongoing (written) | Keep principal current between gates | Snapshot + gate notes |
| CEO update Q&A | Standing window / same-day on request | Questions against the standing updates | Answered, decisions surfaced |
| Pre-meeting positioning | Per board / external meeting | Prep the CEO on the AI story before the room | Talking points + framed snapshot |
| Board / sponsor readout | Quarterly or per event | Investor-ready snapshot | Updated narrative |

---

## 7. Time & Staffing Model

`[TEMPLATE]`

| Phase | CAIO hours/week | Note |
|---|---|---|
| Q1 foundation | ~12 (≈1.5 days) | Discovery + deliverable authoring heavy |
| Steady state (Q2+) | ~8 (≈1 day) | Oversight + narrative + coordination |
| Gate weeks | +2–3 (monthly) / +6–8 (quarterly) | Demand spikes |

**Staffing:** CAIO (advisory) + per-cycle delivery pod (AI lead + embedded engineers, sized to the work). Specialist depth (security/data/compliance) pulled in per cycle, not carried as overhead. Reference ratio: ≤3 teams or ~24 people per embedded engineer for coaching/enablement.

---

## 8. Stakeholder Map - Roles We Always Need

`[TEMPLATE]`

| Role we need | Why | Cadence |
|---|---|---|
| **Principal / sponsor (CEO or equiv.)** | Owns vision + definition of success + board relationship | Monthly + gates |
| **Day-to-day operating partner** (COO / Head of Integration / Ops) | Execution reality; their calendar shapes the roadmap | Weekly |
| **Internal AI owner** (may not exist) | Our counterpart; augment or flag the gap | Weekly / as stood up |
| **Data + platform admins** | Provisioning, environment + data state | Weeks 1–8 |
| **Security / IT** | Controls, audit logging, residency | Governance phase |
| **Legal** | Privacy, confidentiality, regulatory boundaries | Governance phase |
| **HR** | Policy compliance, change-management posture | Governance phase |
| **Unit / department leaders** | Discovery input, pilot candidates, lead-unit selection | Weeks 1–3, then per pilot |
| **Capital sponsor (PE/board)** *(if applicable)* | The narrative's ultimate audience; trust accelerant, not a lever | Per event |

---

## 8A. The Engagement Compact - What We Need From the Client

`[TEMPLATE]`

> **Purpose.** The pace and success of the program depend on a small number of commitments from the client. This is the "what we need from you" section to set during scoping and restate in the charter. Share it broadly. When these are honored, the model runs; when they slip, the program stalls and the slippage is the client's, not ours. Lift this into a one-page client-facing leave-behind by replacing the placeholders.

### A. Time commitment expected - from us and from them

This is a senior advisory engagement, not a full-time seat. The hours are deliberately modest, but the *cadence* is non-negotiable.

| Who | Foundation phase (Q1) | Steady state (Q2+) | Spikes |
|---|---|---|---|
| **Fractional CAIO (us)** | ~12 hrs/wk (≈1.5 days) | ~8 hrs/wk (≈1 day) | +2–3 hrs monthly gate · +6–8 hrs quarterly gate/readout |
| **Principal / sponsor** | ~2–3 hrs/wk (discovery, strategy reviews) | ~1–2 hrs/mo (1:1 + gates) + on-demand Q&A and pre-meeting positioning | Quarterly readout; board/external-meeting prep |
| **Day-to-day operating partner** | ~2–3 hrs/wk (working session + access brokering) | ~1.5 hrs/wk (working session) | Gate prep weeks |
| **Internal AI owner** (if exists) | ~3–5 hrs/wk | ~3–5 hrs/wk | - |
| **Unit / department leaders** | ~2–4 hrs total each, in discovery | Per-pilot, as their unit is sequenced | Pilot launch |
| **Security / Legal / HR leads** | ~2–4 hrs each, weeks 7–8 (governance) | As-needed for gate sign-offs | Governance refresh |
| **Data / platform admins** | As-needed, weeks 1–8 (provisioning) | Light | Per pilot |

**Rule of thumb to set expectations:** the client's *aggregate* people-cost in Q1 is a handful of leaders giving a few hours each during discovery and governance, plus a steady weekly working session. It is light by design - the leverage comes from rhythm and decisions, not hours logged.

### B. Interactions required - the standing rhythm they must show up for

The model is a closed loop; missing a beat breaks it. The client commits to:

- [ ] **Weekly working session** with the day-to-day operating partner (and internal AI owner if present). Standing, ~60–90 min.
- [ ] **Monthly initiative gate** - active participation. Evidence is reviewed and a fund / scale / pause / kill decision is made. Decisions cannot be deferred without stalling capital.
- [ ] **Quarterly portfolio gate** - leadership resets horizon envelopes and refreshes the roadmap. This is a structured 90-day decision moment, not a status meeting.
- [ ] **Monthly principal 1:1** - alignment, narrative, escalations.
- [ ] **Discovery workshops** (Q1, weeks 1–3) - unit and department leaders make themselves available.
- [ ] **Board / sponsor readout** - quarterly or per capital event, with the principal present.
- [ ] **On-demand CEO access (JIT)** - two recurring needs, planned rather than ad-hoc:
  - **Update Q&A.** Standing program updates are delivered as ongoing written comms (snapshot + gate notes). The CEO will want a planned window to ask questions against those updates - not interrupt-driven, but a reliably available slot (e.g., a short standing hold or a same-day-on-request norm). Set the expectation, then protect the capacity.
  - **Pre-meeting positioning.** Ahead of board meetings, investor conversations, and other external-facing moments, the CEO will want the CAIO to prep them on the AI story - what to lead with, what the snapshot says, what questions to expect, and how to frame in-flight vs. optioned work. Treat this as a named, recurring interaction tied to the board/external calendar, not a surprise.

**Decision-rights expectation:** someone in the room at each gate must hold the authority to release the next tranche. Gates without budget authority become theater.

**Capacity note for us:** on-demand CEO access is a feature of this role, not scope creep - a CEO buying a Fractional CAIO is partly buying a person they can call before they walk into a board room. But it has to be *planned* capacity. Map it to the client's board/external-meeting calendar in advance, hold a standing Q&A window, and absorb it into the steady-state hours (it is a meaningful share of the principal-facing time). If it grows beyond a standing window plus pre-meeting prep, revisit the retainer scope.

### C. Access required - what must be granted, and by when

Access is the most common source of delay. Secure it in writing in week 1.

| Access needed | For | By when |
|---|---|---|
| **Leadership availability** - principal, operating partner, unit leaders | Discovery, strategy reviews, gates | Week 1 onward |
| **Data platform** (e.g., Snowflake / warehouse) - admin + state-of-consolidation | Roadmap sequencing, architecture, pilots | Weeks 1–8 |
| **Tenancy / productivity stack** (e.g., M365 / Azure) - admin + provisioning | Environment + pilot stand-up | Weeks 1–8 |
| **Security / IT** | Controls baseline, audit logging, data residency | Governance phase (wk 7–8) |
| **Legal** | Data-privacy controls, confidentiality + regulatory boundaries | Governance phase (wk 7–8) |
| **HR** | Policy compliance, change-management + workforce-impact framing | Governance phase (wk 7–8) |
| **Existing AI work / prior pilots** | Build on (or recover from) organizational memory | Discovery |
| **Budget visibility** - who controls tech spend, centralized vs. federated | Funding + sequencing decisions | Discovery |

### D. The independence statement *(when a shared sponsor or related party exists)*

When client and provider share a capital sponsor or other relationship, name it early and state the engagement is arm's-length B2B governed by NDA and confidentiality. Use the relationship for warmth and context once; let the work stand on its own merits. Help the client state that independence clearly to its own team and stakeholders.

### E. What happens if the compact slips

`[PATTERN]` - Frame this constructively, not as a threat. Use it to protect the program.

- **Access delayed** → roadmap and pilots slip; we re-sequence to whatever is unblocked and flag the dependency at the next gate.
- **Gate skipped** → capital sits idle and evidence goes stale; we hold the tranche rather than release on a guess.
- **Working session lapses** → decisions queue up and the loop loses its tightening effect; we escalate to the principal 1:1.
- **Scope drifts into the retainer** → we name it and re-bid it as an execution program with its own ROI hypothesis.

---

## 9. Discovery Toolkit

`[TEMPLATE]` - Question banks for Phase 1. Trim per client.

**Organizational readiness**
- Where does AI show up in the current plan - funded, or whiteboard?
- Who has driven AI conversations so far, and what happened?

**Data & infrastructure**
- How far along is the data consolidation across units?
- Shared data-governance policy today, or unit-by-unit?

**Commercial pressure**
- What does the next board/investor review look like? What narrative are you bringing?
- Which efficiency or growth metric is leadership under pressure to move?

**Political landscape**
- Who controls the technology budget - centralized or federated?
- Which unit leaders will run a pilot first? Which will resist?

**Prior experience**
- Has any unit run an AI pilot? What worked, what didn't, what's the organizational memory?

**Definition of success**
- Twelve months from now, what makes you say this was worth it?

---

## 10. Decision Gates & Funding Model

`[PATTERN]`

**Horizon funding** - fund AI as a portfolio from a defined pool, released by horizon in evidence-gated tranches. Not anchored to a fixed exit date.

| Horizon | Funds | Model |
|---|---|---|
| **H1 - Run** | Efficiency / task agents, hard near-term ROI | Fixed-fee setup + capped fail-fast pilots; targets self-funding from savings |
| **H2 - Scale** | Workflow automation across units, once governed | T&M, released from validated H1 evidence |
| **H3 - Reinvent** | Client-facing growth bets, asymmetric upside | Option-sized probes from a protected pool |

**Gate logic:** every initiative enters under a hypothesis + cap. At the gate, evidence decides: **fund next tranche / scale / pause / kill.** Freed capital reallocates to the highest-yielding horizon.

**Exit-ready snapshot** (emitted at any gate):

| State | Definition | Role in diligence |
|---|---|---|
| Realized | In production, measured value | Proof of AI leverage |
| In-flight | Funded + live, early signal | Momentum + working engine |
| Optioned | Designed + costed, fund on demand | Defensible roadmap with known economics |

---

## 11. Governance Baseline

`[TEMPLATE]` - Minimum spine before scaling workflow automation.

- [ ] **Audit logging** standards - what is logged, where, retention.
- [ ] **Data-privacy controls** - classification, residency, access boundaries.
- [ ] **HR & policy compliance** - acceptable use, workforce-impact framing.
- [ ] **Human approval points** - who approves what, where the gates sit.
- [ ] **Regulatory / structural constraints** - e.g., attest/non-attest separation, sector rules.
- [ ] **Framework alignment** - SOC 2-style controls; reference NIST CSF / CIS where needed.
- [ ] **Sign-off** - security + legal + HR before any scaled workflow ships.

---

## 12. Measurement & KPIs

`[PATTERN]`

Every initiative carries metrics **before** it starts.

- **Efficiency initiatives:** hours saved, cost reduction, cycle time.
- **Innovation initiatives:** proposal velocity, win rate, recovered capacity.
- **Program level:** initiatives by bucket, pilots validated vs. killed, progress vs. roadmap.
- **ROI framing:** prefer **planned-hire offset / capacity freed** over headcount reduction where the client is growth- or talent-constrained. Reference bar: ~5–10x within 12 months; higher for growth bets to pay for failure rate.

---

## 13. Risk Register

`[PATTERN]` - Recurs across engagements.

| Risk | Signal | Move |
|---|---|---|
| Scope creep into retainer | "Can you also run the rollout / vendors?" | Separate execution bid with its own ROI hypothesis |
| Federated resistance | A unit stalls / refuses a pilot | Re-sequence to a willing unit; win creates pull |
| Governance lag | Pressure to scale before controls exist | Refuse to cross the gate without baseline |
| Exit-timing whiplash | Plan anchored to one close date | Keep horizon envelopes; snapshot stays current |
| Internal-hire ambiguity | Client hires its own AI lead | Reframe to augment-and-accelerate |
| Over-leaning on sponsor relationship | Used as pressure | Use for warmth once; let work stand on merits |
| Shadow AI / data exposure | Staff using personal AI accounts with company data, no policy | Lead with a use-and-data-handling policy in week one; it is often the most urgent felt need, ahead of strategy |
| "Big license number" sticker shock | Client prices broad licensing (e.g., $X00K/yr) and stalls on unproven ROI | Reframe: wrong starting point. Run capped experiments with ROI gates, measure productivity vs. license cost, scale only what proves its thesis. Audit hidden add-on costs (e.g., Snowpark/warehouse AI) |
| Off-the-rack proposal mismatch | A generic program deck was sent before discovery | Name it openly; position the real engagement as custom-scoped from current-state assessment. Do not defend the deck |
| Trapped IP in a single vendor seat | Client has already built real capability inside one AI account/seat (e.g., an Anthropic Cowork seat, a personal ChatGPT account) before we arrive - it works, but isn't owned, audited, or portable | Name the extraction as the first move regardless of which strategic path they pick; every downstream option (sell, scale, or license) requires it, so it is never optional and never sequenced last |
| Builder/founder misalignment | A technical builder (often pre-existing, sometimes a contractor) has been building ahead of or apart from the principal's vision and resists direction | Do not manage the builder directly by default - work through the principal/operating partner, hold a separate technical deep-dive to assess the build, and let the principal set the reporting line explicitly |
| GTM over-diversification ("Cheesecake Factory") | Client's real capability spans many adjacent product/service lines with no chosen entry point | Force a choice of 1-2 entry points before or alongside any strategic (build vs. sell) decision - a diffuse pitch undermines every exit path equally |

---

## 13A. Vertical Pattern - Regulated / Compliance-Heavy Clients

`[PATTERN]` - Surfaced from the Systemic Compliance engagement (pipeline safety / OQ / PSMS). Generalizes to any client whose core asset is a large, regulation-linked requirements corpus (rail, power, chemical, healthcare, financial compliance).

**What is different about this vertical:**

- **The forcing event is regulatory, not competitive.** A voluntary standard moving toward mandatory status (e.g., API RP 1173 / PSMS) or a rulemaking docket is often the real clock, not a capital event or a competitor. Ask directly what's in the Federal Register or state-agency pipeline before assuming the forcing event is commercial.
- **The requirements corpus is the crown-jewel asset, and it is usually a spreadsheet.** Regulated clients tend to have built a real crosswalk (regulation-to-obligation-to-procedure) as a giant spreadsheet before any of this reaches an AI system. That spreadsheet becoming a tagged, queryable database is almost always the highest-leverage early move - it precedes and enables everything else (eval harness, gap analysis, MOC/change-impact tooling).
- **Semantic-only search fails at scale.** Once the corpus grows past what one model session holds reliably, keyword + semantic search alone causes "semantic saturation" - the model merges similar-but-distinct requirements (e.g., two adjacent CFR subclauses). A durable architecture needs four retrieval methods working together: **K**eyword (exact citation match), **S**emantic (meaning/intent), **T**emporal (what applied when - handles grandfathering and effective dates), and **G**raph (linkages, equivalencies, peer relationships). Missing T+G is the most common gap we'll find already built.
- **The evaluation harness is the sales weapon, not just quality control.** An AI checking its own work fails at a high rate in this domain; independent graders, held-out datasets, and edge-case/false-premise tests double as the proof a buyer, auditor, or regulator will ask for. Sequence this earlier than a generic engagement would.
- **Watch for cognitive surrender.** As subject-matter reviewers watch the AI get it right repeatedly, they stop catching the times it doesn't. Track and ask for the reviewer kickback rate directly - a rate near zero after many runs is a warning sign, not reassurance.
- **Governance has to be active, not just a report.** Regulated management systems tend to run Plan-Do-Check-Act; the value of the AI layer is intervention *before* the compliance miss, with trended KPIs, not a static output document after the fact.
- **Data-use consent on the training corpus is a near-certain gap.** If the client has anonymized one customer's/operator's procedures to train or benchmark against others, ask directly whether explicit data-use agreements exist. In our experience they usually do not yet, and it is worth flagging in the first working session rather than waiting to find it - see the shadow-AI/data-exposure risk row above, of which this is a vertical-specific instance.
- **Auditability and model independence are the technical spine to own.** Every AI-assisted determination in this space needs an immutable audit trail (who decided what, on what basis) and a model-agnostic abstraction layer, since regulators and counsel will ask what happens if the underlying model changes or is challenged.

**How this changes the standard playbook:**

- In the Deliverable Catalog (§4), D5 (Governance Baseline) and D6 (Reference Architecture) effectively move earlier and merge with D2/D3 - governance-and-architecture-together is closer to a single week-one conversation than two sequential deliverables.
- In Discovery (§9), add: "What does your requirements corpus look like today - spreadsheet, database, or something else?" and "What's the actual regulatory clock here - is something moving from voluntary to mandatory?"
- In the Risk Register (§13), expect Trapped IP, Builder/founder misalignment, and GTM over-diversification (all added above) to show up together, not independently - they compound.

---

## 14. Commercials

`[PATTERN]`

- **Standing fee:** flat quarterly advisory retainer (Springline reference: $20K/qtr). The only standing cost.
- **Execution:** bid per program, each carrying an explicit ROI hypothesis (named return, metric, 12-month bar).
- **Principle:** never fund a program without a stated return; never scale one that fails its own hypothesis. Keeps standing cost small and ties every execution dollar to a pre-defined return.

---

## 15. Reusable Artifacts & Templates Index

`[TEMPLATE]` - Link as they are built.

- [ ] Engagement charter template
- [ ] Discovery workshop deck + question bank (§9)
- [ ] Maturity-map scoring sheet (per unit)
- [ ] Pilot-scoring template (hypothesis / metric / cap / owner / gate)
- [ ] Gate decision record template
- [ ] Board narrative skeleton (Realized / In-flight / Optioned)
- [ ] Governance baseline checklist (§11)
- [ ] Weekly working-session agenda template
- [ ] Quarterly portfolio-gate template
- [ ] Example deliverables (sanitized) - `<links>`

---

## 16. Lessons Learned Log

`[PATTERN]` - Append after each engagement / milestone. Format: date · engagement · what we learned · what changes in the playbook.

| Date | Engagement | Lesson | Playbook change |
|---|---|---|---|
| 2026-06-18 | Springline (origin) | A shared capital sponsor accelerates trust but must be kept arm's-length and visible as such | Added sponsor-handling guidance to §8 and §13 |
| 2026-06-18 | Springline (June 16 call) | The most urgent felt need was governance / shadow-AI exposure, not strategy. Staff likely using personal AI accounts with company data; no policy yet. The strategy sale lands once the immediate risk is named | Added shadow-AI risk row (§13); flag governance/use-policy as a possible week-one quick win |
| 2026-06-18 | Springline (June 16 call) | Buyer priced broad licensing at ~$600K/yr and stalled on unproven ROI. The capped-experiment / ROI-gate frame is the unlock | Added "big license number" risk row (§13) |
| 2026-06-18 | Springline (June 16 call) | Scope was genuinely open: strategy deliverable vs. augmented leadership role vs. path to delivered implementation. Discovery sells the engagement; do not pre-commit a shape | Reinforces discovery-first sequencing; current-state assessment as the lead offer |
| 2026-06-18 | Springline (June 16 call) | A generic / off-the-rack proposal had been sent ahead of discovery and both sides agreed the real work would be custom. Name it, do not defend it | Added off-the-rack-mismatch risk row (§13) |
| 2026-06-18 | Springline (June 16 call) | Use-case portfolio framed by client as three buckets (back office, front office/sales enablement, practitioner tools). Compressibility x demand matrix: value concentrates in back-office tasks with unlimited demand | Consider a standard 3-bucket use-case lens + demand/compressibility scoring in discovery toolkit |
| 2026-07-10 | Systemic Compliance (Jul 8 whiteboard) | Client had already built a real AI capability (SC.IMS) inside a single Cowork seat before we arrived - working, but unowned and unauditable. Both of their strategic paths (keep-and-scale or sell) required the same first move: get it out of the seat | Added "Trapped IP in a single vendor seat" risk row (§13); this is now treated as a default first-move check on any engagement, not vertical-specific |
| 2026-07-10 | Systemic Compliance (Jul 8 whiteboard) | A technical builder (contractor, pre-existing) had been building ahead of the founder's vision and resisting direction. The founders explicitly asked to be in every conversation going forward rather than have us work with the builder directly | Added "Builder/founder misalignment" risk row (§13): default to working through the principal, not the builder, until told otherwise |
| 2026-07-10 | Systemic Compliance (Jul 8 whiteboard) | Client's real capability spanned five adjacent product/service lines with no chosen go-to-market entry point ("Cheesecake Factory" - client's own words). This surfaced as a live blocker to the build-vs-sell decision, not a separate marketing question | Added "GTM over-diversification" risk row (§13): force 1-2 entry points before or alongside the strategic decision |
| 2026-07-10 | Systemic Compliance (Jul 8-9 sessions) | Engagement is in a regulated/compliance-heavy vertical (pipeline safety). Surfaced vertical-specific patterns not present in the Springline case: regulatory (not competitive) forcing events, spreadsheet-as-crown-jewel requirements corpora, need for combined keyword/semantic/temporal/graph search at scale, evaluation harness as a sales weapon, cognitive-surrender risk, and data-use consent gaps on training corpora | Added §13A Vertical Pattern - Regulated / Compliance-Heavy Clients |
| 2026-07-10 | Systemic Compliance (Jul 9 Orb demo) | A client-built AI feature was running on a different model vendor (Gemini) than the client's own stated platform preference (Claude/Cowork) and our standard stack guidance, discovered only during a technical walkthrough, not during scoping | Vendor/model audit belongs in the governance-baseline discovery pass (§9, §11), not deferred to a later technical deep-dive |

---

## 17. Changelog

| Version | Date | Author | Notes |
|---|---|---|---|
| v0.1 SKELETON | 2026-06-18 | David O'Hara | Initial skeleton, generalized from the Springline engagement. Structure + templates in place; to be filled and refined as the engagement proceeds. |
| v0.2 SKELETON | 2026-06-18 | David O'Hara | Added §8A The Engagement Compact - recommended time commitments, required interactions, access expectations, independence statement, and slippage handling for any similar engagement. Designed to lift into a client-facing one-pager. |
| v0.3 SKELETON | 2026-06-18 | David O'Hara | Added on-demand (JIT) CEO access as a planned interaction: standing update Q&A against ongoing written comms, and pre-meeting positioning ahead of board/external meetings. Reflected in §6 cadence, §8A interactions + time table, and a capacity note. |
| v0.4 SKELETON | 2026-06-18 | David O'Hara | Removed all em-dashes. Folded in implied needs from the June 16 Springline call: shadow-AI/data-exposure, license sticker-shock, open scope, off-the-rack mismatch, and the 3-bucket use-case lens. Added 3 risk rows (§13) and 5 lessons (§16). |
| v0.5 SKELETON | 2026-07-10 | David O'Hara (Jarvis) | Added Systemic Compliance as a second live reference engagement. New §13A Vertical Pattern - Regulated / Compliance-Heavy Clients, generalized from the Jul 8 whiteboard and Jul 9 Orb demo sessions. Added 3 risk rows (§13: Trapped IP, Builder/founder misalignment, GTM over-diversification) and 5 lessons (§16). Updated Origin line to reflect the second engagement. |
