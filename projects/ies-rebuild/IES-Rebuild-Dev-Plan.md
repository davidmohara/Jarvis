# IES Rebuild — Development Plan
## Phased migration from markdown OS to multi-tenant agent platform

* **Document Owner:** David O'Hara, Regional Director, Improving
* **Version:** 2.0
* **Date:** June 27, 2026
* **Companion Documents:** IES Rebuild BRD v2.0, IES Rebuild Evaluation v2.0
* **Team:** 2 Engineers + 1 Part-Time Architect/Lead
* **Total Duration:** ~6-8 months (substrate through external-ready platform)

---

> **Project intent:** See *IES-Rebuild-Evaluation.md* §"Project Intent and Origin" for the full context and reframing rationale that governs this document.

### How to Use This Document
This plan follows the strangler-fig pattern: the new system runs alongside the markdown IES and migrates one capability at a time. Each phase ends with a formal gate — the BRD acceptance criteria that must pass before the next phase begins. The markdown IES remains live and fully operational until the Phase 2 gate is signed off.

The schema is tenant-isolated (Postgres RLS) from Phase 0. Pilot tenants are onboarded in Phase 2c — not before. Phase 3 builds the platform infrastructure (evolution distribution engine, connector catalog UI, Initialization Sequence, admin tools) that turns a working single-tenant system into a distributable product.

---

### Table of Contents
1. Guiding Principles and Prompt Governance
2. Team and Roles
3. Timeline Summary
4. Phase 0: Foundations
5. Phase 1: Core Orchestration (Chief Vertical Slice)
6. Phase 2: Full Single-Tenant Core
7. Phase 3: Multi-Tenant Platform
8. Phase 4: External / Client Ready
9. Testing Strategy and Eval Discipline
10. Definition of Done
11. Out of Scope
12. Ongoing Maintenance

---

### 1. Guiding Principles and Prompt Governance

#### 1.1 Guiding Principles
* **Platform product, not personal tool.** The target is a distributable executive platform for Improving. David's instance is the reference implementation and proving ground — not the end state.
* **Schema is multi-tenant from day one.** Postgres RLS policies are established in Phase 0. No tenant-unaware data patterns are allowed to harden.
* **Single-tenant first is a sequencing strategy, not a scope limit.** We build one vertical slice at a time to maintain quality and velocity. Multi-tenant onboarding begins in Phase 2c; the infrastructure to serve many tenants is Phase 3.
* **Eval gates are not optional.** No agent ships without a passing eval suite. No phase advances without the prior phase gate passing. The ~197 error log entries are the acceptance test.
* **Markdown IES stays live until Phase 2 gate.** Fallback is never removed before the new system has demonstrated 10 consecutive production days as primary.
* **Prose only where prose is correct.** Identity, voice, and personal knowledge layer remain as curated markdown. All orchestration, routing, gates, and state live in code.
* **Strangler fig, not big bang.** Migrate one capability at a time. No capability retires until its replacement has green evals.

#### 1.2 Prompt Governance
Prompts are versioned code, not editable text. Behavioral drift from prompt changes is the primary risk for regression in judgment-class failures.

* All prompt files for agents, skills, and workflows live in git under `prompts/`.
* Every prompt file change triggers the associated agent's eval suite in CI automatically.
* Prompt changes require the same review process as code changes — PR, review, merge.
* Prompt versions are tagged alongside code versions in deployment records.
* The LLM-as-Judge protocol (BRD Appendix C) is used for judgment-class eval cases where binary pass/fail is insufficient.
* A prompt registry tracks current production prompts per agent, per tenant, with the commit SHA and the eval score at time of deployment.

---

### 2. Team and Roles

| Role | Responsibilities |
| :--- | :--- |
| **David O'Hara** (Controller / Platform Owner) | Phase gate sign-off, daily-briefing quality validation (Phase 1), pilot tenant onboarding, eval case review, product direction |
| **Lead Engineer (Eng 1)** | LangGraph orchestration, Postgres schema + RLS, eval harness, CI/CD pipeline, Phase 3 platform infrastructure |
| **Agent Engineer (Eng 2)** | Pydantic AI specialist agents, skills migration, connector catalog implementation, memory layer, Phase 3 tenant tooling |
| **Architect/Lead** (part-time) | Architecture decisions, dependency licensing, pattern review, phase gate review, security audit |

---

### 3. Timeline Summary

