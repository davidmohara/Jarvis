---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->
# Step 05: Summarize and Send Slack Preview

## MANDATORY EXECUTION RULES

1. Always send the Slack notification even if only one viable window is found.
2. If no viable windows exist, still send Slack explaining why — do not silently skip.
3. **Non-interactive execution (scheduled tasks):** If plugin:productivity:slack /
   master-slack is unavailable, write fallback summary to
   `memory/working/golf-preview-YYYY-MM-DD.md` and log error to
   `systems/error-tracking/entries/`. Do NOT fail silently — **QUALITY GATE 5** exists
   specifically to catch this.

---

## EXECUTION PROTOCOL

**Agent:** Sterling
**Input:** `preview-output.json` (validated by Gate 4)
**Output:** Slack message to #golf, or documented fallback

---

## YOUR TASK

Before sending Slack, output the full recommendation summary inline (in the session / task
log). This makes the output reviewable without opening Slack. Format it as follows:

```
**Target Weekend: [Fri date] – [Sun date]**
- Friday [date]: [available ✅ | unavailable — reason]
- Saturday [date]: [available ✅ | unavailable — reason]
- Sunday [date]: [available ✅ | unavailable — reason]

**Heat streak check ([Mon–Fri before target Friday]):** [temp], [temp], [temp], [temp], [temp] → [N] of 5 hit 99°F → heat_streak: [true|false] → default preferred start [1:00 PM | 4:00 PM]

---

**Rank 1 — [Day Month D, Time]** | Score: [N]
$[cost]/player · [temp]°F · [rain]% rain · [wind] mph wind · [condition] · [rationale]

**Rank 2 — [Day Month D, Time]** | Score: [N]
$[cost]/player · [temp]°F · [rain]% rain · [wind] mph wind · [condition] · [rationale]

[Rank 3 if applicable]
```

Then read and follow `.claude/skills/master-slack/SKILL.md`.

Send to **#golf** (C0B15SW9FB5). The Slack message should mirror the inline summary in
condensed form:

```
*⛳ Golf Options — Weekend of [Fri date] – [Sun date]*

_Heat streak: [active 🔥 → default 4 PM | inactive → default 1 PM]_

*1. [Day, Month D] — [Time]*
• 🌤 [temp]°F, [rain]% rain, [wind] mph
• 💰 $[cost]/player · 18 holes · Score: [N]

*2. [Day, Month D] — [Time]*
• 🌤 [temp]°F, [rain]% rain, [wind] mph
• 💰 $[cost]/player · 18 holes · Score: [N]

[3rd option if available]

_Booking at midnight. Reply to redirect — otherwise top option is booked._
```

If `weather_data_missing: true` or `ct_conversion_flag: true` from earlier steps, prepend a
line: `⚠️ [weather data unavailable for target dates | possible timezone issue in calendar check — verify manually]`.

If `top_options` is empty, send instead:
```
⛳ No viable golf windows this weekend — [no_viable_reason]. No booking will be made.
```

---

## QUALITY GATE 5 — Slack Delivery (HARD, WITH MANDATORY FALLBACK)

This is the last gate before the run ends. A silent failure here means David never sees the
weekend's options and finds out only when golf-booking either books nothing or books the
wrong thing at midnight.

```bash
python3 workflows/golf-preview/verify/step-05-slack-delivery.py <<< '{"ies_root": ".", "slack_send_result": <captured result of the master-slack call>}'
```

The script checks:
- The Slack send returned `ok: true` with a timestamp, OR
- A fallback file exists at `memory/working/golf-preview-YYYY-MM-DD.md` (today's date) AND a
  corresponding error entry exists under `systems/error-tracking/entries/`

**On `result: retry`:** Neither the Slack send nor the fallback path completed. Do not close
out this workflow run. Write the fallback file now, log the error, and re-run the gate.

**On `result: pass`:** Log `[Gate 5] PASS — delivered via slack | delivered via fallback` and
mark this step (and the workflow) complete.

---

## SUCCESS METRICS

- Slack message sent to #golf before midnight (at least 1 hour before the golf-booking run),
  OR a fallback file + error log entry exist
- All available days evaluated — no silent skips
- Weather data present for all candidate windows, or explicitly flagged missing

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Slack fails | Write output to `memory/working/golf-preview-YYYY-MM-DD.md` as fallback. Log error to `systems/error-tracking/entries/`. Re-run Gate 5 to confirm the fallback satisfies it. |
| Gate 5 fails on both paths | Escalate — this should not be reachable if the fallback instructions above were followed. Report to controller directly. |

## NEXT STEP

This is the final step of `workflows/golf-preview`. Mark `state.yaml` `status: complete`.
`workflows/golf-booking/workflow.md` picks up from `preview-output.json` at its scheduled
midnight run.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
