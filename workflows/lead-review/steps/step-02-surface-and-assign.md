---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
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
