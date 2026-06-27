# IES Rebuild — Business Requirements Document
## Migrating Jarvis to a Distributed, Model-Agnostic, Multi-Tenant Executive Platform

* **Document Owner:** David O'Hara, Regional Director, Improving
* **Version:** 2.0
* **Date:** June 27, 2026
* **Classification:** Confidential
* **Status:** Pending Validation

---

> **Project intent:** See *IES-Rebuild-Evaluation.md* §"Project Intent and Origin" for the full context and reframing rationale that governs this document.

### Bottom Line Up Front
The IES rebuild migrates the proven Jarvis agent architecture from a single-user markdown OS into a durable, testable, model-agnostic **executive platform** serving Improving leaders. Target stack: **LangGraph** (orchestration) + **Pydantic AI** (leaf agents) + **LiteLLM** (model routing) + **Postgres + pgvector** (state/memory/tenant isolation) + **Langfuse** (observability).

David's current IES instance is the reference implementation. The platform is designed for rollout to all Improving executives (Pilot -> Internal -> External) using the evolution system as the distribution mechanism. The ~197 entries in the IES error log are the primary acceptance test dataset.

---

### Table of Contents
1. Purpose and Scope
2. Stakeholders
3. Business Goals
4. Functional Requirements
5. Non-Functional Requirements
6. Phase Gate Validation Criteria
7. Constraints and Assumptions
8. Risks
9. Glossary
10. Appendix A: Evolution System Specification
11. Appendix B: Connector Catalog Specification
12. Appendix C: LLM-as-Judge Protocol Specification
13. Appendix D: Data Migration Plan

---

### 1. Purpose and Scope

#### 1.1 Background
IES today is a working specification for an executive agent platform expressed as a markdown OS that Claude Code/Cowork interprets at runtime. The conceptual model is sound and production-proven: Master router, specialist agents, layered memory, skills as gated procedures, evolution system, connector catalog, and error-tracking feedback loop. The problem is the substrate: all behavior depends on a model re-reading and re-interpreting prose each session, making it non-deterministic, untestable, single-user by design, and locked to one runtime.

Evidence of the substrate problem is direct: the IES error-tracking system holds ~197 logged corrections, with protocol-skip (rules stated in prose that get ignored) as the single largest failure class at 64 entries.

#### 1.2 Scope

