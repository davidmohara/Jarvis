# Capability Conventions

<!-- system:start -->
The single standard for building skills, workflows, agents, and bundled scripts in IES. Two entry points read this doc — the build path (`rigby-capability-build`) and the improve path (`workflows/skill-optimize`) — but the rules are stated once, here. Do not restate them locally.

Enforcement: `systems/eval-harness/validate-conventions.py`. Size exceptions: `systems/eval-harness/conventions-exceptions.json`. Census: `python3 skills/rigby-skill-audit/scripts/audit.py --census [--json]`.

Source guidance: the four agentskills.io skill-creation guides (best-practices, optimizing-descriptions, evaluating-skills, using-scripts).

## Universal rules

1. **Progressive disclosure.** Body under budget, detail into `references/`. Every pointer states *when* to load it — "Read `references/api-errors.md` if the API returns non-200", never just "see references".
2. **Token economy.** Include only content the agent would get wrong without it. Never explain general concepts the model already knows.
3. **Calibration.** Prescriptive where the task is fragile (exact commands, exact fields); explanatory where variation is fine.
4. **Defaults, not menus.** Give one default plus a brief escape hatch. Never enumerate options and ask.
5. **Procedures over declarations.** Teach the method, not the instance. "Run `--census` to get the distribution" beats "distributions are available".
6. **Gotchas section.** Any capability with environment-specific facts that defy reasonable assumptions carries a `## Gotchas` section. Mine them from the error log (`systems/error-tracking/entries/`, filtered on `related_skill`), eval failures, and transcripts.
7. **Output templates.** Give a concrete structure to fill in, not a prose description of the desired shape.
8. **Validation loops.** Do, validate, fix, repeat. Every procedure ends with how to verify it worked.

## Skills

9. **Two-tier architecture** for agent-specific skills: a library content file (`skills/<name>/SKILL.md` with the full body) plus a fork stub (`.claude/skills/<name>/SKILL.md` with frontmatter and a pointer to the content file). Applies to new builds.
10. **Description:** imperative, states intent not mechanics, pushy, under 1024 characters. Validated by `quick_validate.py`; authored per `improve_description.py`'s 100-200 word prompt.
11. **STATE CHECK pointer** where run state exists (`workflows/<name>/state.yaml`).
12. **No eval-harness machinery in skill files.** Skills teach; the harness measures.

## Scripts

13. **PEP 723 inline dependencies** for any script with non-stdlib imports; run via `uv run <script>`. Stdlib-only scripts run via `python3`.
14. **Non-interactive, hard requirement.** Flags, env vars, or stdin only. `input(` in a bundled script is a FAIL.
15. **`--help` with usage and at least one example.**
16. **Errors state what went wrong, what was expected, and what to try.** To stderr.
17. **Structured data to stdout; progress and diagnostics to stderr.**
18. **Idempotency.** `--dry-run` for destructive operations. Distinct exit codes: 0 success, 1 usage/precondition, 2 execution failure.
19. **Predictable output size.** Summary by default; `--offset` / `--output` for more.
20. **List scripts in SKILL.md; reference them by relative path from the skill root.** Never `(cd dir && python3 -m ...)`.

## Eval scripts

24. **Every eval run records actual token usage.** Scripts that launch `claude -p` subprocesses capture per-run usage (input, output, cache-read, cache-creation tokens, model id) from stream events or the result envelope, and every archive/result they write carries an aggregated usage block (totals, runs measured, per-model counts). Estimates are never a substitute: no usage block in the archive means the driver is broken, not optional. Reference implementation: `run_eval.py`'s `run_single_query`/`run_eval` (usage from `message_delta` stream events, authoritative totals from the `result` event; aggregation happens in the shared runner so no future driver can forget it).

## Workflows

21. **`workflow.md` stays an orchestrator** (under the size guide). Logic lives in step files.
22. **Step frontmatter is execution state only** (agent, model, depends). Outputs go to `state.yaml`. Every step file carries frontmatter.

## Agents

23. **Required sections present. Task Portfolio carries trigger phrases** — one row per skill, no inlined protocol.

## Size guides (aims, not rules)

Calibrated against the 2026-10-17 census (185 skills, 75 workflows, 304 steps, 17 agents, 248 scripts). Each guide sits at roughly the p95 of the live distribution; over-guide files are flagged as WARN, never FAIL, and can carry a recorded exception.

| Artifact | Guide (lines) | Guide (tokens) | Census p90 / p95 | Over today |
|---|---|---|---|---|
| `SKILL.md` | 500 | 5000 | 317 / 435 lines; 3363 / 4118 tokens | 4 files |
| `workflow.md` | 150 | — | 128 / 136 lines | 3 files |
| step file | 200 | — | 199 / 251 lines | 29 files |
| agent file | 400 | — | 312 / 362 lines | 1 file |
| script | 300 preferred | — | 447 lines at p90 | 44 files |

Scripts are "300 preferred" because the live p90 is 447: long scripts are the norm here, and the guide exists to pressure new builds, not to indict old ones.

## Enforcement

Linter: `python3 systems/eval-harness/validate-conventions.py [--target <path>] [--mode report|build-gate]`

- **report mode (default):** prints all findings, exits 0. Used by `workflows/skill-optimize` and the sweep.
- **build-gate mode:** used by `rigby-capability-build` against the newly built artifact. FAIL-class findings exit non-zero and block the build.

### FAIL class (fix, don't tolerate)

- Missing `<!-- system:start -->` / `<!-- system:end -->` blocks in skills, agents, and convention-bearing docs.
- Agent-specific skill missing its stub (build-gate on new builds only).
- Skill unregistered in `skills/_manifest.jsonl`.
- Description over 1024 characters.
- `input(` in a bundled script.
- Script with non-stdlib imports and no PEP 723 block.
- Step file missing frontmatter.

### WARN class (never blocks)

- Over a size guide (`size.skill_body`, `size.workflow_md`, `size.step_file`, `size.agent_file`, `size.script`).
- Description not imperative (does not start with a verb).
- No Gotchas section where error history exists for the skill (`related_skill` entries in the error log).
- Reference pointer without when-to-load phrasing.
- Missing `--help` in a bundled script.

### Exceptions

`systems/eval-harness/conventions-exceptions.json` is the only exception store. WARN-class size findings can be excused; FAIL-class rules cannot. Rigby records exceptions; David approves. The linter matches on path plus rule ID and reports a match as `acknowledged` (does not count against the WARN total). An exception whose `review_after` date has passed re-raises as WARN, so exceptions decay. The census flags exceptions that no longer apply so they can be retired.

Out of scope for size guides: `evolutions/` (point-in-time snapshots and packages).

## Wiring

- Build path (`rigby-capability-build`): hard gate — build-gate mode lint at the lint step.
- `workflows/skill-optimize`: report-mode lint only, reading the same manifest so acknowledged items are not re-reported. Its gate remains the score delta.
- Not wired to evolution packaging, git, or pre-commit hooks.
<!-- system:end -->
