---
status: complete
started-at: "2026-10-05T22:39:00-05:00"
completed-at: "2026-10-05T22:40:00-05:00"
outputs:
  gate_5_result: "pass"
  delivery_path: "fallback"
  fallback_file: "memory/working/golf-preview-2026-10-05.md"
  rank_1_summary: "Saturday Oct 17, 1:00 PM — 18 holes, $21/player (BEST OPTION)"
  rank_2_summary: "Sunday Oct 18, 2:30 PM — 18 holes, $21/player (backup)"
model: haiku
---

<!-- system:start -->
# Step 05: Summarize and Send Slack Preview

## MANDATORY EXECUTION RULES

1. Always send the Slack notification even if only one viable window is found.
2. If no viable windows exist, still send Slack explaining why — do not silently skip.
3. **Slack goes through `master-slack` only.** Follow the "Sending the Slack Message" section
   below exactly. Do not use the workspace shell, any Slack MCP connector, or a Slack API call
   written by hand. Do not read the workflow once and skip its sending steps.
4. **Non-interactive execution (scheduled tasks):** If the master-slack send fails after the
   steps below, write fallback summary to `memory/working/golf-preview-YYYY-MM-DD.md` and log error to
   `systems/error-tracking/entries/`. Do NOT fail silently — **QUALITY GATE 5** exists
   specifically to catch this.

---

## EXECUTION PROTOCOL

**Agent:** Sterling, spawned by the coordinator, never executed inline
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

### Sending the Slack Message (master-slack, mandatory path)

Slack delivery for this workflow goes ONLY through the `master-slack` skill
(`.claude/skills/master-slack/SKILL.md`). Do not call `post.py` from the workspace shell
(`mcp__workspace__bash`), do not use any Slack MCP connector, and do not hand-write a
Slack API request. The workspace shell runs in a Linux sandbox and cannot reach the Mac
paths used by the bot script.

1. **Load Desktop Commander** if its tools are deferred:
   `ToolSearch` with `select:mcp__Desktop_Commander__start_process,mcp__Desktop_Commander__read_process_output`.
2. **Use paths relative to the jarvis repo.** Desktop Commander does not start in the repo: its
   working directory is `/`. Every command must therefore begin with `cd ~/develop/jarvis &&`.
   After that, use only relative paths such as `systems/slack-bot/post.py`. Do not use the
   OneDrive IES path from `master-slack` Option 2. Before sending, confirm the script is present:
   `cd ~/develop/jarvis && test -f systems/slack-bot/post.py && echo ok`. If that check fails,
   go to the fallback in step 6. Do not guess another path.
3. **Send through Desktop Commander** (`mcp__Desktop_Commander__start_process`, `timeout_ms: 15000`),
   using the heredoc pattern from `master-slack` Option 2 with a relative path:
   ```bash
   cd ~/develop/jarvis && python3 - <<'PYEOF'
   import subprocess
   msg = """<message body with real newlines, no literal \n>"""
   r = subprocess.run(["python3", "systems/slack-bot/post.py", "C0B15SW9FB5", msg], capture_output=True, text=True)
   print(r.stdout.strip() or r.stderr.strip())
   PYEOF
   ```
   The channel for `#golf` is `C0B15SW9FB5`. Use real multi-line strings. Never write a literal `\n`.
4. **Read the result.** A response of `{"ok": true, "channel": ..., "ts": ...}` is delivery
   confirmed. Pass that object as `slack_send_result` to Gate 5. Do not resend.
5. **No-duplicate rule (from master-slack).** Do not send a second time unless the first
   returned an explicit error. An empty output does not mean failure. If unsure, read
   `#golf` with `python3 systems/slack-bot/read.py channel C0B15SW9FB5 0.1` through
   Desktop Commander before any retry. One retry maximum.
6. **If the send fails** (explicit error, script missing, or Desktop Commander unavailable),
   use the fallback in Quality Gate 5. Include the exact error text in the fallback file
   and in the error entry.

Record the delivery path and the Slack `ts` in `state.yaml` under `slack_delivery`.

Send to **#golf** (C0B15SW9FB5) using the master-slack skill. The Slack message should mirror the inline summary in
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
