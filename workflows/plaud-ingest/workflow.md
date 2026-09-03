---
name: plaud-ingest
description: Full Plaud recording ingestion pipeline — discover new recordings, trigger transcription, identify speakers via calendar, fetch to staging, and ingest to vault
agent: knox
model: haiku
---

<!-- system:start -->
# Plaud Ingest Workflow

**Goal:** Discover all new Plaud recordings, get them transcribed, identify who was in them, land them as properly tagged Obsidian notes with action items routed to Monday, and share each recording (transcript + summary) with Alice Mburu via email.

**Agent:** Knox — Knowledge Manager

**Architecture:** Sequential 6-step pipeline with one interactive pause point at step-03 (speaker identification). Steps 01-02, 04-05, and 05b are fully autonomous. Step-03 may surface questions to the controller before proceeding.

**Parallelism:** This workflow is designed to run as a background Agent launched during boot. It completes autonomously except for the speaker identification step, where it will surface questions to the controller and then continue after receiving answers. Boot does not wait for this workflow to finish.
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

5. If `status: aborted` or `status: blocked`:
   - Reset to fresh run. Set `status: not-started`. Clear `blocker` field if present.
   - Notify the controller: "[Knox]: plaud-ingest was previously aborted/blocked — resetting to fresh run."
   - Proceed to step-01 immediately. Do NOT wait for instruction.

---

## TOKEN PRE-CHECK PROHIBITION

**Do NOT check for token files before running step-01. Do NOT abort due to missing token files. Do NOT inspect `~/.config/plaud/token.json` or `~/.config/plaud/credentials.json` before executing the skill.**

The `plaud-discover` skill and `fetch_plaud.py` script handle all authentication — including acquiring a new token via Chrome login flow when no cached token exists. Pre-checking for a token file before running the skill is a protocol violation and the direct cause of errors err-20260730T143152-S0TRMO, err-20260803T143125-2W5XDO, and err-20260812T142902-E6Z7KS.

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

Six deterministic gates were added across the steps below (additive hardening — no existing
rule, edge case, or the awaiting-input pause behavior was changed):

| Gate | Step | Type | Checks |
|------|------|------|--------|
| 1 — Token/Auth Confirmation | step-01 | HARD | Post-hoc only — confirms `plaud-discover` actually obtained a usable auth session after it ran; never a pre-check. See step-01 for why that distinction is load-bearing. |
| 2 — Recording Metadata Validation | step-01 | SOFT (hard exclusion only for missing `file_id`) | Validates `file_id`/`transcript_status`/`date`/`duration_seconds`/`name` on every discovered recording before handoff to step-02. |
| 3 — Transcription Success | step-02 | HARD, per-recording | Retries the two-step trigger up to 3 times on transient failure; excludes the recording after 3 failures. Does not apply to the `-1`/`-12` minutes-exhausted case, which stays no-retry. |
| 4 — Speaker Identification Completeness | step-03 | SOFT | Formalizes "unresolved speaker" and logs it to `unresolved_speakers`; does not alter the awaiting-input pause. |
| 5 — Vault Filing Verification | step-05 | HARD, per-note | Confirms the note actually exists at its path with required frontmatter after an Obsidian MCP write reports success. |
| 6 — Delivery Routing Confirmation | step-05b | HARD, per-recording | Confirms the correct recipient (Alice Mburu) and channel (Monday task + share link) before the workflow marks itself complete. Renamed from a requested "Slack routing" gate — this workflow has no Slack delivery; see step-05b for the reinterpretation rationale. |

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
