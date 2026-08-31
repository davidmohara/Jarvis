---
id: eval-signal-write
name: Eval Signal Write
owning_agent: rigby
model: haiku
context: inline
fairness: {applicable: false, reason: "Utility skill — writes an execution-metadata file for the eval harness. No differential treatment of people, no eligibility or scoring decisions."}
trigger_keywords:
  - skill run signal
  - eval harness signal
  - skill complete
---

<!-- system:start -->
# Eval Signal Write

A generic writer for the `systems/eval-harness/skill-runs/{skill}-latest.json` signal file. Every skill in IES ends its run by writing one of these — the `post-tool-use.py` hook watches for the write and creates the eval record automatically. This skill exists so the JSON shape isn't hand-typed and re-typed in every skill's `SKILL COMPLETE` section.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Inputs

| Input | Type | Required | Description |
|-------|------|----------|--------------|
| `skill_name` | string | yes | The skill writing this signal, e.g. `pipeline-snapshot`. Determines the output filename: `systems/eval-harness/skill-runs/{skill_name}-latest.json` |
| `agent` | string | yes | Owning agent, e.g. `chase` |
| `trigger` | string | yes | One of `boot`, `scheduled`, `manual` — see rule below |
| `started` | ISO-8601 string | yes | Actual start time of the calling skill's execution (not this write) |
| `completed` | ISO-8601 string | no | Actual completion time. Include if the caller tracks it. |
| `status` | string | yes | One of `success`, `partial`, `failure` |
| `tool_failures` | integer | no | Default `0` |
| `error_ids` | array of strings | no | Default `[]` |
| `extra_fields` | object | no | Any additional fields the caller wants merged into the written JSON (e.g. `reminder_id`, region flags). Merged at the top level alongside the standard fields. |

**Setting `trigger`:** `"boot"` if called from the morning briefing or a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise.

**Setting `status`:** `"success"` for a normal complete run (a cache-hit short-circuit via `vault-freshness-check` still counts as `"success"`). `"partial"` if the skill completed with degraded output (e.g. only one region's data captured). `"failure"` if the skill could not run at all (e.g. the live source was unreachable and no cache existed).

## Process

1. Build the JSON object:
   ```json
   {
     "skill": "{skill_name}",
     "agent": "{agent}",
     "trigger": "{trigger}",
     "started": "{started}",
     "completed": "{completed}",
     "status": "{status}",
     "tool_failures": {tool_failures},
     "error_ids": {error_ids}
   }
   ```
   Merge in any keys from `extra_fields`.

2. Write it to `systems/eval-harness/skill-runs/{skill_name}-latest.json` (overwrite if it exists — only the latest run per skill is kept here).

3. This write is always the caller's final action. Do nothing after it.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## SKILL COMPLETE

Not applicable — this skill *is* the signal-write mechanism. It does not write a signal file about itself.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
