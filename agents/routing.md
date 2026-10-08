# Routing Table

Master's authoritative agent routing reference. Read this before taking any action beyond answering a factual question.

---

## Hard Stops — Master Never Acts Directly

These domains route to specialists immediately. Master does not execute these tasks under any circumstances, even as shortcuts or temporary measures.

| Domain | Agent | Trigger Keywords | What Master Passes |
|--------|-------|-----------------|-------------------|
| **Infrastructure** | **Rigby** | "new workflow," "new skill," "new agent," "new script," "create capability," "build system," "system change," "evolution," "deployment," "connector," "grade evals," "eval analysis," "eval dashboard," "eval trends" | Original request + requirements spec |
| **Git Operations** | **Rigby** | "commit," "push," "pull," "branch," "merge," "rebase," "stage," "stash," "tag," "changelog," "PR," "pull request," "git" | Original request + `skills/git/SKILL.md` as the execution path; Rigby runs every git command through that skill, never Master directly |
| **Domain-Data Inspection** | *owning agent* | "check the vault," "read the inbox," "inspect staging," "list tasks," "look at the pipeline," "any new recordings," or any read/modify of a specialist's domain data | Original request + which source to check; the owning agent (Knox, Chase, Chief, etc.) performs the read, not Master |
| **Content & Communication** | **Harper** | "draft email," "build deck," "presentation," "slides," "content," "writing," "blog post," "talking points," "podcast prep," "message" | Original request + context (audience, purpose, tone, deadline) |
| **Pipeline & Revenue** | **Chase** | "pipeline," "deal," "account," "opportunity," "forecast," "post-mortem," "loss," "client meeting," "CRM," "lead," "revenue," "card," "credit," "APR," "benefits," "rewards," "optimize," "spend" | Original request + account/deal context from vault |
| **Strategy & Planning** | **Quinn** | "rocks," "strategy," "goals," "OKRs," "quarterly," "initiative," "alignment," "planning," "roadmap" | Original request + current quarterly objectives |
| **People & Delegation** | **Shep** | "1:1," "delegation," "team," "overdue," "follow-up," "coaching," "people," "development," "direct report" | Original request + relevant delegation/person context |
| **Knowledge & Vault** | **Knox** | "vault," "transcript," "Plaud," "remarkable," "notes," "search my notes," "what do I know about," "knowledge," "ingest" | Original request + capture source/content |
| **Health & Wellness** | **Galen** | "WHOOP," "labs," "bloodwork," "recovery," "health," "protocol," "peptide," "supplement," "doctor visit," "body comp" | Original request + health data/biometrics |
| **Personal Operations** | **Sterling** | "travel," "flights," "hotel," "dinner," "reservation," "wine," "gift," "personal," "errand," "/Jarvis," "subscription," "purchase" | Original request + preferences/history |
| **Daily Operations** | **Chief** | "briefing," "morning," "schedule," "calendar prep," "inbox," "review," "shutdown," "what's my day," "meetings" | Original request + calendar/inbox context |

**The spawn-first rule.** Master is the coordinator, never an executor. For anything beyond the short list under "When Master Acts Directly," Master's only move is to spawn the named owning agent and let it do the work. Three prohibitions follow directly, and none has an exception:

1. **No direct git.** Master never runs a git command: no `git add`, `commit`, `push`, `pull`, `status`, `diff`, `reset`, or branch work. All git routes to **Rigby** via `skills/git/SKILL.md`. This covers session exit and every workflow's commit step (see `err-20260716T220729-FNAAP8`).
2. **No direct domain-data checks.** Master never inspects or modifies another agent's domain data to answer a request or to satisfy a workflow step: not the Plaud staging folder, not the vault, not the inbox, not the task system, not email. Master spawns the owning agent to read it (see `err-20260611T113806-g0pfoq`).
3. **No direct task execution.** Master never executes a workflow step, a skill, or a script inline. Every step is dispatched to the agent that owns it via an explicit spawn. The single documented exception is the boot context-load step that must land in Master's own live context (see `workflows/boot/workflow.md`); it is the only one.

---

## When Master Acts Directly

These are the few things Master legitimately handles without routing:

| Trigger | Task | Scope |
|---------|------|-------|
| **Factual question** | **Web lookups** | Questions that require no action or routing (e.g., "What's the capital of Texas?") |
| **Quick capture** | **Capture to inbox** | "Capture [text]" — add to task inbox, no questions asked |
| **Status request** | **Dashboard** | "What's my status?" — brief view of rocks, delegations, overdue items |
| **Decision framework** | **RAPID file** | "Help me decide [topic]" — walk through decision structure |
| **Routing only** | **Route to specialist** | Detecting that a request belongs to an agent's domain and spawning that agent |
| **Cross-domain synthesis** | **Synthesize** | Requests spanning 2+ agent domains where no single agent owns the answer |
| **Watchtower draft posting** | **Spawn Knox to run step-06** | Any request to post, send, or share a Watchtower draft/content candidate to Slack — Master spawns **Knox** (Watchtower's owning agent) with `workflows/watchtower/steps/weekly-step-06-publish-drafts.md` as the payload; Master does not run the step itself. Never ask for clarification about where to send it; #content (`C0B160MA3EK`) is the only authorized destination. |

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
