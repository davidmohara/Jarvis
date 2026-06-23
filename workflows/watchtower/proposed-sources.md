---
purpose: Staging area for source proposals awaiting David's yes/no approval
gate: David must explicitly approve before any source moves to sources.yaml
updated: 2026-06-19
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

### Batch 2 — Approved 2026-06-22

| Name | URL | Topic | Trust | Approved |
|------|-----|-------|-------|---------|
| Dallas Fed — Economic Research | https://www.dallasfed.org/research | texas-regional | high | 2026-06-22 |

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

### Batch 1 — 2026-06-20

| Name | URL | Topic | Reason |
|------|-----|-------|--------|
| Consulting Magazine | https://www.consultingmag.com | it-consulting | Rejected by David 2026-06-20 |
| Agentic AI Institute | https://agenticaiinstitute.org | ai-agentic | Rejected by David 2026-06-20 |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

### Batch 2 — Weekly Run (2026-06-22)

| Name | URL | RSS | Topic | Trust | Why Relevant | Status |
|------|-----|-----|-------|-------|--------------|--------|
| MIT Technology Review — AI | https://www.technologyreview.com/topic/artificial-intelligence/ | https://www.technologyreview.com/feed/ | ai-agentic | high | Editorial-standard AI coverage with strong enterprise and governance angle. Covers the "why it matters" layer — not just model releases but deployment realities. Fills a gap between vendor news (already covered) and practitioner depth. | rejected |
| The Pragmatic Engineer (EU AI / Compliance beat) — via TLDL/AI Weekly | https://aiweekly.co | https://aiweekly.co/feed/ | ai-agentic | med | AI Weekly curates the week's best AI and ML news since 2015. Complements Import AI on the governance/compliance signal — specifically useful for tracking EU AI Act developments heading into August 2 deadline. | rejected |
| Deltek Clarity (Consulting Industry Report) | https://www.deltek.com/en/blog | https://www.deltek.com/blog/feed | it-consulting | high | Publishes annual consulting industry benchmark data and trend analysis. This week's source for consulting bifurcation data. Publishes regularly on project-based business economics — directly relevant for Improving's positioning. | rejected |
| Dallas Fed — Economic Research | https://www.dallasfed.org/research | https://www.dallasfed.org/api/rss/research | texas-regional | high | Federal Reserve Bank of Dallas publishes Texas economic outlook, regional labor data, and sector analysis monthly. Authoritative ground-truth for Texas market thesis. No competitor overlap in sources.yaml. | approved |
| Ahead of AI (Sebastian Raschka) | https://magazine.sebastianraschka.com | https://magazine.sebastianraschka.com/feed | ai-agentic | high | Practitioner-written ML/AI newsletter by a former Meta AI researcher. Covers model architecture, agentic systems, and enterprise AI with technical depth. Ranked among top RSS AI feeds for 2026. Complements Import AI without duplicating it. | rejected |
