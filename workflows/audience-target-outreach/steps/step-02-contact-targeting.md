---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 02: Contact Targeting

## MANDATORY EXECUTION RULES

1. Before executing, write `status: in-progress` and `started-at` to this
   file's frontmatter.
2. Load `accumulated-context.target_accounts` and
   `accumulated-context.audience_profile` from `state.yaml`.
3. Apply the standing rule from `memory/feedback_linkedin_over_crm_titles.md`:
   LinkedIn wins on any CRM/LinkedIn title conflict.
4. Pass through Plan-Only Mode if the controller invoked the workflow that way.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** `accumulated-context.target_accounts`, `accumulated-context.audience_profile`
**Output:** Target contact list, stored in `accumulated-context`

---

## YOUR TASK

1. Read and execute `skills/contact-targeting/SKILL.md` in full, passing the
   target accounts and audience profile's buyer roles.

2. Capture the returned `target_contacts` list.

3. Write outputs to this file's frontmatter:
   ```yaml
   outputs:
     target_contact_count: <int>
     accounts_with_no_qualified_contact: [...]
   ```

4. Update `state.yaml`:
   - `accumulated-context.target_contacts`: the full contact list
   - `current-step: step-03`

5. Mark this file's frontmatter `status: complete` and `completed-at`.

---

## SUCCESS METRICS

- Every contact has a specific, non-generic "why this pain point applies" rationale
- Title source is documented for every contact
- Accounts with no qualified contact are dropped and noted, not padded with a weak fit

## FAILURE MODES

| Failure | Action |
|---------|--------|
| No qualified contact found at any target account | Stop and report to the controller — this likely means the audience profile's buyer role needs adjustment. |
| CRM/LinkedIn/Clay all unreachable | Surface to controller. Do not fabricate contacts. |

## NEXT STEP

Read fully and follow: `step-03-prospect-message-draft.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
