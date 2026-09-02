---
id: visual-verification
name: Visual Verification
owning_agent: rigby
model: sonnet
context: inline
fairness: {applicable: false, reason: "Infrastructure gate for human sign-off on a screenshot. No differential treatment of people, no eligibility or scoring decision."}
trigger_keywords:
  - visual verification
  - visual confirmation
  - manual approval
  - human sign-off
  - screenshot approval
  - confirm the screenshot
---

<!-- system:start -->
# Visual Verification

**Callable by:** Any agent or workflow step that needs a human to look at a screenshot and
make a call before the workflow proceeds. Currently consumed by
`workflows/golf-booking/steps/step-05-visual-verification.md`.

## Purpose

Some decisions cannot be safely automated away — where an automated DOM check has already
been fooled once, or where the cost of a false positive (silently proceeding on a booking,
send, or purchase that didn't actually happen) is high enough that a human eyeball is the
right final gate. This skill is that gate, packaged so any workflow can drop it in without
re-inventing the approval/escalation/record-keeping logic each time.

**This is a HARD gate.** There is no path through this skill that proceeds without either an
explicit approval or an explicit, logged escalation decision. A blank, a timeout, or an
ambiguous response is never treated as approval.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

| Field | Required | Description |
|-------|----------|--------------|
| `screenshot_path` | Yes | Absolute path to the screenshot (or a description of how to capture it, e.g. a Peekaboo/osascript command, if the caller hasn't captured it yet) |
| `reference_context` | Yes | What is being verified and against what — e.g. "Confirm this booking matches: Saturday June 13, 1:00 PM, Frisco Lakes, 2 players (David + Susie)." Give the caller's specific expected values, not a generic description. |
| `escalation_option` | Yes | What the caller should do if verification fails — a Slack message template, an abort instruction, or a named fallback step. The caller must supply this; this skill does not invent one. |
| `caller` | Recommended | The workflow/skill/agent invoking this, and the step name — used in the decision record for traceability |

## Output

Returned to the caller (and written to the decision record — see Process step 4):

```yaml
approval: true | false
decision:
  outcome: "approved" | "rejected" | "escalated"
  reasoning: "<what was seen in the screenshot and why it matches or doesn't match reference_context>"
  escalation_taken: "<what was done if outcome is 'escalated' or 'rejected' — must reference escalation_option, not be improvised>"
timestamp: "<ISO-8601 timestamp of the decision>"
```

## Process

### 1. Display the screenshot

If `screenshot_path` is already a saved file, read it directly (the Read tool renders images).
If the caller passed a capture instruction instead of a path, run it first (Peekaboo skill or
`mcp__Control_your_Mac__osascript` screenshot commands are the usual mechanism), then read the
resulting file. Do not proceed to step 2 without having actually looked at the image content —
a filename existing is not verification.

### 2. Compare against reference context

Hold `reference_context` next to what the screenshot actually shows. Check every specific
value the caller listed (date, time, name, amount, count, status text) individually — do not
give a single holistic "looks right" impression. List each check and its result.

### 3. Prompt for manual approval

Present the screenshot and your comparison to the controller (David) and ask for an explicit
decision. Do not pre-decide on the agent's own visual read alone when the caller's
`reference_context` says this is a critical/high-stakes verification — surface it and wait.
Frame the ask so a one-word answer is unambiguous:

```
[Verification needed] {caller}: {one-line summary of what's being confirmed}

Screenshot: {screenshot_path}
Expected: {reference_context, itemized}
Observed: {what the image actually shows, itemized}

Reply "approve" to proceed, or "reject" to trigger the escalation path.
```

If the environment does not support a live prompt (e.g. this skill is running inside an
unattended/scheduled execution with no controller present to answer), that is not a silent
pass. Treat "no one is available to answer" as a rejection and go straight to step 4's
escalation path — never default to approval because no one was there to say no.

### 4. Record the decision

Regardless of outcome, write a decision record. If the caller didn't specify a location, this
skill's default is `systems/eval-harness/skill-runs/visual-verification-decisions.jsonl`
(append one JSON line per decision — do not overwrite prior decisions):

```json
{"timestamp": "<ISO-8601>", "caller": "<caller>", "screenshot_path": "<path>", "reference_context": "<summary>", "outcome": "approved|rejected|escalated", "reasoning": "<text>"}
```

**If approved:** Return `approval: true` to the caller. Do not run the escalation path.

**If rejected or no answer was available:** Run exactly the `escalation_option` the caller
supplied — do not improvise a different fallback. Return `approval: false` with
`decision.outcome` set to `"rejected"` or `"escalated"` depending on which path fired, and
`escalation_taken` describing what was actually done.

### 5. Return control

Hand `approval`, `decision`, and `timestamp` back to the caller. The caller is responsible for
what happens next (proceed, abort, retry) — this skill's job ends at producing an
unambiguous, recorded decision.

## Error Handling

| Situation | Response |
|-----------|----------|
| `screenshot_path` doesn't exist / capture command fails | Do not guess what the screenshot would have shown. Treat as a failed verification, run `escalation_option`, record `outcome: "escalated"` with reasoning noting the missing screenshot. |
| Caller didn't supply `escalation_option` | Stop before displaying anything. Ask the caller (or the workflow step author, if this is being wired in at build time) to supply one — this skill will not invent an escalation path for a HARD gate. |
| Screenshot is unreadable/corrupted | Same as missing screenshot — escalate, do not approve on faith. |
| Controller approves but the itemized comparison in step 2 shows a clear mismatch | Surface the mismatch explicitly before accepting the approval — "You said approve, but the observed date doesn't match the expected date. Confirm you want to proceed anyway?" Do not silently overrule a human "approve," but do not let a rubber-stamp answer hide a comparison you already found wrong. |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/visual-verification-latest.json
```

Content:
```json
{
  "skill": "visual-verification",
  "agent": "<caller's agent, e.g. sterling>",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output (e.g. escalation ran because no controller was available), `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action, immediately followed by the grading step below.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill visual-verification
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/visual-verification.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
