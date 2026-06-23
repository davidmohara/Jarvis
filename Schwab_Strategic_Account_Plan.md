# Charles Schwab — Strategic Account Plan
**Improving | Prepared for: David O'Hara | June 2026**
**Classification: Internal — Business Development**

---

## Situation Summary

Improving has an active engagement at Charles Schwab in Instructional Design — not a core competency, but a valuable beachhead. A Master Service Agreement and contract vehicle are in place, which eliminates the most common barrier to starting new work. The objective of this plan is to leverage that access to land work in Data/AI and Software Engineering, where Improving has a genuine competitive advantage and Schwab has declared urgent, public strategic intent.

Schwab's CEO has called AI "the most significant growth opportunity in the company's history." Their 2026 Investor Day committed to shipping multiple client-facing AI products this year. Their technology organization just restructured under a single executive covering technology, operations, and data. The window is open and the timing is right.

**Goals:**
- Short-term (90 days): Identify and close a scoped SOW in Data/AI or Software Engineering
- Long-term (12–24 months): Establish Improving as a preferred implementation partner across Schwab's AI and data platform engineering orgs

---

## Schwab's Strategic Technology Priorities (2026)

These are drawn from their FY2025 10-K, 2026 Institutional Investor Day materials, and public press releases.

### 1. AI at Scale — Client-Facing and Internal
Schwab launched its first generative AI retail product (Portfolio Insights) in May 2026, combining portfolio performance data, market news, and research commentary into a single client view. A voice/chat AI assistant for common service requests rolls out summer 2026. An AI-driven research platform for markets is in internal beta. Internally, their Schwab Knowledge Assistant hit 90% employee adoption growth in 2024.

### 2. Data Platform Modernization
Post-TD Ameritrade integration (17M+ accounts migrated, $1.3T in assets transitioned), Schwab is rationalizing data centers, decommissioning duplicate systems, and consolidating disparate data architectures — including merging Schwab's static holdings data with TDA's high-frequency behavioral data. "Books and records modernization" and real-time data pipelines are explicitly cited priorities.

### 3. Application Modernization
Platform rationalization continues post-integration. APIs for RIAs and fintechs are expanding. Personalized Indexing (iRebal) and digital lending are active investment areas. A public job posting for a Director of Software Development & Engineering (Portfolio Management Technology) specifically calls out migrating from legacy development to "GenAI- and agentic-AI-driven development."

### 4. Serving the Under-$1M Client Segment with AI
CEO Rick Wurster has stated AI will serve clients below the $1M threshold — Schwab's largest segment — in ways that weren't economically viable through human advisors. This is a product and engineering execution challenge.

### 5. Workforce AI Enablement
GitHub Copilot adoption is visible in engineering job postings. The Schwab Knowledge Assistant is their internal GenAI productivity tool. Schwab has been explicit about using AI to increase employee productivity without displacing workers.

---

## Improving's Competitive Positioning

Improving's advantage at Schwab is not scale — it's precision. We show up as practitioners who build production systems, not strategy decks. That positioning matters at Schwab because:

- **Azure is Schwab's confirmed primary cloud.** Improving's enterprise stack is Azure-native, including Azure OpenAI. We don't need to learn the environment.
- **Schwab's AI is likely built on Azure OpenAI.** Given their Azure infrastructure and Microsoft's first-mover window on OpenAI frontier models, this is the highest-probability inference. Improving can walk in as a partner who already knows the platform.
- **The Thrivent data integration story is a direct analog.** Improving helped Thrivent build the Thrivent Enterprise Integration Datastore (TEID) — consolidating multi-system data into a governed, real-time platform. Schwab just completed the largest brokerage data migration in history and is still rationalizing the resulting architecture. Same problem, proven pattern.
- **We bridge the research-to-production gap.** Schwab has strong internal data science capability (see contact profiles below). Their challenge is not ideation — it is engineering the infrastructure to make models run in production at scale. That is exactly what Improving does.

**Win-wire story to prepare:** The Thrivent TEID engagement. Have a clean one-page version ready before any technical meeting.

---

## Technology Leadership Map

### Dennis Howard — MD, Chief Technology, Operations & Data Officer
**Effective:** January 29, 2026
**Reports to:** Rick Wurster (CEO)

Howard's role was expanded from CIO to include operations and data, creating a single executive accountable for all three functions. He joined Schwab in 2014 from Visa, where he held CIO-level roles with deep background in enterprise systems, data and analytics, and client-facing product development.

This is the economic buyer for any meaningful AI or data engagement. His expanded mandate signals Schwab is treating technology and data as unified infrastructure — exactly the kind of consolidated accountability that makes cross-functional engagements easier to scope and sell.

**Approach:** Do not cold-reach Howard. Use warm intros from the contacts below to build credibility first. When you do reach his level, frame the conversation around platform modernization and AI engineering capacity — not a tool, not a product, not a methodology.

---

### Sean Law — Principal Data Scientist, Director — R&D, Office of the CTO & A.I. Council

