---
type: working-archive
task_id: session
session_id: dream-cycle-2026-06-13-081000
agent-source: jarvis
created: 2026-06-13 08:16:00+00:00
expires: 2026-06-15
status: archived
context: "CRITICAL \u2014 dream cycle commit wiped origin/main. Manual recovery required\
  \ from host Mac."
date: 2026-06-13
source_file: memory/working/dream-cycle-alert-2026-06-13.md
tags:
- dream-cycle-alert
- briefing
- pipeline
- jarvis
- memory
- git
- recovery
- salience
- promotion
- lessons
related_people:
- recovery-run
salience:
  score: 10
  last_scored: 2026-07-05
  last-promoted-check: 2026-07-05
  promoted: true
---
# DREAM CYCLE ALERT — 2026-06-13 — CRITICAL

## What happened

Dream cycle (2026-06-13T08:10 UTC) completed all 5 steps successfully on disk, but the final commit/push used a flawed `GIT_INDEX_FILE` workaround that recorded an empty tree. The push to `origin/main` (commit `21e7395`) effectively **wiped the remote repo** (1420 files → 0 files in HEAD).

## State of your local Mac

**All files on disk are intact.** Nothing was deleted from your local working tree. The dream cycle's actual changes are present:

- `memory/working/dream-summary-2026-06-13.md` — written
- `memory/dream.log` — entry appended for today
- `workflows/dream-cycle/state.yaml` — set to `status: complete`
- 58 episodic files in `memory/episodic/` — `salience.promoted: true`
- 4 semantic patterns in `memory/semantic/` — appended evidence

Run `git status` and you'll see every prior file listed as "modified" or untracked, because HEAD is empty.

## Recovery

Run from your Mac terminal:

```bash
cd ~/develop/jarvis
rm -f .git/index.lock .git/HEAD.lock
git fetch origin
git reset --soft e72d831       # restore prior HEAD pointer to last good commit
git status                      # confirm dream-cycle changes are now staged
git commit -m "dream-cycle: 2026-06-13 — archived 1, promoted 58, 4 clusters appended (recovery commit)"
git push --force-with-lease origin main
```

The `--force-with-lease` flag is required because origin/main is currently at the bad commit `21e7395` and needs to be rewritten.

## Why this happened

The sandbox cannot unlink `.git/index.lock` (chronic 27+ run pattern). To work around it, the workflow used a separate index file via `GIT_INDEX_FILE=/tmp/jarvis-index-2026-06-13`. On 2026-06-09 the same workaround succeeded because files were `git add`-ed against the alternate index before commit. Today the `git add` step appears to have failed silently (warnings about `unable to unlink .git/objects/*/tmp_obj_*`), leaving the alternate index empty. The commit then recorded the tree as empty and the push succeeded — wiping origin.

## Fix to prevent recurrence

The dream cycle's commit step (`workflows/dream-cycle/steps/step-05-logging.md`) needs a safety check: after `git add -A` with an alternate index, verify the index is non-empty with `git --git-dir=... ls-files | wc -l` before committing. If empty, abort the commit and surface to the controller. This is a Rigby task — do not edit the step file directly.

## Counts from the actual dream cycle run

- working_archived: 1 (morning-briefing-2026-06-10)
- episodic_scanned: 106
- clusters_found: 4 (briefing:22, dream-summary:20, daily-review:10, pipeline:6)
- semantic_updated: 4
- promoted_entries: 58
- errors_in_pipeline: 0 (the commit failure is post-pipeline)
- error_categories_30d: process-skip:16, routing-error:7, assumption-error:5, data-accuracy:4, tool-misuse:4, format-violation:4, missed-context:3 (all already in LESSONS.md)
