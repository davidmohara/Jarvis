---
purpose: Staging area for source proposals awaiting David's yes/no approval
gate: David must explicitly approve before any source moves to sources.yaml
updated: 2026-08-03
---

<!-- system:start -->
# Watchtower — Proposed Sources

This file is the only path to `sources.yaml`. Watchtower's weekly run appends new proposals here. David reviews, says yes or no per row, and Rigby moves approved entries to `sources.yaml`.

**Nothing in this file is active.** Active sources live in `sources.yaml` only.

---

## Approval Queue

<!-- Weekly run appends proposals below this line. Format:
| Name | URL | RSS | Topic | Trust | Why Relevant | Status |
|------|-----|-----|-------|-------|--------------|--------|
-->

### Batch 7 — Weekly Run (2026-08-10)

| Name | URL | RSS | Topic | Trust | Why Relevant | Status |
|------|-----|-----|-------|-------|--------------|--------|
| CyberArk Blog | https://www.cyberark.com/resources/blog/ | https://www.cyberark.com/resources/blog/feed/ | ai-agentic | high | Published "AI Agents and Identity Risks: How Security Will Shift in 2026" — primary source on non-human identity lifecycle management for AI agents. CyberArk (now part of Palo Alto after $25B acquisition) is the market standard for privileged access management and is publishing the most actionable agent identity guidance available. No comparable PAM/NHI source in current registry. | approved |
| Cloud Security Alliance Research | https://cloudsecurityalliance.org/research | https://cloudsecurityalliance.org/feed | ai-agentic | high | Published the definitive NHI governance whitepaper (Non-Human Identity Governance Vacuum) and the CISO note on AI agent governance framework gaps cited in W33 themes. Primary research org for enterprise AI security standards. Distinct from vendor blogs — independent, practitioner-verified. No CSA source currently in registry. | rejected |

### Batch 6 — Weekly Run (2026-07-27)

| Name | URL | RSS | Topic | Trust | Why Relevant | Status |
|------|-----|-----|-------|-------|--------------|--------|
| The New Stack | https://thenewstack.io | https://thenewstack.io/feed/ | it-consulting | high | Broke the AWS $1B forward-deployed engineering story this week and published the enterprise AI model routing analysis on Microsoft's MAI strategy. Consistent practitioner-level coverage of the delivery model shift. Fills a gap between Gartner (analyst) and Stratechery (strategic) with technical implementation depth. | rejected |
| Forward Deployed (Noah Brier) | https://www.forwarddeployed.com | https://www.forwarddeployed.com/feed | it-consulting | high | Substack dedicated to the intersection of AI, software development, and enterprise deployment. Directly tracks the FDE trend that drove W31's biggest theme. FDE job postings grew 729% YoY (643 to 5,330 Apr 2025 to Apr 2026). No comparable source in current registry focused specifically on embedded delivery models. | rejected |
| FinOps Foundation Blog | https://www.finops.org/updates/all-updates/ | https://www.finops.org/feed/ | it-consulting | high | The authoritative source for FinOps practice evolution. Published the 2026 State of FinOps report showing 98% of FinOps teams now manage AI spend and AI cost management is the #1 desired skillset. Directly relevant to the OpenAI token pricing shift and agent spend governance gap surfaced in W31. | rejected |
| The New Stack — AI | https://thenewstack.io/category/ai-ml/ | https://thenewstack.io/category/ai-ml/feed/ | ai-agentic | high | (Scoped feed for AI/ML coverage only from The New Stack. If the top-level feed is approved, this is redundant — note for David's review.) Technical depth on agentic AI architecture, agent security, and enterprise deployment patterns. Published the enterprise AI model routing analysis that frames the Microsoft MAI vs. OpenAI story. | rejected |
| Okta Newsroom / Security Blog | https://www.okta.com/blog/security/ | https://www.okta.com/blog/security/feed/ | ai-agentic | high | Published "AI Agents at Work 2026" — the most cited enterprise agent security dataset this week (53% out-of-scope, 47% security incident, 24.4% visibility). Okta is now a primary data source for agent identity and governance. RSS feed unverified — confirm on first run. | rejected |

### Batch 5 — Weekly Run (2026-07-20)

