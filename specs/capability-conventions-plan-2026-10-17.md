# Capability Conventions Plan, 2026-10-17

**Status:** approved for execution. **Owner:** Rigby, end to end. **Scope:** skills, workflows, agents, and bundled scripts.

Source guidance: the four agentskills.io skill-creation guides (best-practices, optimizing-descriptions, evaluating-skills, using-scripts).

## Headline

IES already implements roughly 70% of this guidance. `rigby-capability-build` is a fork of Anthropic's `skill-creator` and already covers the eval loop, train/validation splits, blind comparison, timing capture, and bundled scripts. `quick_validate.py` enforces the 1024-character description limit; `improve_description.py` bakes the 100-200 word rule into its prompt.

The gaps are concentrated in four places:

1. **Authoring guidance is missing.** The build skill teaches the eval *loop* but not the *writing* rules: progressive disclosure, token economy, scoping, control calibration, gotchas, description authoring.
2. **Script conventions are absent.** No dependency declarations, no `--help`/error/structured-output rules, no dry-run or exit-code conventions.
3. **Two overlapping optimization systems.** `rigby-capability-build` Steps 6-9 and `workflows/skill-optimize` plus `rigby-skill-reflect` share eval machinery but do not reference each other.
4. **No durable landing zone for lessons.** The guidance's highest-value pattern (gotchas) has no home, and the error-log to skill-fix path does not write lessons back into skills.

One indictment worth recording: `rigby-capability-build/SKILL.md` is 668 lines, which blows past the 500-line ceiling it should be teaching.

## Locked decisions

1. **Architecture: shared core, two independent entry points.** The merge unifies shared machinery and conventions, not the invocation surface. `skill-optimize` keeps its own `state.yaml` and triggers and is never invoked as a sub-step of build.
2. **`skill-optimize` stays standalone.** It must remain runnable on its own so ongoing assessment and improvement can happen without a build.
3. **Size limits are guides, not rules.** Aim for them, flex with a declared exception. The linter warns above a guide; it never fails on size.
4. **Exceptions live in a central manifest.** Not file frontmatter, which is read on every run and should not carry point-in-time decisions that only matter on lint and optimize runs.
5. **Lint blocks the build path only.** Not evolution packaging, not git, not `skill-optimize`.
6. **Rigby executes the whole program.** Every new workflow carries `agent: rigby`.
7. **David grants size exceptions for now.** Rigby records them; David approves.

## Gap analysis (baseline)

| Guide | Prescribes | IES today | Gap |
|---|---|---|---|
| best-practices | Start from real expertise; mine runbooks, failure cases | Build skill asks clarifying questions and reads sibling patterns | No harvesting from IES's own operational record (error log, eval failures, transcripts) |
| | Token economy: add what the agent lacks | Not stated | Missing |
| | Progressive disclosure under 500 lines / 5k tokens, detail to `references/`, state *when* to load | `references/` in 6 skills; no rule; build skill itself is 668 lines | Missing as a rule |
| | Calibrate control to fragility; defaults not menus; procedures over declarations | "No vague instructions" only | Missing |
| | Gotchas section | No convention (4 files mention the word, none as a pattern) | Missing, highest single gap |
| | Output templates, checklists, validation loops, plan-validate-execute, bundle repeated scripts | Step files, Step 8 bundling, harness validators | Mostly covered |
| optimizing-descriptions | Imperative, pushy, intent-not-mechanics, 1024 limit | Enforced by script, not stated in prose | Partial |
| | ~20 queries, near-misses, 60/40 split, 3 runs, validation-selected | Fully implemented | Covered |
| | Fresh 5-10 query sanity check after optimizing | Not stated | Missing |
| | Agents only consult skills for tasks beyond their own reach | Not captured | Missing |
| evaluating-skills | `evals.json` with `expected_output` | Schema lacks `expected_output` | Minor |
| | Paired with/without, timing, blind compare, benchmark delta | Fully implemented | Covered |
| | Remove always-pass assertions, fix always-fail ones | Analyzer surfaces non-discriminating assertions | Partial |
| using-scripts | Self-contained scripts (PEP 723), `uv run` | No dependency declarations | Missing |
| | Non-interactive, `--help`, helpful errors, structured stdout / diagnostics stderr | Not stated | Missing |
| | Idempotency, `--dry-run`, exit codes, safe defaults, predictable output size | Not stated | Missing |
| | Relative paths from skill root, list scripts in SKILL.md | Uses `(cd ... && python3 -m ...)` | Divergent |

