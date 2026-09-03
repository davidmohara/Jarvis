---
status: completed
model: haiku
started-at: "2026-08-23T00:05:00Z"
completed-at: "2026-08-23T00:12:00Z"
outputs:
  new-recordings-count: 1
  api-total: 120
  confirmed-in-vault: 119
  gate_1_result: "pass"
  gate_1_auth_method: "cached-token"
  gate_2_result: "pass"
  gate_2_flagged_recordings: []
  previous-run-results:
    - date: "2026-08-22"
      new-recordings-count: 1
      api-total: 120
      confirmed-in-vault: 119
      note: "That recording (8b45065b02f3a852edadfb43c319a9ea) is now confirmed in vault as of this run — it dropped out of today's diff."
    - date: "2026-08-10"
      new-recordings-count: 88
      api-total: 111
      confirmed-in-vault: 23
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
   is the step that has actually accepted an unverified fork result before
   (`err-20260826T190948-QQMBTP`, `err-20260828T140747-814VN9`, `err-20260831T145746-29X2M7`).
   If the ledger is missing, or the new-recordings count is more than double the last
   confirmed baseline below AND more than 10% of total candidates, do not write it to state
   — re-run discovery once with explicit re-enumeration, and if the anomaly persists, mark
   this step blocked and report the discrepancy rather than advancing.

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

## QUALITY GATE 1 — Token/Auth Confirmation (HARD, BLOCKING, POST-HOC — NOT A PRE-CHECK)

**Read this carefully before touching it.** This gate does NOT reintroduce the token
pre-check that the PRE-EXECUTION: AUTH HANDLING section above forbids. It runs strictly
*after* `skills/plaud-discover/SKILL.md` has already executed and attempted its own
Chrome-login/token-acquisition flow. Checking for a token file *before* the skill runs — the
thing this gate must never become — was the direct cause of three prior incidents
(`err-20260730T143152-S0TRMO`, `err-20260803T143125-2W5XDO`, `err-20260812T142902-E6Z7KS`).
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

This step's own MANDATORY EXECUTION RULE #3 already requires capturing `file_id`, `name`,
`date`, `duration_seconds`, `has_transcript`, and `transcript_status` for every new recording
(see the schema in step 3 of YOUR TASK above) — this gate is the explicit checkpoint that
those fields are actually present and well-formed before they get handed to step-02 and
step-03, which both key their logic off `transcript_status` and `date`/time.

Call `skills/schema-validator/SKILL.md` once per entry in `new-recordings`:

```yaml
data: { file_id, transcript_status, date, duration_seconds, name }   # the recording's own fields
schema_spec:
  required_fields:
    - "file_id"    # severity defaults to "error" — this is the one HARD exclusion in this soft gate
  format_rules:
    transcript_status: { enum: ["ready", "pending", "missing"], severity: "warning", default_if_missing: "missing" }
    date: { type: "date", severity: "warning" }
    duration_seconds: { type: "positive_number", severity: "warning" }
    name: { type: "non_empty_string", severity: "warning" }
```

Interpret the skill's `{valid, errors, warnings}` result yourself — this gate's severity split
predates and drives the schema_spec above, the skill doesn't decide it for you:

| Skill result | Action |
|-------|----------------------|
| `errors` contains a `file_id` entry (`required_fields` failure) | **Exclude this recording** from `new-recordings` entirely and log it — step-02/03/04/05 all key off `file_id`; a recording without one cannot be tracked through the pipeline. This is the one per-recording HARD exclusion inside an otherwise soft gate. |
| `warnings` contains a `transcript_status` entry | If absent or unrecognized, apply the skill's reported `default_if_missing` value (`"missing"` — safest assumption, triggers step-02 to attempt transcription rather than silently skipping) and flag it. |
| `warnings` contains a `date` entry | Flag it — step-03's calendar cross-reference cannot run without it, so that recording will very likely fall through to controller escalation in step-03. Do not block on it here; let step-03 handle the downstream consequence. |
| `warnings` contains a `duration_seconds` entry | Flag it — cosmetic for this step (used in reporting), not blocking. |
| `warnings` contains a `name` entry | Flag it and fall back to `file_id` as the display name. |

This gate does **not** halt the workflow — the pipeline already tolerates partial metadata
gracefully further downstream (step-03 has its own escalation path for recordings it can't
date-match, step-05 falls back to `file_id` as a display label). Missing `file_id` is the one
exception because it breaks tracking entirely, not just one feature.

Log the result:
```
[Gate 2] N recordings validated. M flagged (see gate_2_flagged_recordings). K excluded (missing file_id).
```

Write `gate_2_result: "pass"` (nothing flagged) or `"pass-with-flags"` (flagged but none
excluded) or `"pass-with-exclusions"` (one or more excluded for missing `file_id`) to this
step's frontmatter `outputs`, along with `gate_2_flagged_recordings: [{file_id, issue}, ...]`.

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
| No new recordings found | Set `new-recordings: []`, report "No new Plaud recordings", mark workflow complete. Do not proceed to step-02. |
| Gate 2 excludes a recording for missing `file_id` | Log it, continue with the remaining valid recordings. Do not halt the step for one bad entry. |

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
