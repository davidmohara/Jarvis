# Workflow State Tracking & Agent Activation Enforcement

## Problem

IES agents drift, wander, and repeat work they've already done. Two root causes:

1. **No durable workflow state.** Step progress lives only in the conversation context. When context compacts mid-workflow, the agent loses its place and improvises — re-asking questions, skipping steps, or producing inconsistent output.

2. **No agent-level activation enforcement.** Sub-agent files are pure persona definitions. There is nothing inside the file itself that verifies the agent was properly spawned, loaded its permissions, or is operating within its domain. If context drifts, so does the agent.

---

## Change 1: Workflow State File (`state.yaml`)

**What:** Add a `state.yaml` file to every workflow directory alongside `workflow.md`.

**Scope:** All 28 workflow directories.

**Why:** This is the compaction anchor. It lives on disk and survives any amount of context compression. After compaction, Master reads it to know exactly what was interrupted and where. Without it, there is no recovery path — the agent has no choice but to guess or start over.

**Schema:**

```yaml
---
workflow: morning-briefing
agent: chief
status: not-started | in-progress | complete | aborted
session-started: ~          # ISO-8601 when this run began
session-id: ~               # Unique ID to correlate with knowledge layer entries
current-step: ~             # e.g., step-02
original-request: ~         # Verbatim controller request that triggered this workflow
accumulated-context:        # Data passed forward across steps
  # Key-value pairs written by each step as it completes.
  # Keys vary by workflow — defined per-workflow in the step output specs.
  # Example (morning-briefing):
  # calendar-events-count: 4
  # first-meeting: "9:00 AM - CBRE Quarterly"
  # priority-task-count: 3
  # delegation-overdue-count: 1
---
```

**Write protocol:**

| Event | What to write |
|-------|--------------|
| Workflow starts (fresh) | `status: in-progress`, `session-id`, `session-started`, `original-request`, `current-step: step-01` |
| Step N completes | Update `current-step` to step N+1, write step's outputs into `accumulated-context` |
| Workflow completes | `status: complete`, clear `accumulated-context` |
| Interrupted (any cause) | Leave as-is — `status: in-progress` is the recovery marker |

**Initial file state** (template, committed to repo):

```yaml
---
workflow: {workflow-name}
agent: {agent-name}
status: not-started
session-started: ~
session-id: ~
current-step: ~
original-request: ~
accumulated-context: {}
---
```

---

## Change 2: Step File Frontmatter

**What:** Add YAML frontmatter to the top of every step file.

**Scope:** All 104 step files across all 28 workflows. Currently step files open directly with `<!-- system:start -->` — no frontmatter exists.

**Why:** Gives each step its own durable status independent of conversation history. The agent reads frontmatter to determine which steps are done and which aren't — not the transcript.

**Schema:**

```yaml
---
status: not-started | in-progress | complete | skipped
started-at: ~
completed-at: ~
outputs:
  # What this step produced — keyed values the next step needs.
  # Keys are defined per-step. Example (morning-briefing step-01):
  # calendar-events-count: 4
  # first-meeting: "9:00 AM - CBRE Quarterly"
  # conflicts-found: false
---
```

**Write protocol:**

| Event | What to write |
|-------|--------------|
| Before executing step | `status: in-progress`, `started-at: {ISO-8601}` |
| After step completes | `status: complete`, `completed-at: {ISO-8601}`, populate `outputs` |

**Initial file state** (template, all step files):

```yaml
---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---
```

**Output key definitions** are specified per step inside the step file itself (in the YOUR TASK section). Each step should document what keys it writes to `outputs` and what those values represent. These same keys flow into `state.yaml`'s `accumulated-context` when the step completes.

---

## Change 3: STATE CHECK Block in `workflow.md`

**What:** Add a STATE CHECK block to the INITIALIZATION section of every `workflow.md`, before the current execution instruction.

**Scope:** All 28 `workflow.md` files.

**Why:** Without this, the agent always starts at step 01 regardless of what state.yaml says. The STATE CHECK is what converts state.yaml from a passive log into an active resume mechanism.

**Current INITIALIZATION section (example):**

```markdown
## EXECUTION
Read fully and follow: `steps/step-01-gather-calendar.md` to begin
```

**Becomes:**