| Phase | Description | Duration | Cumulative |
| :--- | :--- | :---: | :---: |
| **0** | Foundations (substrate, eval harness, RLS schema) | 2-3 weeks | 3 weeks |
| **0b** | Eval dataset (parallel with Phase 0) | 1-1.5 weeks | 3 weeks |
| **1** | Core orchestration (Master + Chief vertical slice) | 3-4 weeks | 7 weeks |
| **2a** | Remaining agents (Chase, Quinn, Shep, Harper, Rigby) | 4-6 weeks | 13 weeks |
| **2b** | Memory + skills + connector catalog (parallel with 2a) | 2-3 weeks | 13 weeks |
| **2c** | Production run + pilot tenant onboarding | 2 weeks | 15 weeks |
| **3** | Multi-tenant platform | 8-10 weeks | 25 weeks |
| **4** | External / client ready | 4-6 weeks | 31 weeks |

**Key milestones:**
* Phase 0 gate: ~3 weeks
* Phase 1 gate: ~7 weeks
* Phase 2 gate (single-tenant parity): ~15 weeks (~4 months)
* Phase 3 gate (multi-tenant platform): ~25 weeks (~6 months)
* Phase 4 gate (external-ready): ~31 weeks (~8 months)

---

### 4. Phase 0: Foundations

**Goal:** Establish the technical substrate, tenant-isolated data schema, observability, and the eval harness before any agent logic is written. This phase is not optional and is not parallelizable with Phase 1.

**Duration:** 2-3 weeks (Eng 1 + Eng 2 + Lead)

#### 4.1 Infrastructure Setup
* [ ] Repository initialized: branching strategy (main/develop/feature), pre-commit hooks, pinned dependency versions in lockfile
* [ ] LiteLLM proxy deployed and routing to at least 2 LLM backends (Claude 3.5 Sonnet + GPT-4o minimum)
* [ ] Postgres deployed with pgvector extension
* [ ] Langfuse deployed (self-hosted). Test trace emitted and visible in dashboard within 30 seconds
* [ ] CI pipeline configured: runs on every PR, required to pass before merge

#### 4.2 Multi-Tenant Schema (Phase 0 — RLS from Day One)
* [ ] `tenants` table with id, name, evolution_level, created_at
* [ ] `semantic_memory` tenant-scoped with RLS policy
* [ ] `episodic_memory` tenant-scoped with RLS policy
* [ ] `working_memory` tenant-scoped with RLS policy
* [ ] `eval_cases` table: test_id, failure_mode, scenario, expected_output, judge_type, created_at
* [ ] `eval_results` table: linked to test case, tenant, system version, Langfuse trace ID, score, pass/fail
* [ ] Automated cross-tenant query test: insert records for 2 tenants, query from each context, assert zero cross-tenant results
* [ ] Prompt registry table: agent, prompt_version, commit_sha, eval_score, deployed_at, tenant_id (null = all)

#### 4.3 Eval Dataset (Phase 0b — Parallel with 4.1/4.2)
* [ ] Export all ~197 error-tracking entries to structured JSON
* [ ] For each entry: scenario, expected behavior, failure mode tag, judge type (binary / LLM-as-Judge)
* [ ] Load into `eval_cases` table
* [ ] Eval harness runs all cases and produces pass/fail report by failure-mode class
* [ ] All `protocol-skip` cases produce a stub that passes (they will pass by construction once routing is code)
* [ ] Judgment cases produce baseline scores against the markdown IES (establishes the floor)

#### 4.4 Data Migration (Legacy -> Postgres)
* [ ] Parser for identity/MEMORY.md: chunk by fact, embed via LiteLLM text-embedding-3-small, write to `semantic_memory` for David's tenant
* [ ] Parser for Obsidian meeting notes: ingest with frontmatter metadata, embed, write to `episodic_memory`
* [ ] Dry-run output to local JSON before writing to Postgres
* [ ] Integrity check: 10 benchmark semantic queries return expected results with similarity > 0.82

**Phase 0 Gate (BRD AC-P0-01 through AC-P0-07):** All infrastructure operational, RLS confirmed, eval harness running >=197 cases, legacy data seeded.

---

### 5. Phase 1: Core Orchestration (Chief Vertical Slice)

**Goal:** Prove the full LangGraph + Pydantic AI + LiteLLM + Postgres + Langfuse pattern with a single end-to-end vertical slice. Morning briefing is the target — highest daily value, represents the full capability stack.