Toolchain confirmed present: `uv`, `uvx`, `npx`, `bunx`, `go`. Absent: `pipx`, `deno`. Python 3.14.6.

## Target architecture

```
SHARED CORE
  .claude/skills/rigby-capability-build/scripts/   eval machinery
  systems/eval-harness/scoring/                    scoring formula
  skills/rigby-skill-reflect/                      reflection component
  reference/capability-conventions.md              the rules
  systems/eval-harness/validate-conventions.py     the linter
  systems/eval-harness/conventions-exceptions.json exception manifest
        ▲                                   ▲
        │                                   │
   BUILD PATH                          IMPROVE PATH
   rigby-capability-build              workflows/skill-optimize/
   (new capability)                    (existing capability, standalone)
     harvest → clarify → plan            baseline → reflect → candidate
     → author → wire → evals             → score → gate → slow-update
     → run/grade → iterate               → report (lint report-only)
     → description → LINT (hard gate)
     → ship
```

`workflows/skill-optimize/` keeps its structure and its 8 steps. Its eval and scoring calls are repointed at the shared core instead of carrying copies, and it reads the same conventions doc. The build path adopts the same core. That is the whole merge.

The benefit is one scoring formula, one conventions standard, and no logic drift. The cost is two places to update when conventions change, mitigated by having both read the same doc and the same linter rather than restating rules locally.

## The convention set

Canonical home: `reference/capability-conventions.md` (one doc, not four).

### Universal

1. **Progressive disclosure.** Body under budget, detail into `references/`, and every pointer states *when* to load it ("Read `references/api-errors.md` if the API returns non-200").
2. **Token economy.** Only content the agent would get wrong without it. No explaining general concepts.
3. **Calibration.** Prescriptive where the task is fragile, explanatory where variation is fine.
4. **Defaults, not menus.** One default plus a brief escape hatch.
5. **Procedures over declarations.** Teach the method, not the instance.
6. **Gotchas section.** Environment-specific facts that defy reasonable assumptions.
7. **Output templates.** Concrete structure over prose format description.
8. **Validation loops.** Do, validate, fix, repeat.

### Skills

9. Two-tier architecture (content file plus stub) for agent-specific skills.
10. Description: imperative, intent not mechanics, pushy, under 1024 characters.
11. STATE CHECK pointer where run state exists.
12. No eval-harness machinery in skill files.

### Scripts

13. PEP 723 inline dependencies, run via `uv run`.
14. Non-interactive, a hard requirement. Flags, env vars, or stdin only.
15. `--help` with usage and examples.
16. Errors state what went wrong, what was expected, and what to try.
17. Structured data to stdout; progress and diagnostics to stderr.
18. Idempotency, `--dry-run` for destructive operations, distinct exit codes, safe defaults.
19. Predictable output size: summary by default, `--output` / `--offset` for more.
20. List scripts in `SKILL.md`; reference them by relative path from the skill root.

### Workflows

21. `workflow.md` stays an orchestrator. Logic lives in step files.
22. Step frontmatter is execution state only. Outputs go to `state.yaml`.

### Agents

23. Required sections present. Task Portfolio carries trigger phrases. One row per skill, no inlined protocol.

### Size guides (aims, not rules)

| Artifact | Guide |
|---|---|
| `SKILL.md` | 500 lines / 5k tokens |
| `workflow.md` | 150 lines |
| step file | 200 lines |
| agent file | 400 lines |
| script | 300 lines preferred |

## Enforcement

**New:** `systems/eval-harness/validate-conventions.py`, a linter that exits non-zero on FAIL-class findings.

### Severity classes

- **FAIL (blocks build):** missing system/personal blocks; agent-specific skill missing its stub; skill unregistered in `skills/_manifest.jsonl`; description over 1024 chars; `input(` in a bundled script; script with non-stdlib imports and no PEP 723 block; step file missing frontmatter.
- **WARN (never blocks):** over the size guide; description not imperative; no Gotchas section where error history exists; reference pointer lacking when-to-load phrasing; missing `--help`.

Size is never a FAIL. FAIL-class rules do not need exception support, since those are things you fix rather than tolerate.

### Exception manifest

**New:** `systems/eval-harness/conventions-exceptions.json`, co-located with the linter (its only machine consumer).

