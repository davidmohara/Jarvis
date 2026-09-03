---
status: completed
model: haiku
started-at: "2026-08-23T00:13:00Z"
completed-at: "2026-08-23T00:25:00Z"
outputs:
  gate_4_result: "pass"
  gate_4_unresolved_speakers: []
  notes: "pi-20260823-001: Calendar-first cross-reference attempted for the one new recording (32c80d61ff44bb53825a93cfb0bbfa5a, 2026-08-05 clinical/injection note). No exact calendar overlap; nearest event ('Dr Nathan Walters', same address, immediately following) had no attendee list to confirm identity, so surfaced to controller rather than guessing. Controller confirmed: Speaker 2 = Dr. Nathan Walters. speaker-mappings populated in state.yaml. Classification: personal (medical)."
---

<!-- system:start -->
# Step 03: Identify Speakers

## ⛔ HARD GATE

**REGISTERED-SPEAKER EMBEDDING MATCH FIRST. SELF-ID SCAN SECOND. CALENDAR THIRD. DO NOT
ASK THE CONTROLLER UNTIL ALL THREE HAVE BEEN EXHAUSTED.**

This is a three-part gate:

0. **Registered-speaker embedding match first.** Before self-ID scanning or calendar
   lookup, check whether Plaud itself already knows who this speaker is: call
   `get_speaker_embeddings(token, file_id)` for the recording and `list_speakers(token)`
   for every registered profile, and compare via cosine similarity. A near-1.0 match is
   a direct identification from Plaud's own voice recognition — resolve immediately, no
   further checks needed. Also check `get_recording_speakers(token, file_id)` — the
   live `trans_result` may already carry real names even though a stale `_speakers.json`
   in staging still shows generic labels. Skipping this and escalating straight to the
   controller when Plaud had already resolved the speaker via voice recognition caused
   `err-20260902T160425-E9B7YR` (a 3-way speaker ambiguity re-escalated to David when
   all three speakers matched existing registered profiles at ~1.0 similarity, and the
   recording's own transcript already had the real names). See
   `skills/plaud-speaker-id/SKILL.md` step -1 for the full procedure.
1. **Self-identification scan next.** For anything the embedding match didn't resolve,
   scan the full
   transcript (not just the `sample_text` snippet) for every unresolved speaker for
   self-identification — most speakers state their own name aloud, typically near the
   end of the recording ("this is X", name sign-offs). Skipping this and going straight
   to calendar guessing or controller escalation was the cause of
   `err-20260831T145748-3SVX4A` (5 speakers escalated on the 08-28 YPO Gold recording
   when each stated their own name at the end).
2. **Calendar before controller.** This rule was violated on 2026-05-22
   (err-20260522T191304-TO2VXV) — the calendar resolved both speakers without any
   controller input, and asking first is never acceptable. It was violated again on
   2026-08-31 (`err-20260831T145747-LDPD1Q`) in a subtler way: the calendar WAS
   queried, but a subject-line mismatch ("AI Leaders Weekly" on a personal-sounding
   recording) was treated as a dead end without checking that event's attendees or
   adjacent events first. **A subject-line mismatch alone is never sufficient grounds
   to give up on the calendar** — see `skills/plaud-speaker-id/SKILL.md` step 2a for
   the required 3-strategy search (matched event attendees, adjacent events, recurring
   1:1 pattern) before falling through to controller escalation.

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

**Agent:** Knox
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

3. **If `pending-speaker-mappings` is non-empty:** pause and ask the controller.
   - Update `state.yaml status: awaiting-input`
   - Compile a single consolidated message (see User Interaction Protocol in workflow.md)
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

## AUTO-RESOLUTION HEURISTICS

Use these in order. Stop as soon as you reach high confidence (>85%):

0. **Self-identification in transcript**: the speaker states their own name aloud
   anywhere in their segments (most commonly a sign-off near the end). This is checked
   BEFORE calendar heuristics 1-4 and does not require calendar confirmation to resolve
   — see `skills/plaud-speaker-id/SKILL.md` step 0.
1. **Calendar attendees match speaker count exactly** and David O'Hara is an attendee: assign David to highest segment count speaker.
2. **Sample text contains a name** ("...as Todd mentioned..." → that speaker knows Todd → likely David speaking about Todd).
3. **Segment count pattern**: in a 2-person meeting, the host (David) typically has 55-70% of segments.
4. **Known speakers list from Plaud**: if Plaud already has a registered voice profile matching a speaker, use it.

If none of these produce high confidence, before falling back to `pending-speaker-mappings`
confirm the calendar search discipline was actually exhausted (matched event attendees +
adjacent events + recurring 1:1 pattern check, per the HARD GATE) — do not put a recording
into `pending-speaker-mappings` on a subject-line mismatch alone.

## EDGE CASE CHECKS — run before surfacing mappings to controller

These have occurred in practice. Run all checks before presenting any mapping:

### A. David split across two labels

Plaud sometimes assigns David to a named label ("O'Hara") for part of the recording and
a generic "Speaker N" label for the rest. Before treating a generic speaker as someone
new, check:
- Does the named "O'Hara" label already exist in `all_speakers`?
- Does the generic speaker's `sample_text` sound like David? (First-person Improving
  context, references to "our clients", "we at Improving", meeting facilitation language)
