---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

---
step: 2
name: Write Entry to My Leads.xlsx
previous: step-01-identify-lead.md
---

# Step 2: Write Entry to My Leads.xlsx

## Objective

Append the new lead entry to the Excel file in OneDrive.

## Write Methods (in priority order)

### Method 1: Desktop Commander + openpyxl (Preferred)

Use Desktop Commander's `start_process` to run a Python script via openpyxl. The file lives at:
`~/Library/CloudStorage/OneDrive-Improving/Sales/My Leads.xlsx`

**CRITICAL:** The sheet uses a defined Excel Table (`Table2`). After writing data to the next empty row, you MUST expand the table range to include the new row, or the entry won't be part of the table.

```python
import openpyxl
from datetime import datetime
from copy import copy

path = '~/Library/CloudStorage/OneDrive-Improving/Sales/My Leads.xlsx'
wb = openpyxl.load_workbook(path)
ws = wb.active

# Find next empty row
next_row = ws.max_row + 1
prev_row = next_row - 1  # Last populated row — copy formatting from here

# Write the entry
ws.cell(row=next_row, column=1, value=f'=YEAR(B{next_row})')  # Year formula
ws.cell(row=next_row, column=2, value=datetime(YYYY, M, D))    # Date
ws.cell(row=next_row, column=3, value='Client Name')            # Client
# Column 4 (Passed To) — set value or leave None for unassigned

# COPY FORMATTING from the previous row (font, number format, alignment, fill, border)
for col in range(1, 6):
    src = ws.cell(row=prev_row, column=col)
    dst = ws.cell(row=next_row, column=col)
    dst.font = copy(src.font)
    dst.number_format = src.number_format
    dst.alignment = copy(src.alignment)
    dst.fill = copy(src.fill)
    dst.border = copy(src.border)

# EXPAND THE TABLE RANGE to include the new row
tbl = ws.tables['Table2']
tbl.ref = f'A1:E{next_row}'
tbl.autoFilter.ref = f'A1:E{next_row}'

wb.save(path)
```

### Method 2: Browser Automation (Fallback)

If Desktop Commander cannot access the OneDrive file:

1. Open the SharePoint URL in Chrome:
   `https://improving-my.sharepoint.com/personal/david_o'hara_improving_com/Documents/Sales/My Leads.xlsx`
2. Edit in Excel Online — navigate to the last row, type the entry.

### Method 3: Manual Instruction (Last Resort)

If neither automated method works, tell David exactly what to type and where:
- "Add a row to My Leads.xlsx: Year: 2026, Date: 12-Mar, Client: Nexben, Passed To: [blank]"

## Post-Write Verification

After writing, re-read the file to confirm the entry was added correctly. Report back to David:

- "Logged: [Client] — [Date]. Passed To: [AM or 'unassigned — I'll remind you']."

## Lead Review Hook

If "Passed To" was left blank, flag this for the **lead-review** workflow to surface during the next daily briefing or pipeline review.

## Complete

Workflow ends. Return to conversation.
