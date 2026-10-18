# Composite Scoring Formula

<!-- system:start -->
Single statement of the eval scoring formula for the whole system. Both entry points use this: the build path (`.claude/skills/rigby-capability-build`) and the improve path (`workflows/skill-optimize`, via `skills/rigby-skill-reflect`). Do not restate the weights anywhere else — point here.

Read this when scoring an eval record, a baseline, or a candidate.

```
score = (mechanical × 0.25) + (assertion_rate × 0.35) + (grade_score × 0.20) + (feedback × 0.10) + (no_errors × 0.10)
```

Where:
- `mechanical` = 1 if status is "success", 0.5 if "partial", 0 otherwise
- `assertion_rate` = assertions_passed / assertions_checked (0 if assertions_checked = 0, use 0.5 as neutral)
- `grade_score` = A=1.0, B=0.8, C=0.6, D=0.4, F=0.0, null=omit (redistribute weights)
- `feedback` = 1 if "positive", 0 if "negative", omit if null (redistribute weights)
- `no_errors` = 1 if error_ids is empty, 0 otherwise

When grading or feedback is null: drop those components and redistribute their weights proportionally across the remaining components.

Classification: score ≥ 0.7 is success, score < 0.7 is failure.

Mechanical implementation: `systems/eval-harness/scoring/score_eval.py`.
<!-- system:end -->