```json
{
  "version": 1,
  "exceptions": [
    {
      "path": "skills/galen-visit-prep/SKILL.md",
      "rule": "size.skill_body",
      "reason": "dense referral decision tree; splitting loses the chain",
      "granted_by": "david",
      "granted_on": "2026-10-17",
      "review_after": "2027-01-17"
    }
  ]
}
```

Stable rule IDs for size: `size.skill_body`, `size.workflow_md`, `size.step_file`, `size.agent_file`, `size.script`.

Behavior:

- The linter matches on path plus rule ID and reports a match as `acknowledged`, not `warn`. Acknowledged findings do not count against the WARN total.
- `review_after` in the past re-raises the finding as WARN, so exceptions decay rather than becoming permanent.
- The census tool flags exceptions that no longer apply (the file shrank below the guide) so they can be retired.

Frontmatter stays clean. Nothing point-in-time is read on a normal skill run.

### Wiring

- Build path: hard gate at the lint step.
- `workflows/skill-optimize/`: report only. Reads the same manifest so it does not re-report acknowledged items. Never blocks; its gate remains the score delta.
- Not wired to evolution packaging, git, or any pre-commit hook.

## Census tool

**Extend** `skills/rigby-skill-audit/scripts/audit.py` (it already walks both roots) with a reusable `--census` mode. Not a one-off.

Outputs: artifact counts by type; line and token distributions with percentiles; files over each guide; files holding exceptions; manifest coverage gaps; agent-specific skills missing their stub. JSON for machine use, human summary for reading.

Re-run points: Phase 0 calibration, the Phase 5 close-out audit, and any time a convention changes.

It is built to the script conventions in this plan (PEP 723 inline deps, `--help`, structured data to stdout with diagnostics on stderr) as the first dogfooding case.

## Deliverables

| ID | Deliverable | Path |
|---|---|---|
| D1 | Conventions doc | `reference/capability-conventions.md` |
| D2 | Linter | `systems/eval-harness/validate-conventions.py` |
| D3 | Census mode | `skills/rigby-skill-audit/scripts/audit.py` (extend) |
| D4 | Exception manifest | `systems/eval-harness/conventions-exceptions.json` |
| D5 | Build-path lint gate | `rigby-capability-build` build path |
| D6 | Shared-core unification | `workflows/skill-optimize/` repointed at shared eval machinery |
| D7 | Harvest step | new build step: mine error log, eval failures, transcripts, siblings |
| D8 | Script conventions and retrofit | 7 scripts in `rigby-capability-build/scripts/` plus `audit.py` |
| D9 | Gotchas writeback | `workflows/error-improvement/` plus `rigby-error-analysis` |
| D10 | Full library sweep | `workflows/conventions-migration/`, `agent: rigby` |

## Phasing

| Phase | Deliverable | Owner | Exit condition |
|---|---|---|---|
| 0 | Census all files; calibrate guides; write D1 | Rigby | Guides documented against real distribution |
| 1 | Build D2 with both severity classes and exception support (D4); run report-mode against library | Rigby | Linter runs clean in report mode |
| 2 | Shared-core unification (D6); harvest step (D7); script conventions (D8); Gotchas writeback (D9) | Rigby | New builds comply |
| 3 | Activate build-path lint gate (D5) | Rigby | Build path gated |
| 4 | Full library sweep (D10): mechanical fixes, then size | Rigby | Linter WARN count at zero |
| 5 | Close-out audit | Rigby | FAIL count zero, guides documented |

Phase 3 depends on Phase 2 only for new builds to comply. It does not depend on the sweep.

## Risks

1. **Two entry points, one convention set.** Mitigate with single-source docs and a single linter. Watch for drift if a rule gets restated locally.
2. **The merge touches live systems.** `skill-optimize` and `rigby-capability-build` may be referenced from scheduled tasks. Run `rigby-impact` before Phase 2.
3. **The sweep can be cosmetic.** The linter names which of the 373 workflow files actually need changes. Skip files that already comply.
4. **Gotchas writeback needs skill attribution in the error log.** If `systems/error-tracking/entries/` does not record a target skill, add that link in Phase 2 or the writeback has nothing to route on.
5. **Size guides are calibrated guesses until Phase 0.** Do the census before adopting any number, including these.

## Open items

- **Census tooling detail:** extend `audit.py` in place versus a sibling script it invokes. Recommendation: in place, since it already walks both roots.
- **Error-log skill attribution:** confirm the current schema supports it before Phase 2 (see Risk 4).
