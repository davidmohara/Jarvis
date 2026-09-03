---
id: delivery-router
name: Delivery Router
owning_agent: rigby
model: sonnet
context: inline
fairness: {applicable: false, reason: "Infrastructure utility for routing content to delivery backends (Slack/email/Monday/Ghost). No differential treatment of people, no eligibility or scoring decision."}
trigger_keywords:
  - delivery router
  - route delivery
  - deliver content
  - multi-destination delivery
  - delivery-router
---

<!-- system:start -->
# Delivery Router

**Callable by:** Any workflow step that currently hand-rolls "call this API, check it worked,
retry, escalate if it didn't" for one or more delivery backends. Currently consumed by
`workflows/plaud-ingest/steps/step-05b-share-with-alice.md` (Monday task creation — this
workflow's real terminal delivery is a Plaud share link plus a Monday task, not email or
Slack, see note below) and `workflows/content-approval/steps/step-01-approve.md` (Ghost
publish + verification, folded from that step's former separate Gate 4/5 sequence — see
Process, Ghost backend). Flagged as reusable for any future step that needs to push content or
a notification out to one or more of these backends with verified delivery.

## Purpose

Centralizes "send this somewhere, confirm it actually landed, retry once or twice on
transient failure, escalate loudly rather than silently if it never lands" — instead of every
workflow step re-implementing its own retry count, its own definition of "verified," and its
own escalation wording. One skill, one `destinations` array, one consistent
`delivery_status`/`all_succeeded` contract.

**This is effectively a HARD gate when `all_succeeded` matters to the caller.** A destination
marked `required: true` (the default) that fails after retries makes `all_succeeded: false`
and the caller must not report success anywhere downstream — see Process, step 5.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

| Field | Required | Description |
|-------|----------|--------------|
| `content` | Yes | What's being delivered — the payload. Shape depends on backend (see Process): a message string for `slack`, a subject/body pair for `email`, an item name + column values for `monday`, a post_id + target status for `ghost`. |
| `destinations` | Yes | Array of `{backend: "slack"\|"email"\|"monday"\|"ghost", config: {...}, required: true}`. `required` defaults to `true` — set `false` for a "nice to have" destination that shouldn't block `all_succeeded` if it fails. |

## Output

```yaml
delivery_status:
  - backend: "monday"
    success: true
    id: "<item id>"          # or url, whichever the backend returns
    timestamp: "<ISO-8601>"
    error: null
  - backend: "slack"
    success: false
    id: null
    timestamp: "<ISO-8601 of final attempt>"
    error: "<what went wrong, after retries exhausted>"
all_succeeded: false   # false if any REQUIRED destination has success: false
```

## Process

For each entry in `destinations`, in the order given:

### Backend: `slack`
Call `master-slack` (`skills/master-slack/SKILL.md` if it exists in this instance, otherwise
post via the Jarvis bot mechanism that skill documents) with `config.channel` and `content` as
the message body. Success = the post call returns without error. `id` = the message timestamp
(`ts`) if the backend returns one, else the channel name.

### Backend: `email`
Call whichever email-send mechanism `config.via` names (e.g.
`mcp__claude_ai_Microsoft_365__outlook_send_mail` or a Superhuman Mail send tool) with
`config.to`, `config.subject`, and `content` as the body. Success = the send call returns
without error and (if the tool provides one) a message/draft ID. `id` = that identifier.

### Backend: `monday`
Call `create_item` (the Monday MCP tool available in this instance) with `config.board_id`,
`config.group_id`, an item name built from `content`, and `config.column_values` (a JSON
object — pass through verbatim, the caller is responsible for building correct column values
for its board's schema; this skill does not know any one board's schema and must not
hardcode one). Success = the call returns a task ID. `id` = that task ID.

**Do not hardcode a specific board ID, group ID, or person ID inside this skill.** Those are
workflow-specific facts (e.g. plaud-ingest's board `18420619069` / group `new_group29179` /
Alice Mburu `107886956`) that belong in the caller's `config`, not in this shared skill —
hardcoding them here would silently misroute a different caller's Monday delivery.

### Backend: `ghost`
Two-step, because a successful API call is not sufficient proof of delivery:
1. Call `mcp__ghost-blog__update_post(post_id=config.post_id, status=config.target_status)`
   (`target_status` is usually `"published"`). If Ghost returns a concurrent-edit error
   ("Someone else is editing this post"), that is this backend's specific transient-failure
   case — wait 2s and retry, then 5s and retry again, before falling through to this skill's
   general retry budget in step 2 below.
2. **Verify, don't trust the response.** Re-fetch via
   `mcp__ghost-blog__get_post(post_id=config.post_id)` and confirm: `post.status` equals
   `config.target_status`, `post.url` is present and resolves to the expected host (pass
   `config.expected_host` if the caller wants this checked), and `post.published_at` is set
   (when publishing). Success = all of these hold on the re-fetched object, not the raw
   `update_post` response. `id` = `post.url`.

### Retry and escalation (applies to every backend)

1. Attempt the backend call (and, for `ghost`, its verification re-fetch).
2. If it fails (API error, or verification fails), retry up to **2 more times** (3 attempts
   total) with a short pause between attempts. Use the backend-specific transient-failure
   handling above where one exists (e.g. Ghost's concurrent-edit wait/retry) in place of a
   generic pause for that failure type.
3. If all attempts fail: record `{backend, success: false, id: null, timestamp: <final attempt
   time>, error: <the last error message>}`.
4. If `destinations[i].required` is `true` (default) and this destination ultimately failed:
   this destination's failure drives `all_succeeded: false`. If `required: false`, its failure
   is still recorded in `delivery_status` (never silently dropped) but does not affect
   `all_succeeded`.
5. After all destinations are attempted, compute `all_succeeded` = true iff every `required`
   destination has `success: true`. Return the full `delivery_status` list regardless — a
   partial success (some destinations succeeded, others didn't) must always be visible to the
   caller, never collapsed into a single boolean with no detail.

## Plan-Only Mode

If the prompt contains the phrase "do not execute" or `eval-mode: plan-only`, do not call any
backend API for any destination. Instead, produce a markdown plan listing each destination in
order, the exact call you would make (backend, config, content payload) and the verification
step for `ghost`, with rationale. Save the plan to the requested output path and stop. Do not
call Slack/email/Monday/Ghost APIs under any circumstances in this mode.

## Error Handling

| Situation | Response |
|-----------|----------|
| A `required` destination fails after 3 attempts | Record it, set `all_succeeded: false`, return the full status list. Do not retry further — the caller decides whether to escalate to a human, and how (this skill does not send its own escalation notification; escalating is not itself a "delivery" this skill should model recursively). |
| An `optional` (`required: false`) destination fails | Record it, continue with the rest, do not let it affect `all_succeeded`. |
| `destinations` is empty | Return `delivery_status: []`, `all_succeeded: true` (vacuously — nothing required failed). Caller should treat an empty destinations list as its own logic error if that's not expected. |
| `config` for a backend is missing a field this skill needs (e.g. `monday` config with no `board_id`) | Do not guess a default. Record that destination as failed with `error: "missing required config field: <field>"` — do not silently skip it or invent a board/channel. |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/delivery-router-latest.json
```

Content:
```json
{
  "skill": "delivery-router",
  "agent": "<caller's agent, e.g. knox or harper>",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output (e.g. `all_succeeded: false` because an optional destination failed, or a required one failed and the caller's own escalation path took over), `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action, immediately followed by the grading step below.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill delivery-router
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/delivery-router.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
