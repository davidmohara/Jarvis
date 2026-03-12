---
step: 1
name: Scan Leads for Unassigned Entries
next: step-02-surface-and-assign.md
---

# Step 1: Scan Leads for Unassigned Entries

## Objective

Read `My Leads.xlsx` and identify all entries where "Passed To" is blank, empty, or `---`.

## Actions

1. **Read the file:**
   - Use M365 MCP: `read_resource` with file URI.
   - Parse all rows from the Leads sheet.

2. **Identify unassigned leads:**
   - Filter for rows where "Passed To" is blank, empty, null, or contains `---`.

3. **Determine post-call status for each unassigned lead:**
   - **Check calendar for a PAST meeting** with the lead company:
     - `outlook_calendar_search` with query: "[Company]", `beforeDateTime: today`
     - If a past meeting exists → lead is **post-call**. Record the meeting date as the nag clock start.
   - **If no past meeting found**, check email for signs a call happened:
     - `outlook_email_search` with query: "[Company]" — look for language like "great call", "following up on our conversation", recap notes
   - **If neither found** → lead is **Pre-Call**. No nag. Mark status as "pending first contact."

4. **Categorize by urgency (post-call leads only):**
   - Calculate days since the call/meeting date (NOT the log date)
   - 0–3 days post-call → Fresh
   - 4–7 days post-call → Stale
   - 8+ days post-call → Overdue
   - Pre-call leads → No urgency tier. Optionally note "still scheduling."

5. **Enrich with context (optional but preferred):**
   - For each unassigned lead, quick check:
     - Any upcoming calendar events? (`outlook_calendar_search`)
     - Any recent email threads? (`outlook_email_search`)
     - Any Clay contact data? (`searchContacts`)
   - This context helps David make a faster assignment decision.

## Output

Pass to Step 2 a list of unassigned leads:
```
[
  { client: "Company", date_logged: "4-Feb", call_date: "12-Feb" or null, days_post_call: 28 or null, urgency: "Overdue" or "Pre-Call", context: "..." },
  ...
]
```

## Proceed

→ `step-02-surface-and-assign.md`
