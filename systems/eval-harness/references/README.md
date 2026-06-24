# Eval Harness — Reference Solutions

One known-good accepted output per gated capability. Per the Anthropic "Demystifying evals for AI agents" guidance (Step 2), a reference solution proves the task is solvable and that the graders are configured correctly.

## What a reference does

When a future run fails, the reference disambiguates the failure:

- Reference still passes its own assertions → agent regressed.
- Reference also fails its assertions → eval itself broke (grader drift or assertion rot).

## Storage layout

```
references/
  <capability>/
    reference.md          # pinned copy of the accepted output
    reference.meta.json   # pointer + provenance
    history/              # previous references, archived on overwrite
      reference-<promoted_on>.md
      reference-<promoted_on>.meta.json
```

## Meta schema

```json
{
  "capability": "morning-briefing",
  "source_eval_id": "eval-20260623T021234-DH9VSD",
  "source_path": "memory/working/morning-briefing-2026-06-23.md",
  "promoted_on": "2026-06-23T14:05:00Z",
  "promoted_by": "controller_feedback:positive",
  "workflow_version_hash": "2a045accfec69bac",
  "assertions_passed_at_promotion": "5/5",
  "assertions_total_at_promotion": 5,
  "notes": null
}
```

## Promotion rules

1. **Automatic** — fires when you rate a run "positive" at session exit. Requires all assertions to have passed at the time of the run. A positive rating on a run with failing assertions is logged but NOT promoted (surfaced to controller instead).
2. **Manual override** — `promote-reference.py --capability X --eval-id Y` pins any specific run by hand.
3. **Overwrite behavior** — promotion overwrites `reference.md` and archives the previous version to `history/` with a datestamp suffix. History is kept indefinitely for diff-over-time analysis.

## How references are used

- **Grader calibration** — grader subagent receives the reference as the "known-good" exemplar, sharpening pass/fail on subjective capabilities.
- **Eval-health drift check** — `eval-health.py` re-runs each capability's assertions against its own reference. If a reference stops passing its own assertions, the eval drifted and needs attention.
- **Blind comparison anchor** — comparator A/Bs a new run against the reference to detect quality regression even when assertions still pass.

## Capabilities with references

| Capability | Tier | Notes |
|---|---|---|
| morning-briefing | unattended | |
| daily-review | unattended | |
| rock1-revenue-monthly | unattended | |
| rock4-pipeline-weekly | unattended | |
| follow-up-nudges | unattended | |
| inbox-processing | unattended | |
| client-meeting-prep | high-stakes | |
| pipeline-review | high-stakes | |
| presentation-builder | high-stakes | |

Live-mode-only capabilities may also receive references (from a positive-rated real run). Their eval-health check is advisory rather than gating because assertion coverage is weaker without fabricated context.

## Scripts

- `promote-reference.py` — promote a run to reference (auto or manual)
- `eval-health.py` — re-run assertions against all references and report drift
