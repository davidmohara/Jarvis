---
name: peekaboo
owning_agent: rigby
description: "macOS screenshots, UI inspection, clicks, typing, and app/window automation via the Peekaboo CLI."
model: sonnet
trigger_keywords: [screenshot, screen capture, UI inspect, click, type, window automation, peekaboo]
trigger_agents: [rigby, chief]
---

<!-- system:start -->
## Trigger Phrases

- "take a screenshot", "capture the screen", "screenshot of", "peekaboo"
- "inspect the UI", "click on", "automate the window", "what's on screen"
- Invoked when any agent needs visual confirmation of on-screen state or GUI automation

## Binary

Use `peekaboo` from PATH directly. Confirm availability before proceeding:

```bash
peekaboo --version
```

If not found, report the missing install — do not proceed.

## Safety

- Check permissions before any capture or automation: `peekaboo permissions status --json`
- Screenshot requires Screen Recording permission; clicks, typing, and window control require Accessibility.
- On remote Macs, Screen Recording may be blocked while Accessibility still works — fall back to clicks or DOM automation when the target is otherwise knowable.
- Prefer `--json` for machine parsing and `--no-remote` when testing local TCC.
- Do not click, type, or destructively automate unless David explicitly requested it or the target is a controlled test environment.

## Common Commands

```bash
peekaboo permissions status --json
peekaboo list screens --json
peekaboo list apps --json
peekaboo list windows --app Safari --json
peekaboo image --mode screen --screen-index 0 --path /tmp/screen.png --json --no-remote
peekaboo see --app frontmost --path /tmp/frontmost.png --json --annotate
peekaboo tools --json
peekaboo learn
peekaboo click --coords 100,100 --json
peekaboo type "text" --json
```

## Workflow

1. Confirm `peekaboo` is available via `peekaboo --version`.
2. Run `permissions status --json`. If TCC grants are missing, report the exact missing permission — do not attempt the blocked operation.
3. For screenshots, use `image`; include `--path`, `--json`, and `--no-remote`.
4. For element targeting, run `see --json --annotate`, then click by element ID or snapshot reference.
5. For long-running or change-aware capture, use `capture live`; for video frame sampling, use `capture video`.
6. Use `tools --json` for command and tool discovery; use `learn` when the full agent guide is needed.
7. Verify output files with `sips -g pixelWidth -g pixelHeight <path>` or render the image inline.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->


<!-- system:start -->
## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/peekaboo-latest.json
```

Content:
```json
{
  "skill": "peekaboo",
  "agent": "unknown",
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
python3 systems/eval-harness/grade_skill_run.py --skill peekaboo
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/peekaboo.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->
