---
name: campaign-response-log
owning_agent: harper
model: sonnet
trigger_keywords: [log this reply, log campaign response, someone replied to the campaign]
trigger_agents: [harper]
description: >
  Tenth skill in the Podcast-to-Pipeline pipeline. Links an inbound reply back
  to the correct Journey/Contact in Customer Insights – Journeys as a Note or
  Activity with a Response Type — the part reply-tracking that Dynamics does
  NOT do automatically. Opens/clicks/bounces are already tracked natively by
  Email insights and are out of scope here. Runs asynchronously/on-demand
  (surfaced via inbox monitoring or a manual flag), not as part of the main
  send workflow, since replies arrive on their own timeline.
---

<!-- system:start -->
# Campaign Response Log

## Purpose

Dynamics' Customer Insights – Journeys app natively tracks opens, clicks, and
bounces via Email insights — that is real, documented, out-of-box behavior
and this skill does not duplicate it. What it does NOT do, and what
Microsoft's own documentation confirms is not a built-in capability, is
detect an inbound email reply and link it back to the journey that generated
it. **This skill is that missing link, done explicitly and manually — it is
not automating something Dynamics already does; it is filling a real gap.**
Do not describe this skill's output as "automatic reply detection" in any
future documentation — it isn't, by design and by platform limitation.

## Input

One of:
- A reply email David received, surfaced via inbox monitoring (recognizable
  by referencing the campaign/episode content) or flagged manually
- A manual flag: "log this reply from {contact} about {episode/campaign}"

## Output

A Note or Activity attached to the correct Contact and linked to the
originating Journey in Dynamics, with:

```yaml
response_log:
  contact_name: "..."
  journey_name: "..."
  episode: "..."
  response_type: "interested" | "not_interested" | "referred" | "no_reply"
  reply_summary: "1-2 sentence summary of what they actually said"
  logged_as: "Note" | "Activity"
  logged_at: "<ISO-8601 timestamp>"
```

## Process

1. **Identify which Journey/Contact this reply belongs to.** Match on the
   contact's email address and, if ambiguous (a contact could theoretically
   be in more than one active journey), cross-reference the campaign/episode
   content referenced in the reply itself. If it cannot be confidently
   matched, stop and ask the controller rather than guessing.

2. **Classify the Response Type** from the actual content of the reply:
   - `interested` — wants to talk further, asks a follow-up question, agrees
     to a call
   - `not_interested` — explicit decline
   - `referred` — redirects to a colleague or another point of contact
   - `no_reply` — used only for a deliberate "mark as no response after N
     days" log entry, not for an actual reply (see the out-of-scope note
     below on automated cadence)

3. **Write the Note/Activity** to the Contact record in Dynamics
   (Chrome/Playwright — no API/MCP connector), explicitly linked to the
   Journey, since there is no native CampaignResponse-equivalent object in
   this app to attach it to instead.

4. **Do not attempt to build automated follow-up cadence logic here.**
   Surfacing contacts overdue for a follow-up (e.g. "these 12 contacts got a
   campaign email 10 days ago with no response") is explicitly out of scope
   for v1 and belongs with Shep's nudge domain in a future pass — this skill
   only logs what has already happened.

## Plan-Only Mode

If the prompt contains the phrase "do not execute" or `eval-mode: plan-only`,
do not run any live CRM write via Chrome/Playwright. Instead, produce a
markdown plan describing the Contact/Journey match you would make, the
Response Type you would assign and why, and the exact Note/Activity content
you would write. Save the plan to the requested output path and stop. Do not
call any browser-automation write action under any circumstances in
plan-only mode.

## Failure Modes

| Failure | Action |
|---------|--------|
| Reply can't be confidently matched to a Journey/Contact | Stop, ask the controller to confirm which campaign this relates to. Do not guess and log to the wrong record. |
| Contact replied but content is ambiguous (neither clearly interested nor declining) | Log with the best-fit Response Type and note the ambiguity in `reply_summary` rather than forcing a confident classification. |
| Contact has multiple active journeys | Ask which one this reply belongs to if content doesn't make it obvious. |
| CRM login wall / expired SSO | Flag to controller, retry once confirmed. |

## SKILL COMPLETE

After the Note/Activity is written (or the plan is produced in plan-only
mode), write the skill-run signal file so the eval harness captures this
execution:

```
systems/eval-harness/skill-runs/campaign-response-log-latest.json
```

Content:
```json
{
  "skill": "campaign-response-log",
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
`"partial"` if classification was ambiguous but logged with a caveat,
`"failure"` if the reply could not be matched to any Journey/Contact. Use the
actual start time for `started`. This write is always the final action.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill campaign-response-log
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/campaign-response-log.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->
