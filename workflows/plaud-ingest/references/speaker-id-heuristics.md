<!-- system:start -->
# Speaker-ID Heuristics and Edge Cases (plaud-ingest)

Used by step-03 after the primary-source hierarchy is exhausted and before any controller escalation.

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
<!-- system:end -->
