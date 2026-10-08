---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Verify Daily Review Output Against Source Data and State

## MANDATORY EXECUTION RULES

1. You MUST read the daily review output and the capture outputs directly. Do NOT accept the review's own narrative as evidence for its own claims.
2. You MUST return a verdict for every checklist item. No item may be omitted.
3. You MUST NOT fix, edit, or re-run anything. You verify and report; the caller decides.
4. If a source is missing or unreadable, mark the dependent items ⚠️ Unverified. Do not infer correctness from silence.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Review manifest (review file path + capture outputs) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly this run's daily review, its capture outputs, and the state it references.
- Ralph does not re-write the review. He checks the claims that were made.

---

## YOUR TASK

### Sequence

1. **Locate the artifacts.** Read the daily review file for the run date (`reviews/daily/{date}.md` or `reviews/daily/auto-{date}.md`). Read `workflows/daily-review/steps/step-01-capture.md` frontmatter `outputs`. Read `delegations/tracker.md` and `data/omnifocus-unified.json`.

2. **Apply the output-vs-source / completion-vs-state lens.** For each item, re-derive the truth from recorded state, then compare to the review:

   | # | Checklist item | Ground truth source | Verdict |
   |---|----------------|---------------------|---------|
   | 1 | "What got done today" claims | step-01-capture frontmatter `outputs.completed` | ⚠️ if the review claims a completion not present in capture data |
   | 2 | Carry-forward / "not done" claims | step-01-capture `outputs.not_completed` | ⚠️ if a carry-forward item has no capture source |
   | 3 | Delegation changes | `delegations/tracker.md` vs capture | ⚠️ if a delegation is marked complete/removed without a matching capture entry |
   | 4 | Task / inbox state claims | `data/omnifocus-unified.json` | ⚠️ if the review's task numbers disagree with the file |
   | 5 | Tomorrow's priorities | step-02 set-tomorrow outputs | ⚠️ if the review's forward plan is empty or unsupported |
   | 6 | Fabrication check | cross-reference against capture + source files | ⚠️ if the narrative asserts a specific outcome (a deal closed, a decision made) with no traceable source |
   | 7 | Right-day check | review file date vs run date | ⚠️ if the review file is from a different day |

3. **Apply the "are you really done?" test** per item: ✅ Verified (claim traced to recorded state), ⚠️ Unverified (claim unsupported, or state unreadable), ➖ Not applicable (item genuinely has no content this day).

4. **Return the verdict table**, no preamble:

   ```
   | Item | Review claim | Recorded state | Verdict |
   |------|--------------|----------------|---------|
   | ...  | ...          | ...            | ✅/⚠️/➖ |
   ```

   Then one summary line:
   - If all ✅ or ➖: `All review claims traced to recorded state: verified.`
   - If any ⚠️: `Re-run required: [items].`

5. **Update state.yaml** with `status: complete`, `current-step: step-01`, and record the verdict summary in `accumulated-context.verdict-summary` (`all-verified` or `findings`) plus `accumulated-context.findings: [list]`.

---

## SUCCESS METRICS

- Every checklist item has a verdict
- Each ✅ completion claim cites the recorded state it was traced to
- Any ⚠️ item names the specific unsupported claim
- Verdict summary written to state.yaml

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Review file not found | Surface: "No daily review output found: nothing to verify." Mark all items ⚠️. |
| Capture outputs empty | Mark completion/forward-plan items ⚠️ with note "no capture data." |
| A source file missing or unreadable | Mark dependent items ⚠️ Unverified with note "source unreadable." Do not infer correctness. |

---

## NEXT STEP

This is the final step. Return the verdict table to the caller. Workflow complete.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
