---
name: golf-booking
description: Live tee-time booking for Frisco Lakes Golf Club. Runs at midnight, 8 days before the target date. Reads preview-output.json (produced by workflows/golf-preview) for preference order, opens ChronoGolf via Chrome as the David O'Hara Total Member account, evaluates real-time availability, books the best available slot, creates a calendar block, and sends Slack confirmation. Converted from skills/golf-booking/SKILL.md with deterministic quality gates added at every irreversible action.
agent: sterling
model: sonnet
schedule: |
  Wed/Thu/Fri at 11:00 PM CST (midnight EST — when the 8-day booking window
  opens for the target Friday/Saturday/Sunday scored by workflows/golf-preview)
rocks: Personal — Golf & Leisure
---

<!-- system:start -->

# Golf Booking Workflow

**Goal:** Book the highest-ranked viable tee time from `preview-output.json` at Frisco Lakes
Golf Club for David and Susie O'Hara, with zero silent failures and zero unauthorized date
substitutions. You must figure out how to book the tee time — no falling back to manual
booking except as an explicit, Slack-notified last resort.

**Agent:** Sterling — Social Life & Leisure

**Predecessor:** `workflows/golf-preview/workflow.md` produces `preview-output.json`, gated by
its own Gate 4 (Output Schema) before this workflow ever reads it.

---

## WHY THIS EXISTS AS A WORKFLOW, NOT A SKILL

