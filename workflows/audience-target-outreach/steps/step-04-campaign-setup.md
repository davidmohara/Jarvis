---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 04: Campaign Setup

## MANDATORY EXECUTION RULES

1. Before executing, write `status: in-progress` and `started-at` to this
   file's frontmatter.
2. Load `accumulated-context.episode_metadata` and
   `accumulated-context.target_contacts` from `state.yaml`.
3. This is a CRM write step. If the controller invoked the workflow with
   "do not execute" or `eval-mode: plan-only`, this step MUST run in
   Plan-Only Mode per `skills/campaign-setup/SKILL.md` — produce the plan and
   stop, do not create anything live.
4. Run the build-time config sanity check (sending domain/email channel,
   Consent center state) before any write, even if a prior run already
   checked it earlier the same day — config can drift.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** Episode metadata, target contact list
**Output:** Segment/Journey identifiers, stored in `accumulated-context`

---

## YOUR TASK

1. Read and execute `skills/campaign-setup/SKILL.md` in full, passing episode
   metadata and the target contact list.

2. Capture the returned Segment and Journey identifiers (created or reused).

3. Write outputs to this file's frontmatter:
   ```yaml
   outputs:
     segment_name: "..."
     journey_name: "..."
     segment_journey_status: "created" | "reused-existing"
     send_readiness_confirmed: true/false
   ```

4. Update `state.yaml`:
   - `accumulated-context.segment_name`: "..."
   - `accumulated-context.journey_name`: "..."
   - `accumulated-context.contacts_sent`: [] (initialize empty list — tracks
     per-contact send completion for step 05)
   - `current-step: step-05`

5. Mark this file's frontmatter `status: complete` and `completed-at`.

---

## SUCCESS METRICS

- Dedup check ran against existing Journeys (including the 5 known dormant ones)
  before any creation
- Send-readiness (sending domain, Consent center) explicitly confirmed or
  explicitly flagged as not ready
- Every target contact resolved to a CRM Contact record and added to the Segment

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Send-readiness check fails (domain not verified / consent center not ready) | Stop before any write. Report the specific gap to the controller. Set `state.yaml` `status: aborted` until resolved. |
| Name collision with an existing Journey | Do not overwrite. Ask the controller how to disambiguate. |
| CRM login wall | Surface to controller, retry once confirmed. |

## NEXT STEP

Read fully and follow: `step-05-campaign-send.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
