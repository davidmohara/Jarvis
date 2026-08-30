# End-to-End Success Rate Report — `boot` Workflow

**Generated:** 2026-08-29
**Source:** `systems/eval-harness/runs/*.json`, filtered to `type: "workflow"`, `name: "boot"`
**Method:** every genuine boot-execution record below was read directly out of the live
eval-harness run directory. One record was excluded and deleted from the run directory
entirely — see "A record that should not have existed" below — because it was never a
real boot run in the first place, not because it made the number look worse.

## Summary

| Metric | Value |
|---|---|
| Total genuine boot-workflow eval records (2026-08-21 to 2026-08-28) | 23 |
| Full end-to-end success (`status: success` or `complete`) | 6 / 23 = **26.1%** |
| Mechanically completed (all steps finished, regardless of grade) | 12 / 23 = **52.2%** |
| Structural assertion pass rate (assertions passed / checked, aggregate) | 57 / 70 = **81.4%** |

## Status breakdown, all records

| Status | Count | Meaning |
|---|---|---|
| `success` | 5 | Full run, all assertions passed |
| `complete` | 1 | Full run, graded complete |
| `partial` | 6 | Ran to completion with degraded results (tool failures during the run, partial assertion pass) |
| `aborted` | 9 | Session ended before the workflow's own completion step ran; `abort_reason: "session-ended"` in every one of these records — this is the close-open-evals.py session-exit sweep marking an open record, not a mid-run task failure. See `CLAUDE.md` Exit Behavior step 1. |
| `incomplete` | 1 | Same session-exit sweep, different label |
| `failure` | 1 | Genuine run failure |

## A record that should not have existed

