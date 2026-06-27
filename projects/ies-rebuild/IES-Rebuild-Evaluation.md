# IES Rebuild Evaluation
## From Proving Ground to Executive Platform — A Technical Evaluation
*Prepared for David O'Hara | June 27, 2026*

---

### Bottom Line Up Front
David's IES/Jarvis is the **proving ground** — a working specification for an executive agent platform tested in production for over a year. The rebuild is not a personal tool migration; it is an extraction of those validated designs into a durable, model-agnostic, multi-tenant **platform** that equips Improving executives across the organization, with a path to external client deployment.

The recommended target stack is: **LangGraph** (orchestration) + **Pydantic AI** (leaf agents) + **LiteLLM** (model routing) + **Postgres + pgvector** (state/memory/tenant isolation) + **Langfuse** (observability). What changes from the proving ground is scope: the platform must support the full evolution system (system and personal evolutions), a connector catalog for approved integrations, built-in task management with external sync, and row-level tenant isolation from day one in the schema.

A reliable single-tenant core is feasible in ~13–19 calendar weeks with a 2–3 person team. Multi-tenant platform delivery adds roughly 8–12 weeks. The real cost is not the framework — it is owning a software product with an evolution distribution pipeline, a connector catalog, and ongoing maintenance obligations.

---

### Project Intent and Origin

This document — and the two companion documents (BRD, Dev Plan) — were originally drafted to evaluate rebuilding David's personal IES/Jarvis assistant. During the evaluation process, a critical reframing occurred. That reframing is recorded here explicitly so future sessions do not revert to the original, narrower framing.

**What this rebuild is NOT:**
* A migration of David's personal assistant to a new technical stack
* A single-user tool replacement
* A project where OmniFocus, Obsidian, or any specific tool is assumed at the system level

**What this rebuild IS:**
* An extraction of the validated designs in David's IES into a durable, distributable **executive platform for Improving**
* A multi-tenant SaaS product from day one — David's instance is the reference tenant, not the end state
* The vehicle for equipping all Improving executives with an intelligent assistant, with a path to external client deployment

**Key architectural decisions settled during reframing:**

1. **Multi-tenancy is resolved, not optional.** The IES system documentation explicitly marks this as a resolved decision: shared infrastructure with tenant isolation. Standard SaaS model. It is not deferred to a future phase; the Postgres schema uses row-level security from Phase 0.

2. **The evolution system IS the distribution mechanism.** The existing IES system/personal evolution boundary (HTML comment block delineation in definition files) maps directly and powerfully onto the platform's tenancy model. System evolutions are shared code deployed to all tenants. Personal evolutions are per-tenant data, never overwritten. This is the mechanism for shipping new capabilities to N executives at once.

3. **No tool is assumed at the system level.** OmniFocus, Todoist, Obsidian, Slack — none of these are core platform assumptions. The platform defines abstract capability categories (task-management, calendar, crm, knowledge-base). Personal evolutions bind specific connector packages to those categories per executive. David's personal evolution selects OmniFocus; another executive's may select Todoist; a third may use the platform's built-in task management with no external connector at all.

4. **The connector catalog is already designed.** The existing IES system implements a connector catalog (connectors.ts) with manifest structure, audience filtering, min_evolution gating, and package signing. The rebuild replicates this in Python as a first-class platform component.

5. **David's IES is the proving ground.** Over a year of production use, ~197 logged corrections, and a fully articulated agent architecture make it the most valuable input to the rebuild — not a legacy system to be deprecated, but a working specification to be extracted and productized.

---

### Contents
1. The real problem
2. Framework landscape (June 2026)
3. Recommendation: a hybrid, not a single framework
4. Concept-by-concept replication
5. Evidence: what the error log proves
6. What leaving Cowork costs (and what it does not)
7. Server vs local: bucketing every IES capability
8. Multi-tenancy and the evolution boundary
9. Resources & feasibility (2–3 person team)
10. Game plan (strangler-fig migration)
11. Risks & honest caveats

---

### 1. The Real Problem
What IES is today is a working specification for an executive agent **platform**, expressed as a markdown OS that Claude Code/Cowork interprets at runtime. The conceptual model is production-proven: a Master router, specialist agents (Chief, Chase, Quinn, Shep, Harper, Rigby), a layered memory system, skills as gated procedures, an evolution system separating system-owned from personal content, a connector catalog for approved integrations, an error-tracking feedback loop, and workflow state machines.

