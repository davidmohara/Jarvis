---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 02: Pain Point Extraction

## MANDATORY EXECUTION RULES

1. Before executing, write `status: in-progress` and `started-at` to this
   file's frontmatter.
2. Load `accumulated-context.transcript` from `state.yaml` — do not re-fetch
   the transcript.
3. Every pain point must carry a supporting quote. Do not invent pain points
   not present in the transcript.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** Transcript from `state.yaml`'s `accumulated-context`
**Output:** Structured pain point list, stored in `accumulated-context`

---

## YOUR TASK

1. Read and execute `skills/pain-point-extraction/SKILL.md` in full, passing
   the transcript from `accumulated-context`.

2. Capture the returned `pain_points` list.

3. Write outputs to this file's frontmatter:
   ```yaml
   outputs:
     pain_point_count: <int>
     pain_point_ids: [pp-01, pp-02, ...]
   ```

4. Update `state.yaml`:
   - `accumulated-context.pain_points`: the full pain point list
   - `current-step: step-03`

5. Mark this file's frontmatter `status: complete` and `completed-at`.

---

## SUCCESS METRICS

- Every pain point has a verbatim supporting quote
- No fabricated or force-fit pain points

## FAILURE MODES

| Failure | Action |
|---------|--------|
| No distinct pain points found | Report this honestly to the controller: this episode doesn't surface targetable pain points. Set `state.yaml` `status: aborted` unless the controller wants to proceed anyway with a thin brief. |

## NEXT STEP

Read fully and follow: `step-03-audience-profile.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
