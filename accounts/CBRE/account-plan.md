# CBRE — Strategic Account Plan / Pursuit Map

**Improving | Prepared for: David O'Hara | July 2026**
**Classification: Internal — Business Development**

---

## Situation Summary

**Entity anchor.** CBRE Group, Inc. (NYSE: CBRE), headquartered in Dallas, Texas — the world's largest commercial real estate services and investment firm. No meaningful disambiguation risk: the name is distinctive, and the ticker and Dallas HQ match what's already on file internally. `accounts/CBRE/` exists but previously held only a meeting-prep document (`CBRE-Confluent-Prep.md`, a Feb 2026 prep for a Confluent-referral meeting) — no prior `account-plan.md` existed before this run, so this is a fresh build, not an update, though the meeting-prep facts are carried forward below.

**Engagement shape: active-but-underleveraged — now confirmed via a live CRM pull.** Improving has a 9-year relationship with CBRE: a Master Agreement (PSA) active since January 2017, amended September 2021, and a last delivered SOW in Aug–Oct 2022 (an Agile assessment at CBRE's Center of Excellence, delivered by Ed Utley, $85,000, the only closed-won opportunity CBRE has ever produced — 1 of 4 total opportunities on record). There is a **live, currently-open inbound thread**: Confluent's Rob Ogbah referred Improving directly into CBRE's Confluent Cloud environment in a February 2026 meeting, describing CBRE as his "key Confluent Cloud customer." Separately, a parallel ServiceNow-angle thread was opened with a CBRE contact referred to only as "Parsa" — **CRM now confirms his full name is Parsa Sreenivasulu**, and that this thread was formalized as an opportunity ("Kafka POC - ServiceNow," created 3/6/2026) that was **closed Lost on 6/10/2026**, having never progressed past the 10%-Identified stage. **Loss reason confirmed by David:** the opportunity was lost to an internal CBRE team, not to a competitor and not to a stalled Improving-side pursuit — no competitive risk should be inferred from this loss. **CRM access confirmed working this session.** The prior blocker (an M365 authentication wall at `login.microsoftonline.com`, no cached SSO, no credentials available) is resolved — David confirmed the Chrome CRM session is now logged in, and this session navigated directly into `https://improving.crm.dynamics.com`, landed in the live "Enterprise Dashboard," and ran account, opportunity, and contact-level queries successfully (see below and Open Items). **Account ownership confirmed:** the CRM account record's **Owner field lists David O'Hara**, and David has confirmed this is correct — the "Roderic Patane" attribution that appeared elsewhere in this document came from a WorkDay/GTM-rank cross-check, not CRM, and is superseded; David O'Hara is the account owner of record. The CRM account record also shows the "CBRE, Inc." account is a **merged master record** — three duplicate CBRE-named accounts were merged into it between January 12 and February 13, 2026 — and there are currently **zero open opportunities** on the account.

**Timing trigger — confirmed, dated, citable.** CBRE's Q1 2026 earnings call (April 23, 2026) is the clearest trigger: CEO Bob Sulentic raised full-year 2026 core EPS guidance from $7.30–$7.60 to $7.60–$7.80 (20%+ growth at midpoint), driven substantially by the newly created **Critical Infrastructure Services** unit — nearly $950M in Q1 2026 revenue alone, with the segment expected to grow 60%+ for the year. Sulentic stated plainly: *"Our move into critical infrastructure and data center services is going to be at least as profound as our move into outsourcing was in the '90s... and much faster."* This follows the **$1.2B acquisition of Pearce Services** (announced November 4, 2025; digital and power infrastructure technical services), expected to contribute $350M+ of Core EBITDA and $660M+ of revenue in 2026. Combined, CBRE is aggressively scaling data/digital infrastructure delivery capacity right now — directly adjacent to Improving's data engineering and Confluent-stack capabilities, and squarely aligned with the live Confluent referral thread already in motion.

**Goals:**
- Short-term (90 days): convert the open Confluent referral thread into a scoped SOW extending CBRE's Confluent Cloud environment.
- Long-term (12–24 months): become a recognized delivery partner across CBRE's Digital & Technology and Critical Infrastructure Services organizations, beyond the single-SOW pattern of the last decade.

---

## CBRE's Stated Strategic Priorities

Sourced from CBRE's FY2025 10-K/Annual Report, the Q1 2026 earnings call (April 23, 2026), and CBRE's own press materials and technology pages. Four themes:

### 1. Critical Infrastructure & Data Center Services at Scale
CBRE's newly formed Critical Infrastructure Services line — data centers, telecom, and power infrastructure — is now the company's primary growth engine: $3B in infrastructure-related revenue in 2025, nearly $950M in Q1 2026 alone, with 60%+ growth guided for 2026. The $1.2B Pearce Services acquisition (Nov 2025) is expected to add $660M+ revenue and $350M+ Core EBITDA in 2026, with Pearce's revenue mix concentrated in critical power/cooling systems (34%), renewable energy generation/storage (30%), and wireless/fiber networks (29%).
Sources: [CBRE Q1 2026 Earnings Call Transcript — Investing.com](https://www.investing.com/news/transcripts/earnings-call-transcript-cbre-q1-2026-sees-earnings-beat-stock-rises-93CH-4632891); [Pearce Services Acquisition press release — CBRE IR](https://ir.cbre.com/press-releases/detail/256/pearce-services-acquisition-expands-cbres-capabilities); [Pearce Services Acquisition — DCD](https://www.datacenterdynamics.com/en/news/cbre-acquires-engineering-services-firm-pearce-for-12bn/)

### 2. AI at Scale via the Ellis AI Platform and Vantage Analytics
CBRE won Forrester's 2025 Technology Strategy Impact Award for its **Ellis AI** platform — a self-service, multi-model GenAI platform (introduced 2023) used by brokers for research, data analysis, and contract abstraction, reportedly built in part on AWS Bedrock. **CBRE Vantage Analytics'** Next Action Engine analyzes client data at scale to surface opportunities and risks. CEO Sulentic has described a deliberately controlled AI deployment approach: *"We are controlling it, controlling who has access to it, controlling what we use it for."*
Sources: [Where AI Becomes Real — CBRE](https://www.cbre.com/about-us/technology/artificial-intelligence); [Why CBRE built an AI playground — CIO Dive](https://www.ciodive.com/news/CBRE-generative-AI-coding-assistance-self-service-platform/699503/); [CBRE Q1 2026 Earnings Call Transcript](https://www.investing.com/news/transcripts/earnings-call-transcript-cbre-q1-2026-sees-earnings-beat-stock-rises-93CH-4632891)

### 3. Data-Driven Client Intelligence as a Competitive Moat
CBRE's FY2025 10-K explicitly frames its "knowledge platform" — research, data/technology, strategy — built on decades of accumulated proprietary transaction data, as a distinct structural advantage tied directly to its scale and financial strength.
Sources: [CBRE FY2025 10-K — SEC EDGAR](https://www.sec.gov/Archives/edgar/data/1138118/000113811826000005/cbre-20251231.htm); [Data and Technology Across Every Dimension — CBRE](https://www.cbre.com/about-us/technology)

### 4. Continued Portfolio Expansion via M&A, Requiring Integration Capacity
Beyond Pearce, CBRE has also expanded via the Industrious acquisition (flexible workplace). CEO Sulentic has stated M&A remains the company's top capital-allocation priority, with data center services cited as the area of heaviest ongoing acquisition interest — meaning newly acquired businesses require continual systems/process integration work.
Sources: [CBRE Q1 2026 Earnings Call Transcript](https://www.investing.com/news/transcripts/earnings-call-transcript-cbre-q1-2026-sees-earnings-beat-stock-rises-93CH-4632891); [CBRE FY2025 10-K — SEC EDGAR](https://www.sec.gov/Archives/edgar/data/1138118/000113811826000005/cbre-20251231.htm)

*Note on source set:* CBRE is public and files a 10-K; the Q2 2026 earnings call (scheduled July 29, 2026) had not yet occurred as of this research session (July 22, 2026) — Q1 2026 (April 23) is the most recent primary earnings source available.

---

## Improving's Competitive Positioning

**Capability mapping:**

| Priority Theme | Improving Capability | Why It Fits |
|---|---|---|
| Critical Infrastructure & Data Center Services | Data/AI Engineering + Confluent-based event streaming/integration | Direct tie to the live Rob Ogbah referral thread; CBRE's infrastructure buildout needs real-time data integration and systems work at pace, and Improving's existing PSA removes procurement friction that would otherwise slow a new vendor down |
| AI at Scale (Ellis AI / Vantage Analytics) | Applied AI / practitioner-led AI delivery | Ellis AI and Vantage Analytics are proven internal platforms that need continued engineering capacity to extend into new use cases — an execution problem, not a strategy question |
| Data-Driven Client Intelligence | Data platform engineering | CBRE's "knowledge platform" moat requires exactly the foundation-then-AI sequencing Improving positions on |
| M&A Integration Capacity (Pearce, Industrious) | Application modernization / embedded delivery teams | Time-boxed, high-urgency systems-integration work for newly acquired units — the same "overloaded integration office" pattern Improving has positioned into elsewhere |

**Structural advantages:** an existing, active PSA (procurement friction already solved); a live, partner-referred (Confluent) entry channel that removes the cold-start problem entirely; a decade-long, if underleveraged, relationship.

**Win-wire story:** The closest cleared internal analog is the **Thrivent Enterprise Integration Datastore (TEID)** engagement (data consolidation into a governed, real-time platform) — used as the data-platform-modernization reference in Improving's Schwab pursuit map. **Gap flagged:** no Confluent-specific joint reference engagement was identified this session. Given the pursuit is entering through Confluent specifically, recommend checking with Improving's Confluent alliance contacts for a citable joint case study before the next Ogbah conversation, rather than leaning solely on the Thrivent analog.

**Competitive note (honest):**
- **Likely incumbents:** No public signal found naming a specific incumbent SI or vendor for CBRE's AI/data engineering work. CBRE's own Digital & Technology org (now led by Anuj Kadyan, ex-McKinsey Technology Services co-leader) may have an institutional bias toward large-name consultancies given his background — worth watching, not confirmed.
- **Where Improving wins:** an already-open, partner-referred channel (no cold start); an existing PSA (no procurement delay); senior practitioner density; delivery speed.
- **Where Improving loses:** scale and brand recognition against a Big-4/SI-class competitor if CBRE runs a formal RFP for the infrastructure integration work; no established Confluent-specific reference story yet.
- **Positioning:** lead with the live referral and the existing paper — don't lead with a capabilities pitch when the door is already open via Rob Ogbah.

---

## Leadership / Decision-Maker Map

**Source:** CBRE's official Investor Relations executive leadership page (`ir.cbre.com/leadership/executive-leadership`) and corporate leadership page (`cbre.com/about-us/leadership`), fetched in the original research session, plus web search for one-level-down names. **Updated July 22, 2026 (later same-day follow-up session) with a live Dynamics CRM pull** — Chase navigated to `improving.crm.dynamics.com` via Chrome (session already authenticated, per David), searched CRM directly for each named contact below, and opened individual account/contact/opportunity records. `crm_status` values below now reflect this live CRM query, not the earlier Clay-based proxy. Findings: **Chandra Dhandapani** and **Rose Manjarres** are confirmed stale in CRM itself (see detail below), **Debora Haught** and **Kate Johnson** have no CRM record tied to CBRE at all, **Michael Zavalanski** is an active CRM contact but attached to an un-merged duplicate account, and **"Parsa" is confirmed to be Parsa Sreenivasulu**, an active CBRE contact who was the primary contact on a real (and lost) opportunity.

### Full Narrative Profiles (4 most strategically relevant)

**Anuj Kadyan — Chief Technology & Transformation Officer**
Joined CBRE in May 2026 after 17 years at McKinsey & Company, rising to senior partner and co-leader of the Technology Services practice. **CRM status: no-crm-history** (not found in the Clay/CRM cross-check; also too new in-seat to have prior history).
*Role inference (labeled):* Likely the actual economic buyer for any technology/AI transformation engagement — his title and McKinsey pedigree suggest a mandate to modernize and consolidate CBRE's technology delivery model company-wide.
*Pitch angle:* "You're six weeks into standing up CBRE's technology transformation mandate while the Critical Infrastructure business is scaling 60% a year — we're already inside the account on the Confluent side and can show you delivery speed before you formalize a broader vendor strategy."
*What to avoid:* Approaching cold before the Confluent thread has produced a proof point — a McKinsey-background executive is likely to default to familiar large-SI relationships unless Improving has already demonstrated delivery.
Source: [Executive Leadership — CBRE IR](https://ir.cbre.com/leadership/executive-leadership); [Global Executive Leadership — CBRE](https://www.cbre.com/about-us/leadership)

**Josh White — Executive Vice President / Vice Chairman, Advisory & Transaction Services (Dallas)**
**CRM status: existing-crm-contact** — per the Clay cross-check, this is Improving's strongest live relationship at CBRE: active, with a last touch in March 2026. Joined CBRE 2012; 25-year CRE veteran; promoted to Vice Chairman in 2024 (CBRE's highest brokerage-professional distinction). Leads office tenant-representation deals — notably brokered Charles Schwab's Westlake campus, JCPenney's HQ consolidation, and American Airlines' new HQ campus.
*Important scope caveat:* White sits in **Advisory & Transaction Services (brokerage)**, not the Digital & Technology org — he is a senior, warm, internal relationship, but not a technical decision-maker for the AI/data/infrastructure pursuit. Treat him as an internal-CBRE air-cover and introduction asset, not the pitch target himself.
*Pitch angle:* "You've known Improving for years on the real estate side — we're now working the Confluent Cloud thread with your Digital & Tech org. Any read on who we should be talking to over there, or a good way in?"
*What to avoid:* Pitching him the technical Confluent/AI capability directly — that's not his domain, and doing so risks looking like Improving doesn't understand CBRE's org structure.
Source: [Josh White — CBRE](https://www.cbre.com/people/josh-white); prior-session Clay cross-check (`memory/working/account-strategy-2026-07-22-153954.md`)

**Rob Ogbah — Strategic Account Executive, Confluent** *(partner contact, not a CBRE employee — profiled here because he is the direct originator of the live pursuit thread)*
**CRM status: existing-crm-contact** — this is the referral source for the current pursuit; documented in `CBRE-Confluent-Prep.md` from a February 23, 2026 meeting.
*Role inference:* Owns the Confluent-side commercial relationship at CBRE and described CBRE as his "key Confluent Cloud customer" — he is the fastest, most direct path into CBRE's technical org, not a CBRE org-chart entry at all.
*Pitch angle:* Not a pitch — a continuation ask: "Where did the CBRE conversation land after our February meeting? We'd like a direct introduction to whoever owns the Confluent Cloud environment day to day."
*What to avoid:* Letting this thread go cold — per the account-strategy note, this referral had not been confirmed as still active as of this session.
Source: `accounts/CBRE/CBRE-Confluent-Prep.md`

**Michael Zavalanski — Senior Director, Digital & Technology**
**CRM status: existing-crm-contact (data-quality issue).** A live CRM pull (July 22, 2026 follow-up session) found "Mike Zavalanski" as an active contact with a current `Mike.Zavalanski@cbre.com` email and a Dallas-area phone (214-438-8924) — but the record is attached to **"CB Richard Ellis - Dallas,"** an un-merged duplicate account, not the master "CBRE, Inc." record that the rest of this pursuit is tracked against. His cbre.com email suggests he is likely still current, but this is CRM data hygiene debt, not a confirmed org-chart entry point — recommend flagging to whoever owns CRM data quality to merge the duplicate account, and re-verifying his title/role directly before any outreach.
*Role inference:* A working-level technical contact in the Digital & Technology organization — plausible entry point for a scoped technical conversation once a warm intro exists.
*Pitch angle:* Hold until an intro path (via Kadyan's org or the Confluent thread) is confirmed.
*What to avoid:* Cold outreach without a confirmed current role/title — CRM confirms he's a real contact with a live email, but says nothing about his current title or relevance.
Source: [Michael Zavalanski — LinkedIn](https://www.linkedin.com/in/michael-zavalanski-63181812); live CRM contact record, "CB Richard Ellis - Dallas" account (July 22, 2026 session)

### Remaining C-Suite — Compact

| Name | Title | CRM Status |
|---|---|---|
| Robert E. Sulentic | Chair & Chief Executive Officer | no-crm-history |
| Emma Giamartino | Chief Financial Officer & Chief Investment Officer | no-crm-history |
| Chad Doellinger | Chief Legal & Administrative Officer, Corporate Secretary | no-crm-history |
| Andrew (Andy) Glanzman | Chief Executive Officer, Real Estate Investments | no-crm-history |
| Jamie Hodari | Chief Executive Officer, Building Operations & Experience; Chief Commercial Officer | no-crm-history |
| Vikram Kohli | Chief Operating Officer, CBRE; Chief Executive Officer, Advisory Services | no-crm-history |
| Vincent Clancy | Chair & CEO, Turner & Townsend (CBRE-owned subsidiary) | no-crm-history |
| Paul Hawtin | Chief People Officer *(not listed on the official IR executive page — surfaced via LinkedIn/press; flagged for confirmation of formal-officer status)* | no-crm-history |

*Note: sourced from CBRE's own Investor Relations executive leadership page (7 named officers) plus two additional functional leads (Clancy, Hawtin) surfaced via corporate leadership page and press — this is CBRE's full disclosed C-suite as of this session's live fetch.*

### One Level Down (Digital & Technology org — partial, with staleness flags)

| Name | Title (as last found) | Status Note | CRM Status |
|---|---|---|---|
| Michael Zavalanski | Sr. Director, Digital & Technology | Live CRM contact found (`Mike.Zavalanski@cbre.com`), but attached to an un-merged duplicate account ("CB Richard Ellis - Dallas"), not the master CBRE record — likely-current based on live cbre.com email, title/role not re-verified | existing-crm-contact (duplicate-account) |
| Rose Manjarres | *Former* SVP, Digital & Technology | **Confirmed stale in CRM itself**, not just LinkedIn: her CRM contact record shows email `rose.manjarres@atw.com` (not a cbre.com address) and no Company Name populated — consistent with the LinkedIn finding that she's now at MUFG. Do not treat as a current CBRE contact. | stale — do not use |
| Chandra Dhandapani | *Former* Chief Digital & Technology Officer / Chief Administrative Officer, CBRE | **Confirmed departed CBRE September 8, 2024** — now CEO of Magnit. **CRM's own contact record confirms this**: Company Name field reads "Magnit," city Dallas. This name should not appear in any outreach. | stale — do not use (CRM-confirmed) |
| Debora Haught | Unclear — one source shows a CBRE brokerage/listing role; another (Jennifer Pierson item) suggests she left CBRE for a new venture | **CRM searched directly — no contact record tied to CBRE exists at all.** (CRM shows a Samantha Haught at RealPage and a Melissa Haught at NOV, neither CBRE-affiliated.) Do not contact — no current CBRE identity confirmed anywhere. | no-crm-history |
| Kate Johnson | Unclear — search surfaced two different "Kate Johnson" profiles associated with CBRE (Client Services Coordinator vs. Construction Project Management) | **CRM searched directly — no contact record tied to CBRE exists.** Ambiguous identity remains unresolved; do not contact. | no-crm-history |
| **Parsa Sreenivasulu** *(full name now confirmed)* | Job Title not populated in CRM | **Active CRM contact at the master "CBRE, Inc." account.** Was the Primary Contact on a real, formalized opportunity — "Kafka POC - ServiceNow," created 3/6/2026 by David O'Hara, est. revenue $50,000, 10% probability — that was **closed Lost on 6/10/2026**, having never advanced past the "10% - Identified" stage. **David has confirmed the loss reason: the opportunity was lost to an internal CBRE team**, not to a competitor. The specific play (Kafka/ServiceNow) did not convert, but this is a resolved, understood outcome rather than an open question. No email/phone on file. | existing-crm-contact (lost-opportunity history) |

**Update to the prior staleness finding:** the live CRM pull independently confirms the LinkedIn-sourced staleness calls on Manjarres and Dhandapani (both show non-CBRE affiliations directly in their own CRM contact records), resolves Haught and Johnson from "ambiguous" to "no CRM record exists," resolves "Parsa" to a full name and an already-attempted (and lost) opportunity, and surfaces a data-quality issue on Zavalanski (real, live contact — but parked on a duplicate, un-merged account). Net effect: this list is now materially more actionable than the prior "treat as unreliable" holding pattern — two names are confirmed dead ends, two are confirmed non-existent in CRM, one needs an account-hygiene fix before use, and one (Parsa) has a fully specified history that should inform any renewed ServiceNow-angle approach rather than a cold restart.

---

## ICP & Account 9-Box

*(Per workflow instruction, placed immediately after the Leadership/Org Chart section and before the Referral/Partner Network section. Every inference below is flagged for David to verify.)*

### Potential Score

**Revenue factor — best-case annual IT services spend:**
- **Path 1 (public filings, checked first):** CBRE's FY2025 10-K discusses its "knowledge platform" and technology investment as a competitive advantage tied to scale, but does **not disclose a clean, usable total IT/technology spend figure or IT-services-specific breakout.** Path 1 checked, no usable figure found — expected outcome, not a research gap.
- **Path 2 (fallback — company-size benchmark):** CBRE FY2025 revenue: **$40.55B**. CBRE is a professional/business-services firm (not cleanly "asset-heavy" nor "financial services" per the workflow's cited benchmark bands) — applying a mid-range **3% of revenue** IT-spend benchmark for large professional-services firms yields a total IT budget estimate of roughly **$1.22B**. Applying a ~20% discount to isolate the external-services (vs. internal headcount/licensing) portion yields an estimated **best-case annual IT services spend of ~$975M.**
- Record:
  - method: company-size cross-referenced against industry IT-spend benchmark (fallback)
  - source_priority_path: 2 — Path 1 checked (10-K), no usable figure found; fallback used
  - benchmark_used: ~3% of revenue (professional/business-services midpoint, adjacent to but distinct from the workflow's cited asset-heavy 1–3% and financial-services 4–7% bands — CBRE doesn't cleanly fit either), applied to $40.55B FY2025 revenue, then discounted ~20% for the external-services subset
  - estimated_annual_it_services_spend: ~$975M (see recurring workflow-issue flag below)

**Gross margin factor:** Default **36%** — mid-range blended-delivery assumption, leaning toward the lower-middle of Improving's typical range given the likely staff-augmentation-heavy shape of a Confluent-integration entry play.

**Geography factor:**
- Flag (a) same_location_as_buyer: **Y** — Improving's Dallas-based coverage (David O'Hara, confirmed account owner) and CBRE's own Dallas HQ are the same metro.
- Flag (b) Improving_office_in_client_location: **Y** — Improving has a Dallas office.
- Both flags Y → geo_raw = **4** (per the workflow's proposed, single-data-point-inferred scoring curve).

**Scored factors and weighted Potential:**

| Factor | Raw Score | Weight | Weighted |
|---|---|---|---|
| Geography | 4 | 0.10 | 0.4 |
| Revenue | **5 (capped — see flag below)** | 0.70 | 3.5 |
| Gross Margin | 2 (interpolated — 36% sits between 34%→1 and 37%→2, closer to 37%) | 0.20 | 0.4 |
| **Total Potential** | | | **4.3** |

### Realized Score

**No revenue within the trailing twelve months — now confirmed via live CRM, not defaulted from an auth failure.** A follow-up session (July 22, 2026) successfully pulled the live CBRE account and opportunity records from Dynamics CRM. Confirmed: **zero open opportunities** currently exist on the account; the full historical opportunity count is **4 total, 1 closed-won** ($85,000, the Aug–Oct 2022 Agile Coach/COE engagement), and the remaining 3 include at minimum the recently closed **"Kafka POC - ServiceNow"** opportunity (created 3/6/2026, est. $50,000, closed **Lost** 6/10/2026, never advanced past 10%-Identified). So CBRE has a real, decade-long engagement history (active PSA since 2017) and even a real 2026 pursuit attempt — but no revenue landed in the trailing 12 months, and the one 2026 attempt that got furthest (Kafka POC) was lost, not won. This is a confirmed data point now, not a stand-in for missing CRM access.

- **TTM actual revenue:** $0 — confirmed via live CRM: no open opportunities, no won opportunities in the trailing 12 months (last win was Aug–Oct 2022; the one 2026 opportunity attempt was lost).
- **TTM actual gross margin:** 0% — same reasoning; no current engagement to measure margin against.
- **Geography:** same as Potential (structural, doesn't change) — raw = 4.

| Factor | Raw Score | Weight | Weighted |
|---|---|---|---|
| Geography | 4 | 0.10 | 0.4 |
| Revenue | -5 (below the $200K floor band) | 0.70 | -3.5 |
| Gross Margin | -5 (below the 20% floor band) | 0.20 | -1.0 |
| **Total Realized** | | | **-4.1** |

### 9-Box Classification

- Realized = -4.1 → **Low band** (below -1.7)
- Potential = 4.3 → **High band** (above +1.7)
- Grid cell: High Potential / Low Realized → **SIGNIFICANT**

This mirrors Constellation Energy's classification, not Schwab's — an intuitive result given CBRE currently has no revenue within the TTM window despite an active PSA, in contrast to Schwab's active SOWs.

### Inferences Flagged for David to Verify

1. **Geography scoring logic** (0 baseline, +4 for both flags Y) is inferred from a single AT&T data point — unverified for any account with a "Y" flag, including this one.
2. **9-box grid arrangement** beyond the single confirmed AT&T/POISED cell is unverified — CBRE lands in a different, also-unverified cell (SIGNIFICANT).
3. **IT services spend estimate (~$975M)** sourced via Path 2 fallback (3% of revenue benchmark, discounted for services subset) — Path 1 (10-K) checked first, no usable figure found. **Recurring workflow issue (see below).**
4. **Gross margin default (36%)** is Improving's typical-range assumption, not CBRE-specific confirmed data.
5. **TTM revenue/GM confirmed at $0/0%** via a live CRM pull (July 22, 2026) — no longer a default standing in for missing CRM access. Basis: zero open opportunities, only 1 win ever (Aug–Oct 2022) out of 4 total opportunities, and the most recent 2026 pursuit attempt (Kafka POC - ServiceNow) closed Lost. Distinct from true cold-pursuit zero-history — there is a relationship and even recent pursuit activity, just no TTM revenue.
6. **20% GM-band boundary and $200K revenue-band floor**: both TTM inputs land at or below the lookup table's lowest named bands — capped at -5 rather than extrapolated further downward.

### Workflow Issue Found (Recurring — Flagging, Not Smoothing Over)

**Same issue previously flagged in the Schwab pursuit map recurs here.** The Revenue-factor lookup table tops out at $20M → score +5. For any company at CBRE's scale ($40.55B revenue), the Path 2 fallback methodology produces an estimate (~$975M) nearly 50x the table's top band — meaning the Revenue factor is functionally a constant +5 for any large-enterprise target, collapsing Potential scores toward the same ~4.3 regardless of whether the account is a $10B or $100B company. This is now the **second consecutive mega-cap account** (after Schwab) to hit this ceiling identically. Recommend the workflow owner revisit whether Path 2's benchmark should be capped by realistic single-engagement or single-department addressable spend rather than whole-company revenue before running this workflow on additional large-cap targets.

---

## Referral / Relationship Network

*(Kept structurally separate from the leadership/org map above and from the partner network below.)*

### Existing Sponsor Path
- **Applicable:** Yes (active-but-underleveraged).
- **Sponsor:** The live CRM account record's Owner field lists **David O'Hara**, and David has confirmed he is the correct account owner — the earlier WorkDay/GTM-rank-sourced "Roderic Patane" attribution is superseded and no longer authoritative. Separately, the live Confluent referral thread (Rob Ogbah) functions as an active, inbound warm-path sponsor in its own right. A parallel ServiceNow-angle thread also reached a named contact — **confirmed via CRM to be Parsa Sreenivasulu** — and produced a real opportunity ("Kafka POC - ServiceNow") that closed **Lost** on 6/10/2026, **lost to an internal CBRE team, not a competitor**, per David.
- **Status:** CRM ownership field confirmed live this session (July 22, 2026) and confirmed correct by David; Ogbah/Confluent thread status still rests on `CBRE-Confluent-Prep.md`, not re-verified this session; ServiceNow thread outcome confirmed via CRM (lost) with loss reason now confirmed by David (lost internally at CBRE).
- **Note:** Two confirmed Improving-side threads have touched CBRE: David O'Hara's account ownership and the Ogbah/Confluent referral. The ServiceNow angle is now a closed, understood matter (lost internally at CBRE), not an open thread requiring coordination. A live CRM timeline pull also surfaced a **separate, previously undocumented thread**: an internal Improving rep named Josh Harrison has an active, current-day email/meeting cadence with CBRE contact Michael Copella (emails as recent as 7/15/2026, a Teams meeting titled "Josh Harrison/Michael Copella Connect" scheduled 7/15/2026), tied to a separate "Foxen"-related conversation. Recommend David confirm who is actually working CBRE right now before any new outreach (see Immediate Next Actions).

### Personal Network Ties

| Contact | Tie Type | Path | Status | Note |
|---|---|---|---|---|
| Josh White | prior-colleague / existing client relationship | Existing CBRE brokerage-side relationship, active per Clay, last touch March 2026 | confirmed | Senior and warm, but sits in Advisory & Transaction Services, not Digital & Tech — treat as an internal air-cover/intro asset, not a direct pitch target |
| Rob Ogbah (Confluent) | partner-referral | Direct inbound referral into CBRE, Feb 2026 meeting | confirmed | Not a CBRE employee, but the single most direct live channel into the account |

No YPO, alumni, or other personal ties to CBRE were identified this session — stated plainly rather than fabricated.

### Mutual Connections (LinkedIn)

**Unavailable this session.** Claude-in-Chrome/authenticated-LinkedIn tools were not loaded or authenticated in this session, so the mutual-connections lookup could not be run for Kadyan, White, Ogbah, or Zavalanski. Set explicitly to `unavailable` rather than `zero` for all four — this should be re-run in a session with LinkedIn access before outreach begins.

### Referral Network Summary

**Strongest path:** the live Rob Ogbah (Confluent) referral thread — it is already open, partner-sourced, and directly responsible for this pursuit existing at all; no further "getting an intro" work is needed, only re-engagement. **Second:** Josh White, for internal CBRE context and potential intro paths into the Digital & Technology org, despite sitting in a different business line.

---

## Partner Network

*(Improving's fixed 8-partner list — AWS, Microsoft, GCP, Confluent, Databricks, SpaceX/xAI, Snowflake, SAP. Kept separate from the referral network above.)*

| Partner | Likely In Use | Evidence | Partner Contact |
|---|---|---|---|
| **Confluent** | **confirmed** | Rob Ogbah (Confluent Strategic Account Executive) directly describes CBRE as his "key Confluent Cloud customer" — the most direct possible confirmation, sourced from a live account-team relationship rather than inference | **Rob Ogbah** — rogbah@confluent.io, 408.591.4319 — confirmed, and the originating source of this entire pursuit |
| **AWS** | **likely** | Public reporting (CIO Dive) on CBRE's Ellis AI GenAI platform references use of AWS Bedrock as part of its implementation | not-identified |
| **Microsoft (Azure)** | no-signal-found | No CBRE-specific public signal found this session | not-identified |
| **GCP** | no-signal-found | No CBRE-specific public signal found this session | not-identified |
| **Snowflake** | no-signal-found | No CBRE-specific public signal found this session | not-identified |
| **Databricks** | no-signal-found | No CBRE-specific public signal found this session | not-identified |
| **SAP** | no-signal-found | No CBRE-specific public signal found this session (searched ERP/finance-system angle specifically) | not-identified |
| **SpaceX/xAI** | no-signal-found | No relevant public signal — different industry, no referral-node relevance identified | not-identified |

**Partner network summary:** 8 of 8 partners checked. Confirmed: Confluent. Likely: AWS. No signal: Microsoft, GCP, Snowflake, Databricks, SAP, SpaceX/xAI. **Strongest partner path: Confluent, via Rob Ogbah** — not just the strongest partner path, but the reason this pursuit map exists in the first place.

---

## Contact Prioritization & Sequencing

| Priority | Contact | Entry Point | Goal |
|---|---|---|---|
| 1 | **Rob Ogbah** (Confluent, Strategic Account Executive) | Already-open referral channel from Feb 2026 meeting | Re-engage; confirm thread status; request a direct introduction to a named CBRE technical stakeholder in the Confluent Cloud environment |
| 2 | **Josh White** (EVP/Vice Chairman, Advisory & Transaction Services) | Existing warm relationship, last touch March 2026 | Internal CBRE context and any available intro path into Digital & Technology; not a direct technical pitch target |
| 3 | **Anuj Kadyan** (Chief Technology & Transformation Officer) | Cold — via credibility built through the Confluent thread first | Likely economic buyer for a broader technology/AI transformation conversation; approach only after a Confluent-thread proof point exists |
| 4 | **Michael Zavalanski** (Sr. Director, Digital & Technology) | Cold/needs-verification | Potential working-level technical contact once a warm intro path is confirmed |

*Note: David O'Hara is the confirmed CRM account owner (no longer an open question — see Situation Summary). The prior ServiceNow-angle thread with Parsa Sreenivasulu closed Lost 6/10/2026, lost to an internal CBRE team; no further internal coordination is needed on that thread.*

---

## Entry Plays / Opportunity Scenarios

### Option A — Confluent Cloud Services Partner
Formalize Improving as the delivery/services partner for CBRE's Confluent Cloud environment, per Rob Ogbah's original ask — staff augmentation and integration expertise for stream processing and event-driven architecture.

**Entry pitch:** "We've been CBRE's partner for almost a decade, with active agreements already in place — when you're ready to scale the Confluent Cloud environment, we can have certified engineers embedded within weeks, not months of procurement."

### Option B — Critical Infrastructure Delivery Capacity
CBRE's Critical Infrastructure Services unit is integrating a $1.2B acquisition (Pearce) while growing 60%+ annually. Pitch embedded application/data engineering pods to support systems integration for the newly acquired business and the broader data center services platform.

**Entry pitch:** "You're integrating a $1.2 billion acquisition into a business growing 60% a year — that's an execution problem, not a strategy problem. We embed senior engineers who've done exactly this kind of fast-follow systems integration before."

### Option C — Ellis AI / Vantage Analytics Extension
Extend Ellis AI or Vantage Analytics into new use cases via embedded AI engineering capacity, building technical-org credibility ahead of any economic-buyer conversation.

**Entry pitch:** "Ellis AI is a strong foundation — we help teams turn a platform like that from an internal pilot into something that scales reliably across every business line."

**Recommendation: Lead with Option A.** It is the only play with a live, inbound, partner-referred channel already open, removes the cold-start problem entirely, and directly leverages Improving's existing PSA (procurement friction already solved). Options B and C are natural expansion plays once the Confluent engagement proves out and opens a path to Kadyan's broader technology organization.

---

## Multi-Year Strategic Path

*(Active-but-underleveraged shape, per the engagement-shape determination above.)*

| Phase | Timeline | Milestone |
|-------|----------|-----------|
| **Access** | Month 1–3 | Re-engage Rob Ogbah for a direct intro to a named CBRE technical stakeholder; re-engage Josh White for internal context |
| **Prove** | Month 3–6 | Land a scoped SOW extending the Confluent Cloud environment (Option A); execute cleanly as the proof point for further conversations |
| **Expand** | Month 6–12 | Open a parallel workstream into Critical Infrastructure Services delivery capacity (Option B); formal introduction to Anuj Kadyan's organization |
| **Partner** | Year 2+ | Recognized delivery partner across CBRE's Confluent/data-engineering and critical-infrastructure technology stack; explore Ellis AI/Vantage Analytics extension work (Option C) |

---

## Immediate Next Actions

1. **Account ownership: resolved.** David O'Hara is confirmed as account owner of record. The earlier WorkDay/GTM-rank-sourced "Roderic Patane" attribution is superseded — no further action needed.
2. **Kafka POC - ServiceNow loss reason: resolved.** David has confirmed the opportunity (created 3/6/2026, closed Lost 6/10/2026, never advanced past "10% - Identified") was lost to an internal CBRE team, not a competitor. No post-mortem or follow-up is needed before any renewed ServiceNow-angle approach.
3. **Coordinate internally across active/recent CBRE threads**: (a) Rob Ogbah's Confluent referral, and (b) a newly surfaced thread — internal rep **Josh Harrison** has current, active email and meeting contact with CBRE's **Michael Copella** (emails through 7/15/2026, a Teams meeting the same day) tied to a "Foxen"-related conversation. Confirm with David who is actually working this account today before adding a new thread.
4. **Re-engage Rob Ogbah (Confluent)** to check the status of the February 2026 referral thread and request a direct introduction to a named CBRE technical stakeholder in the Confluent Cloud environment.
5. **Re-engage Josh White** for an internal-CBRE gut check and any additional intro paths into the Digital & Technology org, given his active, recent relationship.
6. **Flag the Michael Zavalanski CRM data-quality issue** (real, active contact, but parked on an un-merged duplicate account, "CB Richard Ellis - Dallas," not the master CBRE record) to whoever owns CRM hygiene, and independently verify his current title before outreach. Debora Haught and Kate Johnson are now confirmed to have **no CRM record tied to CBRE at all** — do not pursue either name further absent new information. Manjarres and Dhandapani are confirmed departed in CRM's own data, not just LinkedIn — do not use.
7. **CRM pull: done.** A follow-up session (July 22, 2026) confirmed the Chrome CRM session was authenticated (per David) and successfully queried the live CBRE account, its opportunity history, and the named org-chart contacts — see Situation Summary, Leadership section, and Realized Score above for what was found. No further CRM-access blocker exists.
8. **Draft a one-page Confluent Cloud services capability sheet** referencing the existing PSA, ready for the next Ogbah conversation.
9. **Check with Improving's Confluent alliance contacts** for a citable, Confluent-specific joint reference engagement — the current win-wire story (Thrivent TEID) is a general data-platform analog, not Confluent-specific.

---

## Open Items to Confirm

- **Account ownership: resolved.** David O'Hara is confirmed as account owner of record; the earlier WorkDay/GTM-rank-sourced "Roderic Patane" attribution is superseded. No longer an open item.
- **CRM verification: complete.** A follow-up session (July 22, 2026) confirmed the Chrome CRM session was authenticated and successfully pulled the live CBRE account record, its full opportunity history (4 total, 1 won/$85K, 0 currently open), and individual contact records for every named org-chart contact below. This is no longer an open item.
- **"Kafka POC - ServiceNow" loss reason: resolved.** CRM shows the opportunity closed Lost 6/10/2026 at the 10%-Identified stage; David has confirmed it was lost to an internal CBRE team, not a competitor. No longer an open item — no competitive risk should be inferred from this loss.
- **A previously undocumented internal thread surfaced:** Improving rep Josh Harrison has active, current-day contact with CBRE's Michael Copella (emails through 7/15/2026, a same-day Teams meeting) tied to a "Foxen"-related conversation, unrelated to the Confluent thread. Needs scoping — is this a live motion on the same account that should be coordinated, or a separate matter (e.g., a real-estate/brokerage-side conversation via the Josh White relationship) that doesn't need to be folded in?
- Rose Manjarres and Chandra Dhandapani are confirmed to have left CBRE — **now confirmed in CRM's own contact records** (Manjarres's CRM email is a non-CBRE `atw.com` address; Dhandapani's CRM Company Name field reads "Magnit"), not just LinkedIn. Do not treat either as a current CBRE contact.
- Debora Haught and Kate Johnson: **CRM confirms no contact record tied to CBRE exists for either name.** Treat as no-crm-history, not merely "needs verification" — do not contact absent new sourcing.
- Michael Zavalanski: confirmed as a real, active CRM contact with a current cbre.com email, but the record sits on an un-merged duplicate account ("CB Richard Ellis - Dallas"), not the master CBRE record — a CRM data-hygiene issue to flag, and his current title still needs independent verification before outreach.
- No incumbent SI/vendor identified for CBRE's AI/data engineering work — stated as genuinely unknown, not asserted.
- Geography scoring logic and 9-box grid arrangement (both inferred beyond the single AT&T data point) — standing flag on every run of this workflow.
- The IT-services-spend estimate (~$975M) sits far above the lookup table's $20M ceiling — the same recurring issue flagged in the Schwab pursuit map, now observed on two consecutive mega-cap accounts. (Note: CRM's own Annual Revenue field for CBRE shows $10B, versus the $40.55B FY2025 10-K figure used in this document's Potential-score estimate — worth reconciling which figure to standardize on.)
- LinkedIn mutual-connections lookup did not run this session (Chrome/LinkedIn tools not authenticated for that purpose) — treat as "unavailable," not "zero," and re-run before outreach.
- Whether a Confluent-specific joint reference client exists that Improving is cleared to name to Rob Ogbah or CBRE directly.
- **New from this session, not yet actioned:** five CBRE contacts appear in CRM's "Hand-Raisers" marketing-engagement list, tagged either "CFLT" (Confluent) or "AI," all raised between 10/23/2025 and 12/1/2025 — Vishwak Mukund, Venu Koonamneni, Bhavya Bindela, Satyakiran Kantipudi (all CFLT), and Banke Odunaike (AI). None of these names were previously documented in this account plan; worth evaluating as additional Confluent/AI-interested contacts before the next Ogbah conversation.

---

## Sources

- [CBRE Q1 2026 Earnings Call Transcript — Investing.com](https://www.investing.com/news/transcripts/earnings-call-transcript-cbre-q1-2026-sees-earnings-beat-stock-rises-93CH-4632891)
- [Pearce Services Acquisition Expands CBRE's Capabilities — CBRE IR](https://ir.cbre.com/press-releases/detail/256/pearce-services-acquisition-expands-cbres-capabilities)
- [CBRE Acquires Pearce for $1.2bn — Data Center Dynamics](https://www.datacenterdynamics.com/en/news/cbre-acquires-engineering-services-firm-pearce-for-12bn/)
- [CBRE Q1 2026 Financial Results / Guidance — Barchart](https://www.barchart.com/story/news/3274321/what-to-expect-from-cbre-group-s-q2-2026-earnings-report)
- [Where AI Becomes Real — CBRE](https://www.cbre.com/about-us/technology/artificial-intelligence)
- [Why CBRE built an AI playground — CIO Dive](https://www.ciodive.com/news/CBRE-generative-AI-coding-assistance-self-service-platform/699503/)
- [Data and Technology Across Every Dimension — CBRE](https://www.cbre.com/about-us/technology)
- [CBRE FY2025 10-K — SEC EDGAR](https://www.sec.gov/Archives/edgar/data/1138118/000113811826000005/cbre-20251231.htm)
- [Executive Leadership — CBRE IR](https://ir.cbre.com/leadership/executive-leadership)
- [Global Executive Leadership — CBRE](https://www.cbre.com/about-us/leadership)
- [Josh White — CBRE](https://www.cbre.com/people/josh-white)
- [Michael Zavalanski — LinkedIn](https://www.linkedin.com/in/michael-zavalanski-63181812)
- [Rose Manjarres — LinkedIn](https://www.linkedin.com/in/rosemanjarres/)
- [Chandra Dhandapani — Northern Trust Board Announcement](https://www.northerntrust.com/united-states/pr/2024/northern-trust-names-chandra-dhandapani-to-board-of-directors)
- [Former CBRE Exec Chandra Dhandapani Named CEO of Magnit — Dallas Innovates](https://dallasinnovates.com/former-cbre-exec-chandra-dhandapani-named-ceo-of-magnit/)
- `accounts/CBRE/CBRE-Confluent-Prep.md` (internal, Feb 2026 meeting prep)
- `memory/working/account-strategy-2026-07-22-153954.md` (internal, same-session `chase-account` skill cross-check)
- Live Dynamics CRM pull, `improving.crm.dynamics.com` (internal, July 22, 2026 follow-up session) — CBRE, Inc. account record, opportunity history (including "Kafka POC - ServiceNow" and the Aug–Oct 2022 Agile Coach/COE win), and contact records for Parsa Sreenivasulu, Michael/Mike Zavalanski, Rose Manjarres, Chandra Dhandapani, Debora Haught, and Kate Johnson
