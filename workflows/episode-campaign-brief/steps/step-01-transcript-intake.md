---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 01: Transcript Intake

## MANDATORY EXECUTION RULES

1. Before executing, write `status: in-progress` and `started-at` to this
   file's frontmatter.
2. You MUST determine whether the episode reference is a public URL or an
   internal Improving Edge episode before calling any tool.
3. Do NOT summarize or truncate the transcript — downstream pain-point
   extraction needs the full text.
4. Do NOT proceed to step 02 until a usable transcript is in hand.

---

## EXECUTION PROTOCOL

**Agent:** Harper
**Input:** Controller's episode reference (URL or internal pointer)
**Output:** Transcript + episode metadata, stored in `state.yaml`'s
`accumulated-context`

---

## YOUR TASK

1. Read and execute `skills/episode-transcript-intake/SKILL.md` in full,
   passing the controller's episode reference as input.

2. Capture the returned object:
   ```yaml
   episode: {title, episode_number, guest, date, source, source_url, obsidian_note_path}
   transcript: "full transcript text"
   ```

3. Write outputs to this file's frontmatter:
   ```yaml
   outputs:
     episode_metadata: {...}
     transcript_length_chars: <int>
     transcript_quality_note: "clean" | "auto-generated, may have errors" | ...
   ```
   (Store the actual transcript text in `accumulated-context` in `state.yaml`,
   not duplicated into this frontmatter — keep the step file itself light.)

4. Update `state.yaml`:
   - `accumulated-context.episode_metadata`: the episode object
   - `accumulated-context.transcript`: the full transcript text
   - `current-step: step-02`

5. Mark this file's frontmatter `status: complete` and `completed-at`.

---

## SUCCESS METRICS

- Transcript retrieved in full, not truncated
- Episode metadata captured (title at minimum; other fields as available)
- Source type (public/internal) correctly identified

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Episode reference ambiguous | Ask the controller: "Is this a public episode URL, or an Improving Edge episode already recorded internally?" |
| Intake skill reports a hard failure (unreachable URL, episode not found) | Do not proceed to step 02. Report the failure to the controller and set `state.yaml` `status: aborted`. |

## NEXT STEP

Read fully and follow: `step-02-pain-point-extraction.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
