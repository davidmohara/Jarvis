---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Verify Morning Briefing Claims Against Source Data

## MANDATORY EXECUTION RULES

1. You MUST read the delivered briefing and the source-data files directly. Do NOT accept the briefing's own citations as evidence: re-derive each claim from the data file it names.
2. You MUST return a verdict for every checklist item. No item may be omitted, even if the briefing has no content for it.
3. You MUST NOT fix, edit, or re-run anything. You verify and report; the caller decides.
4. If a source file is missing or unreadable, mark the dependent items ⚠️ Unverified with note "source unreadable." Do not infer correctness from silence.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Briefing manifest (briefing file path + claimed source-data paths) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly the morning briefing for this run and its source data. Nothing else.
- Ralph does not re-synthesize the briefing. He checks the claims that were made.

---

## YOUR TASK

### Sequence

1. **Locate the artifacts.** Find the most recent `memory/working/morning-briefing-*.md` (the delivered briefing) and read it. Read the source files named in the manifest: `data/calendar-unified.json`, `data/email-unified.json`, `data/omnifocus-unified.json`, `delegations/tracker.md`.

2. **Apply the calendar / email / OmniFocus cross-check lens.** For each item below, re-derive the truth from the source file, then compare to what the briefing states:

   | # | Checklist item | Ground truth source | Verdict |
   |---|----------------|---------------------|---------|
   | 1 | Meeting count and times | `data/calendar-unified.json` events for today's date | ✅ if the briefing's calendar table matches the events; ⚠️ if any event is missing, invented, or has a wrong time/date |
   | 2 | Attendee / context claims | calendar events' attendees, cross-referenced against `data/clay-reminders-unified.json` | ⚠️ if a named attendee or context line is not supported by the event data |
   | 3 | Task counts (inbox / due today / overdue / flagged) | `data/omnifocus-unified.json` (and `status` field) | ⚠️ if the briefing's numbers disagree with the file, or if the briefing reports a clean task day when `status: failed` |
   | 4 | OmniFocus disclosure | `data/omnifocus-unified.json` `status` | ⚠️ if the pull was degraded (`status: failed`) and the briefing does not disclose it |
   | 5 | Delegation status | `delegations/tracker.md` active rows | ⚠️ if the briefing names a delegation as overdue/complete that the tracker does not support |
   | 6 | Email / inbox claims | `data/email-unified.json`, `data/jarvis-inbox-unified.json` | ⚠️ if the briefing claims an inbox state the file does not show |
   | 7 | Wrong-day / stale data | file `pulled_at` / mtimes vs the briefing date | ⚠️ if the briefing presents prior-day data as today's |

3. **Apply the "are you really done?" test** per item: ✅ Verified (claim traced to source), ⚠️ Unverified (claim unsupported, source stale, or source unreadable), ➖ Not applicable (briefing legitimately has no content for the item, e.g. no meetings today).

4. **Return the verdict table**, no preamble:

   ```
   | Item | Briefing claim | Source evidence | Verdict |
   |------|----------------|-----------------|---------|
   | ...  | ...            | ...             | ✅/⚠️/➖ |
   ```

   Then one summary line:
   - If all ✅ or ➖: `All briefing claims traced to source data: verified.`
   - If any ⚠️: `Re-run required: [items].`

5. **Update state.yaml** with `status: complete`, `current-step: step-01`, and record the verdict summary in `accumulated-context.verdict-summary` (`all-verified` or `findings`) plus `accumulated-context.findings: [list]`.

---

## SUCCESS METRICS

- Every checklist item has a verdict
- Each ✅ claim cites the source file and the value re-derived from it
- Any ⚠️ item names the specific unsupported claim
- Verdict summary written to state.yaml

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Briefing file not found | Surface: "No delivered briefing found: nothing to verify." Mark all items ⚠️. |
| A source file missing or unreadable | Mark dependent items ⚠️ Unverified with note "source unreadable." Do not infer correctness. |
| Manifest incomplete | Attempt inference from conventions; if a source cannot be resolved, mark the item ⚠️ with note "no verifiable source." |

---

## NEXT STEP

This is the final step. Return the verdict table to the caller. Workflow complete.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