None of that is Claude Code. Claude Code is simply the engine currently reading those files. Because the orchestration lives in prose, every behavior depends on a model re-reading and re-deciding each session. The platform goals — reliability, multi-tenancy, model-agnosticism, and extensibility to N executives — are all blocked by that single architectural fact.

The question is not “CrewAI or LangChain.” It is: which substrate lets the proven IES concepts be encoded as durable, testable, model-agnostic code and **distributed to N executives via the evolution system**, while keeping prose only where prose is genuinely the right representation (identity, voice, the personal knowledge layer)?

---

### 2. Framework Landscape (June 2026)
The space shifted materially in the last six months. The relevant facts for a model-agnostic, reliability-first rebuild:

| Framework | Model-agnostic | State / durability | License | Fit for IES |
| :--- | :--- | :--- | :--- | :--- |
| **LangGraph** | Yes (25+ providers) | First-class checkpointing, durable execution, pause/resume/branch/rollback | MIT | **Strong** — orchestration backbone |
| **Pydantic AI 1.0** | Yes (25+ providers) | Lighter; linear agents; type-safe at dev time | MIT | **Strong** — leaf agents & skills |
| **CrewAI** | Yes | No built-in checkpointing; coarse error handling | MIT | **Weak** — fails reliability bar |
| **OpenAI Agents SDK** | No (OpenAI only) | Built-in tracing/guardrails | MIT | **Disqualified** — not agnostic |
| **Google ADK** | Gemini-first | Early; Vertex-backed | Open | **Disqualified** — not agnostic |
| **AutoGen / AG2** | Yes | Maintenance mode (AG2 fork maturing); 20+ calls/interaction | MIT | **Weak** — cost & momentum |

*   **LangGraph** is the production standard for stateful, auditable agentic systems and has the largest verified enterprise deployment list (JPMorgan, Uber, BlackRock, Replit). Its abstraction — agents as nodes, conditional edges as routing, shared typed state persisted at each step — maps almost one-to-one onto IES. The cost is verbosity and a learning curve.
*   **Pydantic AI** reached 1.0 in April 2026 and is the default for type-safe agents: it catches agent-logic errors at development time and shows lower P95 latency and fewer errors under load than heavier stacks. It is MIT-licensed, so there is no cost or commercial restriction to ship it to a client. It is optimized for linear `input` -> `tools` -> `structured-output` agents — not top-level branching orchestration, which is why it sits at the leaf and LangGraph owns the branching. *(Note: The Sustainable Use License that the same vendor applies to its Logfire observability product does not touch the framework; confirm with legal before any client ship regardless.)*
*   **CrewAI** is the fastest prototype path but has no built-in checkpointing and coarse error handling — a direct conflict with the reliability requirement. The vendor SDKs (OpenAI, Google) are disqualified by the fully-model-agnostic mandate.
*   **LiteLLM** is the load-bearing piece for model-agnosticism: a router that sits beneath any framework and lets you swap or route models per task without touching business logic.
*   **Langfuse** (or LangSmith) supplies the observability layer IES has none of today.

---

### 3. Recommendation: A Hybrid, Not a Single Framework
No single framework is the answer. The strongest architecture pairs a durable orchestration core with typed leaf agents and a model router beneath both:

*   **LangGraph** — orchestration backbone. Master routing, workflow state machines, durable execution, audit trail. This is where reliability, scale, and portability come from.
*   **Pydantic AI** — leaf-level specialist agents and skills with typed inputs/outputs and fast iteration. MIT-licensed, so it ships to clients with no commercial restriction. LangGraph's prebuilt agents cover the same ground if you prefer a single framework; the tradeoff is weaker output typing, not licensing.
*   **LiteLLM** — model router beneath everything for true model-agnosticism and per-task routing.
*   **Postgres + pgvector** — typed state and memory. Keep markdown only where prose is the right representation: identity, voice, personal knowledge.
*   **Langfuse** — OpenTelemetry-native observability, eval traces, and the data backbone for the error-tracking loop.

This follows the standard production pattern: prototype the topology in a readable framework, then harden the production path in LangGraph. You have already done the prototype — IES itself is the working spec.

---

### 4. Concept-by-Concept Replication

