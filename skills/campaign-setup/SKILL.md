---
name: campaign-setup
owning_agent: harper
model: sonnet
trigger_keywords: [set up the campaign, create the journey, create the segment]
trigger_agents: [harper]
description: >
  Seventh skill in the Podcast-to-Pipeline pipeline. Creates the Segment and
  Journey for an episode in Customer Insights – Journeys (not native Sales Quick
  Campaigns), naming per convention, and adds each targeted contact to the
  Segment. Pure CRM write — Plan-Only Mode required, dedup-checks against
  existing journeys before creating anything new. Called by
  workflows/audience-target-outreach/workflow.md step 04, once per episode
  (before the per-contact prospect-message-draft/campaign-send loop).
---

<!-- system:start -->
# Campaign Setup

## Purpose

Create (or correctly reuse) the CRM structures this whole system's attribution
depends on: one **Segment** (the target audience) and one **Journey** (the send
orchestration) per episode in **Customer Insights – Journeys** — the app
verified live in Improving's tenant, alongside 5 existing dormant journeys from
other employees' past experiments (2022–2025, all still Draft, none activated).
This build does **not** use native Sales "Quick Campaigns" or "Campaign
Members" — that native module was explicitly ruled out in favor of Customer
Insights – Journeys' Segment/Journey/Email/Email-insights structure. Do not
"simplify" this to Sales campaigns in a future edit.

## Input

- Episode metadata (title, episode number, date) from `episode-transcript-intake`
- Target contact list from `contact-targeting`

## Naming Convention

`Improving Edge — EP### — {Topic}`

e.g. "Improving Edge — EP047 — Supply Chain Pain Points." Use the episode
number if known; if not (e.g. a solo or unnumbered episode), use the episode
date instead: "Improving Edge — 2026-08-07 — {Topic}."

## Process

1. **Build-time config sanity check (run once per session before any write):**
   - Confirm a sending domain/email channel is actually configured and
     verified in Customer Insights – Journeys. An app being provisioned does
     not mean mail can actually send.
   - Confirm the Consent center's current state — Journeys sends are
     typically gated on recorded consent.
   - If either check cannot be confirmed as ready, stop before any write and
     report the gap to the controller. Do not assume either is ready just
     because the app is licensed and navigable.

2. **Dedup check.** Before creating anything, search existing Journeys/Segments
   in Customer Insights – Journeys for a name match or a clear topical
   collision — including against the 5 known dormant journeys ("Contoso
   Chairs - ABM Campaign," "Contoso Chairs splash campaign," "Houston - Event
   Communication," and two unnamed drafts). If a Segment/Journey for this
   exact episode already exists (e.g. this is a re-run after an interruption),
   reuse it — do not create a duplicate.

3. **Create the Segment** (Audience) named per convention, with filter
   criteria or an explicit static membership list matching the target
   contacts.

4. **Create the Journey** (Engagement) named per convention, in Draft status,
   configured to send from the Segment above. Do not activate/trigger the
   send here — that is `campaign-send`'s job, per-contact, with explicit
   confirmation.

5. **Add each target contact to the Segment.** Verify each contact resolves
   to an existing CRM Contact record (create one if genuinely new — this is
   the one contact-creation write this skill may need to make, and it should
   be flagged distinctly from Segment/Journey creation in the plan-only
   output).

6. **Return the created/reused Segment and Journey identifiers** to the
   caller so `campaign-send` knows exactly which records to use.

## Plan-Only Mode

If the prompt contains the phrase "do not execute" or `eval-mode: plan-only`,
do not run any live CRM write via Chrome/Playwright. Instead, produce a
markdown plan describing, in order: the dedup search you would run and
against which existing journeys; the exact Segment name, Journey name, and
filter/membership criteria you would create; and the list of contacts you
would add to the Segment, with a note on which (if any) require new Contact
records. Save the plan to the requested output path and stop. Do not call
any browser-automation write action under any circumstances in plan-only
mode.

## Failure Modes

| Failure | Action |
|---------|--------|
| Sending domain/email channel not configured or not verified | Stop before any write. Report: "Customer Insights – Journeys is provisioned but the sending domain isn't verified — campaign-setup can create the Segment/Journey in Draft, but campaign-send cannot fire until this is fixed. Flag to whoever owns Dynamics admin." |
| Consent center not in an expected state | Same as above — stop and flag, don't assume. |
| Name collision with an existing (even dormant) Journey | Do not overwrite. Either append a disambiguator to the name or ask the controller how to proceed. |
| CRM login wall / expired SSO | Flag to controller, retry once confirmed, per the CBRE-session pattern. |
| A target contact has no existing CRM Contact record | Create one (this is the one exception to "read-only" in the targeting skills), and clearly flag which contacts were newly created vs. pre-existing. |

## SKILL COMPLETE

After the Segment/Journey are created (or confirmed reused) and contacts are
added, write the skill-run signal file so the eval harness captures this
execution:

```
systems/eval-harness/skill-runs/campaign-setup-latest.json
```

Content:
```json
{
  "skill": "campaign-setup",
  "agent": "harper",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

**Eval-harness exception:** if this invocation is an eval-harness executor run (simulating this skill for grading, benchmarking, or testing rather than a genuine Harper-invoked production run), do NOT write this signal file. Writing it from a simulation would falsely register a live skill run in the production eval-harness tracking system. Only write it when this is an actual production invocation.

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if
called from a scheduled task, `"manual"` otherwise. Set `status` to
`"partial"` if the Segment/Journey were created but the config sanity check
flagged a send-readiness gap, `"failure"` if the write itself could not
complete (auth failure, name collision unresolved). Use the actual start time
for `started`. This write is always the final action.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill campaign-setup
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/campaign-setup.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->
