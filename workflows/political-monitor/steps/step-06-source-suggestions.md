---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 06: Weekly Source Suggestions (Mondays Only)

## MANDATORY EXECUTION RULES

1. Run this step only if today is Monday. Otherwise skip to step-07.
2. For EACH candidate, run the accessibility probe first. A `400` means blocked; never suggest a blocked source.

---

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline in the coordinator's session.
**Input:** The current roster in `sources.json`, today's date
**Output:** Vetted candidate sources written to `suggestions/YYYY-MM-DD.json` and the run JSON's `suggestions` array

---

## YOUR TASK

If today is Monday: propose 2-3 candidate sources NOT already in the roster that fill an underrepresented lean or beat. For EACH candidate, run the accessibility probe first:
`WebSearch(query="politics", allowed_domains=["<candidate_domain>"])` - a `400` means blocked; never suggest a blocked source.
Write the vetted candidates (name, lean, search_domain, one-line rationale, accessible:true) to `systems/political-monitor/suggestions/YYYY-MM-DD.json`, and also add them to the run JSON's `suggestions` array so they render on the dashboard. David replies "add X" / "skip X" to Jarvis, who edits `sources.json`.

## NEXT STEP

Read fully and follow: `step-07-render-validate.md`
<!-- system:end -->
