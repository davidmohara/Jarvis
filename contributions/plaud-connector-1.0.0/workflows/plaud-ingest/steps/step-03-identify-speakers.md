---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
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

**Agent:** Knowledge Manager (Knox)
**Skill:** `skills/plaud-speaker-id/SKILL.md` — read it in full before executing this step.
**Input:** `accumulated-context.ready-for-fetch`, staging folder `_speakers.json` files, calendar (dataverse-aware)
**Output:** `accumulated-context.speaker-mappings` — complete mapping for all recordings

---

## DATAVERSE-AWARE CALENDAR

This step uses the calendar connector configured by `dataverse` in `config/settings.json`.
Per `skills/plaud-speaker-id/SKILL.md`:
- `dataverse: m365` → use M365 Outlook calendar MCP
- `dataverse: google` → use Google Calendar MCP

Do NOT hardcode a specific calendar provider here. The skill handles the lookup.

---

## YOUR TASK

### Sequence

1. **Scan staging for speaker files.** For each recording in `ready-for-fetch`:
   - Check for `plaud_{name}_speakers.json` in `~/Downloads/transcript-staging/`
   - If no speaker file: no generic speakers — this recording needs no mapping. Mark as resolved.

2. **For each `_speakers.json` found:** attempt calendar auto-resolution per `skills/plaud-speaker-id/SKILL.md`:
   - Pull the recording's date and approximate time from the JSON metadata
   - Search calendar via the dataverse-configured connector for events overlapping that time window (+/- 15 minutes)
   - Get attendee list from the matching calendar event
   - Cross-reference attendee names against generic speaker labels using segment count heuristics:
     - Highest segment count is typically the meeting owner (they talk most in their own meetings)
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

1. **Calendar attendees match speaker count exactly** and the owner is an attendee: assign owner to highest segment count speaker.
2. **Sample text contains a name** ("...as Todd mentioned..." → that speaker knows Todd → likely the owner speaking about Todd).
3. **Segment count pattern**: in a 2-person meeting, the host typically has 55-70% of segments.
4. **Known speakers list from Plaud**: if Plaud already has a registered voice profile matching a speaker, use it.

If none of these produce high confidence, put the recording in `pending-speaker-mappings`.

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
| Recording has no calendar event match | Use recording title and known attendees from CRM if available. If still unresolved, ask controller. |
| Controller provides partial answer | Apply what was given. Re-surface remaining unresolved speakers in the next interaction. |

---

## NEXT STEP

Read fully and follow: `step-04-fetch-staging.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
