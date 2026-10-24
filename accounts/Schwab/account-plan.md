# Charles Schwab: Strategic Account Plan / Pursuit Map

**Improving | Prepared for: David O'Hara | Prepared July 2026 | Refreshed October 2026**
**Classification: Internal, Business Development**
**Last updated: 2026-10-23**

> **Refresh note (2026-10-23).** This document was refreshed against primary sources covering the period since the 2026-07-21 validation pass. Net-new or materially changed content is tagged **[NEW 10/23]**; content carried forward unchanged from the July validation is tagged **[VALIDATED 7/21]**. Delta sources are listed in the Sources section. Nothing confirmed in July was removed unless a newer primary source superseded it. **CRM was re-pulled 2026-10-23 via the Dataverse Web API** (opportunity-level data for Charles Schwab & Co), resolving the two open opportunities the July pass left hanging and updating the cumulative figures; contact-level detail still dates to the 2026-07-21 validation. Note on file naming: this content previously lived in `account-plan-pursuit-map-draft.md`, a comparison artifact from the first run of the `account-pursuit-map` workflow. The hand-built `account-plan.md` it was compared against was deleted on 2026-07-21, so this file has been promoted to the canonical `account-plan.md` path defined by the workflow.

> **Validation pass completed 2026-07-21** via authenticated LinkedIn and Improving Dynamics CRM (direct account record, not the email-notification proxy used in the original run). Corrections and newly-confirmed facts are marked inline as **[VALIDATED 7/21]**. This closed most of the open items that required live LinkedIn/CRM access; a few (SpaceX/xAI "Cole" referral chain, incumbent-SI signal) still need direct verification with David since they aren't discoverable from these two systems.

---

## Situation Summary

**Entity anchor.** The Charles Schwab Corporation (NYSE: SCHW), headquartered in Westlake, TX. No disambiguation issue — the name is distinctive and the ticker/HQ match David's own account records unambiguously. `accounts/Schwab/` already existed with a prior plan; this run reads it for context but produces an independent draft per the controller's request, not an in-place update.

**Engagement shape: active-but-underleveraged — confirmed from CRM, not assumed.** Querying email/calendar (the M365-routed proxy for CRM in this session — see Open Items) surfaced actual Dynamics CRM-generated notifications, not just anecdote: an active MSA/contract-vehicle relationship (originally under Zigatta, which Improving acquired; assignment to Improving Enterprises, Inc. executed effective January 1, 2026), and multiple **won** Instructional Design opportunities/SOWs — Julie Navar, Julie King, Raisa Babilonia, Shelmadine Straughan/Joseph Jackson, with a further extension opportunity won June 10, 2026 (~$102,400) and a backfill opportunity created June 2, 2026 ($0 est. value; a separate $70,000 "Instructional Designer - for Brian Matheny" opportunity was also open). Total identifiable active/recent revenue across these SOWs: roughly $900K to $1M, though the direct Dynamics CRM account record puts cumulative closed-won at **$2,554,624** since 8/4/2023 across 16 of 22 opportunities. The Realized Score section below supersedes this early email-derived estimate. CRM contact of record: Vicki Kelly (Sales Rep); opportunity owner Derek Nwamadi. This is genuine engagement-shape evidence, not an inference from web research — satisfies step 01's evidentiary bar.

**[NEW 10/23] CRM re-pulled via the Dataverse Web API.** Cumulative closed-won is now **$2,663,824 across 17 of 24 opportunities (71%)**. Both opportunities left open in the July pass resolved as **losses**: the Joe Jackson backfill (closed 2026-07-24, $0) and the Brian Matheny role (closed 2026-09-21, $70K). One new win landed two days before the pull: **"Extend Andraya Goodwin," $109,200, won 2026-10-21**. One opportunity is open: **"Extend Julie King - Instructional Designer," $104,000, est. close 2026-11-29** (created 2026-09-30). Net read: the instructional-design beachhead is alive and still renewing, but thinner than July implied: two of the three threads then in play closed lost.

**Timing trigger — confirmed, dated, citable.** Schwab held its Institutional Investor Day on **May 14, 2026**, where CEO Rick Wurster made AI the central growth narrative, projected full-year 2026 revenue growth of 14–15% (up from a prior 9.5–10.5% guide), and described an AI-driven "front door" experience for clients, explicitly including the under-$1M segment historically underserved by human advisors. This followed the January 29, 2026 restructuring that created a unified Chief Technology, Operations, and Data Officer role under Dennis Howard. Both events are dated, primary-sourced, and still current as of this July 2026 run.

**[NEW 10/23] Timing trigger update: the window widened, it did not close.** Three primary-sourced additions since the July pass:

