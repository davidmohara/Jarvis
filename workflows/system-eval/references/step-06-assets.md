<!-- system:start -->
# Step-06 Assets (system-eval)

Used by step-06 task 7 (Option C weekly feedback prompt).

## Prompt template

```
[Rigby]: Quick feedback request — {N} recent runs could use a rating.
For each, reply "positive", "negative", or "skip":

1. {eval_id} — {name} on {date}, score {score}, grade {grade}
   "{grader_notes truncated to 80 chars}"

2. {eval_id} — ...

3. {eval_id} — ...

(Or reply "skip all" to defer.)
```

## Rating write-back snippet

```python
# For each rated record:
record["assessment"]["controller_feedback"]["rating"] = "{positive|negative}"
record["assessment"]["controller_feedback"]["timestamp"] = "{ISO-8601 now}"
# Write back to systems/eval-harness/runs/{eval_id}.json
```
## Dashboard Chart.js sed patch (task 2a)

```bash
sed -i '' \
  's|chart\.js@4\.4\.0/dist/chart\.umd\.min\.js|chart.js@4.5.0/dist/chart.umd.js" integrity="sha384-iU8HYtnGQ8Cy4zl7gbNMOhsDTTKX02BTXptVP/vqAWIaTfM7isw76iyZCsjL2eVi" crossorigin="anonymous|' \
  systems/eval-harness/dashboard.html
```
<!-- system:end -->