**Duration:** 3-4 weeks (Eng 1 + Eng 2)

#### 5.1 Master Router
* [ ] LangGraph graph with Master as supervisor node
* [ ] Conditional edges routing to Chief (and stubs for other agents)
* [ ] Typed state schema: session_id, tenant_id, user_input, routing_decision, agent_context, output
* [ ] Full state persisted at every node transition (LangGraph checkpointing)
* [ ] Process restart resumes from last checkpoint with no data loss
* [ ] Langfuse trace emitted for every request: model, tokens, latency, routing decision, tenant ID

#### 5.2 Chief Agent (Morning Briefing Vertical Slice)
* [ ] Pydantic AI agent with typed input (DateContext, UserPreferences) and typed output (BriefingOutput)
* [ ] Integrations: M365 calendar (read), M365 mail (read), working memory (read), episodic memory (read)
* [ ] Output: calendar summary, priority tasks, key communications, context for today
* [ ] 5-day quality validation with David: output rated acceptable on 5 consecutive mornings
* [ ] Chief eval suite derived from Phase 0b cases tagged `chief` or `daily-briefing`

#### 5.3 Prompt Governance (Active from Phase 1)
* [ ] Chief prompt committed to `prompts/chief/morning-briefing.md` with version header
* [ ] CI runs Chief eval suite on every change to `prompts/chief/**`
* [ ] Prompt registry updated on deployment with commit SHA and eval score

**Phase 1 Gate (BRD AC-P1-01 through AC-P1-06):** Master routes 100% of 50-request test set correctly. Morning briefing passes 5 consecutive days. All Phase 0 evals still green. Markdown IES still live.

---

### 6. Phase 2: Full Single-Tenant Core

**Goal:** All 6 agents operational with passing eval suites, full memory system, connector catalog, built-in task management, and 10 consecutive production days as primary system.

**Duration:** ~8-11 weeks total (2a + 2b parallel + 2c)

#### 6.1 Phase 2a: Remaining Agents (4-6 weeks, both engineers)
For each agent — Chase, Quinn, Shep, Harper, Rigby — in priority order:

* [ ] Pydantic AI agent with typed inputs and outputs
* [ ] At least one representative workflow end-to-end (see below)
* [ ] Agent eval suite passing (BRD failure-mode classes)
* [ ] Prompt committed to `prompts/{agent}/` with CI eval hook
* [ ] Independent testability confirmed (agent runs without other agents online)

**Representative workflows per agent:**
* **Chase:** pipeline-review (Dynamics CRM integration via web API required)
* **Quinn:** quarterly-rock-review
* **Shep:** 1on1-prep
* **Harper:** email-drafter
* **Rigby:** evolution-package + evolution-apply (critical — Rigby is the evolution lifecycle manager)