1. **Q3 2026 results, filed October 15, 2026.** Record quarterly net revenue of **$7.2B (+17% YoY)**, GAAP net income of **$2.9B (+23%)**, diluted EPS of $1.62, total client assets of **$13.33T (+15%)**, core net new assets of $190.4B (+38%), and **48.6M total client accounts**. GAAP expenses grew 9%, meaning technology and AI programs are being funded out of a growing revenue base rather than a cost-cutting one. Source: [Q3 2026 earnings release, 8-K Exhibit 99.1, filed 2026-10-15](https://www.sec.gov/Archives/edgar/data/316709/000031670926000035/a3q26exhibit991.htm).
2. **Anthropic partnership announced September 14, 2026.** Schwab and Anthropic are bringing **Claude for Financial Advisors** to more than **16,000 independent RIAs**, with read-only access to Schwab data and contractual limits on model training. This is Schwab's most concrete external AI commitment to date and it directly touches the Advisor Services segment. Source: [Reuters, 2026-09-14](https://www.reuters.com/technology/anthropic-targets-financial-advisers-with-new-claude-tool-2026-09-14/); [Business Wire announcement, 2026-09-14](https://www.businesswire.com/).
3. **Charley launched September 30, 2026.** A generative AI client assistant, described by the CEO as "the foundation of how people interact with us." Within two weeks Schwab was also **blocking unauthorized third-party AI agents** from moving client money and redirecting clients to Charley. Source: [Schwab press release, 2026-09-30](https://pressroom.aboutschwab.com/); [American Banker, 2026-10-15](https://www.americanbanker.com/).

**What this changes for Improving.** The July plan assumed a strategy-to-execution gap on AI. That gap is now visible in public: Schwab has shipped a consumer AI assistant, signed a flagship AI vendor deal, and is simultaneously writing the control rules for AI agents on client money. Those are three different engineering problems (product surface, integration, and agent governance) landing in the same two quarters. That is a widening execution surface, not a narrowing one.

**Goals:**
- Short-term (90 days): land a scoped SOW in Data/AI or Software Engineering, building off the ID beachhead
- Long-term (12–24 months): become a preferred implementation partner across Schwab's AI/data/engineering orgs

**[NEW 10/23] Goal status check.** The 90-day short-term goal was set in July and its window closed in October with no Data/AI or Software Engineering SOW recorded in this document. This is not evidence of failure, but it is evidence that the plan's opening moves were never executed or were executed without being logged here. Treat the goal as reset to a fresh 90 days from 2026-10-23, and treat the reason it slipped as the first thing to diagnose (see Immediate Next Actions).

---

## Charles Schwab's Stated Strategic Priorities

Sourced from the FY2025 10-K, the May 14, 2026 Investor Day materials, the Q2 and Q3 2026 earnings releases, and Schwab press releases. Six themes. Themes 1 through 5 carry forward from the July pass; theme 6 (Digital Assets) is new in this refresh.

### 1. AI at Scale: Client-Facing, Advisor-Facing, and Internal
Schwab launched Portfolio Insights (generative AI retail product) in 2026, and has since moved from "AI in beta" to "AI shipped." Three primary-sourced developments define the theme as of October 2026:

- **Charley, the client AI assistant.** Announced 2026-09-30. A generative AI assistant for retail clients, positioned to help clients "get answers and take action." CEO Wurster described it as "the foundation of how people interact with us," which is the strongest statement of durable strategic intent Schwab has made about any AI product. Source: [Schwab press release, 2026-09-30](https://pressroom.aboutschwab.com/).
- **Claude for Financial Advisors, via Anthropic.** Announced 2026-09-14 with BlackRock as a co-launch partner. Extends Claude to more than 16,000 independent RIAs served by Schwab Advisor Services, with read-only data access and contractual restrictions on using Schwab data for model training. Source: [Reuters, 2026-09-14](https://www.reuters.com/technology/anthropic-targets-financial-advisers-with-new-claude-tool-2026-09-14/); [Forbes, 2026-09-16](https://www.forbes.com/).
- **AI agent governance.** From 2026-10-15, Schwab began blocking unauthorized third-party AI agents from moving client money, pointing clients to Charley instead, with the CEO publicly calling for "rules of the road" on autonomous agent trading. JPMorgan took a parallel step and RBC was reported to be weighing one. Source: [American Banker, 2026-10-15](https://www.americanbanker.com/); [WSJ, 2026-10-18](https://www.wsj.com/).

CEO Wurster has separately restated that AI will extend advisor-quality service to the under-$1M client segment, the firm's largest, "in ways that weren't economically viable through human advisors."
Sources: [2026 Institutional Investor Day Presentation](https://content.schwab.com/web/retail/public/about-schwab/2026_Institutional_Investor_Day.pdf); [Schwab touts AI as its biggest growth lever, InvestmentNews](https://www.investmentnews.com/fintech/schwab-touts-ai-as-its-biggest-growth-lever-at-investor-day/266613); [Schwab CEO Says AI Will Serve Below-$1M Clients, Yahoo Finance](https://finance.yahoo.com/sectors/technology/articles/schwab-ceo-says-ai-serve-140000658.html)

### 2. Data Platform Modernization (Post-TD Ameritrade Integration)
Schwab is still rationalizing the architecture created by the largest brokerage-data migration in industry history (17M+ accounts, $1.3T assets). "Books and records modernization" and real-time pipeline consolidation are explicitly cited.
Sources: [Charles Schwab 2025 10-K](https://content.schwab.com/web/retail/public/about-schwab/SEC_Form10k_2025.pdf); existing account-plan.md citations (CIO Dive, InvestmentNews)

### 3. Application Modernization
Platform rationalization continues; RIA/fintech APIs expanding; job postings for engineering leadership explicitly reference migrating from legacy development toward "GenAI- and agentic-AI-driven development."
Source: Schwab careers postings referenced in the existing account-plan.md (Director of Software Development & Engineering, Portfolio Management Technology)

### 4. Serving the Under-$1M Client Segment with AI
Restated directly by Wurster at the May 2026 Investor Day — a product/engineering execution challenge, not a strategy question.
Source: [Schwab CEO Says AI Will Serve Below $1M Clients](https://finance.yahoo.com/sectors/technology/articles/schwab-ceo-says-ai-serve-140000658.html)

### 5. Workforce AI Enablement
GitHub Copilot adoption visible in engineering job postings; internal "Schwab Knowledge Assistant" GenAI productivity tool cited in prior-year materials.
Source: existing account-plan.md citation trail (job postings, internal comms references)

### 6. Digital Assets as a Growth Vector **[NEW 10/23]**
This is a genuinely new stated priority since the July pass and was absent from the prior plan entirely. Schwab moved from crypto-adjacent to crypto-operating in one quarter:

- **Schwab Crypto launched** in Q2 2026, providing direct retail access to Bitcoin and Ethereum trading. Source: [Q2 2026 earnings release, 8-K Exhibit 99.1, filed 2026-07-21](https://www.sec.gov/Archives/edgar/data/316709/000031670926000027/a2q26exhibit991.htm).
- **Token list expanded** on 2026-08-27 to include Solana, Avalanche, and Chainlink. Source: [The Block, 2026-08-27](https://www.theblock.co/).
- **Transfers enabled** on 2026-10-17, allowing clients to move Bitcoin and Ethereum in and out of Schwab. Source: [CryptoRank, 2026-10-17](https://cryptorank.io/).
- **Q3 2026 earnings** stated Schwab "plans to expand digital assets available in Schwab Crypto." Source: [Q3 2026 earnings release, 2026-10-15](https://www.sec.gov/Archives/edgar/data/316709/000031670926000035/a3q26exhibit991.htm).

Separately, Schwab **sold Forge Trust to Alto Solutions**, announced 2026-10-06, exiting a private-markets custody position while expanding retail crypto. Read together, that says Schwab is concentrating digital-asset investment in the retail and RIA channel rather than private markets infrastructure. Sources: [Yahoo Finance, 2026-10-06](https://finance.yahoo.com/); [Wealth Management, 2026-10-07](https://www.wealthmanagement.com/).

*Note on sourcing: themes 2, 3, and 5 rely partly on citations already vetted in the prior plan. Themes 1, 4, and 6 were independently re-verified against primary sources in this refresh (earnings 8-K exhibits, Schwab press releases, and dated trade press reporting on the Anthropic and Charley announcements).*

---

## Improving's Competitive Positioning

**Capability mapping — re-grounded 2026-10-23 against a live SharePoint offering pull (see the gate note at the end of this section).** Every row below names a real, current Improving offering verbatim from its source document, or is marked `no_match`. The prior version of this table named capability labels ("Azure OpenAI delivery," "embedded engineering coaching," "regulated-platform delivery") that were invented by a prior run; those have been replaced or flagged.

| Priority Theme | Improving Offering (verbatim name, category) | Offering Evidence (as stated in the source doc) | Source Doc | Why It Fits | Match |
|---|---|---|---|---|---|
| AI at Scale | **AI Innovation Lab** (AI Offerings) | Duration: phased ACT engagement (~10-12 weeks: Anchor weeks 1-2, Consistency weeks 3-10, Transition final 1-2 weeks). Price: not stated in doc. Summary: "a hands-on, immersive program designed to fast-track your organization's AI adoption. We embed an on-site team to coach your people and co-create one to three proof-of-concept (PoC) or proof-of-value (PoV) projects." | `General/Sales Support/Sales Offerings/Specific Offerings/AI Offerings/AI Innovation Lab Offering.docx` | Schwab is shipping client-facing AI; the Lab is Improving's real "embed and co-build AI" engagement | matched |
| AI at Scale (governance side) | **AI Governance & Compliance Control Plane** (Improving AI Governance Practice) | Start shape: discovery workshop weeks 1-2, control plane stand-up weeks 3-6, operating model handoff weeks 7-8. Price: not stated in doc. "A Control Plane for Enterprise AI, Not Another Policy Binder." | `General/Presentations/Reference-IP/AI Governance Control Plane - Client One-Pager.pdf` (July 2026) | Maps to Schwab's public agent-governance problem (see Option D) | matched |
| Data Platform Modernization | **Data Enablement Engagement** (Data Enablement) | Duration: 4-8 weeks. Price: $125,000 - $250,000. Summary: "successful data enablement is supported by thoughtful engineering that goes beyond making data accessible. This includes collaboration driven by a product mindset, technical expertise, and process automation." | `.../Specific Offerings/Data Enablement/Data Enablement Engagement.docx` | Scoped discovery-plus-build on a data platform foundation; direct analog to the Thrivent TEID engagement | matched |
| Application Modernization | **Application Modernization** (Application Modernization) + **Code Explorer** (AI Offerings / Code Explorer) | Application Modernization internal delivery guide: assess current state, roadmap, migrate; team of Architect, Product Coach, Modernization Specialist, Cloud Specialist; duration/price not stated. Code Explorer: 2-Week Discovery Sprint $16K-$32K; 4-Week Assessment $32K-$64K; 6-Week Design Sprint $48K-$96K; 8-Week Extended $64K-$128K (at $200/hr). | `.../Specific Offerings/Application Modernization/Application Modernization - Internal Delivery Guide.docx`; `.../AI Offerings/Code Explorer/Code_Explorer_Delivery_Guide.docx` | Schwab's postings cite migration to "GenAI- and agentic-AI-driven development"; Code Explorer is the AI-accelerated codebase-assessment entry | matched |
| Under-$1M AI Segment | **AI Innovation Lab** (AI Offerings) | Same evidence as above | Same as above | Nearest real offering to "AI productization": co-created PoV builds on a live product backlog | matched (nearest real offering; no dedicated productization offering exists) |
| Workforce AI Enablement | **AI Team Enablement Deep Learning Program** (AI Software Engineering - Transformation) | Duration: 12 weeks (6 half-day workshops, up to 24 participants, 1 embedded AI engineer per 3 teams, daily coaching between sessions). Price: per-track plus hourly embedded engineers; "Contact Improving for a customized proposal." | `.../AI Offerings/AI Software Engineering - Transformation/AI Team Transformation.docx` | The real "embedded engineering coaching around Copilot/GenAI tooling" offering; extends the existing Instructional Design engagement into technical teams | matched |
| Digital Assets and Crypto **[NEW 10/23]** | — | — | — | No digital-assets, crypto, or blockchain offering exists anywhere in the Sales Offerings tree or the GMS pipeline. The prior row's "regulated-platform delivery" was an invented capability label. Nearest real offerings are generic Application Modernization / Platform Modernization Enablement, which are not crypto-specific. | no_match |

**Corrected invented claims from the prior version:** "Azure OpenAI delivery" is not a named Improving offering (no Azure-OpenAI-specific offering document exists; the AI offerings are Microsoft-partner-aligned but not branded that way), and "embedded engineering coaching" is now named correctly as the AI Team Enablement Deep Learning Program. "Agentic AI delivery" is real but only as delivered through the AI Team Enablement program's agent-building curriculum and the AI Innovation Lab, not as a standalone offering.

**Structural advantages (facts, retained):** existing MSA (contract vehicle already in place, removing procurement friction); confirmed Azure/GCP dual-cloud alignment at Schwab with Improving's Microsoft and GCP partner relationships; an existing, if narrow, Instructional Design beachhead with $2.66M cumulative closed-won.

**[NEW 10/23] Two structural changes since July worth naming honestly:**

- **Anthropic is now Schwab's marquee AI vendor, and Improving has no Anthropic partnership.** The 16,000-RIA Claude rollout was signed directly between Schwab, Anthropic, and BlackRock. Improving's eight-partner roster (AWS, Microsoft, GCP, Confluent, Databricks, Snowflake, SAP, SpaceX/xAI) does not include Anthropic. That is not disqualifying, because the largest share of the work in an enterprise Claude deployment is integration, data access control, and workflow engineering rather than the model itself, but it does mean Improving cannot lead with a partner credential here. Lead with delivery proof instead.
- **Schwab is expanding its own global capability center.** Reuters reported on 2026-08-19 that Schwab will scale its India technology centre to **2,000 people by 2027**, following a February 2026 reduction of roughly 1,000 roles tied to the TD Ameritrade integration. Source: [Reuters, 2026-08-19](https://www.reuters.com/). This cuts both ways: it depresses appetite for commodity staff augmentation, and it increases appetite for architecture, migration, and enablement work that makes a captive center productive faster.

**Win-wire story:** The Thrivent Enterprise Integration Datastore (TEID) engagement — consolidating multi-system data into a governed, real-time platform. Direct analog to Schwab's post-TDA data rationalization. Prepare a clean one-pager before any technical conversation.

**Competitive note (honest):**
- **Likely incumbents:** No public signal found naming specific SI incumbents at Schwab for AI/data work specifically — large financial-services accounts of this scale almost always carry Accenture/Deloitte/Cognizant-class relationships on major programs, but this is stated as a reasonable industry-pattern assumption, not a confirmed finding (flagged in Open Items).
- **Where Improving wins:** senior practitioner density, delivery speed, embedded/low-ego partnership model, an existing (if small) contractual foothold that removes procurement friction.
- **Where Improving loses:** scale, brand recognition at the enterprise-architecture level, global delivery footprint that a Big-4 SI can offer for multi-region programs.
- **[NEW 10/23] New competitive class: AI-vendor-adjacent delivery.** The Anthropic deal introduces a competitive set that did not exist in the July analysis. Where a model vendor is named directly in an executive announcement, that vendor's own forward-deployed engineering team and its preferred implementation partners typically get first crack at the surrounding work. Improving should assume it is competing against that channel for any Charley- or Claude-adjacent scope, and should avoid pitching directly against the model layer. The defensible ground is the unglamorous middle: data contracts, entitlements, audit and control evidence, and the legacy integration work that has to happen before any of it is usable in a regulated broker-dealer.
- **Positioning:** lead with proof (Thrivent, the ID track record) and precision, not scale — don't compete on the dimensions where Improving is structurally outmatched.

---

## Leadership / Decision-Maker Map

**Source:** Schwab's official Executive Council page (aboutschwab.com/leadership, fetched directly this session), LinkedIn, and news. Cross-referenced against email/calendar (CRM proxy) for every name below.

### Full Narrative Profiles (5 most strategically relevant)

**Dennis Howard — Managing Director, Chief Technology, Operations, and Data Officer**
Reports to Rick Wurster (CEO). Role expanded from CIO (title held 2016–2025) to include Operations and Data, effective January 29, 2026. Joined Schwab 2014 from Visa (CIO-level roles). **CRM status: no-crm-history — with an important caveat.** A "Dennis Howard" does exist in David's LinkedIn/calendar history (a CEO-event connection, follow-up emails about a private CEO gathering in Frisco), **but that is a different person** — a Vistage Chair/Executive Coach and Founder/CEO of LeaderThrive, LLC, not Schwab's CTOO. This is a live name-collision risk (see Open Items) — do not treat that existing relationship as a warm path to the real Dennis Howard.
**[VALIDATED 7/21 — LinkedIn]** The name-collision risk is confirmed and worse than a single stray contact: David has **two separate 2nd-degree "Dennis Howard" connections on LinkedIn.** The real CTOO is `linkedin.com/in/denniswhoward/` — title reads "Chief Technology, Operations & Data Officer at Charles Schwab," 2nd-degree, mutual connections include Samuel Henry and Meghan Kelley-Wehner. The performance-coach one is a *different* profile, `linkedin.com/in/dennischoward/` — "Professional Certified Performance Coach for CEOs," Dallas-Fort Worth, 2nd-degree with **72** mutual connections (a much denser overlap than the CTOO profile, which is exactly the kind of thing that tricks a quick LinkedIn glance into messaging the wrong one). Verify the vanity URL (`denniswhoward`, not `dennischoward`) before any outreach.
*Role inference (labeled):* economic buyer for any cross-functional AI/data engagement, given his newly unified mandate.
*Pitch angle:* "Do not cold-reach directly — build credibility through the practitioner contacts below first, then frame around platform modernization and engineering capacity, not a tool or methodology."
*What to avoid:* Approaching before warm credibility is built; conflating him with the unrelated "Dennis Howard" in David's own network.
Source: [Dennis Howard — About Schwab](https://www.aboutschwab.com/dennis-howard); [CIO Dive — CIO role expanded](https://www.ciodive.com/news/charles-schwab-expands-cio-role/811019/)

**Tim Heier — Executive Vice President, Chief Technology Officer**
Reports to CEO (peer to Howard on the Executive Council — distinct mandate: technology strategy, architecture, and client-facing application development, vs. Howard's infrastructure/ops/data scope). Joined Schwab 1999; background in engineering consulting and Lawrence Livermore National Laboratory. **CRM status: no-crm-history.**
**[VALIDATED 7/21 — LinkedIn]** Current title is **EVP, Chief Technology Officer (CTO)** (an upgrade from the MD title in the prior sourcing — ZoomInfo/MarketScreener were stale), based San Francisco. 2nd-degree connection; mutual connection is Luke Jensen.
*Role inference:* directly owns the client-facing application layer where Portfolio Insights and the AI "front door" get built — a second, distinct technical decision-maker from Howard, easily missed if the org chart only tracks "the CTO."
*Pitch angle:* "You're building the client-facing surface for Schwab's AI bets — Portfolio Insights, the front-door assistant. We help engineering orgs close the gap between a working prototype and a production system that scales to your client base."
*What to avoid:* Treating Heier and Howard as the same role/contact — they are not; confirm which of the two owns any specific initiative before pitching.
Source: [Tim Heier — ZoomInfo](https://www.zoominfo.com/p/Tim-Heier/1161209388); [MarketScreener](https://www.marketscreener.com/insider/TIM-HEIER-A26QSA/)

**Nikhil Sudan — Chief Strategy and Innovation Officer**
**Confirmed — direct CRM/email evidence, not inference.** LinkedIn connection request accepted June 30, 2026 (email confirmed: "Nikhil accepted your invitation... Chief Strategy and Innovation Officer at Charles Schwab | YPO"). Joined Schwab June 2025; owns corporate strategy, corporate development, innovation, AI strategy, and **vendor management**. Ex-President Victory Capital InVest, ex-McKinsey Partner (Wealth & Asset Management), ex-Bridgewater. Active YPO member — David's direct tie.
*Flag:* Sudan's title/bio is independently confirmed via his own aboutschwab.com bio page and The Org, but he did **not** appear on the aggregated Executive Council listing fetched this session (which lists 21 named MDs but omits him) — likely a page-maintenance lag, not evidence his role has changed, but worth a quick confirmation before treating him as sitting on the formal Executive Council roster.
**[VALIDATED 7/21 — LinkedIn]** Confirmed 1st-degree connection. Current headline: "Chief Strategy and Innovation Officer at Charles Schwab | YPO," Dallas-Fort Worth Metroplex. 24+ mutual connections, including Gurmeet Singh, PhD and Mark Hamill. (Executive Council roster absence is a Schwab-website question, not resolvable via LinkedIn/CRM — still an open item.)
*Pitch angle:* "You own AI strategy at a moment when Schwab has committed to shipping multiple client-facing AI products this year. I'd value comparing notes on where the strategy-to-production gap shows up, and where an execution partner who's done it elsewhere could de-risk the roadmap." (Peer-to-peer via YPO, not a sales motion.)
*What to avoid:* Turning the YPO relationship into a pitch on first contact.
Source: [Nikhil Sudan — About Schwab](https://www.aboutschwab.com/nikhil-sudan); LinkedIn connection confirmed via email record, June 30, 2026

**Sean Law — Principal Data Scientist, Director, R&D, Office of the CTO & AI Council**
**Confirmed — and warmer than the existing plan assumed.** Email records show Sean Law messaged David directly via LinkedIn on **June 24, 2026** — this is an existing, active, inbound conversation thread, not a cold or intro-gated contact. Creator/maintainer of STUMPY (open-source time-series library); 20+ years in data science/ML; came to Schwab via the TD Ameritrade acquisition.
*Role inference:* sits in R&D within the Office of the CTO — evaluates/prototypes AI approaches before production, then navigates the research-to-engineering handoff. Also holds institutional knowledge of TDA-integration data debt.
*Pitch angle:* Peer-to-peer, referencing STUMPY/time-series work if genuine: "We work with a lot of data science orgs where the bottleneck isn't the model — it's the engineering infrastructure around it. Given what Schwab is shipping this year, I'd love to understand where that friction shows up for your team."
*What to avoid:* Treating this as a cold outreach — he already opened the channel. Don't let the existing plan's "intro via Caleb Jenkins, follow-up pending" framing override the fact that a direct line is already open.
Source: [Sean Law — LinkedIn](https://www.linkedin.com/in/seanmylaw/); LinkedIn message confirmed via email record, June 24, 2026
**[VALIDATED 7/21 — LinkedIn + Dynamics CRM]** Sean shows as a **2nd-degree** LinkedIn connection (not 1st) — the June 24 direct message stands regardless (LinkedIn allows messaging 2nd-degree contacts), but don't describe him as a 1st-degree connection in any outward-facing material. Mutual connection: **Caleb**. This directly corroborates the original plan's "Caleb Jenkins" intro path — and the Improving Dynamics CRM account record for Charles Schwab & Co lists **Caleb Jenkins (tagged MSFT — Microsoft) as a registered Hand-Raiser on this account since 5/4/2025**, alongside Bipin Karmacharya and Biswajit Debdas (both tagged CFLT — Confluent, 12/1/2025). This resolves two things at once: (1) Caleb Jenkins is a real, CRM-registered contact tied to this account, not just a name in an old plan, and (2) he's a **Microsoft** partner contact — which fills the "not-identified" partner-contact gap in the Partner Network section below.

**Don Yuan — AI Transformation & Governance Leader**
**No CRM/email history found — no-crm-history.** LinkedIn headline: AI Transformation & Governance, Agentic AI/Analytics/Automation delivery. Certifications: Microsoft Fabric Analytics Engineer, AWS ML/Data Analytics Specialty, PMP, PSM. Active in the DFW AI builder community — co-promoted AgentCon Dallas for two consecutive years.
*Role inference:* sits at the intersection of AI strategy and delivery execution; agentic-AI focus signals he's likely responsible for making Schwab's planned automated/agentic client-service capabilities land reliably in production.
*Pitch angle:* Lead peer-to-peer on agentic AI specifically, referencing his AgentCon involvement and Microsoft Fabric certification (direct relevance to Schwab's Azure-native data platform).
*What to avoid:* A generic AI pitch — he is plugged into the practitioner community and will see through surface-level engagement immediately.
*To confirm before meeting:* whether he sits in the data science org (under Howard/Heier) or a broader enterprise AI/automation function.
Source: [Don Yuan — LinkedIn](https://www.linkedin.com/in/donyuan/)
**[VALIDATED 7/21 — LinkedIn]** 2nd-degree connection. Current title on profile: **"Senior Manager, Workplace AI & Intelligent Automation at Charles Schwab"** — more specific than the generic "AI Transformation & Governance Leader" framing above, and it answers the "confirm before meeting" question partially: "Workplace AI" suggests he sits closer to internal workforce-productivity AI than the client-facing product org. 25+ mutual connections, including Tim and George. Confirm the reporting line directly before the meeting regardless.

### Remaining C-Suite (Executive Council, per aboutschwab.com/leadership) — Compact

| Name | Title | CRM Status |
|---|---|---|
| Rick Wurster | President & CEO | no-crm-history |
| Mike Verdeschi | MD, Chief Financial Officer | no-crm-history |
| Stacy Hammond | MD, Chief Marketing Officer | no-crm-history |
| Shannon Jurecka | MD, Chief Administrative Officer (HR/Corp Affairs/Real Estate) | no-crm-history |
| Peter J. Morgan III | MD, General Counsel & Corporate Secretary | no-crm-history |
| Nigel J. Murtagh | MD, Chief Risk Officer | no-crm-history |
| Neesha Hathi | MD, Head of Combined Wealth Advisory and Banking Services **[NEW 10/23]** | no-crm-history |
| Omar Aguilar | CEO & CIO, Schwab Asset Management | no-crm-history |
| Jonathan S. Beatty | MD, Head of Schwab Advisor Services | no-crm-history |
| Jess Bramhall | MD, General Auditor | no-crm-history |
| Jonathan M. Craig | MD, Head of Retail Investing | no-crm-history |
| Andrew D'Anna | MD, Investment Platforms, Solutions, and Strategy | no-crm-history |
| Lisa Kidd Hunt | MD, Head of International Services | no-crm-history |
| James Kostulias | MD, Head of Trading Services | no-crm-history |
| Jeff Starr | MD, Head of Operations | no-crm-history |
| Adele Taylor | MD, Head of Workplace Services | no-crm-history |
| Tyler Woulfe | MD, Chief Banking Officer | no-crm-history |
| Christopher Wyse | MD, Chief Corporate Affairs Officer | no-crm-history |

*Note: this Executive Council list (18 names above + the 5 full-profile contacts = 23) is Schwab's own self-described leadership roster as of this session's live fetch — it is Schwab's stated "C-suite equivalent" for a Managing-Director-titled organization, not a smaller curated subset.*

**[NEW 10/23] Leadership change check (primary source: SEC EDGAR filing index, CIK 0000316709).** No Form 8-K reporting Item 5.02 (departure or appointment of directors and executive officers) has been filed since the 2026-01-29 restructuring filing. That is a verifiable negative: no CEO, CFO, or named executive officer change occurred between July and October 2026. Supporting confirmations:

- **Rick Wurster remains President and CEO.** He is quoted as CEO in the Q3 2026 earnings release filed 2026-10-15 and gave the October 2026 Charley and AI-agent interviews in that capacity.
- **Mike Verdeschi remains CFO.** Quoted as CFO in the same Q3 2026 release.
- **Neesha Hathi's remit was consolidated** in January 2026 into a combined Wealth Advisory and Banking organization at what the CEO called the "No. 1 thing" for RIAs. The table above reflects the revised scope. Source: [RIABiz, 2026-01-29](https://riabiz.com/).
- **Dennis Howard and Tim Heier:** no public indication of a change. Howard appears in an August 2026 Form 4 filing, confirming he was still a Section 16 reporting officer of Schwab as of 2026-08-18. **Heier's continued tenure was not independently re-verified in this refresh** and should be re-checked before any direct outreach.
- **One level down:** James Kostulias was still publicly identified as Head of Trading Services in late July 2026. Two RIA custody departures were reported in August 2026 (a custody unit executive, and veteran Elyn Davis to Raymond James), neither of which touches the technology organization.

### One Level Down (AI/Data/Strategy org — partial, not exhaustive)

| Name | Title | Reports Toward | CRM Status |
|---|---|---|---|
| Hardeep Walia | MD, Head of Firmwide AI | Likely CTOO/CEO org | no-crm-history |
| Brandon Hill | Director, Data Science Engineering, MLOps & GenAI | Likely under Firmwide AI/CTOO org | no-crm-history |
| Andy Furbush | MD, Head of Corporate Strategy | Strategy/Innovation org (Sudan) | no-crm-history |
| Nate Knowlton | Director, AI Strategy | Strategy/Innovation org (Sudan/Furbush) | no-crm-history |
| Sarah Wolf | Director of Business Strategy | Strategy/Innovation org (unconfirmed — see Open Items) | no-crm-history |

**This one-level-down list is explicitly partial** — it covers the AI/Data/Strategy org only, since that's what's discoverable and relevant to this pursuit. A true one-level-down for all 18+ remaining C-suite functions (Legal, Risk, HR, Finance, Trading, Banking, etc.) was not built — flagged honestly rather than padded or presented as exhaustive.

---

## ICP & Account 9-Box

*(Per workflow instruction, placed immediately after the Leadership/Org Chart section and before the Referral/Partner Network section. Every inference below is flagged for David to verify — see also the workflow-issue note below the table.)*

### Potential Score

**Revenue factor — best-case annual IT services spend:**
- **Path 1 (public filings, checked first):** Schwab's FY2025 10-K and quarterly filings discuss technology/equipment expense trends (e.g., "equipment expense increased... due to higher technology equipment and software costs") but do **not disclose a clean, usable total IT/technology spend figure or IT-services-specific breakout.** Path 1 checked, no usable figure found — expected outcome per the workflow's own failure-mode guidance, not a research gap.
- **Path 2 (fallback — company-size benchmark):** Schwab FY2025 net revenue: **$23.9B** (record year, +22% YoY). Headcount: **~33,000**. Applying a financial-services IT-spend benchmark of ~4–7% of revenue (Gartner-style industry range cited in the workflow's own methodology) at the midpoint (~5.5%) yields a total IT budget estimate of roughly **$1.3B**. Applying a ~20% discount to isolate the external-services (vs. internal headcount/licensing) portion yields an estimated **best-case annual IT services spend of ~$260M.**
- **[NEW 10/23] Updated revenue input.** Trailing-twelve-month net revenue is now approximately **$27.0B**, derived from the filed quarters: Q3 2026 net revenue of $7.2B (+17% YoY), H1 2026 net revenue of $13.55B (+18% YoY), and implied Q4 2025 of roughly $6.27B. Re-running the same Path 2 method at 5.5% of $27.0B with the same ~20% services discount yields roughly **$297M**, up from ~$260M. **The score does not change**, because the factor is already capped at +5 and $297M is still more than ten times the lookup table's $20M ceiling. This is recorded for accuracy, not because it moves the 9-box.
- **[NEW 10/23] Corroborating signal on actual technology spend.** Q2 2026 capital expenditures were **$792M**, versus $173M in Q1 2026 and $136M in the prior-year quarter, driven by **$633M of incremental capex tied to a multi-year software license agreement**, with a corresponding liability recognized in long-term debt. That single commitment is larger than a full year of Schwab's normal capex run rate and confirms that a very large platform or software decision has already been made and financed. Source: [Q2 2026 earnings release, 2026-07-21](https://www.sec.gov/Archives/edgar/data/316709/000031670926000027/a2q26exhibit991.htm). **Open question worth asking in the room:** which vendor, and what does the integration tail look like. A commitment of that size almost always generates years of downstream integration, data migration, and adoption work.
- Record:
  - method: company-size cross-referenced against industry IT-spend benchmark (fallback)
  - source_priority_path: 2 — Path 1 checked (10-K/10-Q), no usable figure found; fallback used
  - benchmark_used: Gartner-style IT-spend-as-%-of-revenue range for financial services (~4–7%), applied at 5.5% midpoint to $23.9B FY2025 revenue, then discounted ~20% for the external-services subset
  - estimated_annual_it_services_spend: ~$260M on the FY2025 revenue basis, ~$297M on refreshed TTM revenue as of 2026-10-23. Either figure is **far above** the lookup table's top band, so the factor is capped regardless (see workflow-issue flag below).

**Gross margin factor:** Default **38%** — mid-range blended-delivery assumption per Improving's typical realized range, not account-specific confirmed data.

**Geography factor:**
- Flag (a) same_location_as_buyer: **Y** — David/Improving's Dallas-based team and multiple Schwab contacts (Timothy Hartwell/ID sponsor, Don Yuan, Andy Furbush) are DFW-area based; Schwab's own HQ is Westlake, TX (DFW metro).
- Flag (b) Improving_office_in_client_location: **Y** — Improving has a Dallas office and David's own enterprise coverage includes Dallas.
- Both flags Y → geo_raw = **4** (per the workflow's proposed, single-data-point-inferred scoring curve — see flag below).

**Scored factors and weighted Potential:**

| Factor | Raw Score | Weight | Weighted |
|---|---|---|---|
| Geography | 4 | 0.10 | 0.4 |
| Revenue | **5 (capped — see flag)** | 0.70 | 3.5 |
| Gross Margin | 2 (interpolated — 38% sits between 37%→2 and 40%→3, closer to 37%) | 0.20 | 0.4 |
| **Total Potential** | | | **4.3** |

### Realized Score

**[VALIDATED 7/21 — direct Dynamics CRM account record, not the M365/email-notification proxy]** The account record's own AI-generated summary states: *"We closed opportunities worth $2,554,624 with Charles Schwab & Co since 8/4/2023. We have successfully closed 16 opportunities with them so far from a total of 22"* (73% win rate). This is a **materially higher and more authoritative figure** than the original draft's $900K–$1M summed-email estimate — but it is **cumulative since account creation (4/3/2023), not TTM.** Averaged over ~3.3 years that's roughly $770K/year, which is actually *close to* the prior estimate on an annualized basis — the correction is in precision and source authority, not direction. A true TTM figure would require filtering the CRM's opportunity-close dates to the trailing 12 months specifically, which this pass didn't isolate — flagged as a residual open item below.

**[UPDATED 10/23 — CRM re-pulled via the Dataverse Web API]** Cumulative closed-won is now **$2,663,824 across 17 of 24 opportunities (71%)** — the increase since July is the Andraya Goodwin extension ($109,200, won 2026-10-21). A true TTM cut is now in hand: **$736,600 across 5 deals** closing between 2025-11-26 and 2026-10-21 (2026 Extension Shel & Joe $392K, Julie King $84K, Abby Honerkamp/Julie Navar $49K, Julie King $102.4K, Andraya Goodwin $109.2K). That sits just under the $750K band boundary referenced in the methodology's lookup table. If scored at raw -1 rather than 0, Total Realized moves from 0.2 to roughly -0.5, still inside the Mid band (-1.7 to +1.7), so the **POISED classification does not change either way**. The printed score below is left at 0.2 pending the same band-boundary confirmation flagged on the ORIX run, per the rule against silent re-scoring.

The two opportunities that were open at the July pass have both resolved as **losses**: **"Backfill Instructional Designer for Joe Jackson"** ($0 est., closed lost 2026-07-24) and **"Instructional Designer – for Brian Matheny"** ($70,000 est., closed lost 2026-09-21) — both owned by Derek Nwamadi (confirmed as the account owner of record in CRM). One opportunity is currently open: **"Extend Julie King - Instructional Designer," $104,000, est. close 2026-11-29**. Account WorkDay Customer ID: C-0782.

- **TTM actual revenue:** Still using the ~$900K–$1M banding pending a true TTM CRM filter (see above) — this keeps the 0-point Revenue score unchanged, but confidence in the input is now higher.
- **TTM actual gross margin:** Not available from CRM opportunity records (bill rates/budgets, not cost basis). Estimated at **30%**, unchanged — flagged as an assumption, not a finance-confirmed figure.
- **Geography:** same as Potential (structural, doesn't change) — raw = 4.

| Factor | Raw Score | Weight | Weighted |
|---|---|---|---|
| Geography | 4 | 0.10 | 0.4 |
| Revenue | 0 (interpolated — annualized CRM figure (~$770K/yr) still sits at/near the $1M boundary, rounded to the 0 point) | 0.70 | 0.0 |
| Gross Margin | -1 (30% band) | 0.20 | -0.2 |
| **Total Realized** | | | **0.2** |

### 9-Box Classification

- Realized = 0.2 → **Mid band** (-1.7 to +1.7)
- Potential = 4.3 → **High band** (>+1.7)
- Grid cell: High Potential / Mid Realized → **POISED**

**This is the one grid cell independently verified against the source data (AT&T's confirmed Potential 3.1 / Realized ≈0 → POISED).** Schwab landing in the same verified cell is a point of higher confidence than the other eight zones, which remain unverified inferences.

### Inferences Flagged for David to Verify

1. **Geography scoring logic** (0 baseline, +4 for both flags Y) is inferred from a single AT&T data point (N/N=0) — unverified for any account with a "Y" flag, including this one.
2. **9-box grid arrangement** beyond the single confirmed AT&T/POISED cell is unverified — though Schwab happens to land on the one verified cell.
3. **IT services spend estimate (~$260M)** sourced via Path 2 fallback (Gartner-style benchmark × FY2025 revenue, discounted for services subset) — Path 1 (10-K) checked first and found no usable disclosed figure. **See the workflow-issue flag directly below — this number blows past the lookup table's ceiling and the capping behavior may not be meaningful for large-cap accounts.**
4. **Gross margin defaults** (38% Potential, 30% Realized) are Improving's typical-range assumptions, not Schwab-specific confirmed data.
5. **Realized revenue figure** ($900K–$1M) is a summed-budget approximation from CRM notification emails, not a verified precise TTM pull from Dynamics CRM directly.
6. **$1M revenue-band boundary ambiguity**: the Realized revenue estimate sits at/near the $1M boundary where the source lookup table has an unresolved duplicate entry (0/1) — used the more conservative 0 point.

### Workflow Issue Found (Flagging, Not Smoothing Over)

**The Revenue-factor lookup table tops out at $20M → score +5.** For a company Schwab's size ($23.9B revenue), the Path 2 fallback methodology (industry-benchmark-% × company revenue) produces an estimate (~$260M) that is **more than 10x the table's top band** — meaning the factor is functionally a constant +5 for any large-enterprise target, regardless of whether the target is a $2B regional company or a $200B money-center bank. This materially reduces the score's ability to discriminate between large accounts of different sizes. Notably, the one confirmed data point (AT&T, revenue_raw = 3, not 5) suggests the AT&T source plan did **not** apply a naive revenue-benchmark calculation to AT&T's total company revenue (~$120B+) — it likely used a smaller, more scoped estimate of realistic addressable IT-services spend, not total-company-revenue-times-industry-benchmark. **This is a real gap in the workflow's methodology as literally written in step 04**, not something I should silently paper over by picking a smaller, more "reasonable-looking" number — I applied the stated method faithfully and it broke on a mega-cap account. Recommend David/whoever owns this workflow revisit whether Path 2's benchmark should be capped by realistic single-engagement or single-department addressable spend, rather than whole-company revenue, before running this workflow on other large-cap targets.

---

## Referral / Relationship Network

*(Kept structurally separate from the leadership/org map above and from the partner network below, per workflow requirement.)*

### Existing Sponsor Path
- **Applicable:** Yes (active-but-underleveraged)
- **Sponsor:** The current Instructional Design engagement contacts — Timothy Hartwell (Sr. Instructional Design Manager, Dallas), Sandy Gomes (Director, Learning & Development), Abby Honerkamp — are the confirmed, existing relationship.
- **Status:** confirmed (active SOWs, ongoing invoicing/PM relationship per CRM/email records)
- **Note:** This path can open warm intros toward Sean Law/Don Yuan, but is one hop removed from the technical/AI org — it's a credibility asset, not a direct line to the economic buyer.

### Personal Network Ties

| Contact | Tie Type | Path | Status | Note |
|---|---|---|---|---|
| Nikhil Sudan | YPO | Direct YPO tie; LinkedIn connection accepted June 30, 2026 | **confirmed** | Most senior contact in this network; owns AI strategy and vendor management |
| Sean Law | Prior-inbound-contact | Sean messaged David directly via LinkedIn, June 24, 2026 | **confirmed** | Existing open channel — not a cold or intro-gated contact; upgrade from the prior plan's "intro pending via Caleb Jenkins" framing |
| Andy Furbush, Nate Knowlton | Via named intermediary ("Cole" at SpaceX/xAI, per prior account knowledge) | One hop via Cole | **needs-verification** | Carried forward from the existing hand-built plan; this session found no independent email/CRM/LinkedIn confirmation of "Cole" or these ties — flagged for direct verification with David before treating as confirmed |
| Sarah Wolf | Via named intermediary ("Cole" at SpaceX/xAI) — **but now independently reachable regardless** | Confirmed current LinkedIn profile | **confirmed in-seat** | **[VALIDATED 7/21]** No longer dependent on confirming "Cole" — see below |

### Mutual Connections (LinkedIn)

**[VALIDATED 7/21]** Ran directly via authenticated LinkedIn this session — the earlier "unavailable" status is now resolved for all five profiles below.

| Profile | Degree | Current Title (per LinkedIn) | Mutual Connections |
|---|---|---|---|
| Dennis Howard (real CTOO — `denniswhoward`) | 2nd | Chief Technology, Operations & Data Officer at Charles Schwab | Samuel Henry, Meghan Kelley-Wehner + others |
| Dennis Howard (unrelated coach — `dennischoward`) | 2nd | Professional Certified Performance Coach for CEOs | Debbie Mrazek, Kristin Robertson-Brio Leadership + 72 others |
| Tim Heier | 2nd | EVP, Chief Technology Officer (CTO) at Charles Schwab | Luke Jensen |
| Nikhil Sudan | **1st** | Chief Strategy and Innovation Officer at Charles Schwab \| YPO | Gurmeet Singh PhD, Mark Hamill + 24 others |
| Sean Law | 2nd | Principal Data Scientist, R&D at Charles Schwab | Caleb (matches Caleb Jenkins, CRM-confirmed Hand-Raiser/MSFT on this account) |
| Don Yuan | 2nd | Senior Manager, Workplace AI & Intelligent Automation at Charles Schwab | Tim, George + 25 others |

**New finding — Sarah Wolf confirmed in-seat.** `linkedin.com/in/sarah-k-wolf/`: **"Director, Business Strategy, Trading Services, Charles Schwab,"** Greater Chicago Area, 2nd-degree. This resolves the open item both plans flagged — she is the current, correct, in-seat contact, independent of confirming the "Cole" referral chain.

### Referral Network Summary

**Strongest path:** Nikhil Sudan (direct YPO tie, confirmed LinkedIn connection) — most senior, most direct, executive-level warm path in the account. **Close second:** Sean Law, who has already opened a direct line via LinkedIn message — arguably the single most immediately actionable item in this entire plan, since no further "getting an intro" work is needed.

---

## Partner Network

*(Improving's fixed 8-partner list — AWS, Microsoft, GCP, Confluent, Databricks, SpaceX/xAI, Snowflake, SAP. Kept separate from the referral network above.)*

| Partner | Likely In Use | Evidence | Partner Contact |
|---|---|---|---|
| **Microsoft (Azure)** | **confirmed** | Schwab selected Microsoft Azure Cloud Services for application hosting/computing (2017, AppsRunTheWorld); consistent with the existing account plan's assessment that Azure is Schwab's primary cloud | **[VALIDATED 7/21] Caleb Jenkins** — registered Hand-Raiser (MSFT) on the Schwab account in Improving's Dynamics CRM since 5/4/2025; also the mutual LinkedIn connection and intro path to Sean Law |
| **GCP** | **confirmed** | Schwab job postings (Cloud Data Platform Engineer, Cloud Data Engineer — Southlake/Austin, TX) explicitly cite Google Cloud Platform for the SAM Data team's pipeline work | not-identified |
| **Snowflake** | **confirmed** | Same job postings explicitly reference "Snowflake resources" and cloud-native pipelines built on GCP + Snowflake | not-identified |
| **AWS** | **likely** | Schwab selected Amazon EC2 for application hosting (2021, AppsRunTheWorld) — an older, secondary-cloud signal alongside the confirmed Azure/GCP usage | not-identified |
| **Confluent** | **confirmed — upgraded from likely** | A Confluent "Current" conference session references Schwab's Kafka-based event-streaming architecture handling 2M messages/second. **[VALIDATED 7/21]** Improving's Dynamics CRM lists two Confluent-tagged (CFLT) Hand-Raisers on this account — Bipin Karmacharya and Biswajit Debdas, both since 12/1/2025 — which is a stronger signal than the conference reference alone that this is the commercial Confluent platform, not bare open-source Kafka | **Bipin Karmacharya, Biswajit Debdas** — registered Hand-Raisers (CFLT) on the Schwab account since 12/1/2025 |
| **Databricks** | no-signal-found | No Schwab-specific public signal found this session | not-identified |
| **SAP** | no-signal-found | No Schwab-specific public signal found this session (searched ERP/SuccessFactors/Ariba specifically) | not-identified |
| **SpaceX/xAI** | no-signal-found | No relevant public signal — different industry; only relevant via Cole as a personal referral node, not a tech-stack relationship | not-identified |

**Partner network summary:** 8 of 8 partners checked. Confirmed: Microsoft, GCP, Snowflake, Confluent. Likely: AWS. No signal: Databricks, SAP, SpaceX/xAI. **[VALIDATED 7/21] Strongest partner path now has named contacts** — Caleb Jenkins (Microsoft) and Bipin Karmacharya/Biswajit Debdas (Confluent) are all registered Hand-Raisers on this exact Schwab account in Improving's own Dynamics CRM, not generic alliance-owner routing. Caleb Jenkins is also David's mutual LinkedIn connection with Sean Law — start there.

**[NEW 10/23] Partner relevance reassessment.** No new public signal changes the status of any of the eight partners. Databricks and SAP remain no-signal. Two notes that matter more than a status change:

- **Anthropic is not on Improving's partner roster, and it is now Schwab's named AI vendor.** This is the single biggest change in the partner picture since July. It does not invalidate any row above, but it does mean the Microsoft and Confluent Hand-Raiser paths remain the only credentialed ways in. Do not build a pitch that presumes an Anthropic relationship.
- **The $633M multi-year software license is an unidentified vendor.** It is the largest single technology commitment visible in Schwab's public financials and no public source names the counterparty. Given Schwab's confirmed Azure and GCP footprint, Microsoft or Google are plausible, but that is inference and should be labeled as such. Determining this vendor is now the highest-value unanswered question in the partner section, because the integration tail on a commitment that size is exactly the work Improving sells.

---

## Contact Prioritization & Sequencing

| Priority | Contact | Entry Point | Goal |
|---|---|---|---|
| 1 | **Sean Law** (Principal Data Scientist, Office of the CTO) | **Already-open LinkedIn channel — he messaged David directly, June 24, 2026** | Respond and convert into a real conversation about R&D-to-production friction; no intro needed |
| 2 | **Nikhil Sudan** (Chief Strategy & Innovation Officer) | Direct YPO tie; LinkedIn connection accepted | Peer-level AI-strategy conversation; executive air cover for the account |
| 3 | Existing ID sponsor (Timothy Hartwell / Sandy Gomes) | Existing relationship | Warm intro to Don Yuan and/or Tim Heier's org |
| 4 | **Don Yuan** (AI Transformation & Governance Leader) | Via ID sponsor, LinkedIn, or AgentCon community | Understand agentic-AI delivery pain points |
| 5 | **Tim Heier** (CTO — client-facing app development) | Cold/LinkedIn — no warm path identified | Understand ownership split with Howard's org on AI-powered client experiences |
| 6 | Andy Furbush, Nate Knowlton | Via "Cole" (needs-verification this session) | Confirm the referral path is live before treating as an entry point |
| 6b | **Sarah Wolf** (Director, Business Strategy, Trading Services) | **[VALIDATED 7/21] Confirmed in-seat via LinkedIn — no longer contingent on "Cole"** | Business-outcome framing of platform modernization |
| 7 | **Dennis Howard** (CTOO) | Via credibility built through paths above | Economic buyer — engage only after proof points are established; do **not** confuse with the unrelated "Dennis Howard" (Vistage/LeaderThrive) already in David's network |

**[NEW 10/23] Sequencing caveat: the two front-of-queue paths are aging.** This table was sequenced on 2026-07-21. Two facts have changed with time alone, regardless of any news:

- **Sean Law's inbound message is now four months old** (2026-06-24). An unanswered inbound LinkedIn message has a short half-life. If David has already replied, this row should be updated rather than carried; if he has not, this is no longer a warm open channel, it is a cold one with a mildly awkward history. Rank it accordingly and consider whether to reopen via Caleb Jenkins instead.
- **Both CRM opportunities open at the July pass have now resolved as losses** (re-pulled 2026-10-23 via Dataverse Web API): the Joe Jackson backfill closed lost 7/24 ($0) and the Brian Matheny role closed lost 9/21 ($70K). The beachhead's health rests on renewals: the Julie King extension won 6/10, the Andraya Goodwin extension won 10/21 ($109.2K), and one open extension (Julie King, $104K, est. close 11/29) is in flight. Two losses on new-seat fills against three extension wins says Schwab will keep renewing known-good designers but is not expanding the bench right now.

Everything else in the table is structurally unchanged. Nikhil Sudan remains the strongest executive path, the ID sponsor remains the most reliable warm intro, and the Dennis Howard name-collision warning remains fully in force.

---

## Entry Plays / Opportunity Scenarios

### Option A — AI Innovation Lab on a Shipped-Product Backlog Item
Schwab is actively shipping client-facing AI products (Charley, Portfolio Insights, the AI "front door," under-$1M segment tooling). Offer Improving's AI Innovation Lab: an embedded team that co-creates one to three proof-of-value builds with Schwab's own engineers against a specific, shipped-product backlog item.

**Grounding:** **AI Innovation Lab** (AI Offerings). Embedded on-site team, 1-3 PoC/PoV projects, ACT framework (Anchor weeks 1-2, Consistency weeks 3-10, Transition 1-2 weeks); price not stated in the source doc. Source: `General/Sales Support/Sales Offerings/Specific Offerings/AI Offerings/AI Innovation Lab Offering.docx`. *Correction from the prior version:* the original play pitched a "dedicated engineering pod within 30 days," which maps to **Embedded Delivery Capacity (Microsoft Stack)**, a GMS offering outline still in **draft, unapproved status** that explicitly scopes its target customer at $1-2B-revenue accounts and names Fortune-500-scale pursuits out of scope. It cannot be cited as a runnable offering for Schwab. The runnable, current offering for this play is the AI Innovation Lab.

**Entry pitch:** "You've shipped Charley and signed the Claude rollout for 16,000 RIAs. We embed a senior team alongside yours to co-create the next one to three proof-of-value builds off that backlog, and we leave your engineers able to run the pattern without us. Which shipped-AI backlog item is most starved for senior build capacity right now?"

### Option B — Data Platform Modernization (Data Enablement Engagement)
Post-TDA data architecture rationalization is still an open, cited priority. Pitch Improving's Data Enablement Engagement, leading with the Thrivent TEID story.

**Grounding:** **Data Enablement Engagement** (Data Enablement). Duration 4-8 weeks; Price $125,000-$250,000. Source: `.../Specific Offerings/Data Enablement/Data Enablement Engagement.docx`. *Correction from the prior version:* the engagement was described as "8-12 week discovery-plus-build"; the real offering's stated shape is 4-8 weeks at $125K-$250K, and the pitch now reflects that.

**Entry pitch:** "We've done this exact consolidation pattern before with another large financial services firm. Our Data Enablement Engagement is a 4-to-8-week, scoped build that takes one integration problem off your backlog and hands you a replicable pattern for the rest."

### Option C — AI Developer Productivity Enablement (AI Team Enablement)
Bridges the current ID engagement into technical delivery: Improving's AI Team Enablement Deep Learning Program, a 12-week embedded-coaching program for product and engineering teams adopting Copilot-class and agentic AI tooling, without a hard pivot away from the existing relationship.

**Grounding:** **AI Team Enablement Deep Learning Program** (AI Software Engineering - Transformation). 12 weeks, 6 half-day workshops, up to 24 participants, 1 embedded AI engineer per 3 teams with daily pairing between sessions; priced per track plus hourly, custom quote. Source: `.../AI Offerings/AI Software Engineering - Transformation/AI Team Transformation.docx`.

**Entry pitch:** "There's a real difference between having Copilot licenses and actually shipping faster. Our Deep Learning Program embeds AI engineers with your teams for 12 weeks, with half-day workshops every two weeks and daily pairing in between, until the tool is an actual delivery accelerator."

### Option D: AI Agent Governance and Control Evidence **[NEW 10/23]**
Schwab is now publicly blocking unauthorized third-party AI agents from moving client money, has pointed clients toward its own assistant instead, and its CEO has called for "rules of the road" on autonomous agent trading. That is an unusual opening: a large regulated institution has publicly named a control problem it has not fully solved, in a domain where most SIs have no differentiated answer.

**Grounding:** **AI Governance & Compliance Control Plane** (Improving AI Governance Practice, client one-pager, July 2026). Documented start shape: discovery workshop (weeks 1-2), control plane stand-up (weeks 3-6), operating model handoff (weeks 7-8); price not stated. Source: `General/Presentations/Reference-IP/AI Governance Control Plane - Client One-Pager.pdf`. *Scope-fit caveat:* the offering as documented governs the enterprise AI tool footprint: unified inventory, spend, policy, monitoring and drift detection, runtime enforcement. Schwab's agent-transaction-control problem (entitlement boundaries, action logging, human-in-the-loop thresholds on money movement) is adjacent to and sharper than the documented scope, so validate scope fit with the Chief Consulting Officer's office before scoping an engagement. This is a real offering with a real delivery shape, not an invention; the caveat is about fit, not existence.

**Entry pitch:** "You've said publicly that agents need rules of the road. Most firms have the policy language and not the control evidence behind it. We run an AI governance control plane ourselves, in production, and we stand the same thing up for clients: inventory, policy, monitoring, and enforcement your audit team can actually point at."

**Why this is credible for Improving and not for a Big-4 firm at this size:** it is a bounded, technical, evidence-producing engagement rather than a strategy document. It also produces artifacts Schwab can show a regulator, which is a stronger internal sell than a roadmap.

**Recommendation (revised 2026-10-23).** Lead with **Option A** as the primary ask and carry **Option D** as the differentiated door-opener. Both are grounded in real, current Improving offerings (AI Innovation Lab and the AI Governance & Compliance Control Plane, respectively); the prior version of Option A leaned on an embedded-pod shape that does not exist as an approved offering for an account of Schwab's scale, and it has been reworded accordingly.

The July rationale for Option A still holds: it maps to the most visibly funded initiative and to a shipped product in Charley. What has changed is the approach path. The July recommendation leaned on Sean Law's inbound message as a low-friction way in, and that message is now four months old. Treat the path as cold and rebuild it, most likely through the ID sponsor or Caleb Jenkins.

Option D is the sharper conversation for a first technical meeting precisely because it is narrow, current, and public. It also survives the two objections that kill generic AI pitches at Schwab: it does not require an Anthropic relationship, and it does not compete with the India capability center on headcount. Confirm the scope-fit caveat above with the CCO office before putting a number on it.

> **Offering-grounding gate note (2026-10-23).** The Improving-side capabilities and entry plays in this plan were re-grounded on 2026-10-23 against a live pull of Improving's offering sources: the Sales Offerings tree (`OfficeoftheChiefConsultingOfficer / Shared Documents / General / Sales Support / Sales Offerings / Specific Offerings/`, all eight category folders listed and the relevant offering documents opened and quoted verbatim), the CCO's GMS Materials folder (which surfaced the draft Embedded Delivery Capacity outline and the not-yet-validated Information Security Strategy package), and the Reference-IP library (AI Governance Control Plane one-pager), plus tenant-wide gap-fill searches (including the Central Sales/SPARC site) for security, staff-augmentation, contact-center, and Azure-OpenAI-specific offerings. Offering names, durations, and prices above are verbatim from the source documents, pulled 2026-10-23. Plays or capabilities with no matching real offering are marked `no_match` or Aspirational rather than force-fit. One residual gap: no validated security-strategy offering exists today (the GMS Information Security Strategy package is capacity-flagged Red with "no external pitching" until a delivery lead is named), so any security-led conversation at Schwab is aspirational pending CCO sign-off.

---

## Multi-Year Strategic Path

*(Active-but-underleveraged shape, per step 01's determination.)*

| Phase | Timeline (rebased 2026-10-23) | Milestone |
|---|---|---|
| **Access** | Nov 2026 – Jan 2027 | Re-establish a live human channel (ID sponsor, Caleb Jenkins, or Sudan). Diagnose why the July access phase did not produce a conversation, then fix that specific cause. |
| **Prove** | Jan – Apr 2027 | Land one scoped SOW (Option A, with Option D as the door-opener). Execute flawlessly; embed a senior Improving engineer. |
| **Expand** | Apr – Oct 2027 | 2 to 3 parallel workstreams; known entity across the AI/Engineering and Data orgs. |
| **Partner** | 2028+ | Named preferred implementation partner for AI/data work; positioned for larger enterprise engagements. |

**Note on the rebase.** The July timeline is now spent. Phases were measured in months from a July start, and the Access phase did not visibly convert. The dates above restart the clock from this refresh rather than pretending the first three months happened. If the Access phase had in fact produced conversations not captured here, correct this table rather than defending it.

---

## Immediate Next Actions

**[NEW 10/23] Reconciled as of 2026-10-23.** Items 1 through 9 below are the July list with current status applied. Items 10 through 12 are new this refresh.

1. **Establish whether Sean Law's 2026-06-24 message was ever answered.** If yes, log the outcome here and move to the next step in that thread. If no, decide explicitly between a late, honest reply and a fresh approach via Caleb Jenkins. Do not carry this forward as "the open channel" a fifth month running.
2. **Reach out to Nikhil Sudan via the accepted LinkedIn connection**, framed as a peer YPO exchange on AI strategy execution, not a sales call. Unchanged and still the best executive path.
3. **Verify the "Cole at SpaceX/xAI" referral path is real and current** before treating Andy Furbush or Nate Knowlton as warm. Still unconfirmed after two passes.
4. **Ask the ID sponsor (Timothy Hartwell/Sandy Gomes) for a casual, low-key intro to Don Yuan.** Unchanged.
5. **Confirm Nikhil Sudan's current Executive Council status.** Still open; his bio page confirms the title but he is absent from the aggregated roster.
6. **Do not leverage the unrelated "Dennis Howard"** (Vistage/LeaderThrive) in David's own network. Unchanged, and worth restating because the name collision is easy to repeat.
7. **Prepare the Thrivent TEID win-wire one-pager.** Still not evidenced as done, and now more relevant: the Anthropic and Charley work creates exactly the integration-and-controls problem Thrivent describes.
8. **Confirm whether Tim Heier or Dennis Howard owns the client-facing AI application layer.** This is now more urgent than in July, because Charley is live and someone owns it.
9. **Route the IT-spend methodology question back to the workflow owner.** Unchanged.
10. ~~**Reopen the CRM question first.**~~ **Resolved 2026-10-23 (CRM re-pull via Dataverse Web API).** Both opportunities closed lost: Matheny ($70K, 9/21) and the Joe Jackson backfill ($0, 7/24). New facts the re-pull surfaced: the Andraya Goodwin extension won 10/21 ($109.2K), and a Julie King extension is open at $104K with an estimated close of 11/29. Follow-up that replaces this item: confirm the Julie King extension closes, and ask Derek Nwamadi for loss reasons on the two lost fills, because the pattern (extensions win, new seats lose) shapes how hard to push Option C's bridge into technical delivery.
11. **Identify the counterparty on the $633M multi-year software license.** No public source names the vendor. Ask directly in any technical conversation; a commitment this size generates the integration tail Improving sells.
12. **Reframe the entry pitch around AI governance and control evidence, not just AI build capacity.** Schwab spent mid-October publicly blocking unauthorized AI agents and calling for "rules of the road." That is a stated, dated, executive-level pain that sits directly in Improving's delivery wheelhouse and did not exist as a talking point in July.

---

## Open Items to Confirm

**Resolved 2026-07-21 (via authenticated LinkedIn + direct Dynamics CRM query):**
- ~~Sarah Wolf's current in-seat status~~ — **Confirmed current**: Director, Business Strategy, Trading Services, Charles Schwab (Chicago).
- ~~Confluent tech-stack signal ambiguity~~ — **Upgraded to confirmed**: two Confluent-tagged (CFLT) Hand-Raisers registered on the account in Improving's CRM.
- ~~LinkedIn mutual-connections lookups~~ — **Run for all five profiles**; see updated table above.
- ~~Realized revenue estimate imprecision~~ — **Replaced with direct CRM figure**: $2,554,624 total closed-won since 8/4/2023 (16/22 opportunities, 73% win rate), though a true TTM cut still wasn't isolated (see new item below).
- ~~Partner Network "not-identified" contacts for Microsoft/Confluent~~ — **Named contacts found**: Caleb Jenkins (MSFT), Bipin Karmacharya + Biswajit Debdas (CFLT), all registered Hand-Raisers on this account.
- ~~No native CRM connector~~ — **Resolved**: queried Dynamics CRM directly this session (account record, opportunities, Hand-Raisers) rather than via the M365 email-notification proxy.

**Still open (not resolvable via LinkedIn/CRM — needs David directly):**
- Nikhil Sudan's absence from the live-fetched Executive Council roster (despite his own bio page confirming the title) — quick reconfirmation recommended.
- The "Cole at SpaceX/xAI" referral path to Andy Furbush and Nate Knowlton specifically (Sarah Wolf no longer depends on this) — no email/CRM/LinkedIn trace found this session either.
- Likely incumbent SIs at Schwab for AI/data work — no public signal found; assumed present based on account scale, not confirmed.
- Geography scoring logic and 9-box grid arrangement (both flagged inferences per the workflow's own methodology, beyond the single AT&T data point).
- The IT-services-spend estimate (~$260M) and the workflow's revenue-band ceiling issue for mega-cap accounts (see the 9-Box section) — needs a methodology decision, not just a data point.
- ~~**New:** isolate a true trailing-12-month revenue figure from Dynamics CRM~~ — **Resolved 2026-10-23:** TTM won revenue is $736,600 across 5 deals (11/26/2025 to 10/21/2026), per the Dataverse re-pull. Just under the $750K band boundary; POISED classification unchanged either way (see the Realized Score section).
- ~~**New:** two open CRM opportunities found this session that neither plan tracked~~ — **Resolved 2026-10-23:** both closed lost. Matheny ($70K, closed 9/21) and the Joe Jackson backfill ($0, closed 7/24). One opportunity is open now: Julie King extension, $104K, est. close 11/29.
- Whether Dennis Howard (real, Schwab CTOO) or Tim Heier owns the specific client-facing AI initiatives referenced in Option A — needs direct confirmation before targeting either with a specific pitch.

**Added 2026-10-23 (not resolvable from public sources):**
- Whether Sean Law's June 24 LinkedIn message was ever answered. The plan's entire sequencing assumption depends on this and it is not recorded anywhere in this document.
- ~~Current status of the two open CRM opportunities (Brian Matheny ID role, Joe Jackson backfill).~~ **Resolved 2026-10-23 (Dataverse re-pull):** both closed lost. Loss reasons are not recorded in the opportunity-level pull; ask Derek Nwamadi.
- The counterparty on the $633M multi-year software license agreement disclosed in Q2 2026. No public source names the vendor. This is now the highest-value open question in the partner section.
- Whether Tim Heier remains Schwab's CTO. No contrary evidence found, but his tenure was not independently re-verified this pass.
- Which organization owns Charley, and by extension who the delivery-side buyer is for agent governance work. Charley shipped on 2026-09-30 with no named executive owner in public materials.
- The commercial terms and internal sponsorship of the Anthropic partnership: whether it was signed in Advisor Services, in the Office of the CTO, or at corporate strategy level under Sudan. This determines whether Sudan is a buyer or a bystander for AI work.
- Whether the India capability center expansion to 2,000 by 2027 is additive headcount or substitution for contractor spend. The answer changes the competitive positioning materially.

---

## Sources

- [Charles Schwab 2025 10-K (SEC filing)](https://content.schwab.com/web/retail/public/about-schwab/SEC_Form10k_2025.pdf)
- [2026 Institutional Investor Day Presentation](https://content.schwab.com/web/retail/public/about-schwab/2026_Institutional_Investor_Day.pdf)
- [Schwab touts AI as its biggest growth lever — InvestmentNews](https://www.investmentnews.com/fintech/schwab-touts-ai-as-its-biggest-growth-lever-at-investor-day/266613)
- [Schwab CEO Says AI Will Serve Below-$1M Clients — Yahoo Finance](https://finance.yahoo.com/sectors/technology/articles/schwab-ceo-says-ai-serve-140000658.html)
- [Schwab Reports Record 4Q and Full Year 2025 Results](https://pressroom.aboutschwab.com/press-releases/press-release/2026/Schwab-Reports-Record-4Q-and-Full-Year-2025-Results/default.aspx)
- [Charles Schwab CIO role expanded — CIO Dive](https://www.ciodive.com/news/charles-schwab-expands-cio-role/811019/)
- [Leadership | Charles Schwab (Executive Council, live fetch)](https://www.aboutschwab.com/leadership)
- [Dennis Howard — About Schwab](https://www.aboutschwab.com/dennis-howard)
- [Nikhil Sudan — About Schwab](https://www.aboutschwab.com/nikhil-sudan)
- [Tim Heier — ZoomInfo](https://www.zoominfo.com/p/Tim-Heier/1161209388)
- [Sean Law — LinkedIn](https://www.linkedin.com/in/seanmylaw/)
- [Don Yuan — LinkedIn](https://www.linkedin.com/in/donyuan/)
- [Charles Schwab selects Microsoft Azure — AppsRunTheWorld](https://www.appsruntheworld.com/customers-database/purchases/view/the-charles-schwab-corporation-united-states-selects-microsoft-azure-cloud-services-for-application-hosting-and-computing-services)
- [Charles Schwab selects Amazon EC2 — AppsRunTheWorld](https://www.appsruntheworld.com/customers-database/purchases/view/the-charles-schwab-corporation-united-states-selects-amazon-ec2-for-application-hosting-and-computing-services)
- Charles Schwab Cloud Data Platform Engineer / Cloud Data Engineer job postings (The Muse, Dice, ZipRecruiter — GCP/Snowflake references)
- [Confluent Current 2024 archive — Kafka event-streaming session referencing Schwab](https://current.confluent.io/archive/2024/austin)
- Existing hand-built plan: `accounts/Schwab/account-plan.md` (read in full for context; independently re-verified, not copied)
- Internal: M365 email/calendar query surfacing Dynamics CRM opportunity-notification emails (Zigatta/Improving Enterprises assignment, SOW records, opportunity-won/created alerts)
- **[2026-07-21 validation pass]** Improving Dynamics CRM — direct account record query for "Charles Schwab & Co" (account, opportunities, Hand-Raisers, AI-generated revenue summary)
- **[2026-07-21 validation pass]** LinkedIn (authenticated) — direct profile and mutual-connections checks for Dennis Howard (both profiles), Tim Heier, Nikhil Sudan, Sean Law, Don Yuan, Sarah Wolf
- **[2026-10-23 CRM re-pull]** Improving Dynamics CRM — Dataverse Web API opportunity pull for "Charles Schwab & Co" (accountid 3558854e-073a-e411-b893-6c3be5a8f660): cumulative won now $2,663,824 (17 of 24, 71%); Matheny and Joe Jackson backfill both closed lost; Andraya Goodwin extension won 2026-10-21 ($109,200); one open opportunity (Julie King extension, $104,000, est. close 2026-11-29)
- **[2026-10-23 offering-grounding pull]** Improving SharePoint, Office of the Chief Consulting Officer site, opened and quoted verbatim:
  - `General/Sales Support/Sales Offerings/Specific Offerings/AI Offerings/AI Innovation Lab Offering.docx`
  - `General/Sales Support/Sales Offerings/Specific Offerings/Data Enablement/Data Enablement Engagement.docx`
  - `General/Sales Support/Sales Offerings/Specific Offerings/Application Modernization/Application Modernization - Internal Delivery Guide.docx`
  - `General/Sales Support/Sales Offerings/Specific Offerings/AI Offerings/Code Explorer/Code_Explorer_Delivery_Guide.docx`
  - `General/Sales Support/Sales Offerings/Specific Offerings/AI Offerings/AI Software Engineering - Transformation/AI Team Transformation.docx`
  - `General/Presentations/Reference-IP/AI Governance Control Plane - Client One-Pager.pdf` (July 2026)
  - `General/GMS Materials/Microsoft GMS Offerings/Embedded Delivery Capacity/2026-09-18 Embedded Delivery Capacity Offering Outline.md` (status: draft; basis for the Option A correction)
  - `General/GMS Materials/Global GMS Offerings/Information Security Strategy/2026-09-29 Information Security Strategy Executive Summary.md` (capacity flag Red; basis for marking security-led plays aspirational)

### Sources added in the 2026-10-23 refresh

**Primary filings (SEC EDGAR, CIK 0000316709)**
- [Q3 2026 earnings release, Form 8-K Exhibit 99.1, filed 2026-10-15](https://www.sec.gov/Archives/edgar/data/316709/000031670926000035/a3q26exhibit991.htm): record $7.2B net revenue, Charley, Anthropic partnership, Schwab Crypto expansion, single stock futures
- [Q2 2026 earnings release, Form 8-K Exhibit 99.1, filed 2026-07-21](https://www.sec.gov/Archives/edgar/data/316709/000031670926000027/a2q26exhibit991.htm): Schwab Crypto launch, $633M multi-year software license, $792M quarterly capex
- [Form 10-Q, filed 2026-08-07](https://www.sec.gov/Archives/edgar/data/316709/000031670926000031/0000316709-26-000031-index.htm)
- [EDGAR filing index for Charles Schwab Corp](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000316709&type=8-K&dateb=&owner=include&count=20): used to confirm no Item 5.02 executive change 8-K after 2026-01-29
- [Form 4 filing, 2026-08-18](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000316709&type=4&dateb=&owner=include&count=10): confirms Dennis Howard was a Section 16 reporting officer as of August 2026

**Schwab announcements and trade press**
- [Schwab press release: "Meet Charley, Schwab's New AI-Powered Assistant," 2026-09-30](https://pressroom.aboutschwab.com/)
- [Reuters: Anthropic targets financial advisers with new Claude tool, 2026-09-14](https://www.reuters.com/technology/anthropic-targets-financial-advisers-with-new-claude-tool-2026-09-14/)
- [Forbes: Anthropic Launches Claude For Advisors With Schwab And BlackRock, 2026-09-16](https://www.forbes.com/)
- [Barron's: Anthropic Targets Wealth Management With New AI Tools and Schwab Partnership, 2026-09-14](https://www.barrons.com/)
- [American Banker: Schwab blocks unauthorized AI agents, points clients to Charley, 2026-10-15](https://www.americanbanker.com/)
- [WSJ: AI Agents Trading Stocks While You Sleep? Charles Schwab's CEO Is Skeptical, 2026-10-18](https://www.wsj.com/)
- [The Block: Schwab to add Solana, Avalanche and Chainlink, 2026-08-27](https://www.theblock.co/)
- [CryptoRank: Schwab opens Bitcoin and Ethereum transfers, 2026-10-17](https://cryptorank.io/)
- [Reuters: Charles Schwab to scale India centre workforce to 2,000 by 2027, 2026-08-19](https://www.reuters.com/)
- [Wealth Management: Schwab Sells Forge Trust to Alto in Private Markets Deal, 2026-10-07](https://www.wealthmanagement.com/)
- [RIABiz: Schwab creates organization for Neesha Hathi, 2026-01-29](https://riabiz.com/)
- [CIO Dive: Charles Schwab taps CIO to lead new tech, operations unit, 2026-01-30](https://www.ciodive.com/news/charles-schwab-expands-cio-role/811019/)

**Research method note.** WebSearch was unavailable in this session (the tool returned a search_unauthorized error on every call). All deltas above were therefore gathered by direct fetch of SEC EDGAR filing indexes and exhibits, plus Google News RSS query feeds used as a discovery layer. Every claim in this refresh traces to a filing or a dated article; no claim rests on the RSS headline alone. Where a vendor or fact could not be confirmed from a primary source, it is labeled as inference or listed as an open item rather than asserted.