| Name | URL | RSS | Topic | Trust | Why Relevant | Status |
|------|-----|-----|-------|-------|--------------|--------|
| Oliver Patel — Enterprise AI Governance | https://oliverpatel.substack.com | https://oliverpatel.substack.com/feed | ai-agentic | high | Biweekly Substack compiling 80+ authoritative resources on agentic AI governance. Published the definitive resource guide on proportional governance this week — directly tied to W30 governance theme. No comparable governance-practitioner source in current registry. | rejected |
| The Texas Energy and Power Newsletter | https://www.texasenergyandpower.com | https://www.texasenergyandpower.com/feed | texas-regional | high | Weekly Substack covering Texas grid policy, ERCOT developments, clean energy, and utility regulation. Directly tracks the Abbott/PUC/ERCOT data center policy story and the large-load interconnection queue. Fills a dedicated grid-policy gap that Texas Tribune covers only occasionally. | rejected |
| Utility Dive | https://www.utilitydive.com | https://www.utilitydive.com/feeds/news/ | texas-regional | high | Leading trade publication for electric utility sector — broke the Texas 438 GW queue approval story this week. Covers grid interconnection policy, ERCOT regulatory actions, and data center power policy at a depth no other active source matches. | rejected |
| Gravitee — State of AI Agent Security | https://www.gravitee.io/blog | https://www.gravitee.io/blog/rss.xml | ai-agentic | med | Published the State of AI Agent Security 2026 Report (900+ exec/practitioner survey). Covers API security, agent identity, and governance gaps at a technical-practitioner level. Complements Gartner's governance analysis with field data. RSS feed unverified — confirm on first run. | rejected |
| CIO Dive | https://www.ciodive.com | https://www.ciodive.com/feeds/news/ | it-consulting | high | Industry publication covering CIO-level technology decisions, enterprise software, and AI governance. Broke the Gartner $234B SaaS agentic arbitrage story this week. High editorial bar, practitioner-focused, consistent publication cadence. Fills a gap between Gartner Newsroom (announcements only) and Stratechery (strategic analysis). | approved |

### Batch 4 — Weekly Run (2026-07-13)

| Name | URL | RSS | Topic | Trust | Why Relevant | Status |
|------|-----|-----|-------|-------|--------------|--------|
| Fast Company — Work Life | https://www.fastcompany.com/work-life | https://www.fastcompany.com/section/work-life/rss | it-consulting | high | Published the McKinsey layoffs warning analysis this week. Covers consulting talent model disruption, leadership and org design, and AI in the workplace at a practitioner-friendly level. Fills the business-culture layer between analyst reports and technical coverage. | rejected |
| Kai Waehner | https://www.kai-waehner.de/blog | https://www.kai-waehner.de/blog/feed | ai-agentic | high | Independent practitioner and Principal Technologist at Confluent. Published the 2026 Enterprise Agentic AI Landscape analysis on trust, flexibility, and vendor lock-in this week. Highly technical, architecture-level signal on agentic AI deployment decisions. No comparable practitioner-perspective source currently in registry. | rejected |
| Latitude Media | https://www.latitude.media | https://www.latitude.media/feed | texas-regional | high | Broke the ERCOT large-load queue quadrupling story surfaced in this week's themes. Covers energy infrastructure at the intersection of technology and grid policy. Directly relevant to Texas AI data center and power grid developments that matter for David's clients. | rejected |
| E&E News (POLITICO) | https://www.eenews.net | https://www.eenews.net/rss | texas-regional | high | Surfaced in the Abbott/ERCOT Texas data center grid analysis. Credible energy and environment policy coverage with a strong Texas angle. Published the "Texas governor talks tough on data centers" piece this week. Relevant for regulatory intelligence on the grid policy story. | rejected |
| Outsource Accelerator | https://www.outsourceaccelerator.com | https://www.outsourceaccelerator.com/feed | it-consulting | med | Covers IT services market dynamics, global delivery models, and the impact of AI on consulting and outsourcing. Published McKinsey layoffs AI consulting analysis this week with practitioner framing on talent repricing. Useful signal layer for competitive delivery model intelligence. | rejected |

