---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 09: Cleanup + Commit

## MANDATORY EXECUTION RULES

1. The transient/committed file split and the error-logging rule for this step are stated in YOUR TASK below.

---

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline. All git operations run through `skills/git/SKILL.md` and the `ies-git` wrapper.
**Input:** The run's outputs (sources.json changes, topic_history.json, runs/*.json, suggestions/*.json, dashboard.html)
**Output:** Committed changes

---

## YOUR TASK

`harvest.json` and `clusters.json` are transient (gitignored). `topic_history.json` is NOT transient — it is the cross-day memory that makes relevance decay work; always commit it. Commit `sources.json` changes, `topic_history.json`, the new `runs/*.json`, any `suggestions/*.json`, and `dashboard.html` via `skills/git/SKILL.md`. Suggested message: `chore(rigby): political-monitor daily run YYYY-MM-DD`.

If any step failed (e.g., render.py exited with code 1), log the error to `systems/error-tracking/entries/` before halting, using `new-entry.py --id-only` to generate the error ID.
<!-- system:end -->
