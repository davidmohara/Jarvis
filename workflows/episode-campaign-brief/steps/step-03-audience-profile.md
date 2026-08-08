---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 03: Audience Profile

## MANDATORY EXECUTION RULES

1. Before executing, write `status: in-progress` and `started-at` to this
   file's frontmatter.
2. Load `accumulated-context.pain_points` from `state.yaml` — do not
   re-extract.
3. Every part of the profile must trace back to a specific pain point ID.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** Pain points from `state.yaml`'s `accumulated-context`
**Output:** Audience profile (ICP), stored in `accumulated-context`

---

## YOUR TASK

1. Read and execute `skills/audience-profile-builder/SKILL.md` in full,
   passing the pain points list.

2. Capture the returned `audience_profile` object.

3. Write outputs to this file's frontmatter:
   ```yaml
   outputs:
     industries: [...]
     company_size_band: "..."
     buyer_roles: [...]
   ```

4. Update `state.yaml`:
   - `accumulated-context.audience_profile`: the full profile object
   - `current-step: step-04`

5. Mark this file's frontmatter `status: complete` and `completed-at`.

---

## SUCCESS METRICS

- Every pain point is reflected in the profile, or explicitly noted as
  non-targetable
- Company size band and buyer roles are reasoned, not defaulted

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Pain points too generic to derive a specific ICP | Report honestly. Offer the controller the choice: proceed with a broad profile, or stop here with just the pain points captured. |

## NEXT STEP

Read fully and follow: `step-04-offering-match.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
