# Banking AI Conference Talk: Slide-by-Slide Structure (60-Minute Version)

**Source:** `projects/banking-ai-concepts-anonymized.md`
**Audience:** banking executives (business value first, some technical depth)
**Runtime:** 60 minutes, 32 slides (58 min content + 2 min buffer)
**Working title:** "What AI Makes Possible in Banking: Settlement, Compliance, and the Always-On Bank"

A 30-minute talk needs an argument. A 60-minute talk needs the argument plus evidence, application, and audience work. This structure keeps the five-concept arc and adds: per-concept evidence slides, an economics thread that starts in the opening and pays off per concept, a dedicated implementation-path section, and a structured audience reflection before the close.

## Anonymization Guardrails (apply to every slide and every reused asset)

- No bank names, platform names, customer names, people, or dates.
- No charter or conversion references. Say "regulatory standing and a client base," never "charter." No legislation names; say "rules for digital-asset and stablecoin activity as they take shape."
- No rollout or phase plans for the reference case, no geography.
- Reused slides from client decks (Systemic Compliance briefing, Kazakhstan Delegation, Wendy's QBR) are concept and layout donors only. Rebuild the visuals; never show client-confidential slides as-is, and strip client names from speaker notes.
- Reused slides from `Intelligence_OS_v2.pptx` carry dated labels ("late 2026," "2022-2023"). Strip all dates on adaptation.
- No build-duration facts are used anywhere. Slide 18 previously carried a "first client live within roughly one quarter" line sourced from the private research brief; David replaced it with a generic investment-payback claim, so no private timeline detail appears on any slide.

## Time Allocation

| Section | Slides | Minutes |
|---|---|---|
| 0. Opening frame | 1-4 | 4 |
| 1. The reference case | 5-7 | 5 |
| 2. Concept 1: Remove banking hours | 8-11 | 7 |
| 3. Concept 2: Compliance as product | 12-15 | 8 |
| 4. Concept 3: Bank as infrastructure | 16-18 | 6 |
| 5. Concept 4: Regulatory posture as strategy | 19-21 | 6 |
| 6. Concept 5: Established institutions can build | 22-25 | 8 |
| 7. The implementation path | 26-29 | 9 |
| 8. Reflection and close | 30-32 | 5 |
| Buffer (overrun, extended Q&A drift) | n/a | 2 |

---

## Section 0: Opening Frame (4 min)

### Slide 1: What AI Makes Possible in Banking
**Reuse: NEW**
- Key Point: Five things AI newly makes possible in banking, proven by one institution that built them.
- Content:
  - Subtitle: Settlement, Compliance, and the Always-On Bank
  - One case, five concepts, and a path you can walk on Monday
- Speaker Notes: Open with the promise. The next hour maps to systems that exist, not vendor roadmaps. No names today; the pattern is the point.
- Visual: Clean title card. Nothing else.

### Slide 2: The Divide
**Reuse: `presentations/mit-nanda-genai-divide.pptx`, slide 1 ("95% of enterprise AI pilots deliver no measurable business ROI")**
- Key Point: 95% of enterprise AI pilots deliver no measurable ROI. This talk is about the 5% who ship.
- Content:
  - The failure is integration, not technology
  - The divide is between institutions that demo and institutions that ship
- Speaker Notes: This room has sat through a hundred pilot decks. Set the economics thread here: the money is not where most of the budget goes. (Adaptation: keep the stat card, reframe the subtext for banking, strip the report date.)
- Visual: Single large stat (95%) with one-line framing.

### Slide 3: The Problem Isn't the Technology
**Reuse: `presentations/mit-nanda-genai-divide.pptx`, slide 2 ("The Problem Isn't the Technology" / Wrong Budget Allocation)**
- Key Point: More than half of GenAI spend targets sales and marketing, but the biggest returns are in back-office operations and finance.
- Content:
  - The research calls it the learning gap: failure to integrate AI into workflows, structures, and culture
  - Budget follows visibility, not value
- Speaker Notes: This is the economics thesis of the whole talk in one slide. Settlement and compliance are back office. That is exactly where the returns are, and exactly where nobody's keynote points. (Adaptation: keep the budget-allocation stat, add the banking gloss in notes only.)
- Visual: Split bar: where the spend goes vs where the returns are.

### Slide 4: Banking Is Already the Leader
**Reuse: `reference/Intelligence_OS_v2.pptx`, slides 23-25 ("Financial Services" / "The Clear Leader" / "What's Deployed vs. Emerging")**
- Key Point: Financial services runs more production AI than any other industry, so the question is no longer adoption. It is what the frontier looks like.
- Content:
  - Majority of the industry operates at mid-level maturity; leaders are well beyond it
  - Major institutions run production systems, not pilots
- Speaker Notes: You are not deciding whether to adopt AI. Your peers already did. The live question is what gets built on top of it. (Adaptation: merge the three financial-services slides into one, strip stage numbers and date labels, reframe from "maturity survey" to "the bar has moved.")
- Visual: Industry comparison bar, financial services at the front.

---

## Section 1: The Reference Case (5 min)

### Slide 5: One Bank, Two Systems
**Reuse: NEW**
- Key Point: An established bank built two proprietary systems that work as a gateway and a guardian at once.
- Content:
  - A real-time settlement network: always-on, API-driven, instant execution and finality for institutional clients
  - An AI-native compliance and risk-intelligence system: proactive monitoring with compliance-vetted onboarding
  - A full banking stack behind the API: clearing, settlement, custody, trust services, and commercial lending
- Speaker Notes: Deliberately anonymized. The pairing is the story: access is the product, and the compliance system is what makes that access safe to sell. Note the stack: this is not a payments widget bolted onto a bank. The whole bank sits behind the API.
- Visual: Two-box diagram (settlement network, compliance system) over a "full banking stack" band, feeding "institutional clients."

### Slide 6: The Gateway
**Reuse: NEW**
- Key Point: The settlement network combines reach into legacy payment rails with instant execution and finality, offered exclusively to the bank's institutional clients.
- Content:
  - Always-on execution, API-driven, no cutoff windows
  - Institutional clients only; it is not a public developer product
  - Announced-and-building AI capabilities: intelligent payment routing, real-time anomaly detection, predictive liquidity management
  - Launch-scale flows: est. $100M+ per day in institutional payment capacity
  - Effective settlement coverage: est. 3x the operating hours of legacy rails
  - Finality in seconds vs 1-3 business days on batch rails (comparative, est.)
- Speaker Notes: Discipline moment. Say plainly which capabilities are live and which are announced-and-building; that discipline extends to the numbers, and every figure on this slide is presented as an estimate. Assumptions: the $100M/day figure assumes institutional flows of roughly 5-10% of a $1.5B balance sheet turning daily, consistent with correspondent-heavy books; UBPR peer group 4 (commercial banks $1B-$3B, 529 banks, 6/30/2026) holds 22.3% of assets in demand deposits, roughly $330M per $1.5B bank, so the daily-flow scale is in line with the transaction balances peers actually carry. The 3x coverage figure compares 8,760 always-on hours per year with roughly 2,800-3,000 wire-window hours under standard Fedwire operating schedules; the finality contrast is from Federal Reserve payment-study comparatives. The room will forgive a roadmap; they will not forgive being misled about one.
- Visual: Diagram of one API fronting legacy rails plus instant settlement, with a "live / building" legend.

### Slide 7: The Guardian
**Reuse: NEW**
- Key Point: The compliance system is what makes regulated access to the network a product in itself.
- Content:
  - Proactive monitoring: transaction-pattern analysis, counterparty behavior modeling, emerging-risk detection
  - Compliance-vetted onboarding as the front door
  - Designed to catch exposure before it reaches the balance sheet
  - Legacy institutional onboarding runs 30-90 days (comparative, est.); vetted, automated onboarding targets 5-10 days (est.)
  - Legacy AML monitoring false-positive rates run above 90% (comparative, est.); AI-native triage targets roughly half that (est.)
  - Per-review KYC cost runs $2,000-5,000 (comparative, est.); automation targets a 40-60% reduction (est.)
- Speaker Notes: Gateway and guardian at once. Most banks bolt compliance onto a product after the fact; here the vetting is the access. Assumptions: the onboarding, false-positive, and per-review ranges come from published industry compliance benchmarks and vendor studies, scaled to a $1.5B-asset bank's institutional book; the bank's own figures are not public, so everything here is a comparative labeled est. Scale anchor from UBPR peer group 4 (6/30/2026): total overhead runs 2.51% of assets, roughly $38M a year at $1.5B, with personnel at 1.45% (about $22M, avg $122.7K per employee, about 170 employees at $8.9M assets per employee); compliance is conventionally 5-10% of that overhead base, so $2-4M a year at this size. Hold the full economics for section 3; plant the seed only.
- Visual: Gate metaphor: onboarding vetting as the doorway into the network.

---

## Section 2: Concept 1: Money Moves on Banking Hours; AI Removes the Hours (7 min)

### Slide 8: Concept 1: AI Removes the Hours
**Reuse: NEW (optional backdrop from `reference/Intelligence_OS_v2.pptx`, slide 13, "Three Waves of Enterprise GenAI")**
- Key Point: The first thing AI makes possible: settlement with no banking hours.
- Speaker Notes: Section divider, five seconds. If using the Three Waves backdrop, the point is that always-on operations are the wave after copilots, and this bank is already there. (If used: strip the year labels.)
- Visual: Divider card, large numeral 1.

### Slide 9: The Batch World
**Reuse: NEW**
- Key Point: The incumbent settlement stack is batches, cutoffs, and provisional finality.
- Content:
  - ACH value settles in 1-2 business days, on banking days only: roughly 250 settlement days a year (comparative, est.)
  - Wires carry intraday cutoff risk; miss a mid-afternoon cutoff and value date slips a full day
  - Even the newer instant rails offer only provisional finality
  - Money in flight is not free: est. $10-15K of carry per day per $100M at roughly 5% short rates
  - Cross-border correspondent legs run 1-5 days and 1-6% total cost depending on corridor (comparative, est.)
- Speaker Notes: This is the water your clients swim in, and they have stopped noticing it. Every "real-time" claim they have heard so far is a faster horse. Assumptions: the carry-cost figure is principal times roughly 5% annualized short rates divided by 365; cross-border time and cost ranges are World Bank remittance and industry comparatives; the settlement-day count is the standard ACH banking-day calendar. All figures presented as estimates, from public comparatives rather than the reference case itself.
- Visual: A payment's journey across legacy rails against a cutoff clock.

### Slide 10: A Different Product Category
**Reuse: NEW**
- Key Point: Always-on, AI-driven settlement is not a speed upgrade. It is a different product category.
- Content:
  - Intelligent routing across rails, executing around the clock
  - Real-time anomaly detection on every flow
  - Predictive liquidity: the network anticipates where money needs to be instead of waiting for instructions
- Speaker Notes: The technical-depth beat for this section. The shift is from executing instructions to anticipating need. One sentence of mechanism is enough; the room buys the category point, not the architecture.
- Visual: Side-by-side: "executes on instruction" vs "anticipates and routes."

### Slide 11: What Always-On Unlocks
**Reuse: NEW**
- Key Point: Always-on settlement changes the economics of treasury, collateral, and correspondent relationships, not just their speed.
- Content:
  - Liquidity stops being a buffer you hold and becomes a position you manage continuously
  - Client segments that need it: digital-asset firms, correspondent and international institutions, fintechs, AI-native enterprises
  - Programmable banking is the expectation of the next client generation, not a niche
  - Every $100M of idle liquidity buffer carries roughly $5M a year at roughly 5% short rates (est.)
  - Predictive liquidity management targets a 15-25% buffer reduction (comparative, est.); at a $1.5B bank's scale that is $0.75M-1.25M a year, recurring (est.)
- Speaker Notes: Application slide. Give the room one concrete reframe each for treasury and correspondent business. Assumptions: buffer levels of 10-20% of institutional balances are common practice; the reduction range comes from treasury-technology vendor benchmarks and industry studies; the arithmetic is simply $100M times 5%, and both figures are labeled est. on the slide. Scale anchor from UBPR peer group 4 (6/30/2026): peers hold 5.97% of assets in interest-bearing bank balances plus about 1% noninterest cash, roughly $105M of overnight money per $1.5B bank, so a $100M settlement buffer is what the peer group literally carries every night. The client-segment list doubles as a quiet market-sizing: these are the clients who will not wait for a batch window.
- Visual: Four client-segment tiles, each with one line on what always-on means for them.

---

## Section 3: Concept 2: Compliance Becomes a Product, Not a Cost Center (8 min)

### Slide 12: Concept 2: Compliance as Product
**Reuse: NEW**
- Key Point: The second thing AI makes possible: compliance that wins business instead of consuming budget.
- Speaker Notes: Divider. Set up the inversion: every bank in this room books compliance as overhead.
- Visual: Divider card, large numeral 2.

### Slide 13: Compliance as Distribution
**Reuse: concept from `accounts/Systemic Compliance/client docs/SC_Improving-Briefing_SC.IMS-and-SC.ORB_Deck_2026-07-08.pptx`, slide 2 ("The thesis: compliance should be systemic"): concept only, rebuild the visual, that deck is client-confidential. Supporting stat from `reference/Intelligence_OS_v2.pptx`, slide 33 ("Governance: The Autonomy Safety Net")**
- Key Point: When compliance is good enough, it stops being overhead and becomes the reason institutional clients choose you.
- Content:
  - Transaction-pattern analysis and counterparty modeling catch exposure before it reaches the balance sheet
  - Compliance-vetted onboarding makes hard-to-serve clients (digital-asset firms, foreign institutions) viable at all
  - The moat is the vetting, not the rate
- Speaker Notes: AI does not just cut compliance cost; it turns compliance into distribution. The governance research point lands here: autonomy without governance is where the failures cluster, which is why a vetted gate is sellable.
- Visual: A funnel where the compliance gate is the front door, not the back office.

### Slide 14: The Stakes
**Reuse: `presentations/agent-receipts.pptx`, slide 5 ("Three Incidents. One Pattern."); `presentations/your-ai-agents-leak-data-and-money.pptx`, slide 2 (29M secrets finding); `presentations/graded-by-clients-cloned-by-criminals.pptx`, slide 4 ("Voice Cloning: The Phone Call Attack")**
- Key Point: AI-era fraud and agent misbehavior are why compliance credibility, not compliance paperwork, is what institutional clients buy.
- Content:
  - Documented pattern: AI agents acting outside their permissions, then misreporting what they did
  - Credential leakage at industrial scale through public repos
  - Voice cloning has made the phone call an attack vector
- Speaker Notes: Ninety seconds, no fear mongering. The point is not that AI is dangerous; it is that your counterparties know it is, and they will pay for a bank whose monitoring is as modern as the threats. Pick two of the three evidence points on stage; hold the third for Q&A. (Adaptation: keep incident framing generic, no company names from the source decks.)
- Visual: Three small evidence cards, one line each.

### Slide 15: The Economics: Cost Center to Revenue Line
**Reuse: concept donor `accounts/Systemic Compliance/client docs/SC_Improving-Briefing_SC.IMS-and-SC.ORB_Deck_2026-07-08.pptx`, slide 8 ("The pricing disruption is the message"): concept only, rebuild**
- Key Point: Compliance-as-product converts a fixed cost into a priced feature of access, and the pricing power is the message.
- Content:
  - Cost-center compliance scales with headcount; productized compliance scales with software
  - Clients pay for vetted access because it shortens their own path to market
  - The margin question flips: not "what does compliance cost us" but "what is compliant access worth"
- Speaker Notes: This is the slide a CFO repeats on the drive home. Walk the flip slowly: same regulatory obligation, opposite side of the ledger. (Adaptation: the donor slide's pricing detail is client-confidential; keep only the inversion concept.)
- Visual: Two-column ledger: compliance as cost vs compliance as revenue line.

---

## Section 4: Concept 3: The Winning Bank Is Infrastructure, Not a Destination (6 min)

### Slide 16: Concept 3: Infrastructure, Not Destination
**Reuse: NEW**
- Key Point: The third thing AI makes possible: a bank that other companies build their products on.
- Speaker Notes: Divider. This is the strategic fork in the talk; slow down here.
- Visual: Divider card, large numeral 3.

### Slide 17: Destinations vs Infrastructure
**Reuse: NEW (layout borrow from `reference/Intelligence_OS_v2.pptx`, slides 47-48, "The Agentic Landing Zone" / "What Is an Agentic Landing Zone")**
- Key Point: Banks split into destinations fighting for consumer attention and infrastructure that everyone else builds on.
- Content:
  - Infrastructure banks do not compete on branches or apps; they compete on what their APIs let clients launch
  - The platform serves institutional clients only; it is not a public developer product
  - The economics favor the layer everyone needs, not the storefront everyone sees
- Speaker Notes: This is a choice of lane, not a size contest. Ask the room directly: which lane do your current investments point to? (Adaptation: the Landing Zone slides are about internal AI infrastructure; keep the "layer everyone builds on" visual grammar, reframe as bank-as-client-infrastructure, strip internal-offering language.)
- Visual: Two-lane split. Destination lane: branches, apps, attention. Infrastructure lane: APIs, settlement, compliance.

### Slide 18: The Proof Point
**Reuse: NEW**
- Key Point: A client is already shipping a real product on the platform, which is the proof the infrastructure model works.
- Content:
  - First institutional client went live on the platform recently
  - If the build takes 18 months end to end, the economics still pay it back in under 20 months of operation (est.)
  - est. dozens of institutional prospects in the early pipeline
  - est. $50-250K annual fee income per institutional client across settlement, custody, and compliance bundles
  - Infrastructure claims are cheap; a paying client building on you is not
- Speaker Notes: Resist expanding on the client. One live builder outweighs a hundred partnership announcements. The payback claim is deliberately generic: it makes the investment case without revealing how fast the reference case actually built. Arithmetic for the notes, all at $1.5B scale and all labeled est.: the benefit stack is compliance automation $0.8-2.4M/yr (40-60% of a $2-4M compliance base), liquidity buffer release $0.75-1.25M/yr, platform fee income $0.5-2.5M/yr at ten clients, and the real prize, funding value: institutional clients bring low-cost operating deposits, and $100-200M of institutional balances at a roughly 3-4% spread over wholesale funding is worth $3-8M/yr (UBPR peer group 4, 6/30/2026: peers fund at roughly 1.9% average interest expense while wholesale and short-rate alternatives run near 5%). Total stack roughly $5-14M/yr, central case about $9M. Against an estimated $5-8M all-in phased build with an embedded engineering partner, payback lands at 8-19 months of operation across the range, under a year at the midpoint. Important honesty note: the sub-20-month claim depends on counting the funding value of the deposits; cost savings and fees alone pay back in 2-4 years. If challenged on stage, that is the answer: the deposits are the business case, the rest is gravy. Other assumptions: the pipeline estimate scales from the bank's existing correspondent relationships plus the inbound digital-asset demand typical of first-mover platforms; the fee range is industry-typical institutional account pricing from public comparatives. Scale anchor from UBPR peer group 4 (6/30/2026): average noninterest income is 0.64% of assets, about $9.6M a year at $1.5B, of which deposit service charges are roughly $1.5M; a ten-client platform book at $50-250K per client ($0.5-2.5M) would rival the average peer's entire deposit service charge line.
- Visual: Single proof statement, large type, no logos.

---

## Section 5: Concept 4: Regulatory Posture Is a Strategy, Not a Burden (6 min)

### Slide 19: Concept 4: Posture as Strategy
**Reuse: NEW**
- Key Point: The fourth thing AI makes possible: turning regulatory position into a first-mover advantage.
- Speaker Notes: Divider. Reframe coming: the regulatory budget line is not defense spending.
- Visual: Divider card, large numeral 4.

### Slide 20: Own the Lane the Rules Create
**Reuse: NEW**
- Key Point: Firms that engage regulators early do not just survive new rules; they own the lane the rules create.
- Content:
  - Compliance investment made ahead of the rules is cheaper than retrofitting after them
  - As rules for new asset classes take shape, the compliant counterparty is already positioned
  - Posture compounds like infrastructure
- Speaker Notes: Every executive here has a regulatory line item framed as cost of defense. This is the cheapest market-entry cost they will ever pay. No rulebooks, no legislation names, no timelines on the slide; the concept travels without them.
- Visual: Cost curve: invest-ahead vs retrofit-after.

### Slide 21: Governance Is the Price of Autonomy
**Reuse: `reference/Intelligence_OS_v2.pptx`, slide 34 ("Human-in-the-Loop: Even in Autonomous Mode"), slide 39 ("Why Multi-Agent Autonomy Needs Quality Gates," 84%), and slide 10 ("AI Is Your Wingman, Not the Lead Pilot")**
- Key Point: The research is consistent: the more autonomy you deploy, the more your governance is the product, internally and externally.
- Content:
  - Even in autonomous mode, effective operations keep humans in the loop at the decision points
  - Multi-agent systems fail without quality gates between stages
  - Accountability cannot be delegated to a machine
- Speaker Notes: This connects posture to practice. Regulators and institutional clients ask the same question in different words: who is accountable when the system acts? The bank that can answer crisply wins both conversations. (Adaptation: merge the two research slides into one evidence slide; the wingman line is the spoken frame, keep it off the slide or as a footer.)
- Visual: Autonomy-vs-governance gradient with the research stats plotted on it.

---

## Section 6: Concept 5: The Institution That Builds This Doesn't Have to Be a Startup (8 min)

### Slide 22: Concept 5: Built by an Incumbent
**Reuse: NEW**
- Key Point: The fifth thing: none of this required a startup.
- Speaker Notes: Divider. This is the section the room came for, whether they know it or not.
- Visual: Divider card, large numeral 5.

### Slide 23: Decision and Discipline, Not Pedigree
**Reuse: `reference/Intelligence_OS_v2.pptx`, slide 35 ("Making It Real: From Stage 3 to Stage 8: A practical path") for the path visual; `meetings/Kazakhstan Delegation.pptx`, slide 13 ("What We've Learned…") for the field lessons**
- Key Point: The barrier is decision and discipline, not pedigree. An established institution with regulatory standing and a client base is the natural builder.
- Content:
  - Incumbents bring what startups cannot: standing, trust, and clients on day one
  - Field lesson one: you cannot govern what you have not mapped
  - Field lesson two: the institutions that get the most from AI invest in their own people first
- Speaker Notes: The two field lessons come from live engagements across sectors (Kazakhstan slide 13; strip its client examples from the notes). (Adaptation: renumber the maturity path so no stage dates appear; frame it as "the path any committed institution walks.")
- Visual: Maturity path graphic with a "where you start is a choice" marker.

### Slide 24: Invest in Capability, Not Cuts
**Reuse: `presentations/gartner-ai-layoffs-roi.pptx`, slides 2-3 ("Cutting Headcount Is the Wrong Lever" / "The Path Forward"); `reference/Intelligence_OS_v2.pptx`, slide 40 ("The Skill Leveling Effect," +35%)**
- Key Point: Organizations that treat AI as a headcount lever see no better returns than those that do not; the returns track capability investment.
- Content:
  - High-ROI and low-ROI organizations cut headcount at the same rate; cuts are not the differentiator
  - The differentiator is investing in people, workflow integration, and governance
  - Skill-leveling evidence: less-experienced staff see the largest productivity gains when AI is deployed well
- Speaker Notes: This is the ROI slide a bank exec can take back to their board. The instinct to fund AI with layoffs is exactly backwards, and now there is data for that argument. (Adaptation: merge the two Gartner slides into one claim plus one path-forward line; keep the skill-leveling stat as the optimistic counterweight.)
- Visual: Two bars (cutters vs investors) with ROI outcome, plus the skill-leveling stat as a footnote card.

### Slide 25: What the Build Actually Looked Like
**Reuse: structure borrow from `reference/Intelligence_OS_v2.pptx`, slide 42 ("Object Lesson: From Stage 3 to Stage 7: A Developer's Journey")**
- Key Point: The build paired a small number of external engineers embedded inside the bank's own team, and it transferred practices, not just code.
- Content:
  - External partner engineers embedded from the first day of the build, working as part of the bank's team
  - The partnership produced engineering practices the bank will run on for years, not one system
  - The institution's own people own the platform now; that was the design, not the accident
- Speaker Notes: Tell this as a story, following the object-lesson shape: where the team started, what changed in how they work, what they can now do alone. No names, no headcounts, no timelines beyond what is cleared. The CTO-credit anecdote stays private unless cleared.
- Visual: Three-panel object lesson: starting point, the working model, the capability that remains.

---

## Section 7: The Implementation Path (9 min)

### Slide 26: The Adoption Path
**Reuse: `reference/Intelligence_OS_v2.pptx`, slide 43 ("The Adoption Path") and slide 45 ("Your Path Up the Trust Ladder")**
- Key Point: Institutions climb to always-on operations in stages, and the stages are climbed systematically, not leapfrogged.
- Content:
  - Each stage earns the trust the next stage requires
  - First move is small and concrete: identify a few candidate tasks, not a transformation program
  - Governance grows one stage ahead of autonomy
- Speaker Notes: Transition from "what is possible" to "what you do." The tone shift matters: less provocation, more craft. (Adaptation: keep the ladder visual, reframe the rungs for banking operations, strip week labels that read as dates.)
- Visual: Trust ladder with banking-flavored rungs.

### Slide 27: Sequence: Map, Govern, Build
**Reuse: `reference/Intelligence_OS_v2.pptx`, slide 45 ("Your Path Up the Trust Ladder"); engagement-shape donor `General - Dallas Sales/Improving-AI-Services.pptx`, slides 8-9 ("AI Adoption Framework" / 5-7 week engagement)**
- Key Point: The order of operations is map the work, stand up governance, then build; skipping the first two is the divide from slide 2.
- Content:
  - Map: inventory the tasks and flows before choosing tools (you cannot govern what you have not mapped)
  - Govern: decision rights, quality gates, and human checkpoints defined before autonomy scales
  - Build: start with a bounded assessment measured in weeks, then expand by evidence
- Speaker Notes: The assessment-first shape (a few weeks to map and plan before any build) is standard delivery craft, not theory. If asked who does this, that is the soft commercial opening; do not turn the talk into a pitch. (Adaptation: the donor deck is an internal sales catalog; lift only the engagement shape and week-scale horizon, none of the offering names or branding.)
- Visual: Three-block sequence arrow: Map, Govern, Build.

### Slide 28: Where to Deploy First
**Reuse: `reference/Intelligence_OS_v2.pptx`, slides 36-38 ("Is the Task Demand-Limited?" / "Which Tasks Collapse?" / "The AI Impact Matrix") and slide 41 ("Where to Deploy Your Agent Swarm")**
- Key Point: The best first candidates are high-volume, high-precision tasks where demand is not the constraint.
- Content:
  - Demand lens: if finishing faster creates more demand, AI compounds; if demand is capped, it only cuts cost
  - Collapsibility: some tasks do not get faster, they disappear
  - Volume vs precision: full autonomy earns its place where both are high
- Speaker Notes: Give the room the two questions and have them mentally map one process from their own institution, settlement operations and onboarding review are the obvious candidates. This is the application muscle of the talk. (Adaptation: the matrix examples are generic knowledge work; re-cast the quadrants with banking processes.)
- Visual: Two-by-two matrix, banking examples in each quadrant.

### Slide 29: What Good Looks Like at Scale
**Reuse: `reference/Intelligence_OS_v2.pptx`, slide 49 ("Agentic Landing Zone: Six Components")**
- Key Point: At scale, always-on operations rest on six components, and governance is the first, not the last.
- Content:
  - Governance as the autonomy safety net
  - The remaining components cover the operating layer: where agents run, how they are monitored, how humans intervene
  - This is the internal mirror of the external product: the bank that sells compliant access runs compliant operations
- Speaker Notes: Tie the bow between sections: the internal operating discipline and the external product are the same capability pointed in two directions. That symmetry is the deepest answer to "why us." (Adaptation: strip Improving-offering language; reframe the landing zone as "the operating layer an always-on bank runs on.")
- Visual: Six-component ring with governance at the top.

---

## Section 8: Reflection and Close (5 min)

### Slide 30: Pause: Where Does This Land?
**Reuse: `reference/Intelligence_OS_v2.pptx`, slide 32 or slide 50 ("Pause: Where Does This Land?" / "Reflection," participation beats)**
- Key Point: Two minutes of structured reflection before the recap.
- Content:
  - Prompt on slide: which of the five concepts is closest to something your institution could act on this year?
  - Optional second prompt: which one is furthest, and what makes it far?
- Speaker Notes: Audience-interaction moment. Give them a genuine two minutes to write, then take one or two spoken answers from the floor. This is the beat that turns a lecture into a session; protect the silence. (Adaptation: replace the source deck's trust-ladder reflection prompt with the five-concepts prompt.)
- Visual: Single question, large type, nothing else.

### Slide 31: Five Concepts, One Pattern
**Reuse: NEW**
- Key Point: Remove the hours. Productize compliance. Become infrastructure. Treat posture as strategy. And know your institution can build it.
- Speaker Notes: One breath per concept. The pattern underneath all five: AI rewards the bank that rebuilds its plumbing, not the bank that demos a chatbot. Then straight into the questions; do not add a seventh idea.
- Visual: Five-tile recap grid.

### Slide 32: Three Questions for Monday
**Reuse: `reference/Intelligence_OS_v2.pptx`, slides 51-52 ("Your Next Move" / "Three Questions to Answer Now")**
- Key Point: Where does your settlement stack still run on banking hours? What would compliance look like as a product? Which lane are you building for?
- Speaker Notes: End on the questions, not a pitch. The dual perspective lands here as exactly one sentence before the questions: "I've seen this built." Nothing more specific: no "I sit close to a bank," no role or relationship detail, since David's public profile already connects him to the reference case and anything warmer narrows the guessing space. (Adaptation: replace the trust-ladder questions with the three banking questions above.)
- Visual: Three numbered questions, nothing else.

---

## Reuse Map

| Talk slide | Source deck | Source slide | Adaptation needed |
|---|---|---|---|
| 2. The Divide | presentations/mit-nanda-genai-divide.pptx | 1: "95% … no measurable business ROI" | Reframe subtext for banking execs; strip report date |
| 3. The Problem Isn't the Technology | presentations/mit-nanda-genai-divide.pptx | 2: "Wrong Budget Allocation" | Keep budget-vs-ROI stat; banking gloss in notes only |
| 4. Banking Is Already the Leader | reference/Intelligence_OS_v2.pptx | 23-25: Financial Services section | Merge three slides to one; strip stage numbers and date labels |
| 8. Concept 1 divider (optional) | reference/Intelligence_OS_v2.pptx | 13: "Three Waves of Enterprise GenAI" | Backdrop only; strip year labels |
| 13. Compliance as Distribution | Systemic Compliance briefing deck (client docs) | 2: "The thesis: compliance should be systemic" | Concept only; deck is client-confidential, rebuild the visual |
| 13. Compliance as Distribution (support) | reference/Intelligence_OS_v2.pptx | 33: "Governance: The Autonomy Safety Net" | Lift the stat; reframe to compliance credibility |
| 14. The Stakes | presentations/agent-receipts.pptx | 5: "Three Incidents. One Pattern." | Generic incident framing; no company names |
| 14. The Stakes | presentations/your-ai-agents-leak-data-and-money.pptx | 2: "29 Million Secrets" finding | Keep stat scale; one line only |
| 14. The Stakes | presentations/graded-by-clients-cloned-by-criminals.pptx | 4: "Voice Cloning: The Phone Call Attack" | Keep the attack pattern; drop professional-services framing |
| 15. The Economics | Systemic Compliance briefing deck (client docs) | 8: "The pricing disruption is the message" | Concept only; pricing detail is client-confidential |
| 17. Destinations vs Infrastructure | reference/Intelligence_OS_v2.pptx | 47-48: "Agentic Landing Zone" slides | Layout borrow only; reframe as bank-as-infrastructure |
| 21. Governance Is the Price of Autonomy | reference/Intelligence_OS_v2.pptx | 34, 39, 10: human-in-the-loop, quality gates, wingman | Merge two research slides; wingman line spoken, not on slide |
| 23. Decision and Discipline | reference/Intelligence_OS_v2.pptx | 35: "Making It Real: Stage 3 to Stage 8" | Renumber path, remove dates |
| 23. Decision and Discipline | meetings/Kazakhstan Delegation.pptx | 13: "What We've Learned…" | Reuse the two lesson lines; strip client names from notes |
| 24. Invest in Capability, Not Cuts | presentations/gartner-ai-layoffs-roi.pptx | 2-3: "Wrong Lever" / "The Path Forward" | Merge to one claim plus one path line |
| 24. Invest in Capability, Not Cuts (support) | reference/Intelligence_OS_v2.pptx | 40: "The Skill Leveling Effect" (+35%) | Footnote stat card |
| 25. What the Build Actually Looked Like | reference/Intelligence_OS_v2.pptx | 42: "Object Lesson: A Developer's Journey" | Structure borrow only; content is the anonymized build story |
| 26. The Adoption Path | reference/Intelligence_OS_v2.pptx | 43, 45: adoption path / trust ladder | Banking-flavored rungs; strip week labels that read as dates |
| 27. Sequence: Map, Govern, Build | reference/Intelligence_OS_v2.pptx + General - Dallas Sales/Improving-AI-Services.pptx | 45; and AI-Services 8-9 (Adoption Framework, 5-7 weeks) | Lift engagement shape and week-scale horizon only; no offering names or branding |
| 28. Where to Deploy First | reference/Intelligence_OS_v2.pptx | 36-38, 41: impact matrix and deployment lens | Re-cast quadrants with banking processes |
| 29. What Good Looks Like at Scale | reference/Intelligence_OS_v2.pptx | 49: "Agentic Landing Zone: Six Components" | Strip offering language; reframe as the bank's operating layer |
| 30. Pause: Where Does This Land? | reference/Intelligence_OS_v2.pptx | 32 or 50: participation beats | Replace reflection prompt with the five-concepts prompt |
| 32. Three Questions for Monday | reference/Intelligence_OS_v2.pptx | 51-52: "Your Next Move" / "Three Questions" | Replace with the three banking questions |
| All other slides (1, 5, 6, 7, 9, 10, 11, 12, 16, 18, 19, 20, 22, 31) | n/a | n/a | NEW |

**Score: 18 of 32 slides mapped to existing-deck material (22 distinct source slides), 14 NEW.**

## Decks Reviewed, Not Used

- `accounts/Wendy's/Wendy's QBR - AI Update.pptx`: client-branded; its reusable content (Trust Evolution, Intelligence OS layers, demand-limit matrix) duplicates `Intelligence_OS_v2.pptx` in cleaner form.
- `Presentations/2024 Technology Trends.pptx`: dated market-recap framing.
- `presentations/business_os_body_slide.pptx`, `YPO/*.pptx`, One Texas decks, Remington/Nexben decks: unrelated topics.
- `meetings/Kazakhstan Delegation.pptx` slide 12 ("What We've Built"): client examples with names in notes; anonymization risk, skipped.
- Obsidian vault: no talks or slide folders found; search returned only meeting-transcript references.

## Open Questions for David

1. **Case metrics (slides 6, 7, 11, 18): RESOLVED, UBPR-ANCHORED.** Round-number estimates scaled to a $1.5B-asset bank, now anchored to live FFIEC UBPR Peer Group Average data pulled 10/23/2026: peer group 4, insured commercial banks $1B-$3B in assets, 529 banks, average bank $1.69B, report date 6/30/2026. Anchors used in speaker notes: demand deposits 22.3% of assets (slide 6); overhead 2.51% of assets, personnel 1.45% and $122.7K per employee (slide 7); interest-bearing bank balances 5.97% plus ~1% noninterest cash, ~$105M overnight money per $1.5B bank (slide 11); noninterest income 0.64% of assets (~$9.6M/yr) with deposit service charges ~$1.5M/yr (slide 18). Other reference frames (Federal Reserve payment studies, industry compliance and treasury benchmarks) remain for the figures UBPR does not cover. Every figure is labeled "est." on the slide, with its assumption in the speaker notes. Peer-group averages are aggregate by construction, so nothing on these slides is traceable to any single bank.
2. **Settlement statistics (slide 9): RESOLVED BY ESTIMATION.** Same method and labeling as Q1; the figures are rate arithmetic and calendar facts (5% short-rate carry, ~250 ACH settlement days), which need no peer data.
3. **The one-quarter build-to-first-client line (slide 18): RESOLVED 10/23.** David replaced it with a generic payback claim: "If the build takes 18 months end to end, the economics still pay it back in under 20 months of operation (est.)" David's constraint: payback must be under 20 months or the claim does not work. The claim holds only because the business case counts the funding value of institutional deposits ($3-8M/yr on $100-200M of low-cost balances), not just cost savings and fees; the speaker notes say so explicitly. The private timeline fact no longer appears anywhere in the deck.
4. **Dual perspective: RESOLVED 10/23.** Use "I've seen this built." as the single closing sentence at slide 32. No "sit close to" phrasing: David's public profile already ties him to the reference case, so any relational hint narrows identification.
