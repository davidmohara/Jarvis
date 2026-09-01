---
name: rigby-skill-audit
owning_agent: rigby
description: "Audit Jarvis skill library — structural validation, token pressure, execution health, broken skill detection."
model: sonnet
trigger_keywords: [skill audit, audit skills, skill health, validate skills, skill library]
trigger_agents: [rigby]
---

<!-- system:start -->
## Purpose

Full health audit of the Jarvis skill library across both roots (`skills/` and `.claude/skills/`). Surfaces structural problems, manifest gaps, schema classification issues, token bloat, and execution health before they cause failures in production.

## When This Skill Fires

- "skill audit" / "audit skills" / "skill health" / "validate skills" / "skill library"
- Triggered by Rigby on demand or as part of an evolution pre-flight
- Can be triggered by Master when a skill fails unexpectedly and Rigby is asked to investigate

## Workflow

### Step 1 — Run the audit script

```bash
python3 skills/rigby-skill-audit/scripts/audit.py [--threshold-days N]
```

Default threshold is 90 days. Pass `--threshold-days 30` for a tighter staleness window if David wants it.

The script writes to stdout. Capture output. If the script exits non-zero, surface the error immediately — do not continue.

### Step 2 — Read and parse the report

The report has five sections. Read them in order:

1. **Structural Validation** — parse errors, missing required fields, duplicate names
2. **Root Coverage** — manifest gaps, orphaned directories, cross-root conflicts
3. **Schema Classification** — ambiguous skills, fork/library misclassification
4. **Token Pressure** — heavy skills, bloated descriptions, suspected body bloat
5. **Execution Health** — never-run, stale, and potentially-broken skills

### Step 3 — Present findings to David

Structure the presentation as:

```
SKILL AUDIT — {date}
{total skills} skills across {N} library + {N} fork

CRITICAL ({count})        ← structural errors, parse failures
WARNINGS ({count})        ← missing fields, manifest gaps, ambiguous schema
HEALTH ({count})          ← stale, never-run, potentially-broken
TOKEN PRESSURE ({count})  ← heavy skills, bloated descriptions
```

For each category with findings, list the specific skills and what's wrong. Be direct. Don't pad.

If a category is clean, one line: "Structural: clean."

### Step 4 — Propose actions

For each finding category, propose specific next actions. Frame as confirmable actions — do not auto-execute.

**Example proposals:**
- "3 skills have YAML parse errors — open each file for manual fix, or I can show you the error details."
- "7 skills are in the manifest but have no directory — remove these manifest entries? I'll show you the list."
- "The `chase-pipeline` skill body is 4,200 tokens with a matching workflow — consider trimming the body or delegating to the workflow directly."
- "14 skills have never been run — flag them for eval or mark them as untested in the manifest."

### Step 5 — Execute approved actions

For structural fixes (manifest cleanup, field additions) David approves:
1. Make the change
2. Stage the affected files: `git add {file}`
3. Commit: `git commit -m "skill-audit: {short description of fix}"`

For deletions: confirm once more before executing. Stage and commit after.

Never auto-remediate. Every change requires explicit approval from David.

### Notes

- The audit is read-only unless David approves a specific action.
- If the script fails to run (e.g., PyYAML not installed), surface the install command: `pip3 install pyyaml`
- If `skills/_manifest.jsonl` is missing or malformed, report it as a critical finding before continuing.
- Execution health is a signal, not a verdict. A never-run skill may be intentional (new build). Surface it; let David decide.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->


<!-- system:start -->
## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/rigby-skill-audit-latest.json
```

Content:
```json
{
  "skill": "rigby-skill-audit",
  "agent": "rigby",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action, immediately followed by the grading step below.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill rigby-skill-audit
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/rigby-skill-audit.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->
