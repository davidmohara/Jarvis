---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. Read `identity/VOICE.md` and `identity/MEMORY.md` before scoring — the profile lenses in config.yaml are a terse summary; the identity files are the full picture.
3. Score every item individually. Do not batch-score or average-score a group.
4. Drop items below `config.yaml relevance.awareness_floor`. Do not carry them forward.
5. Mark items at or above `config.yaml relevance.content_flag` as content-worthy.
6. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | sonnet |
| Input | `accumulated-context.deduped_items` (from step-02), `config.yaml relevance`, `identity/VOICE.md`, `identity/MEMORY.md` |
| Output | Scored and filtered item list written to `accumulated-context.scored_items` in `state.yaml` |

---

## CONTEXT BOUNDARIES

- Scope: scoring and filtering only. No summarizing, no drafting.
- Score range: 0–100, integer.
- `awareness_floor` default: 40 (from config.yaml). Items below this are dropped.
- `content_flag` default: 75 (from config.yaml). Items at/above this are content-worthy.
- A "content-worthy" item gets a hook + outline drafted in the WEEKLY run (not here). This step only marks the flag.

---

## YOUR TASK

1. Read `config.yaml`. Note `relevance.awareness_floor`, `relevance.content_flag`, and `profile.lenses`.

2. Read `identity/VOICE.md` and `identity/MEMORY.md`. Internalize David's context, role, and what "highly relevant to what he does" means.

3. For each item in `accumulated-context.deduped_items`:

   **Score it 0–100 against these dimensions:**
   - **Lens alignment (0-40 pts):** How directly does the item relate to one or more of David's four lenses (AI/agentic delivery, IT consulting market, Texas/regional business, leadership/EOS)?
   - **Actionability (0-30 pts):** Can David DO something with this — a decision, a conversation, a competitive move, a speaking angle?
   - **Timeliness (0-20 pts):** Is this fresh news/signal, or evergreen background?
   - **Signal quality (0-10 pts):** Is the source/content substantive, or is it noise/marketing fluff?

   Sum the four dimensions. This is the item's score.

   Apply thresholds:
   - Score < `awareness_floor` → `keep: false`
   - Score ≥ `awareness_floor` → `keep: true`
   - Score ≥ `content_flag` → `keep: true`, `content_worthy: true`

4. Write surviving items (where `keep: true`) to `accumulated-context.scored_items` in `state.yaml`. Schema per item:
   ```yaml
   - title: "string"
     url: "string"
     source_name: "string"
     published_date: "YYYY-MM-DD"
     topic: "ai-agentic|it-consulting|texas-regional|leadership"
     raw_snippet: "string"
     score: <int 0-100>
     content_worthy: <bool>
     score_rationale: "one sentence explaining the score"
   ```

5. **Update the source activity ledger.** For each item where `keep: true` (score >= awareness_floor):
   - Open `workflows/watchtower/source-activity.json`.
   - Find the entry matching `source_name`.
   - Set `last_surfaced` to today's date if it is null or earlier than today.
   - Write the updated file.

   This is how the dormancy tracker knows a source is still producing signal. Step-07-prune reads these values at end of day.

6. Write `outputs` to this file's frontmatter:
   ```yaml
   outputs:
     deduped_count: <int>       # items entering this step
     dropped_below_floor: <int> # items dropped (score < awareness_floor)
     awareness_items: <int>     # items kept (score >= awareness_floor)
     content_worthy_items: <int> # items flagged content_worthy
   ```

---

## SUCCESS METRICS

- Every item in `deduped_items` has been scored.
- Items below `awareness_floor` are absent from `scored_items`.
- Content-worthy items are correctly flagged.
- Score rationale is present for every item.

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `deduped_items` missing | Abort; surface: "[Knox]: Step-02 output missing. Re-run from step-02." |
| Zero items survive floor filter | Continue with empty list; step-04 produces no summaries — this is valid; log it |
| `identity/VOICE.md` unreadable | Score using config.yaml profile only; log warning |

---

## NEXT STEP

`workflows/watchtower/steps/daily-step-04-summarize.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
