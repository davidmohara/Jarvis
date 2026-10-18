# Run and Grade Evals (Step 7 Detail)

Loaded by rigby-capability-build Step 7 when running paired executor subagents, grading, aggregating benchmarks, and surfacing the review viewer. Read this before spawning executors — the aggregator expects the exact directory layout below, and timing capture is a one-shot opportunity on each executor notification.

## Output directory structure

Every config gets a `run-{N}/` subdirectory, default `run-1`:

```
systems/evals/work-{id}/iteration-N/
└── eval-{name}/
    ├── with_skill/run-1/
    │   ├── grading.json
    │   ├── timing.json
    │   ├── metrics.json
    │   ├── transcript.md
    │   ├── user_notes.md
    │   └── outputs/
    ├── without_skill/run-1/   # for new-skill builds
    │   └── ...
    └── old_skill/run-1/        # for skill improvements (mutually exclusive with without_skill)
        └── ...
```

The `run-N/` level exists so future versions can run multiple stochastic passes per config and aggregate variance. For now Rigby always writes `run-1/`.

## Config selection

**For a new skill:**
- `with_skill` — executor loaded with the new skill path, prompt, input files; saves to `.../with_skill/run-1/`
- `without_skill` — same prompt, no skill loaded but persona still loaded; saves to `.../without_skill/run-1/`

**For an existing skill being improved:**
- Snapshot the pre-edit skill on first iteration: `cp -r {skill-path} systems/evals/work-{id}/skill-snapshot/`
- `with_skill` — executor loaded with the edited skill; saves to `.../with_skill/run-1/`
- `old_skill` — executor loaded with the snapshot; saves to `.../old_skill/run-1/`

## Timing capture (one-shot)

Each executor returns a task notification containing `total_tokens` and `duration_ms`. **Capture timing immediately on notification** by invoking the helper — this is the only opportunity, the data is not persisted anywhere else:

```bash
(cd .claude/skills/rigby-capability-build && python3 -m scripts.capture_timing \
  --run-dir ../../../systems/evals/work-{id}/iteration-N/eval-{name}/{config}/run-1 \
  --total-tokens {total_tokens-from-notification} \
  --duration-ms {duration_ms-from-notification})
```

Run this once per executor notification. The script writes `timing.json` with the right shape.

## Grading and aggregation

**Substep 7a — Grade each run.** Spawn the grader subagent (`subagents/grader.md`) for each run directory. Grader writes `grading.json` per run with fields `text`, `passed`, `evidence`. For programmatic assertions (file-format checks, schema validation), the grader writes and executes a verification script rather than eyeballing.

**Substep 7b — Aggregate.** Always pass `--skill-path` and `--executor-model` so `benchmark.json` metadata is reproducible (not placeholder strings). `runs_per_configuration` and the single-config benchmark layout are handled automatically.

```bash
(cd .claude/skills/rigby-capability-build && python3 -m scripts.aggregate_benchmark \
  ../../../systems/evals/work-{id}/iteration-N \
  --skill-name {skill-name} \
  --skill-path {skill-path} \
  --executor-model claude-opus-4-7)
```

Produces `iteration-N/benchmark.json` and `iteration-N/benchmark.md`. With paired configs the table shows With Skill, Baseline, and Delta. With only one config (iteration-1 of an existing-skill improvement, before any edit), the markdown collapses to a single-column layout with a note that there's no baseline yet.

**Substep 7c — Analyzer pass.** Spawn the analyzer subagent (`subagents/analyzer.md` in benchmark-notes mode) with `benchmark.json` and the skill path. **The analyzer returns the analysis as markdown text in its response — it does not write the file itself.** Subagent Write permissions are inconsistent in some IES runtimes, so Rigby (you) persists the returned text to `iteration-N/analysis.md` after the subagent completes. Surface non-discriminating assertions, high-variance evals, and any time/token regressions.

## Review viewer and feedback

**Substep 7d — Generate review and surface to the executive.** Run the eval viewer in static mode (IES has no live browser session):

```bash
(cd .claude/skills/rigby-capability-build && python3 -m scripts.generate_review \
  ../../../systems/evals/work-{id}/iteration-N \
  --skill-name {skill-name} \
  --benchmark ../../../systems/evals/work-{id}/iteration-N/benchmark.json \
  --static ../../../systems/evals/work-{id}/iteration-N/review.html)
```

For iteration 2+, add `--previous-workspace systems/evals/work-{id}/iteration-{N-1}` so the viewer shows the diff.

**Surface to the executive — runtime-aware.** Detect the runtime by checking the `CLAUDECODE` environment variable (set to `1` by Claude Code; absent in Cowork):

- **Claude Code (`CLAUDECODE=1`):** Open the file directly so it loads in the default browser.
  ```bash
  open systems/evals/work-{id}/iteration-N/review.html
  ```

- **Cowork (no `CLAUDECODE`):** Do NOT call `open`. Surface the absolute file path in the chat so the executive can click it to preview in the Cowork app.
  ```
  Review ready. Preview it here:
  /Users/{user}/.../systems/evals/work-{id}/iteration-N/review.html
  ```
  Use `pwd` to resolve the absolute path before printing.

The viewer collects per-eval feedback and exports `feedback.json`. On Claude Code (local Mac) the export lands in `~/Downloads/`; on Cowork the executive will save it back into the iteration directory directly. After the executive confirms the export is complete:

```bash
# Claude Code path:
[ -f ~/Downloads/feedback.json ] && mv ~/Downloads/feedback.json \
  systems/evals/work-{id}/iteration-N/feedback.json

# Cowork: feedback.json should already be at the iteration path. Verify it exists.
test -f systems/evals/work-{id}/iteration-N/feedback.json
```

## feedback.json shape

Produced by the viewer, consumed in Step 8:

```json
{
  "reviews": [
    {
      "run_id": "eval-0-with_skill",
      "feedback": "Missing the contract reference from the prompt context. Tone too formal for Sarah.",
      "timestamp": "2026-05-22T15:42:18Z"
    },
    {
      "run_id": "eval-1-with_skill",
      "feedback": "",
      "timestamp": "2026-05-22T15:43:02Z"
    }
  ],
  "status": "complete"
}
```

One entry per executor run shown in the viewer. `feedback` is freeform text; empty string means the executive was satisfied with that run. `status: "complete"` means the executive finished the review pass (versus saved partial progress). The iteration loop in Step 8 reads this file to know what to fix and to decide when to exit.
