# Case Study: Human Punch-Out, Distinct from Prompt Failure

This documents a real, unmodified example from IES's `plaud-ingest` workflow (owned by the
Knox agent) of a workflow deliberately punching out to a human rather than either (a)
failing silently, or (b) guessing and proceeding. This is the specific Stage 4 requirement:
"proven ways to punch out of the sequence of prompts to engage a human... kept separate
from failure scenarios of the prompt."

## What happened

On 2026-08-28, Knox ran `plaud-ingest` end to end. Discovery correctly identified one
genuinely new recording (a bug in the discovery step's dedup logic, unrelated to this
case study, had been found and fixed earlier the same day — see
`03-monitoring-audit-trail` for the audit trail that surfaced and verified that fix).

Knox then attempted to trigger transcription for that one new recording. The Plaud API
returned:

```json
{"status": -12, "msg": "start trans task error"}
```

Per the workflow's own `plaud-trigger` skill documentation, this specific status code is a
known signature of a Plaud account condition (transcription-minute exhaustion) — not a
transient error worth retrying with variations, and not something the workflow has the
authority or information to resolve on its own.

## The punch-out decision

Knox did not:
- Retry the call with altered parameters (that would be silently masking a systemic
  condition as a transient glitch)
- Skip the recording and continue silently (that would create a data-loss form of failure
  the audit trail wouldn't catch)
- Report this as a workflow "failure" (it isn't one — the workflow performed correctly;
  the *decision* of whether to top up transcription minutes belongs to a human, not the
  agent)

Instead, Knox set `workflows/plaud-ingest/state.yaml` to `status: blocked`, wrote a clear,
structured explanation of exactly what was observed and why it required a human decision,
and surfaced a direct question to the controller: "are you out of Plaud transcription
minutes?" Every other part of the pipeline that did not depend on this open question
continued normally and was reported as complete.

## Why this matters for Stage 4

This is the concrete difference the certification asks for between a prompt *failing* and
a workflow *punching out*:

- A failure is something the workflow itself did wrong and should try to recover from or
  clearly report as broken.
- A punch-out is the workflow correctly recognizing a decision boundary that belongs to a
  human — account status, budget, compliance, or judgment calls the workflow was never
  authorized to make — and stopping cleanly at that boundary rather than either guessing
  past it or crashing.

The distinction is enforced structurally, not just by convention: `state.yaml`'s `blocked`
status is a different signal than `failed` or `aborted` elsewhere in the system, and the
guardrail/eval harness (see `03-monitoring-audit-trail`) treats them differently when
scoring a run.