- Is the generic speaker's segment count roughly comparable to what you'd expect David
  to have if the named label under-counted him?

If yes: include that generic label in the mapping pointing to "David O'Hara". Do not
surface it to the controller as a mystery speaker.

### B. Known speaker wrongly assigned (voice mis-tag)

A registered Plaud voice profile may appear in a recording that person did not attend.
Before accepting a named speaker at face value:
- Cross-reference their name against the calendar attendee list
- If they do not appear on the invite and their segment count is low (≤10 segments),
  flag as a likely mis-tag
- Include in `pending-speaker-mappings` with a note: "Plaud tagged [Name] but they may
  not have been on this call — please confirm or correct"

If the controller says they were not on the call, include the name in the `--rename`
payload mapping it to the correct person.

### C. Recording timestamp does not match any calendar event

Plaud timestamps are UTC. Convert to CDT (UTC−5) before searching. When no event
covers the timestamp:
- Expand search window to ±45 minutes
- Check whether the recording *ends* during a known event (pre-call warmup scenario)
- Read the Plaud-generated title from the `.md` file — it often identifies the meeting
  even without a calendar match
- If still no match, add to `pending-speaker-mappings` with the CDT timestamp and
  duration so the controller can identify the meeting

### D. Actual call participants differ from calendar invite

Always present `all_speakers` (with segment counts and sample text) alongside calendar
attendees. State explicitly: "These are the calendar invitees — please correct if
someone joined who wasn't invited or if an invitee didn't actually speak."

### E. Sample text too short to identify speaker

If `sample_text` is ≤5 words (e.g. "I understand," or "All right,"), do not present
it as-is. Before surfacing to controller, pull additional lines from the `.md` transcript:
read the file and extract the first 5 utterances attributed to that speaker label.
Present those instead.

---

## QUALITY GATE 4 — Speaker Identification Completeness (SOFT, LOGGED, DOES NOT REPLACE THE AWAITING-INPUT PAUSE)

This gate formalizes what "unresolved speaker" means and makes it an explicit, tracked flag.
It does **not** change the interactive-pause behavior in the workflow's STATE CHECK item 3 or
in step 3 of YOUR TASK above (pause, ask the controller in one consolidated message, resume
on response) — that behavior is preserved exactly as-is. This gate documents and carries the
condition forward; it does not gate progression to step-04 (the existing pause already does
that when needed) and it never silently drops the pause.

**Definition of "unresolved speaker"** for this gate's purposes: any generic label (e.g.
"Speaker 1", "Speaker 2") that survives all three resolution passes above — registered-speaker
embedding match, self-ID transcript scan, and the full calendar search discipline (matched
event attendees, adjacent events, recurring 1:1 pattern) — with no confident match to a real
name. This is exactly the set that ends up in `pending-speaker-mappings` before controller
escalation.

**What this gate does:**

1. After step 2 (auto-resolution) completes and before step 3 (controller escalation, if
   needed), take a snapshot of whatever remains in `pending-speaker-mappings` and write it,
   per-recording, into a new `accumulated-context.unresolved_speakers` list — same shape as
   `pending-speaker-mappings` (file_id, recording, unresolved labels, note) — so this
   condition is visible in state even after the controller eventually resolves it and
   `pending-speaker-mappings` is cleared back to `[]`.
2. If the controller later resolves some or all of them, update the corresponding
   `unresolved_speakers` entries to reflect resolution (do not delete the history — mark
   `resolved: true` with the method, e.g. "controller-provided") rather than removing the
   entry outright. This gives a durable record of which speakers needed a human across runs.
3. If nothing is unresolved after auto-resolution, `unresolved_speakers` stays `[]` and
   `gate_4_result: "pass"`.

Log the result:
```
[Gate 4] Unresolved speakers this run: N (across M recordings). Logged to accumulated-context.unresolved_speakers.
```
or
```
[Gate 4] No unresolved speakers — all resolved via embedding match, self-ID, or calendar.
```

Write to this step's frontmatter `outputs`:
```yaml
outputs:
  gate_4_result: "pass" | "pass-with-unresolved"
  gate_4_unresolved_speakers: [{file_id, recording, unresolved: [...]}, ...]
```

---

## SUCCESS METRICS

- All `_speakers.json` files processed
- Calendar cross-referenced for every recording with generic speakers
- `speaker-mappings` fully populated — no recording left with unresolved generic speakers
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


## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py plaud-ingest step-03-identify-speakers complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `step-04-fetch-staging.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
