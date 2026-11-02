---
status: complete
started-at: '2026-11-02T16:19:42Z'
completed-at: '2026-11-02T16:21:27Z'
---

<!-- system:start -->
# Step 05: Synthesize Briefing (Phase 4)

## MANDATORY EXECUTION RULES

1. You MUST run morning briefing step-04 as written. This step handles briefing synthesis — do not replace it with an ad-hoc summary.
2. You MUST incorporate all Phase 2 task findings into the briefing. Data gathered in step-02 is not optional input.
3. Do NOT proceed to step-06 until the briefing is delivered to the controller.

---

## EXECUTION PROTOCOL

**Agent:** briefing subagent (Master persona), spawned by the coordinator after step-04 completes, never executed inline in the coordinator's session (see `workflow.md`).
**Input:** All accumulated-context from steps 01-04
**Output:** Completed morning briefing delivered to the controller

---

## CONTEXT BOUNDARIES

- Morning briefing step-04 owns the format and synthesis logic. Follow it as written.
- Phase 2 findings (lead review, 72-hour look-ahead, email triage, Jarvis inbox) must be woven into the briefing — not appended as raw data.
- Any tasks that failed in step-02 must appear in the briefing as degraded data flags, not silently omitted.

---

## YOUR TASK

1. **Spawn Chief for morning briefing step-04.**
   Spawn **Chief** with `workflows/morning-briefing/steps/step-04-*.md`, the owning agent runs it in full. Provide it with the full accumulated-context as input so all gathered data is incorporated into the briefing.

2. **Ensure Phase 2 findings are incorporated:**
   - Lead review findings (Task F) — surface any unassigned or actionable leads
   - 72-hour look-ahead (Task G) — include the next 3 days of notable meetings
   - Email triage (Task H) — surface any flagged or time-sensitive messages
   - Jarvis inbox (Task I) — surface any items requiring attention
   - Clay reminders and birthdays from step-04 — include in the briefing
   - Watchtower — does not run during boot (it runs via the standalone morning-briefing workflow or on demand). Omit the briefing's Watchtower section unless a `watchtower_output` block from a same-day standalone run is present in accumulated-context; if present, pass it to Chief unchanged. Morning-briefing step-04 renders the section from `watchtower_output.scored_items` (top 5) and omits it when the list is empty. Status `ok` and `reused` render normally; `no-items` omits the section; `failed` omits it and is flagged below.

3. **Flag any degraded data** — if a Phase 2 task failed, note it in the briefing:
   > ⚠️ [Task name] unavailable — data not included.

   Watchtower counts as a task here only when a `watchtower_output` block exists in accumulated-context: `watchtower_output.status: failed` or `ledger_check: mismatch` each get one degraded-data line. A missing `watchtower_output` is the expected state and is never flagged.

4. **Hold the finished briefing** — this step runs inside the briefing subagent Master spawned for steps 05 through 08 (see `workflow.md` EXECUTION section), so "deliver to the controller" here means: carry the complete, verbatim briefing text forward through steps 06-08, then include it in full in this subagent's final message. Master relays it to the controller unabridged — it is the primary output of the entire boot sequence. Do not stop early to message the controller directly; continue to step-06.

5. **Fold the reminders read into the Chief turn.** The due reminders are already itemized in accumulated-context under `task-j-detail`. Inspect `data/reminders.json` in the same turn you spawn Chief, never in a turn of its own, and pass Chief the due reminders verbatim so its Reminders section renders from real data.

6. **Write, following the WRITE PROTOCOL below.** Do not write state until the briefing exists.

---

## WRITE PROTOCOL (this block is the entire bookkeeping cost for this step)

1. One clock read: `date -u +%Y-%m-%dT%H:%M:%SZ`. Reuse that exact value for every write below.
2. Edits to `workflows/boot/state.yaml`, both anchored on fixed literals, no grep and no re-read:
   - Insert this step's key directly beneath the literal `accumulated-context:` line.
   - Change the line `current-step: step-05-synthesize-briefing.md` to `current-step: step-06-scan-workflows.md`.
   If a key already exists (a retry), edit that existing line instead of inserting a second copy.
   **Match whole lines including the line break.** `accumulated-context:` is also the anchor every step uses, and prose values in this file contain text that can collide with a bare substring; the Edit tool refuses a non-unique `old_string`.
3. Edits to `workflows/morning-briefing/state.yaml`: a targeted Edit on `current-step: step-04-synthesize-briefing` → `step-05-verify-briefing`, and a targeted Edit on the `completed:` line → the same clock value. Get that `completed:` line in the same Bash call as the clock read (`grep -n '^completed:' workflows/morning-briefing/state.yaml`), never in a turn of its own. If Chief already advanced either value during its own post-completion protocol, skip that one and do not hunt for an absent anchor. **Never a full-file Write**: today that Write alone cost 2,725 output tokens.
4. One Edit to this step file's frontmatter: `status: complete`, `completed-at` = the clock value.
5. Issue the Edits as parallel tool calls in one turn. The clock read is the only call that must precede them.
6. Never `cat` state.yaml. Never Write state.yaml.

**`briefing_delivered` value:** one line, 200 characters max, with exactly this prefix so the next step's anchor is predictable:

```
briefing_delivered: "yes: 3 paragraphs + N-row calendar + M reminders; WM: memory/working/morning-briefing-YYYY-MM-DD-HHmmss.md"
```

**`current-step`:** `step-06-scan-workflows.md`.

---

## SUCCESS METRICS

- Morning briefing step-04 executed as written
- All Phase 2 task findings incorporated (or their absence flagged)
- Briefing delivered to the controller
- No data silently omitted

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Morning briefing step-04 file missing | Synthesize the briefing directly from accumulated-context using standard briefing format (calendar, tasks, leads, email, look-ahead, Clay). Note: "Step-04 template unavailable — using raw synthesis." |
| No accumulated-context available | Surface what is available. Flag each missing data source explicitly. Do not deliver an empty briefing — deliver a degraded one with clear flags. |

---

## NEXT STEP

Read fully and follow: `step-06-scan-workflows.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
