# Relocated: Plaud speaker-id mis-tag anecdotes

- Origin: skills/plaud-speaker-id/SKILL.md, step 3 validation-gate rationale
- Date: 2026-10-10
- Reason: Incident anecdotes removed from the skill during the commentary cleanup; the rule stays in the skill as a one-line rationale.

This exists because of a real, already-observed failure class: Plaud auto-tagged a
segment as "Robyn Fuentes" in the Jack Claeys "Bifurcated Engagement Strategy" recording
even though Robyn was never an attendee on that call; Knox caught it that time and
flagged it as non-blocking, but the skill itself had no systematic check for this. In
the same session, the "08-25 Meeting: AI Strategy..." recording has Speaker 5 (resolved
to Keith Oltchick) saying "Randy, do we have anyone doing that now?", addressing a
"Randy" who never appears on the calendar invite at all. Nothing mis-happened with Randy
this time, but a future name-drop heuristic (4) matching an off-invite name exactly the
same way would produce exactly the Robyn Fuentes failure again, silently.
