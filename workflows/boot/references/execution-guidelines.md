<!-- system:start -->
## Execution Guidelines

### Parallel Execution (Fire All Simultaneously)

```
Step 01.2 begins
  ↓
Fire all 4 pulls simultaneously:
  ├─ Pull A: Email (M365 API call)
  ├─ Pull B: OmniFocus
  ├─ Pull C: Clay reminders
  ├─ Pull D: Jarvis inbox
  └─ Pull E: YNAB spend
  
Wait for all to complete
  ↓
Record status for each pull
  ↓
Proceed to step 02
```

Do NOT wait for one pull to finish before starting the next. They should all run concurrently.

### Status Reporting

Each pull MUST report one of three outcomes:
- **completed** — Pull succeeded, file written, N items found
- **nothing-to-surface** — Pull succeeded but no items (empty result)
- **failed — [reason]** — Pull failed (API unavailable, permissions, etc.)

Silence is not an option. Every pull must report status.

---
<!-- system:end -->
