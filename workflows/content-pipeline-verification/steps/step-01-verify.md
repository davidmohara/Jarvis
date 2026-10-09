---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- personal:start -->
# Step 01: Account for Every Item End to End

## MANDATORY EXECUTION RULES

1. You MUST read the step outputs, `pending-drafts.json`, the Slack source, and the live Ghost post state directly. Do NOT accept the pipeline run's own narrative as evidence for its own claims.
2. You MUST return a verdict for every checklist item. No item may be omitted.
3. You MUST NOT publish, delete, edit, or re-run anything. You verify and report; the caller decides.
4. If a source is missing or unreadable, mark the dependent items unverified. Do not infer correctness from silence.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Pipeline manifest (step outputs + run-date + Slack source) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly this run's pipeline accounting: discovered, approved, and published items.
- Ralph does not re-run the pipeline. He checks whether each item is accounted for.

---

## YOUR TASK

### Sequence

1. **Locate the artifacts.** Read `workflows/content-pipeline/steps/step-01-discover.md` and `steps/step-02-approve.md` frontmatter `outputs`. Read `workflows/content-pipeline/pending-drafts.json` and `workflows/content-pipeline/state.yaml`. Read the #content Slack pull for the run window.

2. **Apply the end-to-end accounting lens.** Build the full item list from each stage, then reconcile:

   | # | Checklist item | Ground truth source | Verdict |
   |---|----------------|---------------------|---------|
   | 1 | Every discovered item is in `pending-drafts.json` | Slack pull items vs entries | Unverified if a discovered item has no entry |
   | 2 | Every `pending-drafts.json` entry has a Ghost post | `mcp__ghost-blog__get_post` per `ghost_post_id` | Unverified if an entry points at a non-existent post |
   | 3 | Every approved item is published or explained | Ghost status + `pending-drafts.json` `status`/notes | Unverified if approved but neither published nor explained |
   | 4 | Every terminal status is legitimate | `published`/`rejected`/`stalled` vs the recorded reason | Unverified if a status has no supporting evidence |
   | 5 | Stage counts reconcile | discovered >= approved >= published, no gaps without a reason | Unverified if a stage count exceeds its predecessor |
   | 6 | No entry silently dropped | Every entry has a terminal or pending status | Unverified if an entry is neither pending nor terminal |
   | 7 | Right-run check | Entry timestamps vs run-date | Unverified if entries are from a different run |

3. **Apply the "is it accounted for?" test** per item: Verified (item traced through every stage), Unverified (item unsupported or source unreadable), Not applicable (stage genuinely has no items this run).

4. **Return the verdict table**, no preamble:

   ```
   | Item | Pipeline claim | Recorded evidence | Verdict |
   |------|----------------|-------------------|---------|
   | ...  | ...            | ...               | Verified / Unverified / N/A |
   ```

   Then one summary line:
   - If all verified or not-applicable: `All items accounted for end to end: verified.`
   - If any unverified: `Findings: [items].`

5. **Update state.yaml** with `status: complete`, `current-step: step-01`, and record the verdict summary in `accumulated-context.verdict-summary` (`all-accounted` or `findings`) plus `accumulated-context.findings: [list]`.

---

## SUCCESS METRICS

- Every checklist item has a verdict
- Each verified item cites the recorded stage evidence it was traced through
- Any unverified item names the specific silent drop or unsupported claim
- Verdict summary written to state.yaml

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Step outputs empty | Mark stage items Unverified with note "no outputs recorded." |
| `pending-drafts.json` missing | Mark entry items Unverified with note "state file unreadable." |
| Ghost API unreachable | Mark Ghost-dependent items Unverified with note "Ghost unreadable"; do not infer correctness. |

---

## NEXT STEP

This is the final step. Return the verdict table to the caller. Workflow complete.
<!-- personal:end -->