| IES Concept | Replicates as | Difficulty | Notes |
| :--- | :--- | :--- | :--- |
| **Master router** | LangGraph supervisor + conditional edges | Easy | Routing rules become typed edges, not prose |
| **Specialist agents** | Pydantic AI agents in LangGraph subgraphs | Easy | One agent = one typed subgraph |
| **Skills (gated procedures)** | Typed Pydantic AI tools with validation guards | Easy–Med | Pre-flight gates become code preconditions |
| **Memory layers** | Postgres + pgvector, tenant-scoped via RLS | Medium | Working/episodic/semantic/personal as isolated tenant tables |
| **Workflow state machines** | LangGraph graphs | Easy | Native fit |
| **Evolution system** | Manifest-driven package engine; system/personal block merge | Medium–Hard | Core distribution mechanism; Rigby manages lifecycle |
| **Connector catalog** | Package registry with audience filtering, min_evolution gating, signing | Medium | Already in connectors.ts — replicate in Python |
| **Built-in task management** | Internal task store + external connector sync API | Medium | OmniFocus/Todoist are personal evolution connector choices |
| **Error-tracking loop** | Structured eval traces in Langfuse | Medium | Corrections become labeled eval datapoints |
| **Personal evolutions** | Per-tenant data layer; personal blocks survive system merges | Medium | System/personal boundary enforced at data model layer |
| **Jarvis voice/persona** | System prompt + eval suite | Easy | Pin behavior with regression evals |

*   **What is gained:** deterministic routing, typed state, testability, audit trails, model-swapping, true multi-tenancy, evolution distribution, and observability.
*   **What is lost:** the zero-ops simplicity of “it’s just markdown in a git repo.” Behavior changes require code + test + deploy. That is the explicit trade for reliability and scale.

---

### 5. Evidence: What the Error Log Proves
This is not theoretical. The IES error-tracking system holds ~197 logged corrections (149 current entries plus 48 compacted from April). Categorizing them by failure mode shows that over half are architectural — designed out by the rebuild — while the rest are judgment failures the rebuild enables you to fight but does not fix on its own.

| Failure Mode | ~Count | Rebuild Verdict | Why |
| :--- | :---: | :--- | :--- |
| `protocol-skip` | 64 | **Eliminated** | Gates and routing become code preconditions and typed edges, not prose rules to remember |
| `stale-cache` | 11 | **Eliminated** | Typed state + live reads end the “pulled once at boot, trusted all session” bug |
| `wrong-tool` / `tool-ignorance` / `auth` | 9 | **Mostly fixed** | Connector resolution becomes a typed registry; read-only tools fail at type boundary |
| `format-violation` (paths, branding) | 10 | **Mostly fixed** | Output routing becomes validated parameters, not recalled convention |
| `lazy-search` | 9 | **Partially fixed** | “N strategies before not-found” enforced as a tool wrapper |
| `surfaced-resolved-item` | 3 | **Fixed** | Resolved-loop state in Postgres prevents closed items re-surfacing |
| `wrong-assumption` | 41 | **NOT fixed** | Judgment failure — needs evals + model routing, not structure |
| `sloppy-read` / `bad-inference` | 9 | **NOT fixed** | Model reasoning quality; a graph engine does not read more carefully |
| `over-engineering` / `scope-creep` | 3 | **NOT fixed** | Code invites more elaborate solutions than markdown |

Roughly 100 of ~197 errors are structural — led by `protocol-skip`, the single largest bucket, which is the system having a documented rule and not following it. Today those rules live in prose a model is supposed to re-read each session; compliance is probabilistic. The repeat-offender pattern in the log proves it: the same hidden-directory miss was logged 3+ times with the note “no further occurrences are acceptable,” and it recurred. **Prose reminds; code enforces.**

The other ~55 errors are judgment failures. These are exactly why the eval dataset and per-task model routing are not optional add-ons but core scope. Today there is no way to catch a `wrong-assumption` regression except waiting for it to recur and logging it after the fact. That is the gap the eval suite closes.

The decisive point: **the error log is not just the argument for the rebuild — it is the acceptance test for it.** Every entry becomes a test case, so a fix stays fixed instead of recurring next month.

---

### 6. What Leaving Cowork Costs (and What It Does Not)
Today IES does not just run on Cowork — it lives inside it. Cowork is the conversational surface, the connector host, and the bridge to local apps. A rebuild must replace the platform, not only the agent logic.

