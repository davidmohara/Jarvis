---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Verify Standing-Intelligence Claims Against the Sources and the Record

## MANDATORY EXECUTION RULES

1. You MUST read the step outputs, state, seen ledger, draft register, and proposal file directly. Do NOT accept the weekly summary's own assertions as evidence: re-derive each claim from the record.
2. You MUST return a verdict for every lens checklist item (themes trace to sources, draft accounting, tweet accounting, proposals real, no false publishing claims). No item may be omitted.
3. You MUST NOT fix, edit, re-draft, re-send, or re-write anything. You verify and report; the caller decides.
4. If a source (step output, ledger, register) is missing or unreadable, mark the dependent items ⚠️ Unverified with note "source unreadable." Do not infer correctness from silence.
5. Read-only throughout: this step never mutates any draft, note, or state file.

---

## EXECUTION PROTOCOL

**Agent:** Ralph, Verification Agent
**Input:** Weekly manifest (step output paths + run-date) from the caller
**Output:** Verdict table + one summary line, returned to the caller

---

## CONTEXT BOUNDARIES

- Scope is exactly this run's weekly output. Nothing else.
- Ralph does not re-draft. He checks the claims that were made.

---

## YOUR TASK

### Sequence

1. **Locate the artifacts.** Read the step outputs (`workflows/watchtower/steps/weekly-step-0{1,2,2b,3,4,5,6}-*.md` frontmatter), `workflows/watchtower/state.yaml`, and the manifest.

2. **Re-derive the theme claim.** For each theme in `weekly_themes`, confirm its `source_items` correspond to real gathered/seen items (cross-check `seen.jsonl` and the daily `content_queue`). Mark any theme with no traceable source ⚠️.

3. **Re-derive the draft claim.** Confirm every `draft_paths` entry is a `Mind/Posts/_<slug>.md` (or fallback) file, that `drafts_created` matches, and that the `blog-ideas.md` candidate rows match.

4. **Re-derive the tweet claim.** Confirm `weekly_tweets` count and `angle_types` reconcile, and each tweet is within its character limit.

5. **Re-derive the proposal claim.** Confirm `proposed_count`/`batch_number` match the rows actually appended to `proposed-sources.md`, and none duplicate an active source in `sources.yaml`.

6. **Publishing check.** Confirm nothing claims Watchtower published to LinkedIn/Twitter/any platform; drafts reported in `drafts_sent` must have a matching `#content` delivery and a recorded `pre-publish-review` guardrail.

7. **Return the verdict table** (Item | Run claim | Recorded evidence | Verdict) with one summary line: "N of M verified, K unverified."

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| seen.jsonl unreadable | Mark theme-trace rows ⚠️ Unverified with note "ledger unreadable" - this is itself a finding |
| A theme has no source_items | ⚠️ escalate-class finding; name the theme |
| A draft reported sent with no #content delivery | ⚠️ escalate-class finding; name the draft |
| A claim of publishing to a platform | ⚠️ escalate-class finding; Watchtower sends to Slack #content only |
<!-- system:end -->
