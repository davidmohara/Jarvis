---
status: complete
started-at: "2026-10-09T16:56:00Z"
completed-at: "2026-10-09T16:58:00Z"
outputs:
  saved_brief: "meetings/Alice Mburu - 2026-10-09.md"
  sections: ["Summary of Interactions", "Open Action Items", "Key Calendar Events", "Suggested Talking Points"]
  talking_point_count: 7
model: sonnet
---

<!-- system:start -->
# Step 05: Quality Check and Save

## MANDATORY EXECUTION RULES

1. You MUST run every quality check below before saving. Do not skip checks because the brief "looks good."
2. You MUST fix any issues found during quality checks. Do not save a brief that fails a check.
3. You MUST save the brief to the correct knowledge base path. No other location is acceptable.
4. You MUST open the brief in the knowledge base after saving.
5. You MUST report the result to the controller with a one-line summary of the hottest topic.
6. You MUST save the brief to `meetings/{Person Name} - {YYYY-MM-DD}.md` and record its path in `state.yaml` `accumulated-context.saved_brief`. The verifier locates the file on disk by matching the person's name slug under `meetings/` (or the repo root) and validates the exact section headers and the numbered talking points directly from file content; a self-reported path is not accepted.

---

## EXECUTION PROTOCOL

**Agent:** Shep, spawned by the coordinator, never executed inline
**Input:** Assembled brief from step 04
**Output:** Saved, validated prep brief in knowledge base; confirmation message to controller

---

## CONTEXT BOUNDARIES

- This is the final gate. Shep takes quality personally. A sloppy brief means the controller walks into a 1:1 unprepared — that is a failure of care.
- Quality checks are binary. Pass or fix. There is no "close enough."
- Save location is always `working directory/{Person Name} - {YYYY-MM-DD}.md` in the knowledge base.

---

## YOUR TASK

### Quality Checklist

Run each check against the assembled brief. If any check fails, fix the issue before proceeding.

1. **Specificity check** — Every communication thread section includes specific dates, specific names, and specific details.
   - FAIL example: "You discussed several projects recently."
   - PASS example: "On Feb 5, Tom emailed about the Acme proposal delay. He noted pricing was still pending from the vendor."

2. **Action item ownership** — Every row in the Open Action Items table has a clear owner (David, the other person, or Both) and a current status.
   - FAIL: An item with no owner or "TBD" status.
   - PASS: Every item attributed and status updated.

3. **Previous brief continuity** — If a previous brief exists, every open item from that brief is accounted for in the current brief (resolved, carried forward, or explicitly noted as stale).
   - FAIL: Items from the previous brief disappeared without explanation.
   - PASS: "This was in the last brief and has been resolved" or "Still open — 3 weeks now."

4. **Talking point specificity** — All 5-7 talking points reference actual data from the brief. No generic prompts.
   - FAIL: "Discuss current projects."
   - PASS: "Ask about the timeline on the Acme proposal — last update was Feb 8, still waiting on legal review."

