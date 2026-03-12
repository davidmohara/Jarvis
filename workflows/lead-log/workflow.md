---
name: lead-log
description: Log a new lead to David's personal lead tracker (My Leads.xlsx in OneDrive). Captures date, client name, and assigned Account Manager. Fires when a new prospect surfaces in conversation.
agent: chase
---

<!-- system:start -->
# Lead Log Workflow

**Goal:** Every lead David generates gets captured in `My Leads.xlsx` — no exceptions. If it came up in conversation, it goes in the tracker. The execution gap dies here.

**Agent:** Chase — Revenue & Pipeline

**Architecture:** Sequential 2-step workflow. Identify the lead details from conversation context, then write the entry to the Excel file. Confirm with David before writing.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| My Leads.xlsx | Current lead log — to find the next empty row and avoid duplicates | M365 MCP: `read_resource` with file URI (see below) |
| Conversation context | Client name, date, referral source, Account Manager assignment (if known) | Current session |

### File Reference

- **File:** `My Leads.xlsx`
- **Location:** OneDrive → `Sales/My Leads.xlsx`
- **SharePoint URL:** `https://improving-my.sharepoint.com/personal/david_o'hara_improving_com/Documents/Sales/My Leads.xlsx`
- **M365 File URI:** `file:///b!ilmQNHdRSEuxhG1Y66o6s2pUiIQPYJdBpYjAjbtZ8aRPj2M3V6pnT7CvN3AYbbdR/01ZA7BKHDIRSDTOJSU5JF2L2KUC4DMNJMF`
- **Sheet:** `Leads` (first/default sheet)

### Column Schema

| Column | Description | Example |
|--------|-------------|---------|
| **Year** | Year the lead was generated | `2026` |
| **Date** | Date in `DD-Mon` or `M/DD/YYYY` format | `12-Mar` |
| **Client** | Company or person name | `Nexben` |
| **Passed To** | Account Manager assigned. Leave blank if unassigned. | `Diana Stevens` |

### Known Account Managers

Alexander Powell, Craig Fisher, Rod Patane, Mark Miesner, Diana Stevens, Vicki Kelly, Stephen Johnson, Derek Nwamadi. David may also use `Me` (keeping the lead himself) or `---` (explicitly no handoff).

### Triggers

This workflow fires when:
- David explicitly says "log this lead" or "new lead"
- A referred intro surfaces (e.g., someone emails David connecting him with a prospect)
- A new client meeting is scheduled with a company not already in the lead tracker
- Chase detects a new prospect during client meeting prep or pipeline review

### Input

One of:
- Explicit instruction: "Log [Company] as a new lead"
- Implicit: A new prospect surfaces in conversation and Chase recognizes it should be tracked
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Read fully and follow: `steps/step-01-identify-lead.md` to begin the workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
