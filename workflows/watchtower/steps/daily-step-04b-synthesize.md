---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. Read `identity/VOICE.md` before generating any prose — both outputs must match David's register.
3. Do NOT fabricate a pattern if the item count is 0 or 1 — apply the edge-case rules below exactly.
4. Do NOT write to Obsidian, the dashboard, or any vault path — that is step-05's job.
5. Write both fields to `state.yaml` accumulated-context before marking complete.
6. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | sonnet |
| Input | `accumulated-context.summarized_items` (from step-04), `config.yaml profile` and `profile.lenses`, `identity/VOICE.md` |
| Output | `accumulated-context.through_line` and `accumulated-context.consulting_read` written to `state.yaml` |

---

## CONTEXT BOUNDARIES

- Scope: synthesis only. Read summarized items; produce two prose fields. No gathering, no scoring, no vault writes.
- Voice: match David's direct, first-person professional register from `identity/VOICE.md`. Plain prose. No bullet points.
- Source material: `accumulated-context.summarized_items`. Do not re-read raw feeds.
- Lenses: read `config.yaml` `profile.lenses` to understand which topic areas David tracks. Use these to anchor the consulting_read.

---

## YOUR TASK

1. Read `identity/VOICE.md` for tone calibration.

2. Read `config.yaml` and extract `profile.lenses` (the consulting/strategic frames David applies).

3. **Assess item count** from `accumulated-context.summarized_items`:

   **If 0 items:**
   - `through_line`: `"No new signals today."`
   - `consulting_read`: null
   - Skip to step 6.

   **If exactly 1 item:**
   - `through_line`: `"Quiet day — one signal: [one-clause distillation of the single item]."`
   - `consulting_read`: null
   - Skip to step 6.

4. **If 2 or more items — generate `through_line`:**

   Read all summaries. Identify the single most coherent pattern across them — the thread that connects the most significant signals. This is NOT a summary of every item; it is the synthesizing insight that names what the day's signals add up to.

   Write 1-2 sentences. Plain prose. David's voice. Do not name every topic — name the pattern.

   Do NOT fabricate a pattern. If the items are genuinely unrelated across all topics, write: `"No single thread today — signals scattered across [topic A] and [topic B]."` Honest is better than invented coherence.

5. **If 2 or more items — generate `consulting_read`:**

   Frame the day's pattern through David's IT-consulting and Improving lens. This is the editorial callout: what does today's intelligence mean for how David's clients should be thinking, what posture Improving should be taking, or what the market shift implies for relationship-led delivery?

   Write 2-3 sentences. David's voice. Concrete, not generic. Ground it in the actual signals — do not write boilerplate consulting observations unconnected to what surfaced today.

   This is editorial voice, not news summary. It should express a point of view.

6. Write both fields to `state.yaml` accumulated-context:
   ```yaml
   through_line: "string (1-2 sentences, or the edge-case string)"
   consulting_read: "string (2-3 sentences) | null"
   ```

7. Write `outputs` to this file's frontmatter:
   ```yaml
   outputs:
     through_line: "<the generated string>"
     consulting_read: "<the generated string or null>"
     items_synthesized: <int>
   ```

---

## SUCCESS METRICS

- `through_line` is present and matches David's register — no newsletter fluff, no corporate filler.
- `consulting_read` is non-null when 2+ items exist, and grounded in today's actual signals.
- Edge cases (0 or 1 item) produce the prescribed honest fallback strings, not fabricated patterns.
- Neither field exceeds 3 sentences.
- No vault writes occurred in this step.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `summarized_items` missing from accumulated-context | Abort; surface: "[Knox]: Step-04 output missing. Re-run from step-04." |
| `identity/VOICE.md` unreadable | Proceed with Knox's default register; log the gap in outputs. |
| `config.yaml` lenses missing | Generate consulting_read from general IT-consulting context; note the gap. |

---

## NEXT STEP

`workflows/watchtower/steps/daily-step-05-capture.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
