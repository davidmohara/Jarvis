---
status: not-started
started-at: ~
completed-at: ~
---

<!-- personal:start -->
# Step 01: Verify Tracker and Edit Claims Against Ghost and the Slack Record

## MANDATORY EXECUTION RULES

1. You MUST read the step-01 outputs, `pending-drafts.json`, the live Ghost post state, and the Slack replies directly. Do NOT accept the run's own narrative as evidence for its own claims.
2. You MUST return a verdict for every checklist item. No item may be omitted.
3. You MUST NOT publish, delete, edit, or re-run anything. You verify and report; the caller decides.
4. If a source is missing or unreadable, mark the dependent items unverified. Do not infer correctness from silence.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Run manifest (step-01 outputs + run-date + Slack replies) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly this run's resync/edit cycle: the resync status transitions, cleanup removals, and editorial edits it claims, and the `pending-drafts.json` state it wrote.
- Ralph does not publish or delete. He checks the claims that were made.

---

## YOUR TASK

### Sequence

1. **Locate the artifacts.** Read `workflows/content-approval/state.yaml` `accumulated-context` for the step outputs. Read `workflows/content-approval/pending-drafts.json`. For every entry remaining in the tracker, fetch its live state via `mcp__ghost-blog__get_post(id="{ghost_post_id}")`.

2. **Apply the tracker-state-vs-Ghost lens.** For each item, re-derive the truth from Ghost and the Slack record, then compare to the run's claims:

   | # | Checklist item | Ground truth source | Verdict |
   |---|----------------|---------------------|---------|
   | 1 | Every entry tracked as `pending` is actually a draft | Ghost `post.status == "draft"` for each `pending` entry | Unverified if Ghost shows published/scheduled for a `pending` entry |
   | 2 | Every entry tracked as `scheduled` is actually scheduled with a future date | Ghost `post.status == "scheduled"` and `published_at` in the future | Unverified if Ghost disagrees or the date has passed |
   | 3 | Cleanup applied | `pending-drafts.json` has no `status: "published"` rows, no past-`scheduled_at` rows, no `rejected`/`deleted_externally` rows older than 30 days | Unverified if stale rows remain |
   | 4 | Every claimed removal this run | The removed `ghost_post_id` is published/scheduled-past in Ghost, or 404 | Unverified if a removed entry is still a live draft in Ghost |
   | 5 | Every claimed editorial edit | Ghost `updated_at` advanced at/after the claimed `applied_at`, and the edit is visible in the post (link node present, new feature_image, etc.) | Unverified if the post is unchanged |
   | 6 | Right-run check | Status-change timestamps vs run-date | Unverified if claims are from a different run |

3. **Apply the "is Ghost actually showing that?" test** per item: Verified (claim matches Ghost/recorded state), Unverified (claim unsupported, or Ghost unreadable), Not applicable (item genuinely has no content this run, e.g. a clean no-op with no replies).

4. **Return the verdict table**, no preamble:

   ```
   | Item | Run claim | Ghost / recorded state | Verdict |
   |------|-----------|------------------------|---------|
   | ...  | ...       | ...                    | Verified / Unverified / N/A |
   ```

   Then one summary line:
   - If all verified or not-applicable: `All tracker and edit claims match Ghost and the Slack record: verified.`
   - If any unverified: `Findings: [items].`

5. **Update state.yaml** with `status: complete`, `current-step: step-01`, and record the verdict summary in `accumulated-context.verdict-summary` (`all-verified` or `findings`) plus `accumulated-context.findings: [list]`.

---

## SUCCESS METRICS

- Every checklist item has a verdict
- Each verified claim cites the live Ghost post record it was traced to
- Any unverified item names the specific unsupported claim
- Verdict summary written to state.yaml

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Step-01 outputs empty | Mark run-claim items Unverified with note "no outputs recorded." |
| Ghost API unreachable | Mark Ghost-dependent items Unverified with note "Ghost unreadable"; do not infer correctness. |
| Slack replies unavailable | Mark thread-trace items Unverified with note "Slack unreadable." |

---

## NEXT STEP

This is the final step. Return the verdict table to the caller. Workflow complete.
<!-- personal:end -->
