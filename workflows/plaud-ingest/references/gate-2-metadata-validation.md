<!-- system:start -->
## QUALITY GATE 2 — Recording Metadata Validation (SOFT, LOGGED, PER-RECORDING)

This step's own MANDATORY EXECUTION RULE #3 already requires capturing `file_id`, `name`,
`date`, `duration_seconds`, `has_transcript`, and `transcript_status` for every new recording
(see the schema in step 3 of YOUR TASK above) — this gate is the explicit checkpoint that
those fields are actually present and well-formed before they get handed to step-02 and
step-03, which both key their logic off `transcript_status` and `date`/time.

Call `skills/schema-validator/SKILL.md` once per entry in `new-recordings`:

```yaml
data: { file_id, transcript_status, date, duration_seconds, name }   # the recording's own fields
schema_spec:
  required_fields:
    - "file_id"    # severity defaults to "error" — this is the one HARD exclusion in this soft gate
  format_rules:
    transcript_status: { enum: ["ready", "pending", "missing"], severity: "warning", default_if_missing: "missing" }
    date: { type: "date", severity: "warning" }
    duration_seconds: { type: "positive_number", severity: "warning" }
    name: { type: "non_empty_string", severity: "warning" }
```

Interpret the skill's `{valid, errors, warnings}` result yourself — this gate's severity split
predates and drives the schema_spec above, the skill doesn't decide it for you:

| Skill result | Action |
|-------|----------------------|
| `errors` contains a `file_id` entry (`required_fields` failure) | **Exclude this recording** from `new-recordings` entirely and log it — step-02/03/04/05 all key off `file_id`; a recording without one cannot be tracked through the pipeline. This is the one per-recording HARD exclusion inside an otherwise soft gate. |
| `warnings` contains a `transcript_status` entry | If absent or unrecognized, apply the skill's reported `default_if_missing` value (`"missing"` — safest assumption, triggers step-02 to attempt transcription rather than silently skipping) and flag it. |
| `warnings` contains a `date` entry | Flag it — step-03's calendar cross-reference cannot run without it, so that recording will very likely fall through to controller escalation in step-03. Do not block on it here; let step-03 handle the downstream consequence. |
| `warnings` contains a `duration_seconds` entry | Flag it — cosmetic for this step (used in reporting), not blocking. |
| `warnings` contains a `name` entry | Flag it and fall back to `file_id` as the display name. |

This gate does **not** halt the workflow — the pipeline already tolerates partial metadata
gracefully further downstream (step-03 has its own escalation path for recordings it can't
date-match, step-05 falls back to `file_id` as a display label). Missing `file_id` is the one
exception because it breaks tracking entirely, not just one feature.

Log the result:
```
[Gate 2] N recordings validated. M flagged (see gate_2_flagged_recordings). K excluded (missing file_id).
```

Write `gate_2_result: "pass"` (nothing flagged) or `"pass-with-flags"` (flagged but none
excluded) or `"pass-with-exclusions"` (one or more excluded for missing `file_id`) to `state.yaml`
`accumulated-context`, along with `gate_2_flagged_recordings: [{file_id, issue}, ...]`.

---
<!-- system:end -->
