---
name: account-pursuit-map
description: Strategic account pursuit map for landing new work at a target company — active-but-underleveraged expansion or cold/lost re-entry. Distinct from account-strategy (which deep-dives an existing CRM account).
agent: chase
model: sonnet
---

<!-- system:start -->
# Account Pursuit Map Workflow

**Goal:** Build a complete strategic pursuit map for landing new business at a target company — whether Improving already has a beachhead engagement there (Schwab pattern: expand into new capability areas) or has no current footprint / a lost deal to rebuild from (Constellation pattern: cold or lost re-entry). The output tells David exactly who to reach, in what order, with what pitch, and what to do first.

**Agent:** Chase — Revenue & Pipeline

**Architecture:** Sequential 6-step workflow.

1. **step-01-entity-anchor-and-trigger.md** — Disambiguate the target entity, determine active-but-underleveraged vs. cold/lost-re-entry shape, identify the public timing trigger.
2. **step-02-strategic-priorities.md** — Primary-source research into the target's stated strategic priorities (10-K, investor day, press releases, earnings calls). Factual grounding only — no inference.
3. **step-03-competitive-positioning-and-leadership.md** — Map Improving's capabilities to the stated priorities, name a win-wire proof story, note honest competitive positioning, and build a complete C-suite + one-level-down org chart (cross-referenced against CRM for existing engagement history) with full narrative profiles reserved for the 3-5 most strategically relevant contacts.
4. **step-04-icp-account-9box.md** ("ICP & Account 9-Box") — Improving's standard account-planning scoring methodology (sourced from the 2026 AT&T Account Plan): a Potential score and a Realized score, each a weighted formula across Geography (10%), Revenue (70%), and Gross Margin (20%), each factor banded -5 to +5 via fixed lookup tables. Best-case IT services spend is estimated from company size against a cited industry benchmark rather than left blank; gross margin defaults to Improving's typical realized range; TTM actuals for the Realized score are pulled from CRM if engagement history exists, or defaulted to $0/0% if this is a cold pursuit. Classifies the account into one of nine named 9-box zones (IDEAL, SIGNIFICANT, POISED, SOLID, CORE, STEADY, LIMITED, CONSTRAINED, CAPPED). Placed immediately after the Leadership/Org Chart section in the final document — not an early triage gate, not bundled with step 03's competitive positioning. Several elements (geography scoring logic, the 9-box grid arrangement beyond one confirmed data point) are explicitly flagged as inferences for David to verify.
5. **step-05-referral-network.md** ("Referral & Partner Network") — Two separate research tracks in one step: (a) warm paths via YPO, personal ties, sponsors, alumni, mutual connections — reuses the LinkedIn mutual-connections lookup pattern from `workflows/client-meeting-prep/steps/step-03-research-company-and-attendee.md`; and (b) Improving's partner network (AWS, Microsoft, GCP, Confluent, Databricks, SpaceX/xAI, Snowflake, SAP) — which partners the target account likely already uses based on public tech-stack signals, and partner-side contacts who could help.
6. **step-06-synthesize-and-deliver.md** — Synthesize contact sequencing, entry plays, the phased strategic path (branches on step 01's determination), immediate next actions, open items, and sources. Writes the final document to `accounts/{Company}/account-plan.md`, with the ICP & Account 9-Box section placed immediately after the Leadership/Org Chart and before the Referral/Partner Network section.

**Why this is a separate workflow from `account-strategy`:** `account-strategy` is a deep-dive on an account already in an active relationship or CRM record — history, open opportunities, competitive landscape, relationship map for what's already there. `account-pursuit-map` is about strategic *new-business pursuit* — mapping how to land or expand work at a target, whether or not there's existing traction, built around public-source research and a leadership/referral network map rather than CRM pipeline data. These are intentionally distinct capabilities. See the routing disambiguation in `agents/chase.md` and `agents/master.md`.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method | Priority |
|--------|-------------|----------------|----------|
| Primary filings & investor materials | 10-K, 10-Q, investor day decks, press releases, earnings call transcripts | Web search / SEC EDGAR / company IR site | 1st — factual grounding for stated priorities |
| Company leadership pages & LinkedIn | Executive bios, org structure, reporting lines, recent moves | Web search, LinkedIn (Claude in Chrome if logged in) | 2nd — individual profiles |
| CRM | Prior engagement history, opportunity/loss records, existing sponsors | CRM via Chrome/M365 auth | 3rd — confirm engagement status and any loss history |
| General web / news | Recent news, market context, industry trends | Web Search MCP | 4th — supplement only, never the anchor for a stated-priority claim |
| Personal network (parallel track) | YPO, alumni, mutual connections, Clay | LinkedIn via Claude in Chrome, Clay MCP if connected, David's own knowledge | Runs independently of the company-research track above — see step 04 |

**Research source priority is fixed and sequential for company research** (primary filings → leadership pages/LinkedIn → CRM → web/news). Do not substitute a lower-priority source for a claim a higher-priority source could support. Personal network mapping (step 04) is a separate, parallel track — not folded into company research.

### Input

This workflow requires a target company name to begin. One of:
- A specific company name ("build a pursuit map for [company]")
- A direct request using trigger language: "strategic account map", "pursuit plan for [company]", "how do we land [company]"
- An account name already known to be a lost deal or cold prospect

### Paths

- Output document: `accounts/{Company}/account-plan.md` (create the folder if it doesn't exist; if `accounts/{Company}/` already exists, this workflow updates the living document in place rather than creating a duplicate)
- Reference pattern files: `accounts/Schwab/account-plan.md` (active-but-underleveraged pattern), `accounts/Constellation Energy/account-plan.md` (cold/lost re-entry pattern) — read whichever matches step 01's determination before drafting step 05's output, to match tone, depth, and section shape.

### Key Metrics

- Entity disambiguated with confidence before any content is written
- Engagement shape determined (active-but-underleveraged vs. cold/lost-re-entry) — this gates the phased-path shape in step 05
- Every stated-priority claim traceable to a primary source citation
- Org chart complete for C-suite (full, not just tech-relevant) plus one level down, cross-referenced against CRM for existing engagement history
- Full narrative profiles (background, reasoned-inference role label, pitch angle, what-to-avoid) reserved for the 3-5 most strategically relevant contacts; remaining org chart names listed compactly (name/title/CRM-status)
- ICP & Account 9-Box computed using Improving's fixed weighted methodology (Geography 10% / Revenue 70% / Gross Margin 20%, each factor banded -5 to +5); IT spend and gross margin inputs estimated (never left blank) with cited benchmarks/defaults; TTM actuals pulled from CRM or defaulted to $0/0% for cold pursuits; 9-box zone assigned with every inference (geography scoring logic, grid arrangement) flagged for verification
- Referral network and partner network kept structurally separate from the leadership/org map, the ICP/9-box section, and from each other
- All 8 of Improving's partners (AWS, Microsoft, GCP, Confluent, Databricks, SpaceX/xAI, Snowflake, SAP) checked against the target's public tech-stack signals
- Every contact/path/tech-stack claim tagged confirmed vs. needs-verification (or no-signal-found for tech-stack)
- Final document lands in `accounts/{Company}/account-plan.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## STATE CHECK

Before starting, read `workflows/account-pursuit-map/state.yaml`.

**Case 1 — Not started (`status: idle` or file shows no `session-id`):** Begin fresh. Set `status: in-progress`, `session-id: chase-{YYYY-MM-DD}-{HHmmss}`, `session-started`, `original-request`, `current-step: step-01-entity-anchor-and-trigger`. Proceed to EXECUTION.

**Case 2 — In progress (`status: in-progress`, `current-step` populated):** A prior run was interrupted. Check the frontmatter of the step file named in `current-step`. If that step's frontmatter shows `status: in-progress`, re-execute it from the beginning — do not attempt to reconstruct partial results. If it shows `status: complete`, resume at the next step in sequence. Carry forward everything in `accumulated-context`.

**Case 3 — Complete (`status: complete`):** The last run finished. If the controller is asking about the same company as `original-request`, ask whether this is a refresh (re-run) or a genuinely new request before starting over — the pursuit map is a living document, not a one-time artifact, so most re-invocations should update the existing `accounts/{Company}/account-plan.md` rather than starting a parallel workflow run. If the controller names a different company, treat as Case 1 for that company (state.yaml tracks one active run at a time; this is fine since the workflow's persistent output lives in `accounts/{Company}/`, not in state.yaml).

**Case 4 — Aborted (`status: aborted`):** Surface what was completed before the abort (check `accumulated-context` for populated keys) and ask the controller whether to resume from the last completed step or start over.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow, in order:

1. `steps/step-01-entity-anchor-and-trigger.md`
2. `steps/step-02-strategic-priorities.md`
3. `steps/step-03-competitive-positioning-and-leadership.md`
4. `steps/step-04-icp-account-9box.md`
5. `steps/step-05-referral-network.md`
6. `steps/step-06-synthesize-and-deliver.md`

Each step file's frontmatter and `NEXT STEP`/`WORKFLOW COMPLETE` section govern progression. Do not skip ahead.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