```markdown
## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — this is the data already gathered. Do not re-gather it.
   - Check that step's frontmatter:
     - If `status: in-progress`: the step was interrupted mid-execution — re-execute it.
     - If `status: not-started`: begin it fresh.
   - Notify the controller: "[Agent]: Resuming [workflow-name] from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Do not resume automatically. Surface to controller:
     "[Agent]: [workflow-name] was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

## EXECUTION
Read fully and follow: `steps/step-01-....md` to begin
```

---

## Change 4: Master Boot — In-Flight Workflow Detection

**What:** Add one step to the boot sequence in `agents/master.md` and `CLAUDE.md`.

**Scope:** Both files, same addition.

**Why:** After context compaction, the session effectively reboots. This step converts compaction from "silent state loss" into "explicit recovery opportunity." Without it, in-progress workflows are invisible at boot and the controller has no idea they were interrupted.

**In `CLAUDE.md`** — add between step 8 (check evolution manifest) and step 9 (register scheduled tasks):

```
8a. Scan for in-flight workflows:
    - Read state.yaml in every workflows/* directory
    - Collect any where status: in-progress
    - If found, surface immediately in the boot status report:
      "[Master]: You have an interrupted workflow: [workflow-name] was
       in progress at [current-step] (started [session-started]).
       Resume or discard?"
    - Do not auto-resume. Wait for controller instruction before proceeding.
    - If none found, continue boot normally.
```

**In `agents/master.md`** — add to the Boot section of Session Lifecycle, after step 6 (read delegation tracker):

```
7. Scan for in-flight workflows — read state.yaml in every workflows/* directory.
   Surface any where status: in-progress. Do not auto-resume.
```

---

## Change 5: Workflow Lock in Master Active Session

**What:** Add workflow lock behavior to `agents/master.md` in the Active Session section.

**Why:** Compaction isn't the only cause of wandering. A new message arriving mid-workflow causes the agent to abandon the current step to respond — the workflow state is left dangling. This closes that gap.

**Add to the Active Session section of `agents/master.md`:**

```markdown
### Workflow Lock

When a sub-agent has an active workflow (`state.yaml` shows `status: in-progress`),
evaluate incoming requests before routing:

- **Same domain or continuation of the active task:** Pass to the active agent as
  additional context. Do not spawn a new instance.

- **Unrelated request, low urgency:** Capture it, then inform the controller:
  "[Master]: I've captured that. [Agent] is finishing [workflow-name] — I'll surface
  it when done."

- **Unrelated request, urgent:** Surface the conflict explicitly:
  "[Master]: [Agent] is mid-way through [workflow-name] at [current-step].
  Interrupt to handle [new request]? I can resume [workflow-name] after."
  Wait for instruction. Do not silently abandon the in-progress workflow.

Never abandon an in-progress workflow without explicit controller instruction.
If the controller instructs abandonment, set state.yaml status to `aborted`.
```

---

## Change 6: Agent Activation Enforcement

**What:** Add an Activation section as the first section of every sub-agent file.

**Scope:** `chief.md`, `chase.md`, `quinn.md`, `harper.md`, `shep.md`, `rigby.md`

**Why:** These files are currently pure persona definitions — there is nothing inside them that prevents an agent from acting without proper context, operating outside its domain, or starting a workflow without checking if it was interrupted. This enforcement runs before any output, regardless of how the agent was invoked.

**Template** (customize domain, skill path, and connector list per agent):

```markdown
<!-- system:start -->
## Activation

MANDATORY — complete all steps before any output or action:

1. **Verify spawn context.** Confirm you received a spawn payload from Master
   containing: agent name, standing permissions, active connectors, and
   original request text. If the payload is absent or incomplete:
   > "[Agent]: No spawn context received. I require Master to route this request."
   Halt. Do not proceed.

2. **Load standing permissions** from the spawn payload. Do not assume defaults.
   If permissions are missing from the payload, output an elevation request before
   acting on any permissioned operation.

3. **Note active connectors** from the spawn context. Before accessing any data
   source, confirm an active connector exists for that capability. Do not attempt
   CRM access if no `crm` connector is listed as active. Fall back to the defaults
   documented in SYSTEM.md if no connector is available.

4. **Identify the relevant skill.** Based on the original request, identify which
   skill file in `skills/{agent}-*.md` applies. Load and follow that skill's
   workflow. If no skill clearly matches, surface this to Master rather than
   improvising:
   > "[Agent]: The request doesn't clearly map to any of my skills. Returning
   > to Master for routing."

5. **Domain check.** If the request falls outside your domain ({domain description}),
   do not attempt it. State what you can confirm and surface a handoff request:
   > "[Agent]: This crosses into [other domain]. Here's what I've gathered:
   > [summary]. Recommend routing to [Agent] for [specific action]."
   Master handles the spawn. You do not spawn other agents directly.

6. **Check for in-progress workflow.** Before starting any workflow, run the
   STATE CHECK protocol in the relevant `workflows/{name}/workflow.md`.
   Resume if interrupted. Do not start over without checking.
<!-- system:end -->
```

