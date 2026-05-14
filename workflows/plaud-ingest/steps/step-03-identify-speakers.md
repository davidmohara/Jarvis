---
status: skipped
started-at: "2026-05-13T17:00:00Z"
completed-at: "2026-05-13T17:00:00Z"
model: sonnet
outputs:
  disposition: "skipped-per-controller-instruction"
  auto-resolved: 0
  pending-controller-input: 0
  notes: "Controller explicitly instructed to skip speaker identification for all unresolved speakers. Existing Plaud labels retained in vault notes."
---

<!-- system:start -->
# Step 03: Identify Speakers

## MANDATORY EXECUTION RULES

1. You MUST check for `_speakers.json` files in `~/Downloads/transcript-staging/` for every recording in `ready-for-fetch`.
2. You MUST attempt calendar cross-reference BEFORE asking the controller.
3. You MUST batch all unresolved speakers into a single consolidated question — never ask one recording at a time.
4. If ALL speakers resolve via calendar, proceed silently — no user interaction needed.
5. Do NOT rename speakers in Plaud during this step — that happens in step-04 via `--rename`.
6. Do NOT proceed to step-04 until `speaker-mappings` is fully populated for all recordings that have `_speakers.json` files.

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

2. **For each `_speakers.json` found:** attempt calendar auto-resolution per `skills/plaud-speaker-id/SKILL.md`:
   - Pull the recording's date and approximate time from the JSON metadata
   - Search calendar via M365 MCP for events overlapping that time window (+/- 15 minutes)
   - Get attendee list from the matching calendar event
   - Cross-reference attendee names against generic speaker labels using segment count heuristics:
     - Highest segment count is typically David (he talks most in his own meetings)
     - Match remaining attendees to remaining speakers using sample text as context clues
   - If all speakers resolve with high confidence: auto-map them. Log the mapping.
   - If one or more speakers cannot be confidently resolved: add to `pending-speaker-mappings`.

3. **If `pending-speaker-mappings` is non-empty:** pause and ask the controller.
   - Update `state.yaml status: awaiting-input`
   - Compile a single consolidated message (see User Interaction Protocol in workflow.md)
   - Surface it to the controller and stop. Do not proceed until the controller responds.

4. **When controller responds (or if all were auto-resolved):**
   - Parse the controller's speaker assignments
   - Merge with auto-resolved mappings into `accumulated-context.speaker-mappings`
   - Update `state.yaml status: in-progress`
   - Update `accumulated-context.pending-speaker-mappings: []`

5. **Update state.yaml:**
   - `accumulated-context.speaker-mappings` = complete mapping
   - `current-step: step-04`
   - Update this step's frontmatter: `status: completed`, `completed-at: <ISO timestamp>`

6. **Report:**
   ```
   [Knox/Speakers]: Speaker identification complete.
     Auto-resolved: N recording(s)
     Controller-resolved: N recording(s)
     No speaker file (clean): N recording(s)
   ```

---

## AUTO-RESOLUTION HEURISTICS

Use these in order. Stop as soon as you reach high confidence (>85%):

1. **Calendar attendees match speaker count exactly** and David O'Hara is an attendee: assign David to highest segment count speaker.
2. **Sample text contains a name** ("...as Todd mentioned..." → that speaker knows Todd → likely David speaking about Todd).
3. **Segment count pattern**: in a 2-person meeting, the host (David) typically has 55-70% of segments.
4. **Known speakers list from Plaud**: if Plaud already has a registered voice profile matching a speaker, use it.

If none of these produce high confidence, put the recording in `pending-speaker-mappings`.

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

## SUCCESS METRICS

- All `_speakers.json` files processed
- Calendar cross-referenced for every recording with generic speakers
- `speaker-mappings` fully populated — no recording left with unresolved generic speakers
- Controller interaction was a single consolidated message (not per-recording)

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Calendar unavailable | Skip auto-resolution. Add all recordings with speaker files to `pending-speaker-mappings`. |
| Controller does not respond (async context) | Leave `status: awaiting-input` in state. Workflow will resume when controller next interacts. |
| Recording has no calendar event match | Expand to ±45 min window. Read Plaud-generated title from `.md`. Try Clay. If still unresolved, ask controller with CDT timestamp + duration. |
| Controller provides partial answer | Apply what was given. Re-surface remaining unresolved speakers in the next interaction. |
| David appears under two speaker labels | Map the generic label to "David O'Hara" in `--rename`. Do not surface as unknown. See Edge Case A above. |
| Named speaker appears but wasn't on the call (voice mis-tag) | Flag to controller. Apply correction via `--rename` — the script handles renaming existing named labels, not only generic ones. |
| Sample text is too short to be useful | Pull first 5 utterances from the `.md` transcript for that speaker before presenting to controller. |

---

## NEXT STEP

Read fully and follow: `step-04-fetch-staging.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