`skills/golf-booking/SKILL.md` accumulated a long list of incident-driven MANDATORY EXECUTION
RULES over time (see `systems/error-tracking/entries/err-20260813T122205-D64IQ7.json`, the
booking-window date-substitution incident that produced rule #15). Every one of those rules is
preserved verbatim in this workflow's step files. What the skill format didn't give was a
place to make each rule a **checkable gate** with an explicit escalation path, separate from
the narrative instructions. This workflow adds seven gates — one per irreversible or
easily-corrupted action — so a failure at any point produces a specific, logged reason instead
of an ambiguous "something went wrong."

---

## INITIALIZATION

### Data Sources

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| `preview-output.json` | Preference-ranked tee time options | Local file (written by golf-preview) |
| ChronoGolf | Live tee time availability, booking | Control Chrome MCP |
| 1Password | ChronoGolf credentials (login recovery only) | 1Password CLI |
| Calendar.app | Calendar block creation | AppleScript (Family calendar) |
| Slack | Confirmation delivery | master-slack skill |

### Paths

- `preview_output` = `workflows/golf-booking/preview-output.json`
- `state_file` = `workflows/golf-booking/state.yaml`
- `verify_scripts` = `workflows/golf-booking/verify/*.py`
- Booking URL: `https://www.chronogolf.com/dashboard/#/memberships`
- 1Password ChronoGolf item ID: `5xjnwumckxbpiuokidflufwtpi`

### Context Boundaries

- Logged in as: David O'Hara — 41 Frisco Lakes Total Member
- David's email: `david@davidohara.net` (from 1Password)
- Party size: 2 players (a twosome) by default — both as "41 - Frisco Lakes Total Member".
  Override via `preview-output.json`'s `party_size` field only.
- Player 1: David O'Hara (pre-populated). Player 2: Susie O'Hara.
- Course: Frisco Lakes Golf Club (18-hole course). Fallback: PLP / Total - 9 Hole
  (drought/late rounds only).
- Confirmation timer: 5 minutes once the confirmation screen loads — move fast.

---

## STATE CHECK — Run Before Any Execution

1. Read `state.yaml` in this workflow directory.
2. If `status: in-progress`: resume from `current-step`. Load `accumulated-context`.
3. If `status: not-started` or `status: complete`: fresh run. Clear `accumulated-context`.
4. If `status: awaiting-window`: this is the expected state when the target date named by
   `override_instructions` or the top-ranked option is not yet inside the 8-day booking
   window (see Gate 1). Re-check on the next scheduled run — do not re-evaluate or re-rank,
   book exactly what was already validated once the window opens.
5. If `status: aborted` or `status: verification-failed`: surface to controller and wait for
   instruction.
6. **Check for already-booked round this weekend**: search calendar for a golf block on the
   target Saturday/Sunday. Unless otherwise directed by David, if found, skip booking and
   output: `[Sterling]: Golf already booked for this weekend ([date] [time]). No action needed.`

---

## EXECUTION

Read and follow each step file in order. Every gate marked **hard** must pass before the next
step runs — this is a real-money, real-calendar action with a 5-minute confirmation window;
there is no room for "proceed and fix it later."

| Step | File | Produces | Gate |
|------|------|----------|------|
| 1 | `steps/step-01-read-preview-and-window-precheck.md` | Validated target date within booking window | **Gate 1 — Booking Window Pre-Check** (hard, blocking, no-substitution) |
| 2 | `steps/step-02-login-recovery.md` | Authenticated ChronoGolf session | **Gate 2 — Login Verification** (hard, blocking) |
| 3 | `steps/step-03-navigate-select-players.md` | Date, course, holes, and player selections made | (procedural checks inline, no standalone gate — feeds Gate 3) |
| 4 | `steps/step-04-select-time-and-confirm.md` | Confirmed reservation on ChronoGolf | **Gate 3 — Confirmation Success** (hard, blocking, exact-match) |
| 5 | `steps/step-05-visual-verification.md` | Booking visible on Bookings page | **Gate 4 — Visual Verification** (hard, blocking, critical escalation) |
| 6 | `steps/step-06-calendar-block.md` | Calendar event on Family calendar | **Gate 5 — Calendar Event Verification** (soft, fallback notification) |
| 7 | `steps/step-07-slack-confirmation.md` | Slack confirmation to #jarvis | **Gate 6 — Slack Delivery** (hard, blocking with fallback) |
| — | `verify/step-07-terminal-outcome.py` | Post-hoc state.yaml audit | **Gate 7 — Terminal Outcome Honesty** (hard, blocking — booked or documented failure, never silent) |

---

## QUALITY GATE SUMMARY

| Gate | Type | Enforced by | On failure |
|------|------|-------------|------------|
| 1. Booking Window Pre-Check | Hard | Inline date-arithmetic check in step-01 + `verify/step-01-window-precheck.py` | Abort. `status: awaiting-window`. Never substitute a different date (see incident err-20260813T122205-D64IQ7). |
| 2. Login Verification | Hard | Inline DOM-text check in step-02 | Retry recovery once via 1Password. If still failed, Slack alert + abort. |
| 3. Confirmation Success | Hard | Inline exact-string match (`BOOKING-SUCCESS`) in step-04 | Do not treat confirmation-page appearance as success. Move to next ranked option or abort. |
| 4. Visual Verification | Hard | Inline Bookings-page DOM check in step-05 | **Critical.** Send Slack alert, abort, do not claim success even though ChronoGolf's confirmation screen appeared. |
| 5. Calendar Event Verification | Soft | Inline AppleScript verification in step-06 | Fallback Slack notification with manual-add instructions. Continue — booking itself is still valid. |
| 6. Slack Delivery | Hard (with fallback) | Inline check in step-07 | Fallback to `memory/working/`. Never skip silently. |
| 7. Terminal Outcome Honesty | Hard | `verify/step-07-terminal-outcome.py` | Retry — either complete the booking or write a real `resolution-note` explaining the documented failure. A blank failure is the one unacceptable outcome. |

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Session expired on load | **Automatic recovery (Gate 2 / step-02).** Retrieve credentials from 1Password, re-authenticate, continue. |
| Target date outside 8-day booking window | **Gate 1 blocks.** Set `status: awaiting-window`. Retry on next scheduled run. Never substitute a nearer date. |
| 1Password credential lookup fails | Slack alert. Abort. Never invent credentials. |
| reCAPTCHA bypass fails | Try login submit anyway. If redirected to login again, Slack + abort. |
| Confirmation timer expires | Move to next ranked option. |
| All options unavailable | Slack with explanation. Abort. `status: aborted`. |
| Confirmation page appears but booking not visible on Bookings page (Gate 4) | **Critical.** Slack alert with details. Abort. `status: verification-failed`. Do not send success notification. |
| Calendar event creation fails (Gate 5) | Slack with manual-add instructions. Continue — `calendar_event_failed: true` in accumulated-context. |
| Slack confirmation fails (Gate 6) | Fallback file in `memory/working/`. Continue — `slack_notification_failed: true` in accumulated-context. |

---

## OUTPUT

- Confirmed ChronoGolf booking (or a documented, non-silent failure)
- Calendar block on the Family calendar (tee time − 30min through end of round)
- Slack confirmation to #jarvis with date, time, cost, weather snapshot
- `state.yaml` updated: `booking-id`, `booking-date`, `booking-time`, `status: complete`

## NEXT STEP

This is the final phase of the weekly golf booking pipeline. Next run of `workflows/golf-preview`
triggers automatically the following week; this workflow is triggered by the scheduled task
`golf-tee-time-booking` (`config/scheduled-tasks.json`).

## SKILL COMPLETE

After the workflow's final output is delivered, write the skill-run signal file so the eval
harness captures this execution:

```
systems/eval-harness/skill-runs/golf-booking-latest.json
```

Content:
```json
{
  "skill": "golf-booking",
  "agent": "sterling",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this workflow began>",
  "completed": "<ISO-8601 timestamp when this workflow finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"scheduled"` when fired by the scheduled task, `"manual"` otherwise. Set
`status` to `"partial"` if a soft gate degraded (Gate 5) but the booking itself succeeded,
`"failure"` if a hard gate (1-4, 6, or 7) blocked completion with no successful booking. Use
the actual start time of this workflow's execution for `started`. This write is always the
final action.

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