| Cowork Capability | Real Loss? | Replacement |
| :--- | :---: | :--- |
| **Chat UI / desktop app** | Partial | Build or adopt a streaming chat front-end. Days, not weeks, with current scaffolding — but real work that does not improve the agent |
| **MCP connector hosting** | No | MCP is an open protocol; any host is a client. You inherit only the token/auth lifecycle, which is plumbing |
| **Document generation** (docx/pptx) | No | These are libraries (docx, python-pptx, openpyxl, LibreOffice). Run anywhere |
| **Branded output** | No | A template and stylesheet, not a runtime feature |
| **Scheduled tasks** | No | Cron is a solved problem |
| **Live artifacts** | No | A small web view hitting your own API |
| **Local-first / privacy guarantee** | Yes | A server-deployed, DB-backed system inverts `SYSTEM.md`'s first principle. This is a deliberate posture change, not a feature to rebuild |
| **Mac-native app control** | Yes (conditional) | Bound to local macOS execution, not to Cowork. Survives only if the agent runs on the Mac, or via a local sidecar (see Section 7) |

The corrected conclusion: most of what first looked like a Cowork loss is replaceable commodity work. The two genuine items are the local-first privacy posture and Mac-native app control — and the second is really a question of where the agent process runs, not which framework it uses.

---

### 7. Server vs Local: Bucketing Every IES Capability
The platform runs server-side. ~90% of IES capabilities are already cloud-backed and port directly: M365 (mail, calendar, SharePoint), Dynamics CRM (web API), Obsidian, WHOOP, Plaud, Clay, reMarkable sync, Reddit monitor, document generation, and scheduled tasks.

Capabilities currently local-only:

| Capability | Why Local Today | Platform Resolution |
| :--- | :--- | :--- |
| **OmniFocus** | No cloud API; osascript only | Optional connector package. David's personal evolution selects it; another exec may select Todoist or use built-in task management |
| **Todoist / other task tools** | Not currently wired | Optional connector package; built-in task management is the platform default |
| **Power BI extraction** | Browser scraping | Power BI REST API -- more reliable; retires tool-misuse errors |
| **Slack** | Local Desktop Commander | Slack API/MCP -- the local approach was the workaround |
| **Photos tagging** | osascript / local Photos SQLite | Optional connector package (Photos sidecar) for users who need it |

**The key platform principle: no tool is assumed at the system level.** Task management, note-taking, and Mac-local integrations are personal evolution choices delivered as connector packages from the catalog. The platform defines abstract capability categories (task-management, calendar, crm); personal evolutions bind those categories to specific connectors per executive.

Net: server mode works for ~90% of IES directly, improves several scraped integrations, and handles Mac-local capabilities through the connector catalog's optional package mechanism.


---

### 8. Multi-Tenancy and the Evolution Boundary
Multi-tenancy is a **resolved design decision**, not an optional future phase. The platform architecture is shared server infrastructure + Postgres row-level security + per-tenant personal evolution data. This is the standard SaaS model applied to an agent platform.

The system/personal evolution boundary — already proven in David's IES — is the load-bearing tenancy mechanism:

- **System evolutions:** Shared code and config deployed to all tenants. New agents, workflows, skills, and connector catalog entries ship via system evolution packages. Applied automatically for Improving-internal tenants; opt-in for external clients.
- **Personal evolutions:** Per-tenant data. Communication style, connector bindings (which task manager, which CRM adapter), scheduling rules, relationship context, workflow overrides. **Never overwritten by a system evolution.** Survive all upgrades intact.

Capability sharing works correctly at platform scale. A capability built once (e.g., a new Chase workflow for competitive analysis) is published as a system evolution and available to all tenants instantly, with versioning and rollback handled centrally. This is strictly better than the current file-distribution model.

**Rollout sequence (already designed):**
1. **Pilot:** David's instance as reference tenant. Curtis, Susan, Don as first additional tenants.
2. **Internal:** All Improving executives. System evolutions auto-apply.
3. **External:** Client deployments. Evolutions are gated (opt-in). Connector catalog filtered by `audience: external`.

The system/personal boundary does not just survive the rebuild — it becomes the product's core differentiator.

---

### 9. Resources & Feasibility (2–3 Person Team)
Estimates assume two strong Python/agent engineers plus a part-time architect/lead. Calendar weeks assume parallelization across the team.

