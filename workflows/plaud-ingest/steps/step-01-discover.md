---
status: completed
model: kimi-k3
started-at: "2026-10-27T14:57:30Z"
completed-at: "2026-10-27T15:02:00Z"
outputs:
  previous-run-results:
    new-recordings: 4
    confirmed-in-vault: 150
    api-total: 154
---

<!-- system:start -->
# Step 01: Discover New Recordings

## PRE-EXECUTION: AUTH HANDLING

**Run `skills/plaud-discover/SKILL.md` FIRST. Do not pre-check for token files.**

Do not inspect `~/.config/plaud/token.json` or any credentials file before executing this step. Do not abort because no cached token exists. The skill and `fetch_plaud.py` handle token acquisition via Chrome login flow when needed. Knox's job is to run the skill — not to gate on token presence.

Auth failure is only a valid abort reason if the skill's own Chrome login flow has been attempted and failed. A missing token file before the skill runs is not a blocker.

---

## MANDATORY EXECUTION RULES

1. You MUST query the Plaud API for ALL recordings (full enumeration) — do not filter by date by default.
2. You MUST cross-reference against the Obsidian vault to avoid reprocessing already-ingested recordings.
3. You MUST capture recording ID, name, date, duration, and transcription status for every new recording.
4. Do NOT begin downloading or processing transcripts in this step — discovery only.
5. Do NOT proceed to step-02 until the new-recordings list is populated in state.
6. Do NOT use `target-date` as a filter unless it was explicitly passed for a reprocess of a specific date.
7. You MUST NOT accept `plaud-discover`'s output as-is — whether it ran inline or as a
   background/forked subagent — without confirming the skill's dedup ledger
   (`systems/eval-harness/skill-runs/plaud-discover-ledger-latest.json`) exists and every
   `new_recordings` entry traces to a ledger entry with a checked tier. This is the same
   HARD GATE defined in `skills/plaud-discover/SKILL.md`; it is restated here because this
   step has accepted an unverified fork result before (see `err-20260826T190948-QQMBTP`).
   If the ledger is missing, or the new-recordings count is more than double the last
   confirmed baseline below AND more than 10% of total candidates, do not write it to state
   — re-run discovery once with explicit re-enumeration, and if the anomaly persists, mark
   this step blocked and report the discrepancy rather than advancing.

---

## EXECUTION PROTOCOL

**Agent:** Knox, spawned by the coordinator, never executed inline in the coordinator's session.
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
   - Update this step's frontmatter: `status: completed`, and `completed-at` set to the real UTC clock time from `date -u +%Y-%m-%dT%H:%M:%SZ` (never estimate or round).
   - **Refresh the no-op preflight marker** at `data/.plaud-last-seen.json` after
     every successful full enumeration (both the new-recordings path and the
     no-op exit below):
     ```json
     {
       "newest_file_id": "<file_id of the newest recording returned by the API>",
       "newest_create_time": "<its create/start time>",
       "api_total": <total recordings enumerated>,
       "checked_at": "<ISO timestamp>",
       "outcome": "new-recordings | no-new-recordings"
     }
     ```
     This marker is what lets `verify/noop-preflight.py` answer "anything new?"
     in one API call. Without it every run pays the full discovery cost.

5. **Report** (brief, inline — not a separate message):
   ```
   [Knox/Discover]: X new recording(s) found (full enumeration — all dates).
     Ready: N  |  Pending: N  |  Missing transcript: N
   ```
   If target-date override was active: `X new recording(s) found for YYYY-MM-DD.`

---

## QUALITY GATE 1 — Token/Auth Confirmation (HARD, BLOCKING, POST-HOC — NOT A PRE-CHECK)

**Read this carefully before touching it.** This gate does NOT reintroduce the token
pre-check that the PRE-EXECUTION: AUTH HANDLING section above forbids. It runs strictly
*after* `skills/plaud-discover/SKILL.md` has already executed and attempted its own
Chrome-login/token-acquisition flow. Checking for a token file *before* the skill runs is
the bug this gate must never become (see `err-20260730T143152-S0TRMO`).
A future editor tightening this gate into a pre-flight check would resurrect that exact bug.

**What this gate actually checks:** whether the discovery run that just happened came back
with a real, usable auth session, or whether the skill's own login flow ran and failed.

