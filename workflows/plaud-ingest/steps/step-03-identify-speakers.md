---
status: completed
model: kimi-k3
started-at: "2026-10-27T14:57:30Z"
completed-at: "2026-10-27T15:11:00Z"
---

<!-- system:start -->
# Step 03: Identify Speakers

## ⛔ HARD GATE — PRIMARY SOURCE HIERARCHY

**CALENDAR FIRST (REQUIRED). TRANSCRIPT SELF-ID SECOND (REQUIRED). REGISTERED EMBEDDING THIRD (OPTIONAL). DO NOT ASK CONTROLLER UNTIL CALENDAR + TRANSCRIPT BOTH EXHAUSTED.**

This is a hierarchy, not alternatives. Controller escalation only after 1 AND 2 have been fully attempted:

1. **Calendar attendees (PRIMARY SOURCE — MANDATORY FIRST)** — Before any other check:
   - Find the calendar event matching the recording timestamp (±15 min window, converted to CDT)
   - Extract the attendee list from the calendar event
   - Match attendees to speaker labels using segment counts + sample text
   - RULE: If calendar has attendee data for the time window, Speaker ID is RESOLVED. Calendar attendees are the authority.
   - If no event matches after ±15 min search: expand to ±45 min, check adjacent events, check recurring 1:1 patterns with names in transcript
   - Only after this full 3-strategy discipline fails: move to step 2 below
   - **FAILURE MODE PREVENTED**: `err-20260909T000829-0JTVV6`

2. **Transcript self-identification (REQUIRED SECOND)** — For speakers calendar didn't resolve:
   - Read the FULL transcript (not just `sample_text`). Check END OF CALL FIRST (sign-offs), then beginning (introductions), then entire body.
   - Look for explicit self-introduction: "I'm [Name]", "[Name] here", "this is [Name]", or indirect: "my firm is called [Name]", "I work at [Company]"
   - A speaker who self-identifies in the transcript is resolved. No calendar confirmation needed. This step is mandatory.
   - Check for transcription errors that garble names ("even considering me having not known me" → likely "even considering you having not known [Name]")
   - **FAILURE MODE PREVENTED**: `err-20260909T010719-0BCW7C`

3. **Registered-speaker embedding match (OPTIONAL THIRD)** — Only for speakers still unresolved after steps 1 and 2:
   - Check whether Plaud itself already knows this voice via `get_speaker_embeddings()` vs registered profiles
   - A near-1.0 match provides confidence but is not a replacement for calendar or transcript
   - Use this to disambiguate when transcript self-ID is weak or calendar has multiple matches

**Only if all three are exhausted with no confident match: add to `pending-speaker-mappings` for controller escalation.**

> **⛔ ESCALATION EVIDENCE IS MANDATORY (err-20260929T024338-K3K074).** An
> `awaiting-input` escalation is only valid if the run has (1) cross-referenced
> the recording timestamp against calendar attendees and (2) run the transcript
> self-ID scan. Before surfacing the prompt you MUST write the evidence for both
> into `accumulated-context.escalation-evidence` (a single string naming the
> matched event's time and the attendees checked, the adjacent/recurring events
> tried, and what the transcript self-ID scan returned) and record each
> unresolved speaker in `accumulated-context.unresolved_speakers`. An escalation
> that asks the controller without this recorded calendar cross-reference is the
> exact defect this step exists to prevent. The assertion `plaud-k4-escalation-evidence`
> (plaud-ingest) and `plaud-sp-004/005` (this skill) fail a run that escalates
> with no calendar evidence in that field.

> **⛔ NO GENERIC LABELS IN FINAL MAPPINGS.** `accumulated-context.speaker-mappings`
> must map every generic label to a real name. Never leave a value of the form
> `Speaker N` in `speaker-mappings` when an identification was possible — a
> speaker you cannot resolve goes in `unresolved_speakers` /
> `pending-speaker-mappings` with the calendar evidence above, not in
> `speaker-mappings` as `Speaker 1: "Speaker 1"`. Enforced by
> `plaud-k4-no-generic-speaker-labels`.

## MANDATORY EXECUTION RULES

