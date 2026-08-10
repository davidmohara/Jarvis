---
status: completed
started-at: "2026-08-10T00:00:00Z"
completed-at: "2026-08-10T00:15:00Z"
model: haiku
outputs:
  new-recordings-count: 88
  api-total: 111
  confirmed-in-vault: 23
  completion-reason: "Full enumeration via Plaud API; 88 new recordings identified after deduplication against vault"
---

<!-- system:start -->
# Step 01: Discover New Recordings

## MANDATORY EXECUTION RULES

1. You MUST query the Plaud API for ALL recordings (full enumeration) — do not filter by date by default.
2. You MUST cross-reference against the Obsidian vault to avoid reprocessing already-ingested recordings.
3. You MUST capture recording ID, name, date, duration, and transcription status for every new recording.
4. Do NOT begin downloading or processing transcripts in this step — discovery only.
5. Do NOT proceed to step-02 until the new-recordings list is populated in state.
6. Do NOT use `target-date` as a filter unless it was explicitly passed for a reprocess of a specific date.

---

## EXECUTION PROTOCOL

**Agent:** Knox
**Skill:** `skills/plaud-discover/SKILL.md` — read it in full before executing this step.
**Input:** None required by default (full enumeration mode). Optional: `target-date` in `state.yaml accumulated-context` if reprocessing a specific date.
**Output:** `accumulated-context.new-recordings` — list of recording objects not yet in vault

---

## YOUR TASK

### Sequence

1. **Check for explicit target-date override.** If `state.yaml accumulated-context.target-date` is set, this is a targeted reprocess — filter to that date only. Otherwise, run in full enumeration (catch-up) mode: fetch all recordings from the API, dedup against vault.

2. **Run the discovery** per `skills/plaud-discover/SKILL.md`.
   - Enumerate ALL recordings from the Plaud API (paginate through all results).
   - Enumerate notes already in the vault under `zzPlaud/` (all subfolders).
   - Also check `state.yaml accumulated-context.stale-staged-files` — these are orphaned staging files that must be re-queued, not skipped.
   - Diff: recordings present in API but not in vault = new recordings.

3. **Build the new-recordings list.** For each new recording capture:
   ```yaml
   - file_id: abc123
     name: "Meeting with Todd Wynne"
     date: 2026-04-15
     duration_seconds: 3421
     has_transcript: true | false
     transcript_status: ready | pending | missing
   ```

4. **Update state.yaml:**
   - `accumulated-context.new-recordings` = list above
   - `current-step: step-02`
   - Update this step's frontmatter: `status: completed`, `completed-at: <ISO timestamp>`

5. **Report** (brief, inline — not a separate message):
   ```
   [Knox/Discover]: X new recording(s) found (full enumeration — all dates).
     Ready: N  |  Pending: N  |  Missing transcript: N
   ```
   If target-date override was active: `X new recording(s) found for YYYY-MM-DD.`

---

## SUCCESS METRICS

- Plaud API queried for all recordings (full enumeration unless target-date override is set)
- Vault cross-referenced — no duplicate processing
- Stale staged files treated as new (not skipped)
- Every new recording captured with transcription status
- `accumulated-context.new-recordings` written to state

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Plaud API unreachable (token expired) | Run Chrome login flow per `skills/plaud-transcripts/SKILL.md`. Retry once. If still fails, report "Plaud API unavailable" and abort workflow. |
| Vault unreadable | Proceed without dedup — note in report. Risk of duplicate notes is acceptable vs. missing new recordings. |
| No new recordings found | Set `new-recordings: []`, report "No new Plaud recordings", mark workflow complete. Do not proceed to step-02. |

---


## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py plaud-ingest step-01-discover complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

Read fully and follow: `step-02-trigger-transcription.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
