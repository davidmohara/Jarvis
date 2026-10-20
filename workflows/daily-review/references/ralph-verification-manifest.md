<!-- system:start -->
# Ralph Verification Spawn Manifest (daily-review step-auto)

Exact payload for the adversarial-verification spawn in step-auto item 7.

```
   Agent: ralph
   Workflow: workflows/daily-review-verification/workflow.md
   Manifest:
     review-file: "{narrative-path}"
     omnifocus-data: data/omnifocus-unified.json
     delegation-tracker: delegations/tracker.md
     run-date: <YYYY-MM-DD>
   Task: Cross-check the auto narrative's claims against recorded state and return your verdict table.
   ```
<!-- system:end -->