### Batch 3 — Weekly Run (2026-07-06)

| Name | URL | RSS | Topic | Trust | Why Relevant | Status |
|------|-----|-----|-------|-------|--------------|--------|
| Matterfact | https://www.matterfact.com | https://www.matterfact.com/feed | it-consulting | high | Podcast newsletter focused specifically on IT services vs AI — covers consulting business model disruption, billable-hour breakdowns, and delivery model transformation. Surfaced the "Accenture model on trial" framing this week. High signal, consulting-specific. | rejected |
| Data Center Knowledge | https://www.datacenterknowledge.com | https://www.datacenterknowledge.com/rss.xml | texas-regional | med | Industry publication covering data center infrastructure, power, and policy. Published a Texas AI data centers coverage hub (power, policy, progress) that directly covers the Abbott/ERCOT regulatory developments David's clients need to understand. | rejected |
| Future of Consulting | https://futureofconsulting.ai | https://futureofconsulting.ai/feed | it-consulting | high | Dedicated to consulting industry AI transformation — specifically covers the delivery model bifurcation, billable-hours disruption, and outcome-based pricing. Surfaced the "Billions Spent, But the Old Pyramid Persists" analysis this week. No comparable source currently in registry. | rejected |
| AI Weekly | https://aiweekly.co | https://aiweekly.co/feed | ai-agentic | med | Alert-style newsletter covering AI business news with a strong consulting and enterprise lens. Surfaced McKinsey's 25% outcome-tied fee story and the billable-hours breakdown analysis this week. Fills a business-layer AI news gap between Import AI (technical) and Ben's Bites (product). | rejected |
| IBM Think | https://www.ibm.com/think | https://www.ibm.com/blogs/think/feed/ | it-consulting | high | IBM Consulting's editorial publication on business and technology transformation. Published the "forward deployed units" delivery model analysis this week — the IBM field model for scaling AI. High editorial bar, practitioner-focused, and directly competitive/complementary to Improving's delivery positioning. | rejected |

### Batch 2 — Weekly Run (2026-06-29)

| Name | URL | RSS | Topic | Trust | Why Relevant | Status |
|------|-----|-----|-------|-------|--------------|--------|
| MIT Technology Review — Making AI Work | https://www.technologyreview.com | https://www.technologyreview.com/feed | ai-agentic | high | MIT TR launched "Making AI Work" in Feb 2026 — a dedicated newsletter on applying LLMs and agentic AI across industries. High editorial standards, practitioner-focused, not hype-driven. Directly relevant to David's AI consulting conversations. | approved |
| BCG Insights (AI & Tech Services) | https://www.bcg.com/capabilities/artificial-intelligence | null | it-consulting | high | BCG's AI practice publishes primary research — the $200B agentic opportunity report, executive perspectives on AI and software futures. No RSS but search-based gather works. Essential for competitive intelligence on where the big firms are positioning. | approved |
| Stratechery | https://stratechery.com | https://stratechery.com/feed | it-consulting | high | Ben Thompson's analysis of how technology reshapes markets and business models — consistently the most rigorous strategic framing available for the AI/consulting bifurcation story. Not news; signal. | approved |
| AI Business Weekly | https://aibusinessweekly.net | https://aibusinessweekly.net/feed | ai-agentic | med | Daily newsletter written specifically for business leaders and executives — AI funding, product launches, enterprise deployments. 7 AM EST. Complements the technical depth of Import AI with executive-layer news. | rejected |
| Fort Worth Report | https://fortworthreport.org | https://fortworthreport.org/feed | texas-regional | high | Independent nonprofit local newsroom covering Fort Worth and Tarrant County. Broke the Wistron $761M AI facility story. Complements Dallas Innovates with west DFW coverage — the AllianceTexas corridor is now the AI infrastructure epicenter of the region. | rejected |

### Batch 1 — Weekly Run (2026-06-20)

