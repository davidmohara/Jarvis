---
name: inbox-processing
description: Triage task inbox items to zero - assign each item a disposition and execute
agent: chief
model: sonnet
---

<!-- system:start -->
# Inbox Processing Workflow

**Goal:** Process every task inbox item to zero. Each item gets triaged against quarterly rocks and assigned a clear disposition.

**Agent:** Chief — Daily Operations & Execution

**Architecture:** Interactive loop workflow. Pull all inbox items, present each with a recommended disposition, get controller confirmation, execute. Repeat until inbox is empty.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Task management | All inbox tasks (name, note, date created) | `omnifocus-data` skill — `python3 skills/omnifocus-data/scripts/omnifocus_data.py list --kind inbox` |
| Quarterly objectives | Current rocks for prioritization | Read memory/personal/quarterly-objectives.md |
| Delegation tracker | Current delegations for context | Read delegations/tracker.md |

### Disposition Categories

| Disposition | Action |
|-------------|--------|
| **Do** | Urgent + important. Handle today. Assign to a project via the `omnifocus-tasks` skill. |
| **Delegate** | Hand off. Add to delegation tracker. Create task with person tag via the `omnifocus-tasks` skill. |
| **Defer** | Important, not urgent. Assign to project with due date via the `omnifocus-tasks` skill. |
| **Decide** | Needs a decision file. Create in decisions/ folder. |
| **Reference** | Not actionable. File into knowledge layer or reference docs. |
| **Delete** | Not worth keeping. Mark complete via the `omnifocus-tasks` skill — assign it to a project first, because inbox tasks cannot be completed directly. |

Every OmniFocus write in this workflow goes through `skills/omnifocus-tasks/SKILL.md`, which is gate-enforced on project and tag. Every OmniFocus read goes through `skills/omnifocus-data/SKILL.md`. There is no other authorized path.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
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

Read fully and follow: `steps/step-01-pull-inbox.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
