# Relocated content: audience-target-outreach rationale

- Origin: workflows/audience-target-outreach/workflow.md (INITIALIZATION, "Why This Exists" section, ~lines 45-60)
- Date: 2026-10-10
- Reason: Phase A cleanup. Narrative rationale is not an instruction. The load-bearing rule (send path goes through Customer Insights - Journeys, never Outlook/Superhuman) stays in the workflow file as a short note; the full rationale is preserved here.

## Original text

A grounded episode brief is only valuable if it turns into real outreach to real people, and that outreach has to be attributable, not a pile of personal emails David can't tie back to a campaign later. This workflow exists to guarantee: real accounts and contacts (never invented), content held to the same quality bar as `harper-email`, and a send path that is CRM-native by design so response tracking actually works.

**Send path, read before touching this workflow:** Outbound send goes through a Dynamics **Customer Insights - Journeys** Segment/Journey, never through Outlook or Superhuman. This is deliberate, not a placeholder to be "reconciled" later. See `skills/campaign-setup/SKILL.md` and `skills/campaign-send/SKILL.md` for the full rationale. David's personal email drafting via `harper-email` is untouched and still used for everything else.