| Signal | Interpretation |
|--------|----------------|
| Skill returned an enumerated recording list (any length, including empty) from a live API call | Auth succeeded. **PASS.** Record `gate_1_auth_method` as `cached-token` or `fresh-chrome-login` (whichever the skill reported using). |
| Skill explicitly reported a Chrome login attempt that failed (bad credentials, MFA block, session timeout mid-flow) | Auth confirmed unavailable. **HARD FAIL.** |
| Skill returned an auth-failure/401/token-invalid signal from the Plaud API itself after attempting acquisition | Auth confirmed unavailable. **HARD FAIL.** |

**On HARD FAIL:** Do not proceed to step-02. Do not silently continue with an empty or
partial recording list as if nothing were found — that would look identical to "no new
recordings" and hide a real outage. Set `state.yaml status: blocked`, write a `blocker` field
describing the auth failure, and report to the controller:
```
[Knox/Discover]: Plaud auth failed — the Chrome login flow ran and did not produce a usable
token. Workflow halted before step-02. This is a genuine auth failure, not a missing-token
pre-check (see step-01 Gate 1 for why that distinction matters).
```

Log the outcome regardless of pass/fail:
```
[Gate 1] Auth method: cached-token | fresh-chrome-login
[Gate 1] PASS — proceeding to metadata validation.
```
or
```
[Gate 1] FAIL — Chrome login flow attempted and failed. Halting before step-02.
```

## QUALITY GATE 2 — Recording Metadata Validation (SOFT, LOGGED, PER-RECORDING)

Run the Gate 2 protocol in `references/gate-2-metadata-validation.md` (read it before handing recordings to step-02): per-recording schema validation via `skills/schema-validator/SKILL.md`, the severity-split interpretation table, the `file_id` hard-exclusion rule, and the `gate_2_result` state.yaml writes. This gate does not halt the workflow.

---

## SUCCESS METRICS

- Gate 1 confirms a real auth outcome (pass or genuine hard fail) before any recording data is trusted
- Every new recording passes or is explicitly flagged/excluded by Gate 2 before reaching step-02
- Plaud API queried for all recordings (full enumeration unless target-date override is set)
- Vault cross-referenced — no duplicate processing
- Stale staged files treated as new (not skipped)
- Every new recording captured with transcription status
- `accumulated-context.new-recordings` written to state

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Plaud API unreachable (token expired or missing) | Run the skill. The skill runs `fetch_plaud.py` which handles Chrome login flow and token acquisition. A missing token file is NOT a pre-execution blocker — it is handled here. Only abort if the Chrome login flow itself fails after attempting. |
| Gate 1 hard fail (Chrome login attempted and failed) | Set `state.yaml status: blocked`. Do not proceed to step-02. Report the auth failure to the controller per Gate 1 above. |
| Vault unreadable | Proceed without dedup — note in report. Risk of duplicate notes is acceptable vs. missing new recordings. |
| No new recordings found | Set `accumulated-context.new-recordings: []`, write the top-level `outcome: no-new-recordings` (the documented no-op disposition — see below), report "No new Plaud recordings", set `state.yaml status: complete`, mark workflow complete. Do not proceed to step-02. |
| Gate 2 excludes a recording for missing `file_id` | Log it, continue with the remaining valid recordings. Do not halt the step for one bad entry. |

---

## NO-OP EXIT (no new recordings)

When discovery finds zero new recordings, this run is a **deliberate no-op**, not a
failure and not a phantom. Terminate the workflow honestly and leave the audit trail
intact:

1. Set `accumulated-context.new-recordings: []`.
2. Write the top-level `outcome: no-new-recordings` on `state.yaml`. This is the
   machine-readable no-op disposition the eval harness keys on: with it present, the
   run's eval record is kept in `runs/` and marked `status: no-op` / `no_op: true`
   (excluded from success-rate metrics) instead of being quarantined as a phantom.
   Omitting it makes a legitimate no-op indistinguishable from a workflow that never ran.
3. Set `state.yaml status: complete`, `current-step: step-01`, and stamp `completed-at` from `date -u`.
4. **Refresh `data/.plaud-last-seen.json`** with the newest API recording's `file_id`, its create/start time, `api_total`, `checked_at`, and `outcome: "no-new-recordings"` (schema in YOUR TASK step 4 above). This is what makes the next run's preflight a single cheap call.
5. Report: `[Knox/Discover]: No new Plaud recordings — no-op run (outcome: no-new-recordings).`
6. Do **not** proceed to step-02. Do **not** delete or leave the run unrecorded.

---


## NEXT STEP

Read fully and follow: `step-02-trigger-transcription.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