| Name | URL | RSS | Topic | Trust | Why Relevant | Status |
|------|-----|-----|-------|-------|--------------|--------|
| AI Governance Institute | https://aigovernance.com/news | https://aigovernance.com/news/feed | ai-agentic | high | Publishes "AI Governance Weekly" — tracks agentic AI governance, enterprise rollback patterns, and regulatory frameworks. Directly feeds David's AI advisory conversations with clients. | approved |
| Turing Post | https://www.turingpost.com | https://www.turingpost.com/feed | ai-agentic | high | Regarded as the newsletter of record for AI governance, geopolitics, and open-source AI policy. High signal, low noise. Covers the "why this matters" layer above vendor news. | approved |
| Dallas Innovates | https://dallasinnovates.com | https://dallasinnovates.com/feed | texas-regional | high | Dedicated DFW innovation/tech coverage. Ranks DFW third nationally for tech job postings. Fills the local tech story gap that Dallas Morning News (search-only) misses on depth. | approved |
| Consulting Magazine | https://www.consultingmag.com | https://www.consultingmag.com/feed | it-consulting | med | Industry trade publication covering consulting firm news, M&A, delivery model trends, and market moves. Useful for tracking competitive landscape and mid-market bifurcation signals. | rejected |
| Agentic AI Institute | https://agenticaiinstitute.org | null | ai-agentic | med | Research-focused coverage of enterprise agentic AI adoption data (sourced the 72% production / 60% governance gap stats). No confirmed RSS but publishes regularly. Relevant for client-facing research grounding. | rejected |

---

## Approved — Moved to sources.yaml

### Batch 5 — Approved 2026-07-20

| Name | URL | Topic | Trust | Approved |
|------|-----|-------|-------|---------|
| CIO Dive | https://www.ciodive.com | it-consulting | high | 2026-07-20 |

### Batch 2 — Approved 2026-06-29

| Name | URL | Topic | Trust | Approved |
|------|-----|-------|-------|---------|
| MIT Technology Review — Making AI Work | https://www.technologyreview.com | ai-agentic | high | 2026-06-29 |
| BCG Insights (AI & Tech Services) | https://www.bcg.com/capabilities/artificial-intelligence | it-consulting | high | 2026-06-29 |
| Stratechery | https://stratechery.com | it-consulting | high | 2026-06-29 |

### Batch 1 — Approved 2026-06-20

| Name | URL | Topic | Trust | Approved |
|------|-----|-------|-------|---------|
| AI Governance Institute | https://aigovernance.com/news | ai-agentic | high | 2026-06-20 |
| Turing Post | https://www.turingpost.com | ai-agentic | high | 2026-06-20 |
| Dallas Innovates | https://dallasinnovates.com | texas-regional | high | 2026-06-20 |

### Batch 0 — Approved 2026-06-19

All 10 entries approved by David on 2026-06-19. Moved to `sources.yaml` with `status: active`, `added: 2026-06-19`.

| Name | URL | Topic | Trust | Approved |
|------|-----|-------|-------|---------|
| The Pragmatic Engineer | https://newsletter.pragmaticengineer.com | it-consulting | high | 2026-06-19 |
| Import AI (Jack Clark) | https://importai.substack.com | ai-agentic | high | 2026-06-19 |
| Ben's Bites | https://bensbites.beehiiv.com | ai-agentic | med | 2026-06-19 |
| Texas Tribune | https://www.texastribune.org | texas-regional | high | 2026-06-19 |
| Dallas Morning News — Business | https://www.dallasnews.com/business | texas-regional | med | 2026-06-19 |
| Gartner Newsroom | https://www.gartner.com/en/newsroom | it-consulting | high | 2026-06-19 |
| The Information | https://www.theinformation.com | ai-agentic | high | 2026-06-19 |
| Hacker News (top stories) | https://news.ycombinator.com | ai-agentic | med | 2026-06-19 |
| Axios Pro — Tech | https://www.axios.com/pro/tech-deals | it-consulting | med | 2026-06-19 |
| EOS Worldwide Blog | https://www.eosworldwide.com/blog | leadership | med | 2026-06-19 |

Also added by David as named sources (approved same session, 2026-06-19):

