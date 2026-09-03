---
id: schema-validator
name: Schema Validator
owning_agent: rigby
model: haiku
context: inline
fairness: {applicable: false, reason: "Pure data-shape validation utility. No differential treatment of people, no eligibility or scoring decision."}
trigger_keywords:
  - validate schema
  - schema validation
  - content validation
  - metadata validation
  - schema-validator
---

<!-- system:start -->
# Schema Validator

**Callable by:** Any workflow step that currently hand-rolls a validation checklist against an
object it just built or fetched. Currently consumed by `workflows/plaud-ingest/steps/step-01-discover.md`
(Gate 2, recording metadata) and `workflows/content-discovery/steps/step-01-discover.md`
(Gate 2, content schema) and `workflows/content-approval/steps/step-01-approve.md` (Gate 4,
publishing pre-flight). Flagged as reusable for any future gate that boils down to "check this
object against a checklist before letting it through."

## Purpose

Several workflow gates independently re-implement the same shape: a table of field → expected
value → what to do on failure, followed by a log line and a pass/fail write to frontmatter
`outputs`. This skill centralizes that pattern as pure, deterministic, side-effect-free
validation: it never calls an external API, never retries, never sends a notification — it
only looks at the `data` object it's given and reports what's wrong with it. The caller (the
workflow step) still owns what a violation means for its own control flow (hard-stop the step,
soft-flag and continue, exclude one item from a batch, etc.) — this skill's job ends at
producing an accurate, itemized `errors`/`warnings` list.

**This skill does not use judgment calls or LLM inference on the object's content.** If a check
requires narrative/qualitative judgment (e.g. "does this read as David's personal angle rather
than a source recap," "are these four post-arc elements actually present in the prose"), the
calling step must resolve that judgment itself and pass the result in as a plain boolean or
string field in `data` — this skill only checks the fields it's given against the rules it's
given, mechanically.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## Input

| Field | Required | Description |
|-------|----------|--------------|
| `data` | Yes | The object to validate — a flat or shallow dict of field → value. Pre-compute any judgment-based fields (booleans, counts, extracted strings) before calling; this skill does not parse free text for meaning. |
| `schema_spec` | Yes | The validation rules, see shape below |

### `schema_spec` shape

```yaml
required_fields:
  # Either a bare field name (defaults to severity: error / hard-blocking), or an object
  # for explicit control:
  - "file_id"
  - { field: "date", severity: "warning" }   # present-but-optional-strength check

word_count:
  field: "word_count"    # optional — defaults to "word_count" if omitted
  min: 300
  max: 500
  severity: "error"       # optional — defaults to "error"

format_rules:
  # field -> constraint. Supported constraint shapes:
  transcript_status: { enum: ["ready", "pending", "missing"], severity: "warning", default_if_missing: "missing" }
  date: { type: "date", severity: "warning" }
  duration_seconds: { type: "positive_number", severity: "warning" }
  name: { type: "non_empty_string", severity: "warning" }

tags:
  field: "tags"                     # field in `data` holding the tag list
  allowed_list: ["ai", "leadership", "..."]   # locked-list check
  format: "object_with_id"          # "object_with_id" | "bare_string" — enforce shape
  severity: "error"

em_dash_check:
  field: "body"          # field in `data` holding the text to scan
  enabled: true
  severity: "error"

custom_checks:
  # Anything not covered above — mechanical checks only, no free-text judgment.
  - { field: "meta_title", rule: "max_length", value: 70, severity: "error" }
  - { field: "meta_description", rule: "max_length", value: 155, severity: "error" }
  - { field: "feature_image_landscape", rule: "must_be_true", severity: "error" }
  - { field: "has_hook", rule: "must_be_true", severity: "error" }
  - { field: "has_story", rule: "must_be_true", severity: "error" }
  - { field: "has_insight", rule: "must_be_true", severity: "error" }
  - { field: "has_challenge", rule: "must_be_true", severity: "error" }
```

Every rule block is optional — pass only the sections relevant to what you're validating. All
severities default to `"error"` unless specified as `"warning"`.

## Output

```yaml
valid: true | false        # false iff at least one "error"-severity check failed
errors:                    # error-severity failures — these are what the caller should treat as blocking
  - { field: "file_id", rule: "required_fields", actual_value: null }
warnings:                  # warning-severity failures — informational, not blocking by this skill's own contract
  - { field: "date", rule: "required_fields", actual_value: null }
```

`valid` reflects **only** the `errors` list. A caller that wants "warnings" to also block (or
vice versa — wants specific "errors" to not block, e.g. plaud-ingest's per-recording soft gate
which excludes only on missing `file_id`) makes that call itself by inspecting `errors` and
`warnings` individually rather than relying on `valid` alone. This skill's hard-gate contract
(`valid: false` should block downstream processing) is the *default* recommendation, not a
constraint that removes the caller's judgment about per-field severity — that's exactly why
severity is configurable per rule in `schema_spec` rather than fixed by this skill.

## Process

1. **required_fields:** for each entry, check `data[field]` is present and not `None`/empty
   string. On failure, record `{field, rule: "required_fields", actual_value: data.get(field)}`
   at the entry's severity (default error).
2. **word_count:** if present in `data` (using `word_count.field`, default `"word_count"`),
   check it falls within `[min, max]` inclusive. On failure record
   `{field, rule: "word_count", actual_value: <the count>}`.
3. **format_rules:** for each field, apply its constraint:
   - `enum`: value must be one of the listed options. If missing/unrecognized and
     `default_if_missing` is set, do not treat as a failure — instead record the default as
     an informational note in `warnings` with `rule: "defaulted"` (caller is responsible for
     actually applying the default to its own working data — this skill only flags it).
   - `type: "date"`: must be parseable as a date (any common ISO/human format).
   - `type: "positive_number"`: must be a number > 0.
   - `type: "non_empty_string"`: must be a non-empty string after trimming.
4. **tags:** check every tag in `data[tags.field]` is present in `allowed_list` (if given),
   and that the collection's shape matches `format` (`object_with_id` = every entry is an
   object with an `id` key; `bare_string` = every entry is a plain string). Record one error
   per offending tag, plus one error if the format doesn't match.
