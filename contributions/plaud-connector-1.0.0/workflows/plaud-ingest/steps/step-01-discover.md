---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Discover New Recordings

## MANDATORY EXECUTION RULES

1. You MUST query the Plaud API for recordings — do not rely solely on what is already in staging.
2. You MUST cross-reference against the configured KMS to avoid reprocessing already-ingested recordings.
3. You MUST capture recording ID, name, date, duration, and transcription status for every new recording.
4. Do NOT begin downloading or processing transcripts in this step — discovery only.
5. Do NOT proceed to step-02 until the new-recordings list is populated in state.

---

## EXECUTION PROTOCOL

**Agent:** Knowledge Manager (Knox)
**Skill:** `skills/plaud-discover/SKILL.md` — read it in full before executing this step.
**Input:** Today's date (from `state.yaml accumulated-context.target-date`, or default to yesterday if not set)
**Output:** `accumulated-context.new-recordings` — list of recording objects not yet in KMS

---

## YOUR TASK

### Sequence

1. **Set target date** in `state.yaml accumulated-context.target-date` if not already set.
   - Default: yesterday (`today - 1 day`). Boot passes today's date; use it.
   - For a catch-up run, use the `--all` flag behavior (fetch all, dedup against KMS).

2. **Run the discovery** per `skills/plaud-discover/SKILL.md`.
   - Enumerate recordings from the Plaud API for the target date range.
   - Enumerate notes already in the KMS under the meeting root (all subfolders).
   - Diff: recordings present in API but not in KMS = new recordings.

3. **Build the new-recordings list.** For each new recording capture:
   ```yaml
   - file_id: abc123
     name: "Meeting with Todd Wynne"
     date: 2026-04-15
     duration_seconds: 3421
     has_transcript: true
     transcript_status: ready | pending | missing
   ```

4. **Update state.yaml:**
   - `accumulated-context.new-recordings` = list above
   - `current-step: step-02`
   - Update this step's frontmatter: `status: completed`, `completed-at: <ISO timestamp>`

5. **Report** (brief, inline — not a separate message):
   ```
   [Knox/Discover]: X new recording(s) found for YYYY-MM-DD.
     Ready: N  |  Pending: N  |  Missing transcript: N
   ```

---

## SUCCESS METRICS

- Plaud API queried for target date range
- KMS cross-referenced — no duplicate processing
- Every new recording captured with transcription status
- `accumulated-context.new-recordings` written to state

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Plaud API unreachable (token expired) | Run Chrome login flow per `skills/plaud-transcripts/SKILL.md`. Retry once. If still fails, report "Plaud API unavailable" and abort workflow. |
| KMS unreadable | Proceed without dedup — note in report. Risk of duplicate notes is acceptable vs. missing new recordings. |
| No new recordings found | Set `new-recordings: []`, report "No new Plaud recordings", mark workflow complete. Do not proceed to step-02. |

---

## NEXT STEP

Read fully and follow: `step-02-trigger-transcription.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