| Name | URL | Topic | Trust | Approved |
|------|-----|-------|-------|---------|
| Superhuman AI | https://www.superhuman.ai | ai-agentic | med | 2026-06-19 |
| The Rundown AI | https://www.therundown.ai | ai-agentic | med | 2026-06-19 |
| NVIDIA Newsroom | https://nvidianews.nvidia.com | ai-agentic | high | 2026-06-19 |
| OpenAI News | https://openai.com/news/ | ai-agentic | high | 2026-06-19 |
| Anthropic News | https://www.anthropic.com/news | ai-agentic | high | 2026-06-19 |
| xAI News | https://x.ai/news | ai-agentic | high | 2026-06-19 |
| Google DeepMind / Google AI Blog | https://blog.google/technology/ai/ | ai-agentic | high | 2026-06-19 |
| Meta AI Blog | https://ai.meta.com/blog/ | ai-agentic | med | 2026-06-19 |
| Microsoft AI Blog | https://blogs.microsoft.com/ai/ | ai-agentic | high | 2026-06-19 |

---

## Rejected

### Batch 6 — 2026-08-03

| Name | URL | Topic | Reason |
|------|-----|-------|--------|
| The New Stack | https://thenewstack.io | it-consulting | Rejected by David 2026-08-03 |
| Forward Deployed (Noah Brier) | https://www.forwarddeployed.com | it-consulting | Rejected by David 2026-08-03 |
| FinOps Foundation Blog | https://www.finops.org/updates/all-updates/ | it-consulting | Rejected by David 2026-08-03 |
| The New Stack — AI | https://thenewstack.io/category/ai-ml/ | ai-agentic | Rejected by David 2026-08-03 |
| Okta Newsroom / Security Blog | https://www.okta.com/blog/security/ | ai-agentic | Rejected by David 2026-08-03 |

### Batch 4 — 2026-08-03

| Name | URL | Topic | Reason |
|------|-----|-------|--------|
| Fast Company — Work Life | https://www.fastcompany.com/work-life | it-consulting | Rejected by David 2026-08-03 |
| Kai Waehner | https://www.kai-waehner.de/blog | ai-agentic | Rejected by David 2026-08-03 |
| Latitude Media | https://www.latitude.media | texas-regional | Rejected by David 2026-08-03 |
| E&E News (POLITICO) | https://www.eenews.net | texas-regional | Rejected by David 2026-08-03 |
| Outsource Accelerator | https://www.outsourceaccelerator.com | it-consulting | Rejected by David 2026-08-03 |

### Batch 5 — 2026-07-20

| Name | URL | Topic | Reason |
|------|-----|-------|--------|
| Oliver Patel — Enterprise AI Governance | https://oliverpatel.substack.com | ai-agentic | Rejected by David 2026-07-20 |
| The Texas Energy and Power Newsletter | https://www.texasenergyandpower.com | texas-regional | Rejected by David 2026-07-20 |
| Utility Dive | https://www.utilitydive.com | texas-regional | Rejected by David 2026-07-20 |
| Gravitee — State of AI Agent Security | https://www.gravitee.io/blog | ai-agentic | Rejected by David 2026-07-20 |

### Batch 3 — 2026-07-06

| Name | URL | Topic | Reason |
|------|-----|-------|--------|
| Matterfact | https://www.matterfact.com | it-consulting | Rejected by David 2026-07-06 |
| Data Center Knowledge | https://www.datacenterknowledge.com | texas-regional | Rejected by David 2026-07-06 |
| Future of Consulting | https://futureofconsulting.ai | it-consulting | Rejected by David 2026-07-06 |
| AI Weekly | https://aiweekly.co | ai-agentic | Rejected by David 2026-07-06 |
| IBM Think | https://www.ibm.com/think | it-consulting | Rejected by David 2026-07-06 |

### Batch 2 — 2026-06-29

| Name | URL | Topic | Reason |
|------|-----|-------|--------|
| AI Business Weekly | https://aibusinessweekly.net | ai-agentic | Rejected by David 2026-06-29 |
| Fort Worth Report | https://fortworthreport.org | texas-regional | Rejected by David 2026-06-29 |

### Batch 1 — 2026-06-20

| Name | URL | Topic | Reason |
|------|-----|-------|--------|
| Consulting Magazine | https://www.consultingmag.com | it-consulting | Rejected by David 2026-06-20 |
| Agentic AI Institute | https://agenticaiinstitute.org | ai-agentic | Rejected by David 2026-06-20 |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