**Per-agent domain descriptions:**

| Agent | Domain |
|-------|--------|
| Chief | Daily operations: morning briefings, inbox processing, calendar prep, daily review, shutdown |
| Chase | Revenue: pipeline reviews, account strategy, client meeting prep, win/loss analysis |
| Quinn | Strategy: quarterly rock reviews, goal alignment, initiative tracking, weekly review, leadership prep |
| Harper | Communication: email drafting, presentation building, talking points, content calendar, email coaching |
| Shep | People: delegation tracking, 1:1 prep, follow-up nudges, team health pulse |
| Rigby | Platform: evolution deployment, system diagnostics, capability building, connector installation |

---

## Change 7: SYSTEM.md Convention Additions

**What:** Add two new sections to `SYSTEM.md` in the Conventions area.

**Why:** Conventions in SYSTEM.md are the authoritative reference for all agents. Without documenting these patterns there, future evolutions and agents won't have a source of truth for how state files work.

### Section A: Workflow State Convention

```markdown
## Workflow State Convention

Every workflow directory contains a `state.yaml` file that tracks the workflow's
execution state across steps and sessions.

### When to read
- At the start of every workflow execution (STATE CHECK protocol)
- At Master boot (in-flight workflow detection)
- When an agent is spawned and needs to check for interrupted work

### When to write
- On fresh workflow start: initialize all fields
- After each step completes: update `current-step` and `accumulated-context`
- On workflow completion: set `status: complete`, clear `accumulated-context`
- On explicit abort: set `status: aborted`

### Schema reference
See the state.yaml template in each workflow directory.

### accumulated-context keys
Each workflow defines its own context keys in the step files (YOUR TASK section).
Keys written by step N are available to step N+1 and beyond. They are also written
to the step file's `outputs` frontmatter field for per-step traceability.

### session-id format
`{agent}-{YYYY-MM-DD}-{HHmmss}` — e.g., `chief-2026-04-03-091532`
Correlates state.yaml with any knowledge layer entries written during the session.
```

### Section B: Step Frontmatter Convention

```markdown
## Step Frontmatter Convention

Every workflow step file begins with YAML frontmatter tracking per-step execution state.

### Schema
- `status`: not-started | in-progress | complete | skipped
- `started-at`: ISO-8601 timestamp written immediately before step execution begins
- `completed-at`: ISO-8601 timestamp written immediately after step completes
- `outputs`: key-value map of what this step produced. Keys are defined in the
  step's YOUR TASK section. These same keys are written into state.yaml's
  accumulated-context when the step completes.

### Write sequence
1. Before executing: write `status: in-progress`, `started-at`
2. After executing: write `status: complete`, `completed-at`, populate `outputs`

### Recovery behavior
If a step's frontmatter shows `status: in-progress` at resume time, the step was
interrupted mid-execution. Re-execute it from the beginning. Do not attempt to
reconstruct partial results — start the step cleanly and overwrite the frontmatter.
```

---

## Implementation Order

Do these in sequence — each depends on the previous being in place.

1. **Add `state.yaml` templates** to all 28 workflow directories (no logic changes yet — just the empty files)
2. **Add frontmatter** to all 104 step files (no logic changes — just the schema at the top)
3. **Add STATE CHECK block** to all 28 `workflow.md` files (now the schema is there to be read)
4. **Add Activation sections** to all 6 sub-agent files
5. **Update `agents/master.md`** — boot scan + workflow lock
6. **Update `CLAUDE.md`** — boot step 8a
7. **Add convention sections** to `SYSTEM.md`

---

## File Count Summary

| Change | Files |
|--------|-------|
| New `state.yaml` files | 28 |
| Step files with new frontmatter | 104 |
| `workflow.md` files with STATE CHECK | 28 |
| Sub-agent files with Activation section | 6 |
| `agents/master.md` | 1 |
| `CLAUDE.md` | 1 |
| `SYSTEM.md` | 1 |
| **Total** | **169** |
