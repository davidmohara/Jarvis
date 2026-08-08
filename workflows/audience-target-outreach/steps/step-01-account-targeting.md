---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 01: Account Targeting

## MANDATORY EXECUTION RULES

1. Before executing, write `status: in-progress` and `started-at` to this
   file's frontmatter.
2. Confirm `accumulated-context.audience_profile` exists in `state.yaml`
   (either loaded from a prior `episode-campaign-brief` run or supplied
   directly by the controller at workflow start). If missing, ask the
   controller for it before proceeding.
3. You MUST run `skills/account-targeting/SKILL.md`'s mandatory compliance
   pre-check before any research call — do not skip it.
4. If the controller invoked this workflow with "do not execute" or
   `eval-mode: plan-only`, pass that through to this step (Plan-Only Mode is
   supported per `skills/account-targeting/SKILL.md`).

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** `accumulated-context.audience_profile`
**Output:** Target account list, stored in `accumulated-context`

---

## YOUR TASK

1. Read and execute `skills/account-targeting/SKILL.md` in full, passing the
   audience profile.

2. Capture the returned `target_accounts` list.

3. Write outputs to this file's frontmatter:
   ```yaml
   outputs:
     target_account_count: <int>
     accounts_with_existing_crm_relationship: <int>
   ```

4. Update `state.yaml`:
   - `accumulated-context.target_accounts`: the full account list
   - `current-step: step-02`

5. Mark this file's frontmatter `status: complete` and `completed-at`.

---

## SUCCESS METRICS

- Compliance pre-check ran and passed (or halted the workflow if flagged)
- Every account field carries a source
- Account list is right-sized to the audience profile's actual specificity, not padded

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Compliance pre-check flags ambiguous data ownership | Stop immediately. Set `state.yaml` `status: aborted`. Surface to controller for a decision before any further research. |
| CRM login wall | Surface to controller per the CBRE-session pattern, retry once confirmed. Do not proceed on fabricated data. |
| No qualifying accounts found | Report honestly. Ask the controller whether to broaden the audience profile or stop here. |

## NEXT STEP

Read fully and follow: `step-02-contact-targeting.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
