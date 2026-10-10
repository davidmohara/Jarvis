---
name: plaud-ingest
description: Full Plaud recording ingestion pipeline — discover new recordings, trigger transcription, identify speakers via calendar, fetch to staging, and ingest to vault
agent: knox
model: haiku
---

<!-- system:start -->
# Plaud Ingest Workflow

**Goal:** Discover all new Plaud recordings, get them transcribed, identify who was in them, land them as properly tagged Obsidian notes with David-owned action items routed to Monday (unassigned — Alice Mburu triages), and share each recording (transcript + summary) with Alice Mburu via email.

**Agent:** Knox — Knowledge Manager

**Architecture:** Sequential 7-step pipeline with one interactive pause point at step-03 (speaker identification). Steps 01-02, 04-05, 05b, and 06 are fully autonomous. Step-03 may surface questions to the controller before proceeding. Step-06 is the adversarial verification pass (Ralph) that accounts for every discovered recording.

**Parallelism:** This workflow is designed to run as a background Agent launched during boot. It completes autonomously except for the speaker identification step, where it will surface questions to the controller and then continue after receiving answers. Boot does not wait for this workflow to finish.

**Dispatch model:** This workflow runs as a **Knox** subagent spawned by the coordinator (background during boot), never inline in the coordinator's session. The coordinator never touches Plaud staging, the vault, or Monday directly; Knox owns every step below.
<!-- system:end -->

---

<!-- system:start -->
## STATE CHECK

Read and follow `reference/state-check-protocol.md` before any execution. Workflow: `plaud-ingest`; agent: `knox`.

**Variant:** extra case `status: awaiting-input`: the run is paused for speaker identification. Read `accumulated-context.pending-speaker-mappings`, do not re-ask, apply any answers and proceed to step-04, or re-surface the speaker questions if none are present. `status: blocked` is treated with aborted: reset to `status: not-started`, clear the `blocker` field, notify the controller, and proceed to step-01 without waiting.

---

## TOKEN PRE-CHECK PROHIBITION

**Do NOT check for token files before running step-01. Do NOT abort due to missing token files. Do NOT inspect `~/.config/plaud/token.json` or `~/.config/plaud/credentials.json` before executing the skill.**

The `plaud-discover` skill and `fetch_plaud.py` script handle all authentication — including acquiring a new token via Chrome login flow when no cached token exists. Pre-checking for a token file before running the skill is a protocol violation (see `err-20260730T143152-S0TRMO`).

The only authorized auth check: let the skill run. If the skill's own auth flow fails after attempting the Chrome login, then report auth failure and abort.

---

## EXECUTION

Run STATE CHECK above, then begin at step-01.

---

## Steps

| Step | File | Skill | Description |
|------|------|-------|-------------|
| 01 | `steps/step-01-discover.md` | `skills/plaud-discover/SKILL.md` | Query Plaud API and identify recordings not yet in vault |
| 02 | `steps/step-02-trigger-transcription.md` | `skills/plaud-trigger/SKILL.md` | Trigger transcription for recordings missing it; check pending queue |
| 03 | `steps/step-03-identify-speakers.md` | `skills/plaud-speaker-id/SKILL.md` | Cross-reference speakers against calendar; prompt controller if unresolvable |
| 04 | `steps/step-04-fetch-staging.md` | `skills/plaud-transcripts/scripts/fetch_plaud.py` | Run fetch script to pull all ready transcripts to staging |
| 05 | `steps/step-05-ingest-vault.md` | `skills/plaud-transcripts/SKILL.md` | Transform staged files into Obsidian notes, route Monday, clean up |
| 05b | `steps/step-05b-share-with-alice.md` | `skills/plaud-transcripts/scripts/fetch_plaud.py --share` | Share each ingested recording publicly (transcript + summary) and email link to Alice Mburu |
| 06 | `steps/step-06-verify-ingest.md` | `workflows/plaud-ingest-verification/workflow.md` | Adversarial verification (Ralph): account for every discovered recording as a note or a logged skip, zero silent drops |

## Deterministic Step Guardrails

Every step transition is machine-checked. The verifiers in `workflows/plaud-ingest/verify/` run at each step's completion (dispatched by `.claude/hooks/step-complete.py`) and record a pass/retry/fail verdict with derived fields on the run's eval record. Manual review is not the gate. Step-06 adds the adversarial layer: Ralph's ingestion-accounting verdict is recorded as an `adversarial-verification` guardrail checkpoint.

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
  recording-classification: {}      # {file_id: "personal" | "work"} — set in step-03
  ready-for-fetch: []               # file_ids confirmed ready after all above
  staged-files: []                  # filenames written to ~/Downloads/transcript-staging/
  ingested-notes: []                # vault paths of notes successfully written
  unresolved_speakers: []           # Gate 4 (step-03): snapshot of speakers that survived
                                     # embedding-match, self-ID, and calendar resolution —
                                     # tracked here even after the awaiting-input pause
                                     # resolves and pending-speaker-mappings is cleared
```

## Quality Gates

Six deterministic gates run across the steps below:

| Gate | Step | Type | Checks |
|------|------|------|--------|
| 1 — Token/Auth Confirmation | step-01 | HARD | Post-hoc only — confirms `plaud-discover` actually obtained a usable auth session after it ran; never a pre-check. See step-01 for why that distinction is load-bearing. |
| 2 — Recording Metadata Validation | step-01 | SOFT (hard exclusion only for missing `file_id`) | Validates `file_id`/`transcript_status`/`date`/`duration_seconds`/`name` on every discovered recording before handoff to step-02. |
| 3 — Transcription Success | step-02 | HARD, per-recording | Retries the two-step trigger up to 3 times on transient failure; excludes the recording after 3 failures. Does not apply to the `-1`/`-12` minutes-exhausted case, which stays no-retry. |
| 4 — Speaker Identification Completeness | step-03 | SOFT | Formalizes "unresolved speaker" and logs it to `unresolved_speakers`; does not alter the awaiting-input pause. |
| 5 — Vault Filing Verification | step-05 | HARD, per-note | Confirms the note actually exists at its path with required frontmatter after an Obsidian MCP write reports success. |
| 6 — Delivery Routing Confirmation | step-05b | HARD, per-recording | Confirms no assignee is set (Alice Mburu triages and assigns in Monday) and the correct channel (board/group + share link) before the workflow marks itself complete. Renamed from a requested "Slack routing" gate — this workflow has no Slack delivery; see step-05b for the reinterpretation rationale. |

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

This workflow only adds files to the vault and Monday — it never modifies or deletes existing content. If an ingest produces bad output, delete the specific vault note. The staging folder is cleaned up at the end of step-05, but the Plaud API data is never modified except for speaker renames explicitly requested during step-03.
<!-- system:end -->

<!-- personal:start -->
> **⚠️ Task E enforcement — Plaud ingest:** Spawning Knox as a background Agent with `workflows/plaud-ingest/workflow.md` is the ONLY way to satisfy this step. A manual `ls` of `~/Downloads/transcript-staging/` or reading `plaud_pending.json` does NOT count. If Knox is not spawned and allowed to run all 5 steps (discover → trigger → identify speakers → fetch → ingest), Task E is NOT complete. Mark it failed, not completed. (Error ref: err-20260611T113806-g0pfoq)
<!-- personal:end -->
