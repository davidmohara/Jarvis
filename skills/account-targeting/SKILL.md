---
name: account-targeting
owning_agent: harper
model: sonnet
trigger_keywords: [find target accounts, account targeting, who should we target for this]
trigger_agents: [harper]
description: >
  Fifth step of the Podcast-to-Pipeline pipeline (first step of the
  audience-target-outreach workflow). Takes an audience profile and produces a
  target account list, CRM-first then public/LinkedIn research to fill gaps.
  Every field carries a source. Includes a mandatory compliance pre-check
  before any research proceeds. Called by
  workflows/audience-target-outreach/workflow.md step 01.
---

<!-- system:start -->
# Account Targeting

## Purpose

Turn an audience profile into a list of real target companies, sourced with
provenance on every field. This is CRM-write-adjacent research (it feeds
`campaign-setup`, which does write to CRM) but this skill itself only reads —
it does not create or modify any CRM record.

## Input

The `audience_profile` object from `audience-profile-builder` (industries,
company size band, buyer roles, buying-trigger signals).

## Mandatory Pre-Check — Run Before Any Research

Before pulling any data, confirm: is the data this skill is about to touch
Improving's own commercial CRM data, or could it be a client's
confidential material (e.g. a client-specific account plan, a client's own
customer list surfaced through cross-contaminated search results)? If there is
any ambiguity about the source or ownership of a dataset before querying it,
**stop and flag it to the controller** rather than proceeding. This system's
CRM data is Improving's own sales pipeline data — that is in scope. A client's
confidential materials are never in scope for this skill, even if they happen
to reference companies that would otherwise fit the audience profile.

## Output

```yaml
target_accounts:
  - company_name: "..."
    industry: "..."
    size_signal: "employee count / revenue band, as found"
    fit_rationale: "how this account matches the audience profile"
    buying_trigger_evidence: "specific signal found (funding, leadership change, tech shift), or 'none found' "
    existing_crm_relationship: true/false
    crm_notes: "if true - stage, owner, history summary"
    fields:
      - field: "industry"
        source: "CRM" | "LinkedIn" | "public web"
      - field: "size_signal"
        source: "..."
      - field: "buying_trigger_evidence"
        source: "..."
```

## Process

1. **Run the mandatory pre-check above.** Do not skip.

2. **CRM first.** Search Dynamics (via Chrome/Playwright browser automation —
   there is no API/MCP connector today) for accounts matching the audience
   profile's industry and size band. This is a read-only query.
   - If a login wall or expired SSO session is hit (the CBRE-session failure
     mode), do not silently fail: flag it to the controller — "CRM session
     appears logged out — confirm you're signed into
     improving.crm.dynamics.com and I'll retry" — and retry once confirmed.
     Do not fabricate CRM data or proceed as if CRM returned nothing when the
     real cause was an auth failure.
   - Note which candidate accounts already have an existing relationship
     (owner, stage, history) — these carry forward into `campaign-setup` with
     that context, and existing-relationship accounts may warrant a different
     outreach approach than cold accounts (flag this for the controller's
     awareness, but don't exclude them — that's a controller call).

3. **Public/LinkedIn research to fill remaining gaps.** Use Playwright-driven
   browser research (never a manual search David has to do himself) to fill
   anything CRM didn't cover — firmographic detail (headcount, revenue, tech
   stack) and buying-trigger signals in particular (funding announcements,
   leadership changes, press) are often only visible via public search now
   that there's no firmographic enrichment source in the loop.

4. **Tag every field with its source.** A reviewer should be able to tell
   at a glance whether a data point came from Improving's own CRM or public
   research.

5. **Do not exceed what the audience profile actually supports.** If the
   profile only strongly supports 5-8 real target accounts, return 5-8, not
   a padded list of 20 with weak fits. Without ZoomInfo-grade firmographic
   coverage, be more conservative about claiming a strong size/industry fit
   on thin public-research evidence — flag lower-confidence fits explicitly
   rather than presenting them with the same confidence as a CRM-sourced hit.

## Plan-Only Mode

If the prompt contains the phrase "do not execute" or `eval-mode: plan-only`,
do not run any live CRM (Chrome/Playwright) or public-research
browser automation. Instead, produce a markdown plan describing the searches
you would run, in order, with the exact query terms and rationale for each,
and the accounts/sources you expect to check. Save the plan to the requested
output path and stop. Do not call any browser-automation or MCP-write tool
under any circumstances in plan-only mode. (This skill has no CRM-write
step of its own, but the CRM browser session it opens is shared with
write-capable skills in this pipeline, so plan-only discipline still applies
to avoid any accidental navigation-triggered side effect.)

## Failure Modes

| Failure | Action |
|---------|--------|
| CRM login wall / expired SSO | Flag to controller, retry once confirmed. Never substitute fabricated data. |
| Ambiguous data ownership (possible client-confidential material) | Stop immediately, flag to controller, do not proceed with that source. |
| Public research has no coverage for a niche industry | Note the gap, rely more heavily on CRM for that segment, and flag the resulting list as lower-confidence. |
| Audience profile too broad to produce a focused list | Ask the controller to narrow (e.g. pick one industry or size band) rather than returning a sprawling, low-fit list. |

## SKILL COMPLETE

After the target account list is returned to the caller, write the skill-run
signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/account-targeting-latest.json
```

Content:
```json
{
  "skill": "account-targeting",
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
`"partial"` if public research was unreachable but CRM still produced a usable
list, `"failure"` if the compliance pre-check halted the run or CRM access
could not be restored. Use the actual start time for `started`. This write is
always the final action.
<!-- system:end -->
