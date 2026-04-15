---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

---
step: 1
name: Identify Lead Details
next: step-02-write-entry.md
---

# Step 1: Identify Lead Details

## Objective

Extract the lead details from conversation context. Confirm with David before writing.

## Actions

1. **Extract from context:**
   - **Client name** — the company or person. Use the company name if known (e.g., "Nexben" not "Lauren Sweda").
   - **Date** — use today's date unless David specifies otherwise.
   - **Account Manager** — if David has already stated who gets the lead, capture it. If not, leave blank.

2. **Check for duplicates:**
   - Read `My Leads.xlsx` via M365 MCP (`read_resource` with the file URI).
   - Search the Client column for the company name.
   - If the company already exists, **do not add a duplicate**. Instead, inform David: "Already in the tracker — logged on [date], passed to [AM]."

3. **Confirm with David:**
   - State what you're about to log: "Logging [Company] as a new lead, dated [date]. Passed To: [AM or 'unassigned']. Good?"
   - Wait for confirmation before proceeding to Step 2.
   - If David provides an AM assignment during confirmation, capture it.

## Output

Pass to Step 2:
- `year`: e.g., `2026`
- `date`: e.g., `12-Mar`
- `client`: e.g., `Nexben`
- `passed_to`: e.g., `Diana Stevens` or blank

## Proceed

→ `step-02-write-entry.md`
