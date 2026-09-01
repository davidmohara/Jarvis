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

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill eval-signal-write
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/eval-signal-write.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
