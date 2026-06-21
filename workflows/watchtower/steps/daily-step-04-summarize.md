---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. One summary per item. No combining items into a single paragraph.
3. Lead every summary with the takeaway — what David should know, not what happened.
4. Plain prose only. No bullet points inside summaries.
5. Target length: 60–100 words per summary. Strict upper bound: 120 words.
6. Do NOT editorialize beyond what the item actually says. No hype. No padding.
7. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | sonnet |
| Input | `accumulated-context.scored_items` (from step-03), `identity/VOICE.md` |
| Output | Summarized item list written to `accumulated-context.summarized_items` in `state.yaml` |

---

## CONTEXT BOUNDARIES

- Scope: write summaries only. No vault writes, no dashboard updates — that is step-05.
- Voice: match David's direct, first-person professional register from `identity/VOICE.md`.
- Each summary answers: "What is this, and why does it matter to David right now?"
- Do not repeat the item title verbatim in the opening sentence.

---

## YOUR TASK

1. Read `identity/VOICE.md` for tone calibration.

2. For each item in `accumulated-context.scored_items`:

   Write a single paragraph (60–100 words). Structure:
   - Sentence 1: The takeaway — what David should know or do with this.
   - Sentences 2-3: Context that makes the takeaway credible or actionable.
   - Final sentence (optional): A specific question or angle worth David's attention, if genuinely relevant.

   Example structure (not a template — vary the language):
   > "Anthropic shipped a new multi-agent orchestration API that cuts coordination overhead significantly. This is relevant because [consulting angle or David's lens]. Worth watching whether [specific implication]."

3. Write summarized items to `accumulated-context.summarized_items` in `state.yaml`. Schema per item — extend the scored_items schema with:
   ```yaml
   summary: "string (60-120 words)"
   ```
   All other fields from scored_items carry forward unchanged.

4. Write `outputs` to this file's frontmatter:
   ```yaml
   outputs:
     items_summarized: <int>
     avg_word_count: <float>   # average summary length
   ```

---

## SUCCESS METRICS

- Every scored item has a summary.
- No summary exceeds 120 words.
- No summary leads with the title restatement.
- Tone is direct, professional, Jarvis-style — not newsletter-fluffy.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `scored_items` missing | Abort; surface: "[Knox]: Step-03 output missing. Re-run from step-03." |
| Zero scored items | Write `summarized_items: []`; continue to step-05 which will produce an empty daily note |
| Summary exceeds 120 words | Trim before writing. This is an execution constraint, not a suggestion. |

---

## NEXT STEP

`workflows/watchtower/steps/daily-step-04b-synthesize.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