5. **Calendar hygiene** — The Key Calendar Events section does not contain any excluded recurring meetings (all-hands, sales standups, recurring standups, townhalls, and any others defined in the controller's preferences).
   - FAIL: An excluded recurring meeting appears in the calendar section.
   - PASS: Only relevant, non-routine events listed.

6. **Sensitive item handling** — Any HR, compensation, legal, or performance items are present in the brief but flagged with `**[Sensitive]**`.
   - FAIL: Sensitive item omitted entirely, or included without a flag.
   - PASS: Flagged and included with appropriate context.

7. **Tone check** — The brief reads like Shep: warm, direct, useful. Not robotic, not padded, not vague.
   - FAIL: Reads like a database export or a corporate report.
   - PASS: Reads like a trusted advisor briefing you before a conversation with someone you care about.

### Save Sequence

After all quality checks pass:

1. **Save to knowledge base** via knowledge base API.
   - Path: `working directory/{Person Name} - {YYYY-MM-DD}.md`
   - Content: The full assembled and validated brief.

2. **Open in knowledge base** for the controller to review.
   - This ensures the controller can see it immediately.

3. **Report to controller.** Deliver a concise confirmation:
   ```
   Your {Person Name} 1:1 brief is ready. {One-line summary of the hottest topic}.
   ```
   Examples:
   - "Your {Person A} 1:1 brief is ready. The Acme proposal has been stuck for 10 days — they're waiting on you to unblock pricing."
   - "Your {Person B} 1:1 brief is ready. Three delegations are overdue and the event still has no confirmed date."
   - "Your {Person C} 1:1 brief is ready. Clean slate — no open items, no drama. Good time for a forward-looking development conversation."

### Handoff Rules

If during brief assembly any of these conditions were detected, flag them in your report:

- **Client/deal context needed** — A talking point involves a specific client or deal that Chase would have deeper context on. Flag: "Chase may have additional context on {account}."
- **Content deadline involved** — A talking point involves a content deliverable (presentation, blog post, document) with a deadline. Flag: "Harper is tracking a deliverable related to {topic}."
- **Goal drift detected** — A pattern in the communications suggests the controller or the person is drifting from quarterly rocks. Flag: "Quinn should assess — {observation} may indicate misalignment with {rock name}."

### Output Persistence (MANDATORY)

The verifier for this step does not read a nested block; it finds the saved brief on disk and validates its content directly. Save the brief to `meetings/{Person Name} - {YYYY-MM-DD}.md` and record its path in `state.yaml` `accumulated-context.saved_brief`, plus this step's frontmatter `outputs`. The saved file MUST contain these four exact section headers (verbatim strings the verifier greps for) and at least five talking points formatted as a numbered list with a bold lead, matching the pattern `^\d+\.\s+\*\*`:

```yaml
# state.yaml -> accumulated-context
saved_brief: "meetings/{Person Name} - {YYYY-MM-DD}.md"

# step-05-quality-check-and-save.md -> frontmatter
outputs:
  saved_brief: "meetings/{Person Name} - {YYYY-MM-DD}.md"
  sections: ["Summary of Interactions", "Open Action Items", "Key Calendar Events", "Suggested Talking Points"]
  talking_point_count: 5
```

Required section headers in the saved file:

- `## Summary of Interactions`
- `## Open Action Items`
- `## Key Calendar Events`
- `## Suggested Talking Points`

Talking points MUST be written as `1. **{Topic}**: {specific point}` so the numbered-bold pattern matches; fewer than five fails verification.

---

## SUCCESS METRICS

- All 7 quality checks passed
- Brief saved to correct knowledge base path
- Brief opened in knowledge base
- Controller received confirmation with one-line hottest topic summary
- Cross-agent flags delivered if applicable

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Quality check fails | Fix the issue in the brief and re-check. Do not save until all checks pass. |
| Knowledge base unavailable | Fall back: output the full brief as text in the conversation. Tell the controller: "Knowledge base unavailable — here's your brief inline. Save it manually if needed." |
| File already exists at the save path | Overwrite it. The latest brief is always the most current. Note: "Updated existing brief for {Person Name}." |

---

## EVAL RECORD

**Before closing the one-on-one-prep workflow**, write an eval record for this run.

Determine status:
- `success` — all 7 quality checks passed, brief saved, controller received confirmation
- `partial` — brief saved but one or more quality checks had to be skipped (knowledge base down), or brief delivered inline due to save failure
- `failure` — brief could not be assembled or quality checks failed without resolution

Run:
```bash
python3 systems/eval-harness/close-eval-record.py \
  --name one-on-one-prep \
  --type workflow \
  --agent shep \
  --status {success|partial|failure} \
  --trigger manual \
  --started "{session_started from state.yaml}" \
  --steps "step-01-identify-meeting,step-02-gather-communications,step-03-gather-tasks,step-04-assemble-brief,step-05-quality-check-and-save"
```

## NEXT STEP

**After writing the eval record**, update `state.yaml`: set `current-step: step-06` (do NOT set `status: complete` yet).

Then read fully and follow `step-06-adversarial-verify.md`, the terminal adversarial verification step. Ralph cross-checks the brief's open action items and talking points against the delegation tracker and OmniFocus records and records the `adversarial-verification` checkpoint. The workflow is marked complete only at the end of step-06.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