5. **em_dash_check:** if enabled, scan `data[em_dash_check.field]` for `—`, `–` used as a dash,
   or `--`. Record one error (not one per occurrence) with the first offending snippet as
   `actual_value` if any are found.
6. **custom_checks:** apply each mechanically:
   - `max_length` / `min_length`: length of `data[field]` (string or list) against `value`.
   - `must_be_true`: `data[field]` is truthy.
   - `must_be_false`: `data[field]` is falsy.
   - `must_equal`: `data[field] == value`.
   - Any other `rule` name not listed here: treat as unsupported, record a warning
     `{field, rule: "unsupported_custom_check", actual_value: rule_name}` rather than silently
     skipping it or guessing at behavior — this makes a schema_spec typo visible instead of a
     silently-never-checked field.
7. Assemble `errors` (all "error"-severity failures) and `warnings` (all "warning"-severity
   failures, plus any `defaulted`/`unsupported_custom_check` notes). Set
   `valid: len(errors) == 0`.
8. Return `{valid, errors, warnings}` to the caller. Do not log, notify, or take any other
   action — that's the caller's job.

## Error Handling

| Situation | Response |
|-----------|----------|
| `schema_spec` references a field not present anywhere in `data` | Not itself an error unless a `required_fields` entry names it — a `format_rules`/`custom_checks` entry on an absent field is skipped and noted in `warnings` as `{field, rule: "field_absent", actual_value: null}`, since checking a rule against nothing that exists is not the same as that field failing its rule. |
| `data` is not a dict/object | Return `valid: false`, single error `{field: null, rule: "invalid_input", actual_value: type(data)}`. Do not attempt partial validation. |
| `schema_spec` is empty/missing all sections | Return `valid: true`, empty `errors`/`warnings` — an empty spec validates everything, by design; the caller decides whether that's the right spec to be passing. |
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

<!-- system:start -->
## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/schema-validator-latest.json
```

Content:
```json
{
  "skill": "schema-validator",
  "agent": "<caller's agent, e.g. knox or harper>",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action, immediately followed by the grading step below.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill schema-validator
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/schema-validator.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