**In Scope:**
* All agent logic in agents/*.md (Master, Chief, Chase, Quinn, Shep, Harper, Rigby)
* All workflow state machines in workflows/*
* All skills in .claude/skills/*
* Memory architecture (working, episodic, semantic, personal layers)
* Evolution system (system and personal evolution engine, manifest processing, Rigby lifecycle management)
* Connector catalog (package registry, audience filtering, min_evolution gating, package signing)
* Built-in task management with external connector sync API
* Error-tracking and eval harness systems
* Multi-tenant platform infrastructure (Postgres RLS, Initialization Sequence, tenant onboarding)
* Training and progression system

**Out of Scope (deferred):**
* External customer-facing billing and auth for non-Improving users (Phase 4)
* Integration of net-new capabilities not currently in IES
* Voice output (V2+)

#### 1.3 Rollout Phases

| Phase | Audience | Scope |
| :--- | :--- | :--- |
| **Pilot** | David (reference tenant), Curtis, Susan, Don | Core system, 6 agents, single-tenant validation, evolution delivery |
| **Internal** | All Improving executives | Full platform, system evolutions auto-apply, connector catalog open |
| **External** | Improving clients | Gated evolutions (opt-in), external connector catalog, client branding |

---

### 2. Stakeholders

| Name / Role | Stake | Validation Authority |
| :--- | :--- | :--- |
| **David O'Hara** (Controller / Platform Owner) | Primary user; IP owner; reference tenant | Signs off on every phase gate. Ultimate arbiter of acceptance criteria. |
| **Improving Executives** (Pilot: Curtis, Susan, Don) | End users; early adopters | Validate platform usability, onboarding, and agent quality during pilot. |
| **Lead Engineer** | System delivery | Owns technical implementation, eval harness, and phase demos. |
| **Architect/Lead** | Design integrity | Reviews architecture decisions, licensing, and pattern consistency. |
| **Improving IT / Platform Admin** | Infrastructure and tenant provisioning | Manages server infrastructure, deployment pipeline, and tenant onboarding ops. |

---

### 3. Business Goals

| Goal | Problem Today | Target State | Success Metric |
| :--- | :--- | :--- | :--- |
| **G1: Reliability** | protocol-skip errors recur because rules live in prose. Same error class logged 3+ times. | Architectural rules enforced in code. Protocol skips become impossible, not improbable. | 0 protocol-skip errors in first 30 days of production use. |
| **G2: Determinism** | Same input produces different outputs across sessions. | Typed state, deterministic routing, audit trails. Replay any session from checkpointed state. | Identical inputs produce identical routing decisions in 100% of automated eval cases. |
| **G3: Model-Agnosticism** | System is locked to Claude/Cowork. Switching models requires rebuilding the surface. | LiteLLM router beneath all agents. Model swap requires one config change, zero code changes. | Successful execution of full daily-briefing on at least 2 different LLM backends. |
| **G4: Testability** | No way to catch regressions except waiting for them to recur in production. | Eval suite of 197+ test cases derived from error log. Every phase ships with green evals. | 100% of Phase 0 eval cases pass before Phase 1 begins. |
| **G5: Platform Distribution** | Insights and capabilities are locked to David's single instance. | Multi-tenant platform serving all Improving executives via the evolution system. New capabilities ship once and reach all tenants. | Pilot: 3 additional tenants operational with independent personal evolutions. Internal: all Improving executives onboarded. |

---

### 4. Functional Requirements

#### 4.1 Orchestration Layer (Master Router)
* **FR-01:** Master router must classify every incoming request and route it to the correct specialist agent using deterministic conditional edges in LangGraph.
    * *AC:* Given a set of 50 representative requests, routing decisions match expected agent assignment in 100% of cases.
* **FR-02:** Master router must persist full typed state at each node transition. State must be recoverable after process restart without data loss.
    * *AC:* Kill the process mid-workflow. Restart. Workflow resumes from last checkpoint with no data loss.
* **FR-03:** Master router must produce a structured audit trace for every request: input, routing decision, agent invoked, tools called, output, and latency.
    * *AC:* Langfuse trace exists for 100% of requests with all required fields.
* **FR-04:** Master must support configurable per-task model routing without code changes.
    * *AC:* Configure Chief to use Model A and Chase to use Model B. Langfuse traces confirm different models invoked.
* **FR-05:** All routing rules currently in agents/routing.md must be encoded as LangGraph conditional edges, not prose.
    * *AC:* Code review confirms no routing logic depends on prose interpretation.

#### 4.2 Specialist Agents
* **FR-06:** Each specialist agent (Chief, Chase, Quinn, Shep, Harper, Rigby) must be implemented as a Pydantic AI agent with typed inputs and outputs.
    * *AC:* Each agent rejects malformed inputs at the type boundary. Invalid inputs raise validation errors, not silent failures.
* **FR-07:** Chief (daily briefing, calendar, scheduling) must achieve functional parity with the current morning-briefing workflow as the Phase 1 vertical slice.
    * *AC:* Run morning-briefing end-to-end. Output rated acceptable by David on 5 consecutive days.
* **FR-08:** Each agent must be independently testable without other agents running.
    * *AC:* Execute Chief eval suite with all other agents offline. All Chief tests pass.
* **FR-09:** Chase (pipeline, sales, CRM) must integrate with Dynamics CRM via web API.
    * *AC:* Run pipeline-review workflow. Output matches expected format and data within 10% variance on numeric fields.
* **FR-10:** Quinn, Shep, Harper, and Rigby must achieve parity by end of Phase 2a.
    * *AC:* Each agent's eval suite passes. At least one representative workflow per agent executes end-to-end.

#### 4.3 Memory Architecture
* **FR-11:** All memory tables must be tenant-scoped via Postgres row-level security. A query from tenant A must never return data belonging to tenant B.
    * *AC:* Insert records for two tenants. Query from each tenant context. Zero cross-tenant results returned.
* **FR-12:** Working memory must be stored as typed Postgres records with session scoping. Markdown working memory files are retired.
    * *AC:* Write a working memory entry. Kill the session. Restart. Entry is retrievable with correct session ID and timestamp.
* **FR-13:** Episodic memory (meeting notes, daily reviews, decisions) must be stored in Postgres with full-text and vector search via pgvector.
    * *AC:* Write 10 episodic records. Run a semantic query. Top result matches expected entry. P95 query latency under 500ms.
* **FR-14:** Semantic memory (facts, knowledge, learned behaviors) must support embedding-based retrieval with similarity scoring.
    * *AC:* Query semantic memory with a natural-language question. Top-3 results with similarity scores are contextually relevant.
* **FR-15:** Identity and voice files (identity/*.md) remain as curated prose injected as context, not stored in the database.
    * *AC:* Identity files are read-only inputs. No agent writes to identity/* files. Confirmed by code review.

#### 4.4 Skills System
* **FR-16:** All skills in .claude/skills/ must be catalogued with: domain, agent owner, input/output schema, and pre-flight gate requirements.
    * *AC:* Skills manifest exists in code with full catalogue. 100% of current skills have an entry.
* **FR-17:** Skills must be implemented as typed Pydantic AI tools with validated inputs and outputs. Pre-flight checks must be enforceable gates, not optional prose.
    * *AC:* Invoke a skill with missing required inputs. System raises a validation error. Skill does not execute.
* **FR-18:** Skills must be versioned. Deploying a new skill version must not break existing invocations from tenants on prior versions.
    * *AC:* Deploy skill v2. Invoke v1 explicitly from a pinned tenant. v1 executes correctly.

#### 4.5 Evolution System
* **FR-19:** The platform must implement a manifest-driven evolution engine that applies system evolutions to all tenants while preserving personal evolution blocks.
    * *AC:* Apply a system evolution containing a merge-type file. Personal blocks survive unchanged. System blocks are updated. Evolution recorded in history.
* **FR-20:** System evolution packages must support four file actions: add, replace, merge, delete. Merge must parse, preserve, and re-inject all personal blocks.
    * *AC:* Run merge action on a file with 3 personal blocks. Post-merge: all 3 personal blocks present at correct logical positions. System content updated.
* **FR-21:** A delete action must halt if the target file contains personal blocks. User must review before deletion proceeds.
    * *AC:* Attempt to delete a file with a personal block. Process halts. User is presented with the conflict and resolution options.
* **FR-22:** Rigby must manage the full evolution lifecycle: validate manifest, snapshot current state, apply, verify personal block integrity, record history.
    * *AC:* Apply an evolution. Verify: pre-application snapshot exists, all personal blocks present post-apply, history.md updated.
* **FR-23:** Personal evolutions must survive all system evolution applications. Personal blocks must be immutable to system evolution actions.
    * *AC:* Apply 3 consecutive system evolutions to a file with personal blocks. All personal blocks intact after each application.

#### 4.6 Connector Catalog
* **FR-24:** The platform must implement a connector catalog (package registry) with: name, version (semver), source, description, audience (internal/external/all), min_evolution gating, and SHA-256 package signing.
    * *AC:* Submit a connector package. Catalog stores it with correct metadata. Signature validated on install.
* **FR-25:** Connectors must be filterable by audience. Internal connectors are not visible to external tenants.
    * *AC:* Query catalog from external tenant context. No internal-only connectors returned.
* **FR-26:** Connector installation must validate min_evolution compatibility before applying.
    * *AC:* Attempt install of a connector with min_evolution higher than the tenant's current level. Install rejected with clear error.
* **FR-27:** The connector catalog must support abstract capability categories (task-management, calendar, crm, knowledge-base). Personal evolutions bind specific connector packages to these categories per tenant.
    * *AC:* Tenant A's task-management is bound to OmniFocus. Tenant B's is bound to Todoist. Both execute "create task" successfully via their respective connectors.

#### 4.7 Built-In Task Management
* **FR-28:** The platform must provide a built-in task management system as the default task layer for all agents.
    * *AC:* Create, read, update, and complete tasks via the built-in system without any external connector installed.
* **FR-29:** The built-in task management system must expose an external sync API so optional connectors (OmniFocus, Todoist) can read and write tasks.
    * *AC:* Install OmniFocus connector. Create a task via the platform. Confirm task appears in OmniFocus. Modify in OmniFocus. Confirm sync back to platform.

#### 4.8 Eval Harness and Error Tracking
* **FR-30:** All ~197 entries in the IES error log must be converted to structured eval test cases before Phase 1 begins.
    * *AC:* Eval dataset contains >=197 structured cases, all machine-runnable, all tagged by failure mode.
* **FR-31:** The eval harness must execute against the running system and produce a pass/fail report by failure-mode class.
    * *AC:* Report shows counts by class. All protocol-skip cases pass. Judgment cases show current model accuracy baseline.
* **FR-32:** New error corrections from production must generate a draft eval case. A developer reviews and commits the case before it enters the required-passing set.
    * *AC:* Trigger an error correction. Draft eval case created automatically. Case does not enter required-passing set until developer commits it.
* **FR-33:** Eval results must be stored in Langfuse with traceability back to the specific test case, tenant, and system version.
    * *AC:* Each result is linked to a trace, test case ID, tenant ID, and system version tag.
* **FR-34:** Regression detection must be automated. Any eval case that was previously passing and begins failing must trigger an alert.
    * *AC:* Introduce a deliberate regression. Alert fires within one eval cycle.

#### 4.9 Multi-Tenant Platform
* **FR-35:** The platform must support tenant onboarding via an Initialization Sequence that interviews the executive, configures initial agent settings, and generates their personal evolution.
    * *AC:* Run Initialization Sequence for a new tenant. Personal evolution file created with role, goals, team, and rhythm data. Agent settings active on first session.
* **FR-36:** Each tenant must have isolated connector credentials. Tenant A's M365 credentials must never be accessible to tenant B.
    * *AC:* Code review confirms per-tenant credential scoping. Automated test confirms no cross-tenant credential leak under concurrent requests.
* **FR-37:** System capability updates must be deployable to all tenants without loss of personal evolution data or session continuity.
    * *AC:* Deploy a system evolution mid-session. Active session resumes. Personal evolutions intact. No capability regression in eval suite.
* **FR-38:** Platform admin tools must support: view tenant health, deploy system evolutions, view evolution history per tenant, manage connector catalog submissions.
    * *AC:* Admin can list all tenants with health status, trigger a system evolution deployment, and approve/reject a connector package submission.

#### 4.10 Training and Progression System
* **FR-39:** The platform must implement a progressive achievement model that guides new tenants through capability tiers.
    * *AC:* New tenant onboards via Initialization Sequence. System suggests first tasks (Morning Briefing, Inbox Processing) before advanced capabilities are introduced.
* **FR-40:** When a new agent or skill is deployed via system evolution, the training system must surface a contextual "Try the new [X]" prompt for the tenant.
    * *AC:* Deploy a new skill via system evolution. Tenant's next session includes a Try prompt for the new capability.

#### 4.11 Evolution and Deployment Pipeline
* **FR-41:** Git version control must be maintained for all system-owned code and config. All deployments must reference a specific commit SHA.
    * *AC:* Every deployment record includes a git commit SHA. Rolling back to a prior SHA restores prior system behavior.
* **FR-42:** Prompt files for all agents must be versioned in git. Prompt changes trigger a full eval suite run in CI.
    * *AC:* Modify a prompt file. CI pipeline runs associated agent eval suite automatically.

---

### 5. Non-Functional Requirements

* **NFR-01: Reliability - Durable Execution:** System recovers from process restart with zero data loss. Tested by forcibly terminating the process 10 times during active workflows.
* **NFR-02: Performance - P95 Response Latency:** Daily briefing workflow completes within 60 seconds P95. Memory queries complete within 500ms P95.
* **NFR-03: Model-Agnosticism:** Full daily-briefing slice executes successfully on at least 2 different LLM backends with no code changes.
* **NFR-04: Security - Data at Rest:** Postgres encrypted at rest. Credentials stored in environment variables or secrets manager. No credentials in code or config files.
* **NFR-05: Security - Tenant Isolation:** Row-level security enforced on all tenant-scoped tables. Confirmed by code review and automated cross-tenant query tests prior to pilot launch.
* **NFR-06: Observability:** 100% of agent invocations produce a Langfuse trace including: model, tokens, latency, input hash, output hash, tenant ID, and eval result when applicable.
* **NFR-07: Dependency Licensing:** All runtime dependencies are MIT or Apache 2.0 licensed. Confirmed by automated license scan in CI before Phase 4 (external distribution).
* **NFR-08: Maintainability - Test Coverage:** Unit test coverage >=80% for all orchestration and routing logic. Integration tests exist for all agent-to-connector paths.
* **NFR-09: Connector Resilience:** Non-critical connector failures (optional personal connectors) log a warning and allow workflow to continue. Critical paths (M365, Postgres) employ exponential backoff with circuit breaker.
    * *AC:* Simulate an optional connector failure during daily briefing. Briefing completes. Output notes connector unavailable. Langfuse records degraded status.
* **NFR-10: Privacy - Data Locality Documentation:** Architecture decision on server-side hosting is documented. Reversibility path documented for future assessment.

---

### 6. Phase Gate Validation Criteria

#### 6.1 Phase 0 Gate: Substrate and Eval Harness Ready
* **AC-P0-01:** LiteLLM router operational and proxies requests to at least 2 LLM backends.
* **AC-P0-02:** Postgres deployed with pgvector. Schema includes RLS policies on all tenant-scoped tables. CRUD operations succeed. Cross-tenant query returns zero results.
* **AC-P0-03:** Langfuse operational. Test trace visible in dashboard within 30 seconds of emission.
* **AC-P0-04:** Eval dataset contains >=197 structured test cases, all machine-runnable, all tagged by failure mode.
* **AC-P0-05:** Eval harness produces a pass/fail report organized by failure-mode class.
* **AC-P0-06:** Git repository initialized with dependency pinning and CI configured. Prompt file changes trigger eval suite in CI.
* **AC-P0-07:** Legacy memory data seeded into Postgres. Retrieval queries return contextually relevant results matching legacy definitions.

#### 6.2 Phase 1 Gate: Master + Chief Vertical Slice
* **AC-P1-01:** Master router classifies and routes 100% of a 50-request test set to the correct agent.
* **AC-P1-02:** Typed state persists at every LangGraph node. Process restart resumes workflow from last checkpoint.
* **AC-P1-03:** Morning briefing executes end-to-end and is rated acceptable by David on 5 consecutive days.
* **AC-P1-04:** All Phase 0 eval cases still pass. Chief-specific eval cases pass.
* **AC-P1-05:** Langfuse trace exists for every morning-briefing execution with full payload and metadata.
* **AC-P1-06:** Markdown IES still live as fallback. Both systems logging activity.

#### 6.3 Phase 2 Gate: Full Single-Tenant Core
* **AC-P2-01:** All 6 specialist agents have passing eval suites and at least one representative workflow executing end-to-end.
* **AC-P2-02:** Memory system operational across all layers. Tenant-scoped read/write confirmed. Cross-tenant isolation confirmed.
* **AC-P2-03:** Connector catalog operational. At least one connector package installed per abstract category. Personal evolution binding confirmed.
* **AC-P2-04:** Built-in task management operational. External connector sync API tested with at least one connector (OmniFocus or Todoist).
* **AC-P2-05:** Full eval suite (>=197 cases) passes. protocol-skip class: 100%. Overall: >=90%.
* **AC-P2-06:** System has operated as primary for 10 consecutive working days without fallback.

#### 6.4 Phase 3 Gate: Multi-Tenant Platform
* **AC-P3-01:** Pilot tenants (Curtis, Susan, Don) onboarded via Initialization Sequence. Each has independent personal evolution. Cross-tenant data isolation confirmed in production.
* **AC-P3-02:** System evolution successfully deployed to all pilot tenants. Personal blocks preserved for all tenants. Evolution history recorded per tenant.
* **AC-P3-03:** Connector catalog UI operational. Admin can submit, review, approve, and publish connector packages.
* **AC-P3-04:** Training and progression system operational. New tenants progress through progression tiers guided by the system.
* **AC-P3-05:** Performance targets met across all pilot tenants: daily briefing P95 <=60s, memory queries P95 <=500ms.
* **AC-P3-06:** Security review passed: tenant isolation audit, credentials in secrets manager, license scan complete.

#### 6.5 Phase 4 Gate: External / Client Ready
* **AC-P4-01:** Gated evolution delivery operational. External tenant must explicitly opt in before a system evolution is applied.
* **AC-P4-02:** External connector catalog filtered correctly. No internal-only connectors visible to external tenants.
* **AC-P4-03:** Deployment runbook documented and tested. Clean deployment in under 60 minutes.
* **AC-P4-04:** Full Phase 3 gate criteria re-verified post-external configuration changes.

---

### 7. Constraints and Assumptions

**Constraints:**
* Team size: 2 engineers + 1 part-time architect/lead.
* All core dependencies (LangGraph, Pydantic AI, LiteLLM) must be MIT or Apache 2.0.
* The markdown IES remains live and fully operational until Phase 2 gate is signed off.
* The strangler-fig migration pattern is mandatory.
* Pilot tenants are not onboarded until Phase 2c gate is signed off.

**Assumptions:**
* David is available for daily-briefing testing during Phase 1 (5 consecutive days minimum).
* Existing IES error log (~197 entries) is complete and accurate.
* Pilot executives (Curtis, Susan, Don) are available for onboarding during Phase 2c.
* Server infrastructure is available for Postgres, LiteLLM, and Langfuse by Phase 0 start.
* Framework versions pinned at Phase 0.

---

### 8. Risks

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--- | :--- | :--- |
| **Scope creep across phase boundaries** | High | High | Phase gates are formal sign-off checkpoints. No phase begins without prior gate passing. |
| **Framework churn** (LangGraph, Pydantic AI) | High | Medium | Pin all dependency versions at Phase 0. Schedule upgrade sprints. CI fails on unpinned installs. |
| **Evolution merge engine correctness** | Medium | High | Extensive test suite for merge logic with real mixed files before first pilot evolution. |
| **Cross-tenant data leak** | Low | Critical | RLS from Phase 0 schema. Automated cross-tenant query tests in CI. Manual security review before Phase 3 gate. |
| **Dependency licensing violation** | Low | High | Automated license scan in CI. Self-hosted Langfuse. Legal review before Phase 4. |
| **Daily briefing quality regression during migration** | Medium | High | Phase 1 gate requires 5/5 quality ratings. Markdown IES available as fallback until Phase 2 gate. |
| **Pilot tenant onboarding friction** | Medium | Medium | Initialization Sequence designed for non-technical users. Dry-run with David before pilot launch. |

---

### 9. Glossary

* **IES:** Intelligent Executive System - the agent platform currently running as Jarvis via Cowork.
* **Jarvis:** The operational name for the IES agent system.
* **LangGraph:** Python framework for stateful, multi-actor agent systems as directed graphs with durable execution.
* **Pydantic AI:** Python framework for type-safe agents with validated inputs and structured outputs. MIT-licensed.
* **LiteLLM:** Model-agnostic LLM proxy/router that normalizes the API surface across providers.
* **pgvector:** Postgres extension for storing and querying vector embeddings.
* **Langfuse:** OpenTelemetry-native observability platform for LLM traces, evals, and cost tracking. Self-hosted.
* **Master Router:** The top-level LangGraph node that classifies every request and routes it to the appropriate specialist agent.
* **Specialist Agent:** Domain-specific Pydantic AI agent: Chief, Chase, Quinn, Shep, Harper, Rigby.
* **System Evolution:** A versioned upgrade package (agents, workflows, skills, connectors) authored by the platform team and distributed to all tenants.
* **Personal Evolution:** Per-tenant customization data (connector bindings, tone directives, scheduling rules). Never overwritten by a system evolution.
* **Connector Catalog:** The package registry of approved MCP integrations available to tenants. Filtered by audience and min_evolution.
* **Initialization Sequence:** The onboarding flow that interviews a new executive and generates their initial personal evolution.
* **Strangler Fig:** Migration pattern: new system runs alongside old system. Capabilities migrate one at a time.
* **Phase Gate:** A formal checkpoint with defined acceptance criteria signed off before advancing.
* **Eval Case:** A structured test scenario derived from the IES error log.
* **Protocol-Skip:** Error class: a documented rule was ignored. The largest single error category (~64 of 197 entries).
* **RLS:** Row-Level Security - Postgres mechanism that enforces tenant data isolation at the database layer.
* **System-Owned:** Behavior or config managed by the platform team. Shared across all tenants.
* **Personal Content:** Per-tenant data (identity, voice, goals, memory, connector bindings). Never overwritten by system updates.

---

### Appendix A: Evolution System Specification

The evolution system is the core distribution mechanism for the platform. It delivers capability updates to all tenants while guaranteeing personal evolution data survives every upgrade.

#### A.1 Evolution Types

| Type | What It Contains | Owned By | Application |
| :--- | :--- | :--- | :--- |
| **System** | New agents, workflows, skills, connector catalog entries, permissions | IES platform team | Auto-applied (internal); opt-in (external) |
| **Personal** | Connector bindings, tone directives, scheduling rules, relationship context, workflow overrides | The tenant | Never touched by system evolutions |

#### A.2 File Delineation
Definition files use HTML comment tags to mark ownership inline:

```
<!-- system:start -->
... system-owned content ...
<!-- system:end -->

<!-- personal:start -->
... user-owned content - immutable to system evolutions ...
<!-- personal:end -->
```

Content outside any block is treated as system-owned by default.

#### A.3 Manifest Format
Every evolution package includes an `evolution.manifest.json`:

```json
{
  "id": "ies-evolution-2026-Q3",
  "version": "2026.3.0",
  "name": "Q3 2026 - Chase Pipeline Intelligence + Analyst Agent",
  "type": "system",
  "compatibility": { "minimum_base_version": "2026.1" },
  "files": [
    { "path": "agents/analyst.md", "type": "system", "action": "add" },
    { "path": "agents/chase.md", "type": "mixed", "action": "merge" },
    { "path": "workflows/pipeline-review/workflow.md", "type": "system", "action": "replace" }
  ]
}
```

#### A.4 File Actions

| Action | Behavior |
| :--- | :--- |
| `add` | Write new file. If file exists, treat as merge. |
| `replace` | Overwrite file. Halts if personal blocks detected. |
| `merge` | Extract personal blocks, write system version, re-inject personal blocks at original logical positions. Verify all blocks present. |
| `delete` | Remove file. Halts if personal blocks detected. |

#### A.5 Application Protocol
1. Validate manifest - confirm all files present in package.
2. Snapshot current state of all files listed in manifest.
3. Scan for personal blocks in all merge/replace/delete targets.
4. Apply each file action per rules above.
5. Verify all personal blocks from pre-application scan are present post-apply.
6. Record in evolutions/history.md: version, date, files changed, blocks preserved, conflicts.

---

### Appendix B: Connector Catalog Specification

The connector catalog is the package registry of approved MCP integrations available to tenants. It replaces tool-specific assumptions with an abstract capability binding model.

#### B.1 Connector Manifest Schema

```json
{
  "name": "omnifocus-sidecar",
  "version": "1.0.0",
  "source": "improving-internal",
  "description": "OmniFocus task management via local Mac sidecar",
  "min_evolution": "2026.1",
  "audience": "internal",
  "required_capabilities": ["task-management"],
  "connection": {
    "type": "mcp",
    "command": "ies-sidecar",
    "args": ["--connector", "omnifocus"],
    "env": {
      "SIDECAR_TOKEN": { "prompt": "Enter sidecar API token", "secret": true }
    }
  }
}
```

#### B.2 Catalog Properties

| Property | Type | Description |
| :--- | :--- | :--- |
| `audience` | internal / external / all | Controls visibility. Internal connectors not shown to external tenants. |
| `min_evolution` | semver | Minimum platform evolution version required for install. |
| `required_capabilities` | string[] | Abstract capability categories this connector satisfies. |
| Signature | SHA-256 | Package integrity hash validated on install. |

#### B.3 Capability Categories

| Category | Default | Example Personal Bindings |
| :--- | :--- | :--- |
| `task-management` | Built-in task store | OmniFocus sidecar, Todoist MCP, Jira connector |
| `calendar` | M365 Calendar | Google Calendar MCP |
| `crm` | (none - required for Chase) | Dynamics 365, Salesforce, HubSpot |
| `knowledge-base` | Built-in knowledge layer | Obsidian MCP |
| `notifications` | (none) | Slack MCP, Teams MCP |

#### B.4 Installation Protocol
1. Tenant selects connector from catalog.
2. Platform validates min_evolution compatibility.
3. Platform validates package signature.
4. Rigby guides tenant through credential configuration in plain language.
5. Connector added to tenant's personal evolution (connector binding).
6. Connector registered in tenant's packages.manifest.json.

---

### Appendix C: LLM-as-Judge Protocol Specification

Nuanced judgment failures (~55 of 197 errors) cannot be validated with binary string matching.

#### C.1 Model Selection
* Primary reasoning agents: Claude 3.5 Sonnet (or equivalent via LiteLLM).
* Judge: GPT-4o via LiteLLM - separate from the primary model to avoid self-grading bias.

#### C.2 Judge Prompt Template

```
You are an expert system auditor evaluating the output of an Intelligent Executive System (IES).

[User Request]
{user_request}

[Ground Truth Reference / Correct Criteria]
{ground_truth}

[Agent Actual Output]
{actual_output}

Evaluate the actual output on correctness, completeness, tone, and adherence to instructions.
Score from 1 to 5:
1 - Completely wrong or failed to adhere to critical constraints.
2 - Minor correct elements, missed core requirements or hallucinated information.
3 - Mostly correct, lacks completeness or has minor formatting deviations.
4 - Correct and complete; fully adheres to constraints.
5 - Flawless; indistinguishable from or superior to the ground truth.

Respond in JSON: { "reasoning": "...", "score": 4 }
```

#### C.3 Thresholds and Review
* **Pass:** Score >= 4.
* **Fail:** Score <= 3. Case written to /systems/evals/failed_cases.json and flagged in Langfuse.
* **Review cadence:** David reviews failures weekly (~15 minutes). False failures (judge error) are overridden in the database.

---

### Appendix D: Data Migration Plan

#### D.1 Legacy Data Mapping

| Legacy Source | Target Postgres Table | Method |
| :--- | :--- | :--- |
| identity/MEMORY.md | semantic_memory (tenant-scoped) | Parse Markdown, chunk by fact, embed via LiteLLM, write to Postgres |
| systems/error-tracking/entries/ (~197 files) | eval_cases | Python parser extracts metadata, writes to relational eval table |
| Obsidian Vault Meeting Notes | episodic_memory (tenant-scoped) | Ingest notes with frontmatter tags into pgvector store |

#### D.2 Postgres Schema (Core Tables)

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    evolution_level VARCHAR(50) DEFAULT '2026.1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE semantic_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    source_file VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE episodic_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    title VARCHAR(255),
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1536),
    created_at TIMESTAMP NOT NULL
);

-- Row-level security
ALTER TABLE semantic_memory ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON semantic_memory
    USING (tenant_id = current_setting('app.current_tenant')::UUID);

ALTER TABLE episodic_memory ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON episodic_memory
    USING (tenant_id = current_setting('app.current_tenant')::UUID);
```

#### D.3 Migration Validation
* Dry run: parse and output to local JSON before inserting.
* Integrity: row count matches legacy source. 10 benchmark vector queries return expected results with similarity > 0.82.
* Gate AC-P0-07: must pass before Phase 1 begins.