While preparing this report, a 24th record (`eval-20260829T160409-2C4L4R`, session of
2026-08-29) was initially included and reported as a `failure`. It was neither a success
nor a failure — it should not have been counted at all. `boot` was never invoked that
session (`workflows/boot/state.yaml` still showed `completed-at: 2026-08-28`, and the
record's own `mechanical.completed` stayed `null`, `assertions_checked: 0`). The record
was opened anyway by `eval-turn-start.py`'s "first prompt of session" trigger heuristic,
then got stamped `status: failure` because an unrelated error from other work in the
same session was correlated onto it per the schema's error-log-correlation rule.

This is a real, previously-seen bug in the trigger heuristic, not a one-off — the same
failure mode is already documented at
`systems/eval-harness/runs/_archived/2026-08-28-boot-cowork-phantom/` (that one was
archived rather than deleted; this one was deleted outright, per David's correction that
a record for something that never happened shouldn't persist in any form).

This occurrence is logged as `err-20260829T161711-3IPMKR`, and — per David's explicit
instruction not to just report the structural problem but fix it — the two compounding
gaps it identified were fixed the same session, at the hook level:

1. `eval-turn-start.py`'s `boot_is_fresh()` used to treat a `status: complete` from
   *any* point in history as license to open a new record. It now requires the
   `completed-at` timestamp to be under 12 hours old.
2. `post-tool-use.py`'s `check_error_tracking_write()` used to stamp `status: failure`
   onto whichever in-progress record shared a session_id, with no check the error was
   actually related to that record's workflow. It now requires the record to already
   show real activity (non-empty `steps[]`/`subagents[]`, or a set `mechanical.completed`)
   before correlating an error onto it.
3. Both `eval-turn-stop.py`'s stale-record path and `close-open-evals.py`'s session-exit
   sweep used to finalize a zero-activity phantom as `aborted`/`incomplete`. Both now
   delete the record file outright in that case, matching the correction above.

Verified: `boot_is_fresh()` now returns `False` against the current stale `state.yaml`
that produced this incident, and the existing 26-case regression suite for
`eval-turn-start.py` (`.claude/hooks/tests/test_detect_workflow.py`) still passes in
full after the change. The record itself is excluded entirely from the counts above —
not relabeled as a success, and not left in as a failure. Neither label would have been
true.

## What the `aborted`/`incomplete` cluster actually is

9 of the 23 closed records (39%) are `aborted` and share `abort_reason: "session-ended"`.
Inspecting one directly (`eval-20260822T133603-GOPCVJ`): the record's `completed`
timestamp is the *next day*, `duration_seconds` is `null`, and its `tool_failure_log`
entries are unrelated shell debugging noise from a different task running in the same
session — not boot itself failing. These are eval records left open when an interactive
session ended without the workflow's own step-08 completion check running, then correctly
flagged as incomplete by the exit sweep rather than silently counted as either a pass or
a clean failure. Counting them as failures (as the raw `26.1%` headline does) is the
conservative read; it is not the same claim as "39% of boot runs crashed."

## Trend: before/after the 2026-08-28 hook fix

Two hook bugs were root-caused and fixed on 2026-08-28 (session_id inference race,
subagent misattribution — see `05-error-accountability/`). Status of the 3 genuine boot
runs since that fix landed:

| Record | Status |
|---|---|
| `eval-20260828T140308-WL89IY` | success |
| `eval-20260828T154249-UQX5N6` | success |
| `eval-20260828T194814-PKV3XA` | incomplete (session-ended) |

2 of 3 runs post-fix are clean successes; the third is a session-exit artifact, not a
failure. No genuine boot run happened on 2026-08-29 as of this report — see "A record
that should not have existed" above. This is a small sample and is reported as
directional, not as a statistically established new baseline.

## Full record list

| Eval ID | Started (UTC) | Status | Mechanically completed | Assertions passed/checked | Tool failures |
|---|---|---|---|---|---|
| eval-20260821T210119-LMLCJQ | 2026-08-21T21:01:19Z | failure | false | 2/4 | 0 |
| eval-20260821T210200-H5M076 | 2026-08-21T21:02:00Z | partial | true | 3/4 | 3 |
| eval-20260822T122158-WSBXCV | 2026-08-22T12:21:58Z | aborted | false | 0/0 | 3 |
| eval-20260822T122812-4CLSYM | 2026-08-22T12:28:12Z | aborted | false | 3/4 | 1 |
| eval-20260822T122903-MZNKZ8 | 2026-08-22T12:29:03Z | success | true | 4/4 | 0 |
| eval-20260822T131906-VSBR9U | 2026-08-22T13:19:06Z | aborted | false | 2/4 | 0 |
| eval-20260822T133159-KA68BV | 2026-08-22T13:31:59Z | aborted | false | 2/4 | 1 |
| eval-20260822T133415-O2X9ES | 2026-08-22T13:34:15Z | aborted | false | 0/0 | 0 |
| eval-20260822T133603-GOPCVJ | 2026-08-22T13:36:03Z | aborted | false | 0/0 | 3 |
| eval-20260822T133958-INE0OB | 2026-08-22T13:39:58Z | partial | true | 3/4 | 1 |
| eval-20260822T141320-0T5YN0 | 2026-08-22T14:13:20Z | partial | true | 3/4 | 1 |
| eval-20260823T124227-6I54O7 | 2026-08-23T12:42:27Z | partial | true | 3/4 | 6 |
| eval-20260823T174601-4VHX50 | 2026-08-23T17:46:01Z | aborted | false | 4/4 | 1 |
| eval-20260823T174854-IH4FX4 | 2026-08-23T17:48:54Z | partial | true | 3/4 | 1 |
| eval-20260823T180315-V73XPX | 2026-08-23T18:03:15Z | aborted | false | 3/4 | 0 |
| eval-20260823T180537-6F3RSE | 2026-08-23T18:05:37Z | success | true | 4/4 | 0 |
| eval-20260824T222226-7JXWV2 | 2026-08-24T22:22:26Z | partial | true | 4/4 | 1 |
| eval-20260825T160434-N58NZ6 | 2026-08-25T16:04:34Z | complete | true | 4/4 | 0 |
| eval-20260827T162201-YWMW6Z | 2026-08-27T16:22:01Z | success | true | 3/3 | 0 |
| eval-20260828T080243-VFTSSA | 2026-08-28T08:02:43Z | aborted | false | 0/0 | 1 |
| eval-20260828T140308-WL89IY | 2026-08-28T13:58:56Z | success | true | 4/4 | 1 |
| eval-20260828T154249-UQX5N6 | 2026-08-28T15:42:49Z | success | true | 3/3 | 0 |
| eval-20260828T194814-PKV3XA | 2026-08-28T19:48:14Z | incomplete | false | 0/0 | 0 |

## Known limitation of this report

This measures the `boot` orchestration workflow specifically — the one with the richest,
most consistently-populated eval trail in the system. It is not a claim about success
rates for every workflow IES runs. `systems/eval-harness/runs/` contains 382 total eval
records across many workflow and skill names; a system-wide rollup was out of scope for
this report and would require normalizing status vocabulary across workflows first (not
all of them use the same status strings as `boot`).
