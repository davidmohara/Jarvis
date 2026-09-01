---
name: contact-targeting
owning_agent: harper
model: sonnet
trigger_keywords: [find contacts, contact targeting, who do we reach out to]
trigger_agents: [harper]
description: >
  Sixth step of the Podcast-to-Pipeline pipeline (second step of the
  audience-target-outreach workflow). Drills from target accounts down to
  individual contacts matching the audience profile's buyer role. CRM/Clay-first,
  LinkedIn as tie-breaker and authority on title conflicts. Called by
  workflows/audience-target-outreach/workflow.md step 02.
---

<!-- system:start -->
# Contact Targeting

## Purpose

For each target account from `account-targeting`, identify the specific
individuals who match the audience profile's buyer role, with enough context
to explain why the episode's pain point applies to them personally — not just
a name and title pulled off a directory.

## Input

- `target_accounts` from `account-targeting`
- `audience_profile` (specifically `buyer_roles`) from `audience-profile-builder`

## Output

```yaml
target_contacts:
  - name: "..."
    title: "..."
    account: "..."
    email: "..." (if found; note source)
    title_source: "CRM" | "Clay" | "LinkedIn"
    why_this_pain_point_applies: "One line connecting this person's role to the specific pain point/episode angle"
    existing_relationship: true/false
    relationship_notes: "if true - prior interaction summary from CRM/Clay"
```

## Process

1. **CRM first.** For each target account, search Dynamics (Chrome/Playwright)
   for existing contacts matching the buyer role(s) from the audience profile.
   Note any existing relationship/interaction history.

2. **Clay next.** Cross-reference or supplement with Clay
   (`mcp__clay__*` / `mcp__claude_ai_Clay_custom__*`) for personal relationship
   context David may already have with someone at the account, even if they
   aren't the exact buyer-role title — a warm path is worth surfacing even if
   it's not the primary target.

3. **LinkedIn as tie-breaker and title authority.** Use LinkedIn (via
   Playwright) to find contacts CRM/Clay didn't surface, and to resolve title
   conflicts. **Standing rule: when CRM and LinkedIn disagree on a contact's
   title, LinkedIn wins** (per `memory/feedback_linkedin_over_crm_titles.md`).
   Always note which source the final title came from.

4. **Write the "why this applies" line for each contact.** This is not
   boilerplate — it should reference the specific pain point and the
   contact's actual role, e.g. "As VP of Supply Chain Ops, [Name] would own
   the multi-region visibility gap the episode describes." A generic line
   like "this person works in the target industry" is not sufficient.

5. **Cap the list to genuinely qualified contacts.** One well-matched contact
   per account is better than three loosely-matched ones. If an account has
   multiple genuinely distinct buyer-role contacts (e.g. both a VP Eng and a
   VP Ops), list both with separate rationale.

## Plan-Only Mode

If the prompt contains the phrase "do not execute" or `eval-mode: plan-only`,
do not run any live CRM, Clay-write, or LinkedIn browser automation. Instead,
produce a markdown plan describing the lookups you would perform, in order,
with the accounts/contacts you'd search for and why. Save the plan to the
requested output path and stop. Do not call any browser-automation or
MCP-write tool under any circumstances in plan-only mode. (Clay lookups here
are read-only; the plan-only gate exists because this skill shares a live CRM
browser session with write-capable skills downstream.)

## Failure Modes

| Failure | Action |
|---------|--------|
| CRM/LinkedIn title conflict | Use LinkedIn's title, note the CRM discrepancy in `relationship_notes` so it can be corrected in CRM later. |
| No contact found matching the buyer role at a target account | Drop that account from the contact list for this run, note it, and surface to the controller — don't force a lower-relevance contact just to keep the account in play. |
| LinkedIn profile is stale (person has left the company per other signals) | Do not include. Note the discrepancy. |
| Clay and CRM both have no relationship history | Fine — mark `existing_relationship: false`, this is a legitimate cold-outreach case. |

## SKILL COMPLETE

After the target contact list is returned to the caller, write the skill-run
signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/contact-targeting-latest.json
```

Content:
```json
{
  "skill": "contact-targeting",
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
`"partial"` if some target accounts yielded no qualified contact, `"failure"`
if CRM/Clay/LinkedIn were all unreachable. Use the actual start time for
`started`. This write is always the final action.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill contact-targeting
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/contact-targeting.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->