**Background:**
Sean is a practitioner-researcher with 20+ years in data science and ML. He is the creator and core maintainer of STUMPY, a widely used open-source Python library for time series analysis (matrix profile, motif/anomaly discovery, semantic segmentation). He speaks at SciPy and PyData conferences and co-organizes PyData Ann Arbor. He came to Schwab through the TD Ameritrade acquisition, where he held senior data science roles and created patented technologies.

**What his role likely means:**
Sean sits in R&D within the Office of the CTO. He evaluates and prototypes new AI/data approaches before production — and then navigates the handoff from research to engineering. That last mile (getting models from notebooks into production systems at scale) is almost universally where this type of team hits friction.

He also knows exactly where the data debt from the TDA integration is buried — he lived it.

**Pitch angle:**
Lead peer-to-peer, not vendor-to-client. Reference STUMPY or a time series use case if anyone on the Improving team has used it — it signals you did your homework. Then:

> "We work with a lot of data science orgs where the bottleneck isn't the model itself — it's the engineering infrastructure around it. MLOps, pipelines, deployment patterns, observability. Given the breadth of what Schwab is shipping this year, I'd love to understand where that friction shows up for your team and whether there's a fit."

**What to avoid:** Don't mention the instructional design engagement as a credential. Don't lead with a capabilities list. Get him talking about a specific problem.

---

### Don Yuan — AI Transformation & Governance Leader, Charles Schwab (Plano, TX)

**Background:**
Don's LinkedIn headline is: *Driving AI Transformation & Governance | Delivering Strategic Agentic AI, Analytics, & Automation Solutions | Product, Program, and Portfolio Management.* His certifications include Microsoft Fabric Analytics Engineer, AWS Certified Data Analytics Specialty, AWS Certified Machine Learning Specialty, PMP, and PSM — a profile that spans both technical execution and delivery management.