#### 6.2 Phase 2b: Memory, Skills, Connector Catalog (2-3 weeks, parallel with 2a)
* [ ] Memory system: full read/write across all layers (working, episodic, semantic, personal)
* [ ] Cross-tenant isolation test in integration suite (automated, runs on every PR)
* [ ] Skills catalogue: all .claude/skills/* catalogued with schema + pre-flight requirements
* [ ] Skills migrated to typed Pydantic AI tools with enforceable pre-flight gates
* [ ] Connector catalog: package registry with audience filtering, min_evolution gating, SHA-256 signing
* [ ] Abstract capability categories defined: task-management, calendar, crm, knowledge-base, notifications
* [ ] At least one connector package installed per category via personal evolution binding
* [ ] Built-in task management: create, read, update, complete via platform API
* [ ] External sync API: tested with at least one connector (OmniFocus sidecar or Todoist MCP)

#### 6.3 Phase 2c: Production Run + Pilot Tenant Onboarding (2 weeks)
* [ ] Full eval suite (>=197 cases) passes: protocol-skip 100%, overall >=90%
* [ ] System operates as primary for 10 consecutive working days without fallback to markdown IES
* [ ] Markdown IES retired as primary (kept as documented rollback option)
* [ ] Initialization Sequence dry-run with David: validate interview flow and personal evolution generation
* [ ] Onboard pilot tenants: Curtis, Susan, Don via Initialization Sequence
* [ ] Each pilot tenant has: independent personal evolution, connector bindings, first morning briefing completed
* [ ] Cross-tenant isolation confirmed in production (automated test + manual review)

**Phase 2 Gate (BRD AC-P2-01 through AC-P2-06):** All 6 agents green, memory + connectors operational, full eval suite >=90%, 10 days as primary, 3 pilot tenants live with independent personal evolutions.

---

### 7. Phase 3: Multi-Tenant Platform

**Goal:** Build the platform infrastructure that turns the working single-tenant system into a distributable product: evolution distribution engine, connector catalog UI, admin tools, and training/progression system.

**Duration:** 8-10 weeks (2-3 engineers)

#### 7.1 Evolution Distribution Engine
* [ ] Evolution package format: `evolution.manifest.json` with file actions (add, replace, merge, delete)
* [ ] Merge action: extract personal blocks, write system version, re-inject personal blocks, verify all blocks present
* [ ] Replace/delete halt: if personal blocks detected, halt and present conflict to user
* [ ] Pre-application snapshot of all files in manifest
* [ ] Post-application verification: all personal blocks from pre-scan present post-apply
* [ ] Evolution history recorded per tenant: `evolutions/history.md` with version, date, files changed, blocks preserved
* [ ] Rigby agent integration: Rigby manages full lifecycle (validate, snapshot, apply, verify, record)
* [ ] Test suite: merge logic tested extensively with real mixed files from David's IES before any production evolution
* [ ] System evolution deployed to all 3 pilot tenants simultaneously: personal blocks preserved for all tenants

#### 7.2 Connector Catalog Web UI
* [ ] Catalog browsing: list all approved connectors by category and audience
* [ ] Connector detail view: manifest, version history, capabilities, installation instructions
* [ ] Admin submission flow: upload connector package, validate manifest + signature, review queue
* [ ] Admin approval/rejection: approved packages published to catalog, rejected packages with feedback
* [ ] Tenant install flow: browse catalog, Rigby guides credential configuration in plain language
* [ ] External audience filter: no internal-only connectors visible to external tenant contexts

#### 7.3 Admin Tools
* [ ] Tenant health dashboard: list all tenants with status (active, degraded, error), evolution level, last activity
* [ ] Evolution management: deploy system evolution to individual tenant or all tenants, view history per tenant
* [ ] Connector catalog management: submission queue, approval workflow, published packages
* [ ] Eval dashboard: pass/fail rates by failure-mode class, per-tenant performance, regression alerts
* [ ] Platform ops: service health, Langfuse integration status, LiteLLM router status

#### 7.4 Training and Progression System
* [ ] Progression tier model: Getting Started (0-25%), Building Rhythm (25-50%), Strategic Mode (50-75%), Full System (75-100%)
* [ ] New tenant onboarding: Chief tasks introduced first (morning briefing, inbox processing)
* [ ] Achievement tracking: first-time task completion earns progress; repeated use builds toward tier unlock
* [ ] Evolution onboarding: when a new agent/skill ships via system evolution, "Try the new [X]" prompt surfaced at tenant's next session
* [ ] Progression state stored per tenant in Postgres (tenant-scoped)

**Phase 3 Gate (BRD AC-P3-01 through AC-P3-06):** Pilot tenants fully operational with independent personal evolutions, system evolution delivered to all pilots successfully, connector catalog UI live, training system active, performance and security targets met.

---

### 8. Phase 4: External / Client Ready

**Goal:** Enable deployment to Improving clients. Gated evolution delivery, external connector catalog filtering, client branding, and a documented deployment runbook.

**Duration:** 4-6 weeks (2 engineers)

#### 8.1 Gated Evolution Delivery
* [ ] External tenant evolution flow: new system evolution staged, not auto-applied
* [ ] Tenant receives "New evolution available" notification with changelog
* [ ] Explicit opt-in required before evolution is applied to external tenant
* [ ] Account team review step: evolution presented with guided context before client activation

#### 8.2 External Connector Catalog
* [ ] Catalog filtered by `audience: external` for all external tenant contexts
* [ ] Internal-only connectors invisible to external tenants (enforced at API layer, not just UI)
* [ ] External-approved connector package submission path for client-specific connectors

#### 8.3 Client Branding and Deployment
* [ ] Platform name configurable per deployment ("Improving Executive System" for all Improving deployments)
* [ ] Deployment runbook: documented, tested, clean deployment in under 60 minutes
* [ ] Guest Entra ID account provisioning path documented (access model for external clients)

#### 8.4 Security and Compliance Baseline
* [ ] Full dependency license scan: all runtime deps MIT or Apache 2.0, confirmed by automated scan
* [ ] Legal review of dependency tree completed before any external deployment
* [ ] Security review: tenant isolation audit, credentials-in-secrets-manager confirmation, RLS policy audit

**Phase 4 Gate (BRD AC-P4-01 through AC-P4-04):** Gated evolutions operational, external catalog filtering confirmed, deployment runbook tested, security review complete.

---

### 9. Testing Strategy and Eval Discipline

#### 9.1 Test Layers

| Layer | Tool | Scope | When |
| :--- | :--- | :--- | :--- |
| Unit tests | pytest | Orchestration logic, routing rules, skill gates, memory queries | Every PR |
| Integration tests | pytest + LangGraph test client | Agent-to-connector paths, memory read/write, cross-tenant isolation | Every PR |
| Eval harness | Custom harness + Langfuse | All 197+ error log cases; regression detection | Every PR, daily in CI |
| LLM-as-Judge | GPT-4o via LiteLLM | Judgment-class eval cases | Weekly + on prompt changes |
| Phase gate validation | Manual + automated | BRD AC criteria | At each phase gate |

#### 9.2 Coverage Requirements
* Unit test coverage >=80% for all orchestration and routing logic
* Integration tests for every agent-to-connector path
* 100% of error log entries converted to eval cases before Phase 1 begins
* No agent ships without its eval suite established and passing

#### 9.3 Regression Policy
* Any eval case that was previously passing and begins failing triggers an automated alert
* Regressions block the next phase gate
* New production errors generate a draft eval case automatically; developer reviews and commits before it enters the required-passing set
* David reviews LLM-as-Judge failures weekly (~15 minutes). False failures overridden in database.

#### 9.4 Eval Reporting by Failure-Mode Class
Every eval run produces a report showing pass/fail counts per class:

| Class | Target | Notes |
| :--- | :--- | :--- |
| `protocol-skip` | 100% by Phase 1 | Eliminated by code enforcement |
| `stale-cache` | 100% by Phase 1 | Eliminated by typed state |
| `wrong-tool` / `tool-ignorance` | >=95% by Phase 2 | Connector registry |
| `format-violation` | >=95% by Phase 2 | Validated output schemas |
| `wrong-assumption` | >=70% by Phase 2; >=80% Phase 3 | Judgment class — eval + model routing |
| `sloppy-read` / `bad-inference` | >=70% by Phase 2 | Model quality — eval + prompt governance |

---

### 10. Definition of Done

A phase is done when:
1. All BRD acceptance criteria for that phase gate have passed
2. David has signed off in writing (or in the project tracker)
3. Langfuse shows green traces for all workflows covered in the gate
4. The eval report for that phase has been committed to the repo
5. Deployment record exists: git commit SHA, phase gate name, date, sign-off

A capability (agent, skill, workflow) is done when:
1. Its eval suite exists and passes
2. Its prompt is committed to `prompts/` with CI hook active
3. At least one end-to-end workflow integration test passes
4. It has been validated in David's production session (or pilot tenant session from Phase 2c)

---

### 11. Out of Scope

* External customer-facing billing, payments, or subscription management (Phase 4+)
* Net-new agent capabilities not in the current IES (new agents are system evolutions post-platform launch)
* Voice output (V2+, separate initiative)
* Full mobile app (web dashboard is mobile-responsive; native app is future)
* Custom white-label branding beyond name/logo configuration (enterprise tier, future)

---

### 12. Ongoing Maintenance

Post-Phase 2 gate, the platform is live software with ongoing obligations:

| Obligation | Cadence | Owner |
| :--- | :--- | :--- |
| Dependency upgrades (framework pinning review) | Monthly | Lead Engineer |
| Eval suite maintenance (new cases, false failure review) | Weekly (David: 15 min) + monthly (eng) | David + Eng 1 |
| Evolution package authoring (new capabilities) | As needed | Platform team |
| Connector catalog curation (submission review) | As submissions arrive | Platform Admin |
| Prompt governance review (drift detection) | Monthly | Eng 2 + David |
| Security audit | Quarterly | Architect/Lead |
| Performance baseline review (P95 targets) | Monthly | Eng 1 |
| Pilot tenant health review | Weekly (Phase 3) | Lead Engineer |
