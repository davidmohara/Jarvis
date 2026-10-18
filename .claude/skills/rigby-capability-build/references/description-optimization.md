# Description Optimization (Step 9 Detail)

Loaded by rigby-capability-build Step 9 when the capability is **phrase-triggered** (invoked because the user said something matching the description). Skills invoked by explicit `/skill-name` syntax skip this step. Read this before authoring the trigger eval set or running the optimization loop.

## Substep 9a — Generate trigger eval set

Author 20 queries: 8-10 should-trigger and 8-10 should-not-trigger. Should-not-trigger queries are **near-misses** sharing keywords or concepts but needing different tools, not obviously-irrelevant negatives. Mix formal and casual phrasings, include typos and abbreviations, prioritize edge cases over clarity.

Write to `systems/evals/work-{id}/description-tuning/trigger_eval.json`:

```json
[
  {"query": "draft an email to the AT&T VP about the migration risk", "should_trigger": true},
  {"query": "what's on my calendar tomorrow", "should_trigger": false}
]
```

## Substep 9b — Executive review of the eval set

Render `assets/eval_review.html` with the query set, skill name, and current description substituted in:

1. Read `.claude/skills/rigby-capability-build/assets/eval_review.html`
2. Replace `__EVAL_DATA_PLACEHOLDER__` with the JSON array (no quotes; it's a JS variable assignment)
3. Replace `__SKILL_NAME_PLACEHOLDER__` with the skill name
4. Replace `__SKILL_DESCRIPTION_PLACEHOLDER__` with the current description
5. Write to `/tmp/eval_review_{skill-name}.html`
6. Surface using the same runtime-aware pattern as the eval run protocol (`CLAUDECODE` check):
   - **Claude Code:** `open /tmp/eval_review_{skill-name}.html`
   - **Cowork:** print the absolute path so the executive can click to preview in the app

The executive edits queries, toggles `should_trigger`, adds and removes entries, and clicks "Export Eval Set." Retrieve the exported file:

```bash
# Claude Code: arrives in ~/Downloads
[ -f ~/Downloads/eval_set.json ] && mv ~/Downloads/eval_set.json \
  systems/evals/work-{id}/description-tuning/trigger_eval.json

# Cowork: executive saves directly to the tuning dir. Verify.
test -f systems/evals/work-{id}/description-tuning/trigger_eval.json
```

## Substep 9c — Run the optimization loop

Preflight: confirm the `claude` CLI is available (it's required by `run_eval.py` and `improve_description.py`, which shell out via `claude -p`). On Claude Code it's always present. On Cowork Desktop it is also present; on Cowork web it is not, so this step is gated to Desktop runtimes:

```bash
if ! command -v claude >/dev/null 2>&1; then
  echo "[Rigby]: claude CLI not on PATH — Step 9 requires Claude Code or Cowork Desktop." >&2
  echo "[Rigby]: Skipping description optimization. Update description manually if needed." >&2
  exit 0
fi
```

Then run the loop:

```bash
(cd .claude/skills/rigby-capability-build && python3 -m scripts.run_loop \
  --eval-set ../../../systems/evals/work-{id}/description-tuning/trigger_eval.json \
  --skill-path ../../../{skill-path} \
  --model claude-opus-4-7 \
  --max-iterations 5 \
  --results-dir ../../../systems/evals/work-{id}/description-tuning/ \
  --verbose)
```

`run_loop.py` splits the eval set 60% train / 40% test, evaluates the current description (3 runs per query), proposes improvements via Claude, re-evaluates, iterates up to 5 times. It selects `best_description` by test-set score to avoid overfitting.

Run this in the background. Periodically tail the output and report iteration progress to the executive.

## Substep 9d — Apply

When the loop exits, read `description-tuning/results.json`. Show the executive a before/after diff with trigger-rate scores. On approval, update the `description:` field in the skill's frontmatter.
