---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- personal:start -->
# Step 01: Verify Approval Claims Against Ghost and the Slack Record

## MANDATORY EXECUTION RULES

1. You MUST read the step-01 outputs, `pending-drafts.json`, the live Ghost post state, and the Slack replies directly. Do NOT accept the approval run's own narrative as evidence for its own claims.
2. You MUST return a verdict for every checklist item. No item may be omitted.
3. You MUST NOT publish, delete, edit, or re-run anything. You verify and report; the caller decides.
4. If a source is missing or unreadable, mark the dependent items unverified. Do not infer correctness from silence.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Approval manifest (step-01 outputs + run-date + Slack replies) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly this run's approval cycle: the publishes, rejects, edits, and regenerations it claims, and the `pending-drafts.json` transitions it wrote.
- Ralph does not publish or delete. He checks the claims that were made.

---

## YOUR TASK

### Sequence

1. **Locate the artifacts.** Read `workflows/content-approval/steps/step-01-approve.md` frontmatter `outputs`. Read `workflows/content-approval/pending-drafts.json` and `workflows/content-approval/state.yaml`. For every post the run claims to have published, fetch its live state via `mcp__ghost-blog__get_post`.

2. **Apply the approval-state-vs-Ghost lens.** For each item, re-derive the truth from Ghost and the Slack record, then compare to the run's claims:

   | # | Checklist item | Ground truth source | Verdict |
   |---|----------------|---------------------|---------|
   | 1 | Every "published" claim (`published` count) | Ghost `post.status == "published"` and a resolvable url | Unverified if Ghost still shows draft/scheduled |
   | 2 | Every publish has a matching David approval reply | #content thread reply from U0ANHV5UXEW with an approval keyword, before the publish | Unverified if a post was published with no approval reply |
   | 3 | Every publish has a `[PUBLISHED]` Slack confirmation | #content thread message for the post | Unverified if no confirmation was posted |
   | 4 | Every "rejected" claim | Ghost post deleted (404) or `status` transition matching the claim | Unverified if the draft still exists after a claimed reject |
   | 5 | Every edit/regeneration claim | Ghost `updated_at` advanced, or a new `ghost_post_id` present | Unverified if the post is unchanged |
   | 6 | Cleanup applied (published entries removed) | `pending-drafts.json` has no `status: "published"` rows | Unverified if published rows remain |
   | 7 | Right-run check | Status-change timestamps vs run-date | Unverified if claims are from a different run |

3. **Apply the "is Ghost actually showing that?" test** per item: Verified (claim matches Ghost/recorded state), Unverified (claim unsupported, or Ghost unreadable), Not applicable (item genuinely has no content this run, e.g. a clean no-op with no replies).

4. **Return the verdict table**, no preamble:

   ```
   | Item | Approval claim | Ghost / recorded state | Verdict |
   |------|----------------|------------------------|---------|
   | ...  | ...            | ...                    | Verified / Unverified / N/A |
   ```

   Then one summary line:
   - If all verified or not-applicable: `All approval claims match Ghost and the Slack record: verified.`
   - If any unverified: `Findings: [items].`

5. **Update state.yaml** with `status: complete`, `current-step: step-01`, and record the verdict summary in `accumulated-context.verdict-summary` (`all-verified` or `findings`) plus `accumulated-context.findings: [list]`.

---

## SUCCESS METRICS

- Every checklist item has a verdict
- Each verified publish cites the live Ghost post record it was traced to
- Any unverified item names the specific unsupported claim
- Verdict summary written to state.yaml

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Step-01 outputs empty | Mark publish/reject items Unverified with note "no outputs recorded." |
| Ghost API unreachable | Mark Ghost-dependent items Unverified with note "Ghost unreadable"; do not infer correctness. |
| Slack replies unavailable | Mark approval-trace items Unverified with note "Slack unreadable." |

---

## NEXT STEP

This is the final step. Return the verdict table to the caller. Workflow complete.
<!-- personal:end -->
