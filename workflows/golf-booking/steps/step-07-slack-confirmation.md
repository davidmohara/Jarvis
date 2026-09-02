---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 07: Send Booking Confirmation via Slack

## MANDATORY EXECUTION RULES

1. **SLACK NOTIFICATION IS MANDATORY.** After Gate 4 (step-05) confirms the booking is visible
   on the Bookings page, ALWAYS invoke master-slack to send booking confirmation to #jarvis.
   Do NOT skip, suppress, or omit this step under any circumstances. Silence on this step is a
   critical failure mode.
2. If Desktop Commander is unavailable, log the failure explicitly and create a fallback
   notification. Never silently omit the notification.

---

## EXECUTION PROTOCOL

**Agent:** Sterling
**Input:** Verified booking (step-05) + calendar outcome (step-06)
**Output:** Slack confirmation to #jarvis, or documented fallback — **QUALITY GATE 6**

---

## YOUR TASK

### 7a — Invoke master-slack Skill

Execute the master-slack skill from `.claude/skills/master-slack/SKILL.md` using Desktop
Commander:

```
Tool: mcp__Desktop_Commander__start_process
Command: python3 "$(mdfind -name 'post.py' | grep 'systems/slack-bot/post.py' | head -1)" C0AN2PQNXBR "[MESSAGE]"
Timeout: 15000
```

### 7b — Message Template

Send to **#jarvis** (C0AN2PQNXBR):

```
*⛳ Tee Time Booked — Frisco Lakes*

📅 [Day, Month D] at [Time]
🏌️ [18|9] holes · David + Susie
💰 $[cost] due at course
🌤 [temp]°F · [rain]% rain · [wind] mph wind
📍 Frisco Lakes Golf Club
🚗 Arrive by [tee_time - 30min] for range warm-up

Booking #[booking_number]

[If any fallback was taken]: _Note: booked [time] — preferred [preferred_time] was unavailable._
[If drought flag]: _First round in 21+ days — enjoy it._
```

Variable substitution: `[Day, Month D]` e.g. "Saturday, June 27"; `[Time]` e.g. "4:45 PM";
`[18|9]` actual hole count; `[cost]` e.g. "$32.48"; `[temp]`/`[rain]`/`[wind]` from the weather
data in `preview-output.json`; `[tee_time - 30min]` arrival time; `[booking_number]` from
ChronoGolf confirmation.

### 7c — Critical Formatting Rules

1. Use actual multi-line strings — do NOT use literal `\n` characters. Pass the message with
   real newlines through the shell.
2. Escape special characters — dollar signs need `\$` in double-quoted strings.
3. Max 5000 characters — split into multiple sends if exceeded.
4. No "Hi David" — lead with the content.
5. Tight formatting — Slack markdown with emojis for scannability.

---

## QUALITY GATE 6 — Slack Delivery (HARD, WITH MANDATORY FALLBACK)

### 7d — Verify Success

Check the Desktop Commander response:
```json
{"ok": true, "channel": "C0AN2PQNXBR", "ts": "1234567890.123456"}
```

**If `ok: true`:** Log `[Gate 6] PASS — ts=<timestamp>`. Notification delivered. Record the
timestamp.

**If the response indicates failure:** proceed to 7e — this is not optional.

### 7e — Fallback (if Desktop Commander unavailable)

1. Log the failure with error details.
2. Create a fallback notification file in `memory/working/` with the booking confirmation.
3. Notify in the task output: "Slack notification could not be sent — booking confirmed but
   Desktop Commander unavailable."
4. Set `state.yaml`'s `accumulated-context`: `slack_notification_failed: true`. Workflow can
   still complete — the booking itself is valid — but this flag must be present so the failure
   is never invisible.

**Under no circumstances should the notification be silently omitted.**

If the post.py script itself isn't found: search with
`mdfind -name 'post.py' | grep 'systems/slack-bot/post.py'`. If still not found, log error and
create the fallback notification per 7e. If `SLACK_BOT_TOKEN` is missing, log the error and
follow token setup in master-slack's SKILL.md — do not proceed without a token or a documented
fallback.

---

## SUCCESS METRICS

- Gate 6 passes with either a confirmed `ok: true` Slack send or a fully documented fallback
- `preview-output.json` and `state.yaml` updated with the booking result
- `state.yaml` `status: complete`
- No success claimed anywhere without: (1) Gate 4 visual confirmation, (2) Gate 5 calendar
  event verified OR fallback initiated, AND (3) Gate 6 Slack notification delivered OR
  fallback initiated

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Slack notification fails | Fallback file in `memory/working/`. Set `slack_notification_failed: true`. Continue — `status: complete`. |
| `post.py` script not found | Search via `mdfind`. If not found, log error, create fallback notification. Do not proceed silently. |
| `SLACK_BOT_TOKEN` missing | Log error, follow master-slack's token setup. Do not proceed without a token or fallback. |

## NEXT STEP

This is the final step of `workflows/golf-booking`. Update `state.yaml`: `status: complete`,
`booking-id`, `booking-date`, `booking-time`. Then run the terminal audit gate:

```bash
python3 workflows/golf-booking/verify/step-07-terminal-outcome.py <<< '{"ies_root": "."}'
```

This is **QUALITY GATE 7 — Terminal Outcome Honesty**: it re-reads `state.yaml` after this
workflow claims completion and confirms either a real booking (`booking-id`/`booking-date`/
`booking-time` all populated) or a documented failure (a substantive `resolution-note` or
`accumulated-context` explaining why, per the FAILURE MODES table in `workflow.md`). A result
that looks like a failure with nothing recorded at all is the one outcome this gate will not
pass — the workflow can legitimately fail, but it cannot fail silently.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
