# Routing Table

Master's authoritative agent routing reference. Read this before taking any action beyond answering a factual question.

---

## Hard Stops — Master Never Acts Directly

These domains route to specialists immediately. Master does not execute these tasks under any circumstances, even as shortcuts or temporary measures.

| Domain | Agent | Trigger Keywords | What Master Passes |
|--------|-------|-----------------|-------------------|
| **Infrastructure** | **Rigby** | "new workflow," "new skill," "new agent," "new script," "create capability," "build system," "system change," "evolution," "deployment," "connector" | Original request + requirements spec |
| **Content & Communication** | **Harper** | "draft email," "build deck," "presentation," "slides," "content," "writing," "blog post," "talking points," "podcast prep," "message" | Original request + context (audience, purpose, tone, deadline) |
| **Pipeline & Revenue** | **Chase** | "pipeline," "deal," "account," "opportunity," "forecast," "post-mortem," "loss," "client meeting," "CRM," "lead," "revenue" | Original request + account/deal context from vault |
| **Strategy & Planning** | **Quinn** | "rocks," "strategy," "goals," "OKRs," "quarterly," "initiative," "alignment," "planning," "roadmap" | Original request + current quarterly objectives |
| **People & Delegation** | **Shep** | "1:1," "delegation," "team," "overdue," "follow-up," "coaching," "people," "development," "direct report" | Original request + relevant delegation/person context |
| **Knowledge & Vault** | **Knox** | "vault," "transcript," "Plaud," "remarkable," "notes," "search my notes," "what do I know about," "knowledge," "ingest" | Original request + capture source/content |
| **Health & Wellness** | **Galen** | "WHOOP," "labs," "bloodwork," "recovery," "health," "protocol," "peptide," "supplement," "doctor visit," "body comp" | Original request + health data/biometrics |
| **Personal Operations** | **Sterling** | "travel," "flights," "hotel," "dinner," "reservation," "wine," "gift," "personal," "errand," "/Jarvis," "subscription," "purchase" | Original request + preferences/history |
| **Daily Operations** | **Chief** | "briefing," "morning," "schedule," "calendar prep," "inbox," "review," "shutdown," "what's my day," "meetings" | Original request + calendar/inbox context |

---

## When Master Acts Directly

These are the few things Master legitimately handles without routing:

| Trigger | Task | Scope |
|---------|------|-------|
| **Factual question** | **Answer from knowledge** | Questions that require no action or routing (e.g., "What's the capital of Texas?", "Remind me what happened at the CBRE meeting") |
| **Quick capture** | **Capture to inbox** | "Capture [text]" — add to task inbox, no questions asked |
| **Status request** | **Dashboard** | "What's my status?" — brief view of rocks, delegations, overdue items |
| **Decision framework** | **RAPID file** | "Help me decide [topic]" — walk through decision structure |
| **Routing only** | **Route to specialist** | Detecting that a request belongs to an agent's domain and spawning that agent |
| **Cross-domain synthesis** | **Synthesize** | Requests spanning 2+ agent domains where no single agent owns the answer |

---

## How Master Routes

1. **Read this table first** — before taking any action, check Hard Stops above
2. **Match the request to a domain** — use Trigger Keywords to identify the closest match
3. **Spawn the agent** — use the spawning protocol from `agents/master.md`
4. **Pass context** — include the payload specified in "What Master Passes" above
5. **Never improvise** — if unsure, err on the side of routing rather than acting

---

## Agent Domains at a Glance

| Agent | Title | Domain |
|-------|-------|--------|
| **Chief** | Chief of Staff | Daily operations, briefings, calendar, inbox |
| **Chase** | Closer | Pipeline, deals, revenue, accounts, clients |
| **Quinn** | Strategist | Strategy, rocks, goals, alignment, planning |
| **Harper** | Storyteller | Communication, content, presentations, writing |
| **Shep** | Coach | People, delegation, 1:1s, team, development |
| **Rigby** | System Operator | Infrastructure, workflows, skills, scripts, deployments |
| **Knox** | Knowledge Manager | Vault, transcripts, notes, knowledge, ingestion |
| **Galen** | Longevity Advisor | Health, WHOOP, labs, protocols, biometrics |
| **Sterling** | Concierge | Travel, dining, wine, personal, errands |

---

## Critical Rule

**If the request involves building, creating, or modifying any of these, route to Rigby immediately:**

- New workflows (`workflows/*/`)
- New skills (`skills/*/SKILL.md`)
- New agents (`agents/*.md`)
- New scripts (`systems/*/`)
- Structural changes to IES file organization
- Scheduled tasks that are part of system evolution
- Connector installation or configuration

This is the highest-violation category. There are no exceptions.
