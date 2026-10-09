---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- personal:start -->
# Step 01: Verify Discovery Claims Against the Slack/Digest Source

## MANDATORY EXECUTION RULES

1. You MUST read the step-01 outputs, `pending-drafts.json`, and the Slack source directly. Do NOT accept the discovery run's own narrative as evidence for its own claims.
2. You MUST return a verdict for every checklist item. No item may be omitted.
3. You MUST NOT fix, edit, re-draft, or re-run anything. You verify and report; the caller decides.
4. If a source is missing or unreadable, mark the dependent items unverified. Do not infer correctness from silence.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Discovery manifest (step-01 outputs + run-date + Slack source) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly this run's discovery: the drafts it created, the skips it claimed, and the entries it appended to `pending-drafts.json`.
- Ralph does not re-draft. He checks the claims that were made.

---

## YOUR TASK

### Sequence

1. **Locate the artifacts.** Read `workflows/content-discovery/steps/step-01-discover.md` frontmatter `outputs`. Read `workflows/content-approval/pending-drafts.json` and `workflows/content-discovery/state.yaml`. Read the #content Slack pull for the run window (passed in the manifest, or re-read via `systems/slack-bot/read.py`).

2. **Apply the draft-claims-vs-source lens.** For each item, re-derive the truth from the recorded source, then compare to the run's claims:

   | # | Checklist item | Ground truth source | Verdict |
   |---|----------------|---------------------|---------|
   | 1 | Every draft claimed (`posts_drafted` count) | `pending-drafts.json` entries with `created_at` in the run window | Unverified if a claimed draft has no matching entry |
   | 2 | Every draft traced to a real source | Slack pull message (`ts`) or digest text for each entry | Unverified if a draft has no source message (invented angle) |
   | 3 | Every skip claimed has a matching source message | Slack pull: the skipped URL/digest must exist in the pull | Unverified if a skip names a source not present in the pull |
   | 4 | `new_urls` / `new_digests` counts | Slack pull routing classification vs `outputs` | Unverified if counts disagree with the pull |
   | 5 | `gate_1_result` / `gate_2_result` | The recorded Gate 1 response and Gate 2 validation outcome | Unverified if a gate is claimed PASS with no supporting response recorded |
   | 6 | Every `pending-drafts.json` entry has a Slack notification | `slack_thread_ts` set, or a documented fallback | Unverified if an entry is pending with no notification path |
   | 7 | Right-run check | Entry `created_at` dates vs run-date | Unverified if entries are from a different run |

3. **Apply the "is it really there?" test** per item: Verified (claim traced to the recorded source), Unverified (claim unsupported, or source unreadable), Not applicable (item genuinely has no content this run, e.g. a clean no-op run with zero drafts).

4. **Return the verdict table**, no preamble:

   ```
   | Item | Discovery claim | Recorded evidence | Verdict |
   |------|-----------------|-------------------|---------|
   | ...  | ...             | ...               | Verified / Unverified / N/A |
   ```

   Then one summary line:
   - If all verified or not-applicable: `All discovery claims traced to the source: verified.`
   - If any unverified: `Findings: [items].`

5. **Update state.yaml** with `status: complete`, `current-step: step-01`, and record the verdict summary in `accumulated-context.verdict-summary` (`all-verified` or `findings`) plus `accumulated-context.findings: [list]`.

---

## SUCCESS METRICS

- Every checklist item has a verdict
- Each verified draft cites the recorded source it was traced to
- Any unverified item names the specific unsupported claim
- Verdict summary written to state.yaml

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Step-01 outputs empty | Mark draft/skip items Unverified with note "no outputs recorded." |
| Slack pull not available | Mark source-trace items Unverified with note "source unreadable"; do not infer correctness. |
| `pending-drafts.json` missing | Mark draft items Unverified with note "state file unreadable." |

---

## NEXT STEP

This is the final step. Return the verdict table to the caller. Workflow complete.
<!-- personal:end -->
