---
step: step-05-save-to-obsidian
workflow: one-texas-scorecard
description: Check recency, prompt if needed, then append consolidated scorecard to Obsidian.
---

# Step 5 — Save to Obsidian

## 5a — Check Last Entry Date

Read the tracking file from Obsidian:

```
mcp__obsidian-mcp-tools__get_vault_file
path: Mind/One Texas/One Texas Scorecard Tracking.md
```

If the file does not exist, create it with a header and proceed directly to 5c:

```
mcp__obsidian-mcp-tools__create_vault_file
path: Mind/One Texas/One Texas Scorecard Tracking.md
content: # One Texas Scorecard Tracking

_Automated snapshots appended by Chase via one-texas-scorecard workflow._

---

```

If the file exists, scan for the most recent date header. Date headers follow this format:
`## [YYYY-MM-DD]`

Extract the most recent date. Calculate the number of days between that date and today.

## 5b — Recency Gate

If the most recent entry is **less than 28 days ago**:

> "[Chase]: The last One Texas Scorecard entry was [date] — [N] days ago. That's within
> the 28-day window. Append anyway?"

Wait for confirmation before proceeding. If the controller says no, set
`state.yaml status: aborted` and stop. If yes, proceed to 5c.

If the most recent entry is **28 or more days ago**, or the file was just created, proceed
directly to 5c without prompting.

## 5c — Assemble and Append

Assemble the full snapshot from `accumulated-context` in this order:

```markdown
## [Today's Date — YYYY-MM-DD]

### Revenue

[revenue output from step-01]

---

### Co-Sell Pipeline

[co-sell output from step-02]

---

### Pipeline Snapshot

[pipeline output from step-03]

---

### New Clients

[new-clients output from step-04]

---
```

Append to the file:

```
mcp__obsidian-mcp-tools__append_to_vault_file
path: Mind/One Texas/One Texas Scorecard Tracking.md
content: [assembled snapshot above]
```

## 5d — Confirm and Close

Confirm to the controller:

> "[Chase]: One Texas Scorecard updated — [Today's Date] entry appended to
> `Mind/One Texas/One Texas Scorecard Tracking.md`."

Update `state.yaml`:
- `status: complete`
- `current-step: complete`
