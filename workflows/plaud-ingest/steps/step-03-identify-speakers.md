---
status: completed
model: haiku
started-at: "2026-09-18T17:03:30Z"
completed-at: "2026-09-18T17:06:00Z"
outputs:
  gate_4_result: "pass"
  gate_4_unresolved_speakers: []
  notes: >
    pi-20260918-001: 1 recording in ready-for-fetch (f96b2c110fc35162f390ac5288d6f7f4,
    "09-18 Meeting: AI Project Architecture and Data Routing", 2026-09-18 15:36 UTC /
    10:36 CDT, ~31.5 min). No _speakers.json in staging (pre-fetch); queried live API
    per skill step -1. Recording's live trans_result already carries real names — Plaud
    auto-resolved both speakers (registered voice profiles): Speaker 1 = O'Hara (David,
    39 segments), Speaker 2 = Vladimir Avila (48 segments, Improving Mexico delivery,
    known from 09-17 GEHC sync). Zero generic labels — no embedding computation, self-ID
    scan, or controller escalation needed. Self-ID corroborated by transcript ("Hey Vlad.
    Hey David."). Calendar cross-reference: no event matches the recording window — David
    is on an all-day personal retreat (Houston hotel check-in 09-18); this was an impromptu
    ad-hoc call, consistent with transcript small talk ("Are you in the hotel"). No
    invite exists, so step-3 attendee validation is n/a; both names are registered Plaud
    profiles (exempt). Informational only: "Mike" referenced as the author of a shared
    document (likely Michael Braunstein, GEHC team) — mentioned, not a speaker; not
    blocking. Classification: work (client AI POC architecture/routing discussion; no
    personal keywords in title or content). Gate 4: pass.
  notes_prior_run: >
    pi-20260917-001: 1 recording in ready-for-fetch (e2d6f3c0cfe76328329cd273da8d55cb,
    "09-16 Weekly Meeting: P2 AI Project Plan, Model Testing, and Scope Risks",
    2026-09-16 15:00-15:45 UTC). 9 speakers detected: 2 already natively named
    (O'Hara = David, Devlin) and 7 generic labels (Speaker 1,2,4,6,7,8,9). None of
    the 7 generic voices matched a registered Plaud profile (checked list_speakers;
    all 7 are first-time voices for this account). Full-transcript self-ID scan with
    introductions resolved every label directly: Speaker 1 self-identified "I'm Chris
    Miller... Dev Manager here at Simpson"; Speaker 2 "my name's Gilbert"; Speaker 4
    addressed as "Lynn" throughout (Lyn Barrett, improving.com); Speaker 6 "John"
    (Simpson side); Speaker 7 "my name AI... working with the team in Vietnam side";
    Speaker 8 addressed as "Fernando" (Improving delivery, brought in by Lynn with
    Jose); Speaker 9 addressed as "Lauren" (John: "Lauren's gonna own it"). Calendar
    cross-reference matched event "AI Takeoff Weekly Touch - Improving & SST"
    (organizer givelasquez@strongtie.com), 15:00-15:45 UTC, exact window match.
    Attendee emails map Speaker 1 = Chris Miller (chmiller@strongtie.com), Speaker 2 =
    Gilbert Velasquez (givelasquez@strongtie.com), Speaker 4 = Lyn Barrett
    (lyn.barrett@improving.com), Speaker 6 = John Tsiros (jtsiros@strongtie.com),
    Speaker 9 = Lauren Clack (lauren.clack@improving.com). Speaker 7 (Ai) and Speaker 8
    (Fernando) are Improving Vietnam/Mexico delivery team members not on the top-line
    invite; both self-identified or were directly named on-call, resolved without
    controller escalation (off-invite note only). No unresolved speakers across the
    recording -- Gate 4 result: pass. Classified work (Simpson Strong-Tie P2 AI
    project weekly).
  notes_prior_runs: >
    pi-20260914-001: 3 recordings, all resolved via calendar/self-ID, Gate 4 pass.
    pi-20260909-001: 1 recording (Speaker 2) escalated to controller, resolved
    separately from that run.
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
   - **FAILURE MODE PREVENTED**: err-20260909T000829-0JTVV6 (spent 30+ minutes searching calendar via MCP, got null attendees, asked controller instead of reading calendar file directly)

2. **Transcript self-identification (REQUIRED SECOND)** — For speakers calendar didn't resolve:
   - Read the FULL transcript (not just `sample_text`). Check END OF CALL FIRST (sign-offs), then beginning (introductions), then entire body.
   - Look for explicit self-introduction: "I'm [Name]", "[Name] here", "this is [Name]", or indirect: "my firm is called [Name]", "I work at [Company]"
   - A speaker who self-identifies in the transcript is resolved. No calendar confirmation needed. This step is mandatory.
   - Check for transcription errors that garble names ("even considering me having not known me" → likely "even considering you having not known [Name]")
   - **FAILURE MODE PREVENTED**: err-20260909T010719-0BCW7C (skipped reading full transcript, asked controller for "Renzi Stone" when "Renzi" was mentioned in transcript)

3. **Registered-speaker embedding match (OPTIONAL THIRD)** — Only for speakers still unresolved after steps 1 and 2:
   - Check whether Plaud itself already knows this voice via `get_speaker_embeddings()` vs registered profiles
   - A near-1.0 match provides confidence but is not a replacement for calendar or transcript
   - Use this to disambiguate when transcript self-ID is weak or calendar has multiple matches

**Only if all three are exhausted with no confident match: add to `pending-speaker-mappings` for controller escalation.**

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