Importantly, Don is not just a corporate practitioner — he is an active member of the DFW AI builder community. He has co-promoted AgentCon Dallas (part of the Global AI Community's AgentCon World Tour) for two consecutive years, most recently for the June 26, 2026 event. He posts about agentic AI frameworks, live demos, and real-world deployment patterns. This is someone who cares about building AI systems that actually work, not just managing the program around them.

**What his role likely means:**
Don sits at the intersection of AI strategy and delivery execution. His focus on *agentic AI* specifically is a meaningful signal — agentic systems (multi-step, tool-using AI workflows) are significantly harder to operationalize than simple LLM queries, and Schwab is heading directly into that territory with its planned AI assistant and automated client service capabilities. Don is likely the person responsible for making those systems land inside the organization: governance, delivery, adoption, automation infrastructure.

His pain is not ideation — it is turning agentic AI strategy into production systems that are reliable, governed, and scalable at Schwab's volume.

**Pitch angle:**
Lead peer-to-peer on agentic AI specifically — not a generic AI pitch. He is plugged into the practitioner community and will see through a surface-level conversation immediately. The opening:

> "I saw you're involved with AgentCon — that's the right conversation to be in right now. Agentic AI is where the real delivery complexity lives. We're working through exactly that with clients: how do you move from a demo that works in a sandbox to an agent that runs reliably in production, with proper guardrails, at enterprise scale? Given what Schwab is shipping this year, I'd love to understand where you're seeing that friction."

**Specific hooks:**
- **AgentCon Dallas** (June 26, 2026 — this Friday) — if timing allows, attending or referencing it shows you're in the same community, not pitching from outside it.
- **Microsoft Fabric** — his certification is directly relevant to Schwab's Azure-native data platform. Improving can come in as an experienced Fabric implementation partner.
- **AI governance** — his updated headline now leads with governance, which reflects a real maturation in how Schwab is thinking about AI risk. Responsible AI, auditability, and guardrails are as important to him as delivery speed.

**What to clarify before the meeting:** Confirm whether Don sits within the data science org (under Meena) or in a broader enterprise AI/automation function. His agentic AI focus suggests he may span both. Either way, the pitch above works — just adjust whether you emphasize data pipeline infrastructure or agent orchestration and governance.

---

## Contact Prioritization & Sequencing

| Priority | Contact | Entry Point | Goal |
|---|---|---|---|
| 1 | **Current ID sponsor** | Existing relationship | Warm intro to Sean Law and/or Don Yuan |
| 2 | **Sean Law** | Intro via ID sponsor or LinkedIn | Understand R&D pain points; position around research-to-production gap |
| 3 | **Don Yuan** | Intro via ID sponsor or LinkedIn | Understand delivery pain points; position around AI program throughput |
| 4 | **AI.x team head** | Via Sean Law or LinkedIn search (SF-based MD/SVP) | Access to the GenAI product build-out |
| 5 | **Director, Portfolio Management Technology Engineering** | Open role — hiring manager is the target | Direct entry into AI-driven application modernization |
| 6 | **Dennis Howard** | Via credibility built through 2–5 | Economic buyer; engage only after proof points are established |

---

## Opportunity Scenarios (90-Day Targets)

### Option A — GenAI Application Delivery Pod
Schwab is shipping multiple client-facing AI products in 2026 (Portfolio Insights, AI assistant, research platform). They are actively hiring AI engineers. Offer a dedicated engineering pod (2–3 engineers + technical lead) to accelerate a specific product feature or backlog.

**Entry pitch:** "We can put experienced Azure OpenAI engineers on your team within 30 days. What's the highest-priority AI feature that's waiting on engineering capacity?"

### Option B — Data Platform Modernization Sprint
Schwab's post-TDA data architecture still requires rationalization. Pitch a scoped 8–12 week engagement — discovery + build — for a specific data integration or pipeline problem. Lead with the Thrivent TEID story.

**Entry pitch:** "We've done this exact consolidation pattern before with another large financial services firm. An 8-week scoped engagement could take a specific integration problem off your backlog and give you a replicable pattern for the broader platform work."

### Option C — AI Developer Productivity Enablement
Schwab is adopting GitHub Copilot and internal GenAI tooling. Offer a practitioner-led enablement engagement — not training (that's ID), but embedded engineering coaching that measurably accelerates their teams' AI-assisted delivery. This bridges the current ID engagement into technical delivery without seeming like a hard pivot.

**Entry pitch:** "There's a real difference between having GitHub Copilot licenses and actually shipping faster. We embed engineers who help teams develop the habits and patterns that turn the tool into a delivery accelerator."

---

## Multi-Year Strategic Path

The goal is to become Schwab's go-to implementation partner for AI and data — sitting between their internal strategy and the hyperscalers. Improving's positioning: *we build the production-grade systems that turn Schwab's AI strategy into client-facing reality.*

| Phase | Timeline | Milestone |
|---|---|---|
| **Access** | Month 1–3 | Warm intro through ID sponsor → meeting with Sean Law and/or Don Yuan |
| **Prove** | Month 3–6 | Land one scoped SOW; execute flawlessly; embed a senior Improving engineer |
| **Expand** | Month 6–12 | 2–3 parallel workstreams; known entity in the AI Engineering and Data orgs |
| **Partner** | Year 2+ | Named preferred partner for AI/data implementation; positioned for enterprise engagements |

---

## Immediate Next Actions

1. **AgentCon Dallas is this Friday, June 26.** Don Yuan is actively promoting it. If you or someone from Improving can attend, do it — it's free, in Plano, and puts you in the room with Don on his turf, not in a formal sales meeting. Even if you can't attend, reference it when you reach out: "I saw you're involved with AgentCon this week — that's exactly the right conversation."
2. **Ask the ID sponsor for warm intros to Sean Law and Don Yuan** — keep it casual. "We've been doing some interesting AI and data work and I'd love to connect with the right people."
3. **Research Dennis Howard on LinkedIn** — identify mutual connections; do not cold-reach him yet.
4. **Confirm Don Yuan's reporting relationship and exact function** before the meeting — ask the intro contact whether he sits in the data science org or a broader enterprise AI function.
5. **Prepare the Thrivent TEID win-wire story** — one page, outcome-focused, ready to share.
6. **Scan Schwab's open AI/engineering roles weekly** — job postings reveal current pain points and give fresh conversation hooks.
7. **Know which AI products are in-flight at Schwab** before any meeting — Portfolio Insights (live), AI voice/chat assistant (summer 2026), AI research platform (internal beta).

---

## Reference Sources

- [Charles Schwab 2025 Annual Report — CEO Letter](https://www.aboutschwab.com/annual-report-2025/ceo-letter)
- [2026 Institutional Investor Day Presentation](https://content.schwab.com/web/retail/public/about-schwab/2026_Institutional_Investor_Day.pdf)
- [Schwab touts AI as biggest growth lever — InvestmentNews](https://www.investmentnews.com/fintech/schwab-touts-ai-as-its-biggest-growth-lever-at-investor-day/266613)
- [Schwab Launches AI-Powered Portfolio Insights — Press Release](https://pressroom.aboutschwab.com/press-releases/press-release/2026/Charles-Schwab-Launches-AI-Powered-Capability-That-Helps-Investors-Understand-Portfolio-Performance-and-Market-Activity/default.aspx)
- [Schwab CIO expanded to lead Technology, Operations & Data — CIO Dive](https://www.ciodive.com/news/charles-schwab-expands-cio-role/811019/)
- [Dennis Howard — About Schwab](https://www.aboutschwab.com/dennis-howard)
- [Sean Law — LinkedIn](https://www.linkedin.com/in/seanmylaw/)
- [Don Yuan — LinkedIn](https://www.linkedin.com/in/donyuan/)
- [Improving Financial Services Capabilities](https://www.improving.com/toronto/financial-services/)
- [Schwab selects Microsoft Azure — AppsRunTheWorld](https://www.appsruntheworld.com/customers-database/purchases/view/the-charles-schwab-corporation-united-states-selects-microsoft-azure-cloud-services-for-application-hosting-and-computing-services)
- [Charles Schwab AI Strategy — Klover.ai](https://www.klover.ai/charles-schwab-ai-strategy-analysis-of-dominance-in-financial-services/)
