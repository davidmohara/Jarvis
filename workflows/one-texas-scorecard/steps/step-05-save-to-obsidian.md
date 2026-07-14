---
status: complete
started-at: "2026-07-14T00:09:00"
completed-at: "2026-07-14T00:10:00"
outputs:
  recency_checked: true
  within_28_day_window: true
  last_entry_date: "2026-06-22"
  days_since_last_entry: 22
  append_outcome: "appended — last entry was partial (new clients only), this is first full H1 workflow run since 2026-04-21"
  entry_date: "2026-07-14"
model: sonnet
---

<!-- system:start -->
# Step 05: Save to Obsidian

## MANDATORY EXECUTION RULES

1. You MUST check the tracking file for a last entry date before appending. No blind appends.
2. You MUST prompt the controller before appending if the last entry is less than 28 days ago.
   Do not proceed without explicit confirmation.
3. You MUST assemble the full snapshot from accumulated-context — do not re-pull any data.
4. You MUST include today's date as a `## [YYYY-MM-DD]` header in the appended content.
5. Do NOT overwrite existing file content — append only.

---

## NEXT STEP

Workflow complete. No further steps.
<!-- system:end -->


## WRITE WORKING MEMORY

After the workflow output has been delivered, write a working memory file to `memory/working/` using this filename pattern:

```
one-texas-scorecard-YYYY-MM-DD-HHmmss.md
```

where `YYYY-MM-DD-HHmmss` is the local date and time at the moment of writing. Use the session start time from `state.yaml` if available; otherwise use current time.

The file must begin with this YAML frontmatter (all fields required):

```yaml
---
type: working
task_id: "session"
session_id: "chase-{YYYY-MM-DD}-{HHmmss}"
agent-source: chase
created: {YYYY-MM-DD}T{HH:MM:SS}
expires: {YYYY-MM-DD+2}T{HH:MM:SS}
status: active
context: "One Texas scorecard — {YYYY-MM-DD}"
---
```

Body: 3-5 bullet points summarizing key outputs, decisions, and any flags from this run. Keep it under 200 words.

---
<!-- personal:start -->
<!-- personal:end -->