| Phase | Scope | Calendar Time | Team Load |
| :--- | :--- | :---: | :--- |
| **0. Foundations** | Repo, LiteLLM, Postgres (RLS schema from day one), Langfuse, CI/eval harness | 2–3 weeks | 2 eng + lead |
| **0b. Eval dataset** | Convert ~197 error entries into structured test cases (parallel with Phase 0) | 1–1.5 weeks | 1 eng + lead |
| **1. Core orchestration** | Master router, Chief vertical slice, durable execution | 3–4 weeks | 2 eng |
| **2a. Remaining agents** | Chase, Quinn, Shep, Harper, Rigby — eval-gated | 4–6 weeks | 2 eng |
| **2b. Memory + skills + connectors** | Memory layers, typed skills, connector catalog, built-in task management | 2–3 weeks | 2 eng |
| **2c. Production run** | 10-day pilot with David's instance as primary; onboard first pilot tenants | 2 weeks | David + eng |
| **3. Multi-Tenant Platform** | Tenant isolation (RLS enforcement), Initialization Sequence, evolution distribution engine, connector catalog UI, admin tools | 8–10 weeks | 2–3 eng |
| **4. External / Client** | Gated evolutions, client branding, external connector catalog | 4–6 weeks | 2 eng |

- Phase 0b runs parallel with foundations — one engineer on substrate, one mining the error log.
- Phases 2a and 2b run in parallel.
- **Single-tenant core (Phases 0–2c):** ~13–19 calendar weeks.
- **Multi-tenant platform (through Phase 3):** ~5–7 months total.
- **External/client-ready (Phase 4):** ~6–8 months total.

Skills needed: strong Python, LangGraph state-machine design, async/durable execution, Postgres + vector search + RLS, prompt/eval engineering, platform/devops.

Ongoing obligations: dependency upgrades, eval maintenance, evolution package authoring, connector catalog curation, infra. The markdown system has near-zero ops; this platform does not.

---

### 10. Game Plan (Strangler-Fig Migration)
Do not rewrite IES in one shot. Run the new core alongside the existing markdown system and migrate capability by capability, retiring the old path only once the new one has eval-verified parity.

1. **Stand up the substrate with RLS from day one.** LiteLLM + Postgres (tenant-isolated schema) + Langfuse + CI/eval harness. Establish the test discipline and tenancy model before any agent logic.
2. **Port one vertical slice end-to-end.** Daily briefing: Master → Chief → memory → output. Prove the pattern on a workflow used every day.
3. **Build the eval suite from the error log in Phase 0.** Convert each of the ~197 entries into a structured, machine-runnable test case before Phase 1 begins. This is the acceptance test the entire migration is measured against.
4. **Migrate agents one at a time, eval-gated.** Each agent ships only when its eval suite is green. Markdown IES stays live as fallback.
5. **Bring up pilot tenants during Phase 2c.** David's instance as reference tenant; Curtis, Susan, Don as first additional tenants. Validate isolation and evolution delivery in production before full internal rollout.
6. **Build and ship the evolution + connector catalog infrastructure in Phase 3.** This is what turns a working single-tenant system into a distributable platform. Do not start Phase 3 until Phase 2c gate is signed off.

---

### 11. Risks & Honest Caveats
*   **Scope boundary discipline.** The platform has four distinct delivery phases. Scope must be held at each gate. Pilot tenants in Phase 2c, not Phase 1.
*   **Framework churn.** LangGraph and Pydantic AI ship frequent changes. Pin versions at Phase 0; schedule upgrade sprints per phase.
*   **Dependency licensing.** Core stack is MIT (LangGraph, Pydantic AI, LiteLLM). Self-hosted Langfuse avoids the Sustainable-Use license. Confirm the full dependency tree with legal before Phase 4.
*   **Evolution merge complexity.** The system/personal block merge engine is non-trivial. Test extensively with real mixed files before any production evolution applies to pilot tenants.
*   **Multi-tenant data isolation.** RLS in Postgres is the right mechanism but requires disciplined schema design from Phase 0. Retrofitting it later is expensive.
*   **Loss of edit-by-prose agility.** Behavior changes require code + test + deploy. That is the accepted trade.
*   **Maintenance reality.** This is a software product with a database, deployment pipeline, evolution distribution, and connector catalog to maintain. Budget accordingly.

---
*Recommendation: begin with a Phase 0-1 spike on the daily-briefing slice using LangGraph + LiteLLM + Langfuse, with Postgres RLS-ready from the first schema migration. This validates feasibility at low cost while establishing the multi-tenant foundation before any tenant-unaware patterns harden into the codebase.*