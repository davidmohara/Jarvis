---
name: one-texas-scorecard
description: Pull revenue, co-sell, pipeline, and new client data for One Texas via Chase skills and append to the Obsidian scorecard tracking file.
agent: chase
---

# One Texas Scorecard Workflow

**Goal:** Assemble a complete One Texas scorecard snapshot by running four Chase skills in
sequence, then append the consolidated output to the Obsidian tracking file with today's date.

**Agent:** Chase — Revenue & Pipeline

**Architecture:** 5-step sequential workflow. Steps 1-4 each run a Chase skill and collect
output. Step 5 checks the Obsidian file for recency, prompts if last entry is recent, then
appends the full snapshot.

---

## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — data already gathered. Do not re-pull it.
   - Notify the controller: "[Chase]: Resuming one-texas-scorecard from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`,
     write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Surface to controller: "[Chase]: one-texas-scorecard was previously aborted at
     [current-step]. Resume or start fresh?"
   - Wait for instruction.

---

## EXECUTION

Read and follow each step file in order:

1. `steps/step-01-revenue.md`
2. `steps/step-02-co-sell.md`
3. `steps/step-03-pipeline.md`
4. `steps/step-04-new-clients.md`
5. `steps/step-05-save-to-obsidian.md`

Do not proceed to the next step until the current step is complete. After each step,
update `state.yaml` with `current-step` and append the step's output to
`accumulated-context`.
