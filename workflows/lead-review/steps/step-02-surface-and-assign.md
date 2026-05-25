---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

---
step: 2
name: Surface Unassigned Leads and Capture Assignment
previous: step-01-scan-leads.md
---

# Step 2: Surface Unassigned Leads and Capture Assignment

## Objective

Present unassigned leads to David with urgency-appropriate language. Capture his AM assignments and write them back to the file.

## Presentation Format

### During Daily Briefing (embedded in revenue section)

If there are unassigned leads, Chase surfaces them after the calendar and before the task list:

**Example (Chase voice):**

> "You've got 3 unassigned leads in the tracker:
>
> **Post-call — needs assignment:**
> 1. **Nexben** — call was yesterday. Fresh. Who gets it?
>
> **Pre-call — still scheduling:**
> 2. **Integrated Financial Settlements** — logged Feb 4. Still in email ping-pong. No call yet.
> 3. **Cardinal IT Solutions (Kashif)** — logged Feb 13. No meeting on the books yet.
> 4. **Paragon Brokerage** — logged Feb 17. Same — no call yet.
>
> No nag on 2-4 until you've had the call. Once you do, I'll start the clock."

### During Pipeline Review (standalone section)

Add a "Lead Tracker" section at the end of the pipeline review output.

### On Explicit Request

Full table with all leads, showing assigned and unassigned, sorted by date descending.

## Capturing Assignments

When David assigns an AM:
1. Confirm: "Got it — assigning [Client] to [AM]. Updating the tracker."
2. Write the "Passed To" value to `My Leads.xlsx` using the **lead-log** workflow's Step 2 write methods.
3. Re-read and verify the entry was updated.
4. Report: "[Client] → [AM]. Done."

If David says "kill it" or "drop it":
- Write `---` to the "Passed To" field (consistent with existing pattern for explicitly declined leads).
- Report: "[Client] marked as no-handoff."

If David says "Me" or "I'll keep it":
- Write `Me` to the "Passed To" field.
- Report: "[Client] stays with you."

## Edge Cases

- **If no unassigned leads:** Skip silently during briefings. On explicit request, say: "Lead tracker is clean — everything's assigned."
- **If the file can't be accessed:** Tell David: "I can't reach My Leads.xlsx right now. Here are the unassigned leads from my last read: [list from memory]. I'll update the file when access is restored."
- **If David adds a new lead during the review:** Chain to the **lead-log** workflow to capture it, then continue the review.

## Complete

Workflow ends. Return to briefing or conversation.

## WRITE WORKING MEMORY

After the workflow output has been delivered, write a working memory file to `memory/working/` using this filename pattern:

```
lead-review-YYYY-MM-DD-HHmmss.md
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
context: "Lead review — {YYYY-MM-DD}"
---
```

Body: 3-5 bullet points summarizing key outputs, decisions, and any flags from this run. Keep it under 200 words.

---