1. You MUST check for `_speakers.json` files in `~/Downloads/transcript-staging/` for every recording in `ready-for-fetch`.
2. You MUST run the self-identification transcript scan for every unresolved speaker BEFORE calendar cross-reference. This is non-negotiable — see `skills/plaud-speaker-id/SKILL.md` step 0.
3. You MUST attempt calendar cross-reference (including attendees and adjacent events, not just the single matched event's subject line) BEFORE asking the controller. This is non-negotiable.
4. You MUST batch all unresolved speakers into a single consolidated question — never ask one recording at a time.
5. If ALL speakers resolve via self-ID and/or calendar, proceed silently — no user interaction needed.
6. Do NOT rename speakers in Plaud during this step — that happens in step-04 via `--rename`.
7. Do NOT proceed to step-04 until `speaker-mappings` is fully populated for all recordings that have `_speakers.json` files.

---

## EXECUTION PROTOCOL

**Agent:** Knox, spawned by the coordinator, never executed inline in the coordinator's session.
**Skill:** `skills/plaud-speaker-id/SKILL.md` — read it in full before executing this step.
**Input:** `accumulated-context.ready-for-fetch`, staging folder `_speakers.json` files, M365 calendar
**Output:** `accumulated-context.speaker-mappings` — complete mapping for all recordings

---

## YOUR TASK

### Sequence

1. **Scan staging for speaker files.** For each recording in `ready-for-fetch`:
   - Check for `plaud_{name}_speakers.json` in `~/Downloads/transcript-staging/`
   - If no speaker file: no generic speakers — this recording needs no mapping. Mark as resolved.

2. **For each `_speakers.json` found:** resolve per `skills/plaud-speaker-id/SKILL.md`, in this order:
   - **Self-ID scan first (step 0):** read the full transcript (not just `sample_text`) for
     every unresolved speaker and check for self-identification — check the end of the
     recording first (sign-offs), then the beginning (introductions), then anywhere else.
     A speaker who names themselves is resolved directly, no calendar needed.
   - **Calendar auto-resolution (step 2a) for whatever's left:**
     - Pull the recording's date and approximate time from the JSON metadata
     - Search calendar via M365 MCP for events overlapping that time window (+/- 15 minutes)
     - Get attendee list from the matching calendar event
     - **If the matched event's subject line doesn't obviously fit the transcript's
       topic, that is not a reason to stop** — still check that event's attendees, then
       check adjacent events (±30-60 min), then check for a recurring 1:1 pattern with
       any name mentioned in the transcript, before treating the calendar as unhelpful.
     - Cross-reference attendee names against generic speaker labels using segment count heuristics:
       - Highest segment count is typically David (he talks most in his own meetings)
       - Match remaining attendees to remaining speakers using sample text as context clues
   - If all speakers resolve with high confidence (via self-ID or calendar): auto-map them. Log the mapping and method (self-id / calendar).
   - Only after self-ID and the full calendar search discipline above are exhausted: add remaining unresolved speakers to `pending-speaker-mappings`.

3. **If `pending-speaker-mappings` is non-empty:** GUARDRAIL CHECKPOINT BEFORE escalating to controller.
   - **GATE**: Run this check before asking the controller:
     ```
     python3 systems/eval-harness/guardrail-checkpoint.py plaud-ingest step-03-pre-escalation step-03 <result> "<reason>"
     ```
     - If calendar search is incomplete (no calendar query attempt, or subject-line mismatch treated as final): `result=escalate reason="Calendar search was not fully attempted before escalation — re-run with full 3-strategy discipline (event attendees + adjacent events + recurring 1:1 pattern)"`
     - If transcript self-ID scan shows no evidence of end-of-call or name search: `result=escalate reason="Transcript self-ID scan incomplete — check end of recording and full text for speaker names before escalating"`
     - If both calendar and transcript were exhausted: `result=pass reason="Calendar and transcript fully exhausted; controller escalation is appropriate"`
   - If checkpoint returns `escalate`: **re-execute step-02/03 with full discipline**, do not ask controller yet
   - If checkpoint returns `pass`: proceed below to ask controller
   
   - **Write the escalation evidence to `state.yaml` BEFORE surfacing the prompt** (required — see the HARD GATE above):
     ```yaml
     accumulated-context:
       unresolved_speakers:
         - {file_id: <id>, recording: <name>, unresolved: ["Speaker 3"], evidence: "<what the calendar lookup returned and why it was insufficient>"}
       escalation-evidence: "<calendar: matched event <time> attendees <names>; adjacent/recurring tried <...>; transcript self-ID scan: <...>>"
     ```
   - Update `state.yaml status: awaiting-input`
   - Compile a single consolidated message (see User Interaction Protocol in workflow.md) that includes evidence of calendar search (event times, attendees checked, adjacent events) and transcript scan (end of call checked, names looked for)
   - Surface it to the controller and stop. Do not proceed until the controller responds.

4. **Classify recordings as personal or work:**
   - For each recording in `accumulated-context.speaker-mappings`, check:
     - **Calendar event title and description** for personal keywords: "doctor", "appointment", "personal", "medical", "wellness", "checkup", "lunch", "private", "family"
     - **Calendar event category** (if available in M365) for "Personal" or equivalent marking
     - **Plaud title** (from staged `.md` file) for personal indicators
   - If ANY personal keyword match: mark recording as `personal: true` in `accumulated-context`
   - If none match: mark as `personal: false`
   - Populate new field in accumulated-context: `recording-classification` (keyed by file_id):
     ```yaml
     recording-classification:
       <file_id>: "personal" | "work"
     ```
   - Log classification results in step output

5. **When controller responds (or if all were auto-resolved):**
   - Parse the controller's speaker assignments
   - Merge with auto-resolved mappings into `accumulated-context.speaker-mappings`
   - Update `state.yaml status: in-progress`
   - Update `accumulated-context.pending-speaker-mappings: []`

6. **Update state.yaml:**
   - `accumulated-context.speaker-mappings` = complete mapping
   - `accumulated-context.recording-classification` = personal/work labels for all recordings
   - `current-step: step-04`
   - Update this step's frontmatter: `status: completed`, `completed-at: <ISO timestamp>`

7. **Report:**
   ```
   [Knox/Speakers]: Speaker identification complete.
     Auto-resolved: N recording(s)
     Controller-resolved: N recording(s)
     No speaker file (clean): N recording(s)
   
     Personal recordings: N
     Work recordings: N
   ```

---

## AUTO-RESOLUTION HEURISTICS AND EDGE CASES

Read `references/speaker-id-heuristics.md` when resolving speakers after the primary-source hierarchy and before surfacing any mapping to the controller. It holds the ordered auto-resolution heuristics (stop at >85% confidence) and the five edge-case checks (A-E) that must all run before presenting mappings.

## QUALITY GATE 4 — Speaker Identification Completeness (SOFT, LOGGED, DOES NOT REPLACE THE AWAITING-INPUT PAUSE)

Run the Gate 4 protocol in `references/gate-4-unresolved-speakers.md` (read it after auto-resolution, before any controller escalation): snapshot `pending-speaker-mappings` into `accumulated-context.unresolved_speakers`, the resolution-marking rule, the log format, and the state.yaml schema (`gate_4_result`, `unresolved_speakers`, `escalation-evidence`). It does not gate progression to step-04 and never drops the interactive pause.

---

## SUCCESS METRICS

- All `_speakers.json` files processed
- Calendar cross-referenced for every recording with generic speakers
- `speaker-mappings` fully populated — no recording left with unresolved generic speakers
- `speaker-mappings` contains no generic-label VALUES (`Speaker N`); unresolved speakers are recorded in `unresolved_speakers` instead
- Any escalation wrote `accumulated-context.escalation-evidence` naming the calendar lookup performed before asking
- Controller interaction was a single consolidated message (not per-recording)

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Calendar unavailable | Self-ID scan still runs and resolves what it can. Skip calendar auto-resolution for the rest. Add remaining recordings with speaker files to `pending-speaker-mappings`. |
| Controller does not respond (async context) | Leave `status: awaiting-input` in state. Workflow will resume when controller next interacts. |
| Matched calendar event's subject line doesn't fit the transcript topic | Not a stop condition by itself. Check that event's attendees anyway, then adjacent events, then recurring 1:1 patterns, before treating as unresolved. |
| Recording has no calendar event match after full search (matched event, adjacent events, recurring pattern) | Expand to ±45 min window. Read Plaud-generated title from `.md`. Try Clay. If still unresolved, ask controller with CDT timestamp + duration. |
| Controller provides partial answer | Apply what was given. Re-surface remaining unresolved speakers in the next interaction. |
| David appears under two speaker labels | Map the generic label to "David O'Hara" in `--rename`. Do not surface as unknown. See Edge Case A above. |
| Named speaker appears but wasn't on the call (voice mis-tag) | Flag to controller. Apply correction via `--rename` — the script handles renaming existing named labels, not only generic ones. |
| Sample text is too short to be useful | Pull first 5 utterances from the `.md` transcript for that speaker before presenting to controller. |

---


## NEXT STEP

Read fully and follow: `step-04-fetch-staging.md`
<!-- system:end -->
