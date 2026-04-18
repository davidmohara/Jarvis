---
name: plaud-ingest
description: Full Plaud recording ingestion pipeline — discover new recordings, trigger transcription, identify speakers via calendar (dataverse-aware), fetch to staging, and ingest to the configured knowledge management system
agent: knox
model: haiku
---

<!-- system:start -->
# Plaud Ingest Workflow

**Goal:** Discover all new Plaud recordings, get them transcribed, identify who was in them,
and land them as properly tagged notes in the configured knowledge management system (KMS),
with action items routed to OmniFocus.

**Agent:** Knowledge Manager (Knox)

**Architecture:** Sequential 5-step pipeline with one interactive pause point at step-03
(speaker identification). Steps 01-02 and 04-05 are fully autonomous. Step-03 may surface
questions to the controller before proceeding.

**Parallelism:** This workflow is designed to run as a background Agent launched during boot.
It completes autonomously except for the speaker identification step, where it will surface
questions to the controller and then continue after receiving answers. Boot does not wait
for this workflow to finish.

## Configuration Dependencies

This workflow reads two configuration keys from `config/settings.json` before executing:

| Key | Purpose | Default |
|-----|---------|---------|
| `kms` | Knowledge management system target for ingest | `obsidian` |
| `dataverse` | Calendar provider for speaker identification | `m365` |

The `kms` key determines where notes are written (step-05).
The `dataverse` key determines which calendar is queried for speaker resolution (step-03).
<!-- system:end -->

---

<!-- system:start -->
## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context` — this is data already gathered. Do not re-gather it.
   - Check that step's frontmatter:
     - If `status: in-progress`: the step was interrupted mid-execution — re-execute it.
     - If `status: not-started`: begin it fresh.
   - Notify the controller: "[Knox]: Resuming plaud-ingest from [current-step]."

3. If `status: awaiting-input`:
   - The workflow is paused waiting for speaker identification input from the controller.
   - Read `accumulated-context.pending-speaker-mappings` to see what questions were asked.
   - Do NOT re-ask. If the controller is providing answers now, apply them and proceed to step-04.
   - If no answers are present in this session yet, re-surface the speaker questions.

4. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id` as
     `pi-YYYYMMDD-NNN`, write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

5. If `status: aborted`:
   - Do not resume automatically. Surface to controller:
     "[Knox]: plaud-ingest was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.

---

## EXECUTION

Run STATE CHECK above, then begin at step-01.

---

## Steps

| Step | File | Skill | Description |
|------|------|-------|-------------|
| 01 | `steps/step-01-discover.md` | `skills/plaud-discover/SKILL.md` | Query Plaud API and identify recordings not yet in KMS |
| 02 | `steps/step-02-trigger-transcription.md` | `skills/plaud-trigger/SKILL.md` | Trigger transcription for recordings missing it; check pending queue |
| 03 | `steps/step-03-identify-speakers.md` | `skills/plaud-speaker-id/SKILL.md` | Cross-reference speakers against calendar (dataverse-aware); prompt controller if unresolvable |
| 04 | `steps/step-04-fetch-staging.md` | `scripts/fetch_plaud.py` | Run fetch script to pull all ready transcripts to staging |
| 05 | `steps/step-05-ingest-vault.md` | `skills/plaud-transcripts/SKILL.md` | Transform staged files into KMS notes, route OmniFocus, clean up |

---

## State Schema

`accumulated-context` carries forward across steps:

```yaml
accumulated-context:
  target-date: YYYY-MM-DD           # date being processed
  new-recordings: []                # file_ids discovered in step-01
  transcription-triggered: []       # file_ids where transcription was triggered
  pending-recordings: []            # file_ids still generating transcript
  speaker-mappings: {}              # {file_id: {Speaker 1: "Real Name", ...}}
  pending-speaker-mappings: []      # recordings needing controller input
  ready-for-fetch: []               # file_ids confirmed ready after all above
  staged-files: []                  # filenames written to ~/Downloads/transcript-staging/
  ingested-notes: []                # KMS paths of notes successfully written
```

## User Interaction Protocol

When step-03 needs speaker identification input from the controller:

1. Pause execution. Update `state.yaml` with `status: awaiting-input`.
2. Surface a single consolidated block — all unresolved recordings at once, not one at a time:
   ```
   [Knox]: I need your help identifying speakers in X recording(s) before I can finish ingesting them.

   **"Recording Title" (2026-04-15)**
   Calendar attendees: David O'Hara, Todd Wynne
     Speaker 1 (42 segments): "I think we should look at the AI maturity..."
     Speaker 2 (31 segments): "The timeline for the POC is..."
   Who is Speaker 1 and Speaker 2?

   *(You can reply: "Speaker 1 = David, Speaker 2 = Todd" — I'll handle the rest.)*
   ```
3. Wait for controller response. When received, parse it, populate `speaker-mappings` in state, update `status: in-progress`, and continue from step-04.

## Rollback

This workflow only adds files to the KMS and OmniFocus — it never modifies or deletes existing
content. If an ingest produces bad output, delete the specific note from the KMS. The staging
folder is cleaned up at the end of step-05, but the Plaud API data is never modified except
for speaker renames explicitly requested during step-03.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
