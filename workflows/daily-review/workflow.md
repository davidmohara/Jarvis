---
name: daily-review
description: End-of-day shutdown - capture completions, carry-forwards, and tomorrow's priorities
agent: chief
---

<!-- system:start -->
# Daily Review Workflow

**Goal:** Close the day with accountability. Capture what happened, surface what didn't, and set tomorrow's priorities so the morning briefing has something to work with.

**Agent:** Chief — Daily Operations & Execution

**Architecture:** Two modes. Interactive (default): Chief guides the controller through a structured shutdown, then updates system files. Auto (pass `auto` as argument): fully autonomous, no user interaction — synthesizes from data sources and writes narrative to the knowledge system only.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Task management | Tasks completed today, tasks created today, inbox state | Task management API |
| Calendar | What meetings happened today | M365 MCP |
| Delegation tracker | Any delegations completed or created today | Read delegations/tracker.md |
| Quarterly objectives | Current rocks for alignment check | Read context/quarterly-objectives.md |

### Paths

- `delegation_tracker` = `{project-root}/delegations/tracker.md`
- `quarterly_objectives` = `{project-root}/context/quarterly-objectives.md`
- `daily_review_output` = `{project-root}/reviews/daily/YYYY-MM-DD.md`
- `daily_review_template` = `{project-root}/reviews/daily/_template.md`
- `morning_briefing` = `{project-root}/reviews/daily/YYYY-MM-DD.md` (if exists, for cross-check)

### Output

- Interactive mode: daily review file (`reviews/daily/YYYY-MM-DD.md`) + knowledge system narrative + updated delegation tracker
- Auto mode: knowledge system narrative only (no local filesystem write, no delegation updates)
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Check `$ARGUMENTS` for the word `auto` (case-insensitive).

- If `auto` is present: read fully and follow `steps/step-auto.md`. Do not load any other step files.
- Otherwise: read fully and follow `steps/step-01-capture.md` to begin the interactive workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
