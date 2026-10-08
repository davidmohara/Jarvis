# Stage 5 Submission Evidence Index

**Created:** 2026-10-08 (Phase 6 prep) · **Use:** pre-submission self-audit. Walk Tim's 9 findings in his own vocabulary and confirm each row's evidence exists before the bundle ships. Status column updated as the data window closes.

| # | Tim's finding (his vocabulary) | Evidence artifact | Status |
|---|-------------------------------|-------------------|--------|
| 1 | Guardrails incomplete, not all adversarial | Phase 4A wiring: deterministic per-step verifiers (`workflows/<wf>/verify/step-*.py` dispatched by step-complete.py) at every transition of all 4 candidates, boot step-06.5 now machine-checked (freshness + briefing currency + credential scan + checkpoint-presence), Ralph-spawned adversarial verification with lens checklists for all 4 (`workflows/*-verification/`, guardrail `adversarial-verification`, assertions boot-004/morning-008/daily-007/plaud-002) | Complete |
| 2 | Punch-out mechanisms not bypass-tested | `projects/stage-4-evidence/bypass-tests/` (BT-01..BT-04 matrix + logs; BT-02 found 2 real holes, both fixed same day with closed-loop re-test evidence in `BT-02-fix-verification-2026-10-08.md`) | Complete |
| 3 | No end-to-end success rate for any workflow | `projects/stage-4-evidence/success-rate-baseline-2026-10-08.{md,csv}` (daily-review 98%, morning-briefing 94%, plaud-ingest ~89% pending no-op verification, boot 75%); final numbers from the instrumented data window | Baseline done; final numbers pending data window |
| 4 | Per-step input tokens, output tokens, cost missing | `systems/eval-harness/step_audit.py` + `export-step-audit.py` (CSV/JSON, per-step model/tokens/cost/owning_agent/token_source); 3-5 instrumented runs per candidate to export via `export-step-audit.py --runs <ids> --out systems/eval-harness/audit-exports` | Instrumentation done; instrumented runs pending data window |
| 5 | No Stage 3 artifacts for component agents | `systems/eval-harness/stage3/<agent>.md` x11 (prompt definition, 4 criteria each, measured results with repro commands, iteration histories) | Drafts complete; threshold gaps need fresh measured runs in data window |
| 6 | Coordinator purity violations | Phase 1 refactor (42 files, spawn-first Hard Stops, all steps spawn named agents) + remediation log entries `err-20261008T195835-EW45PB`, `err-20261008T195836-0BTS1J`, `err-20261008T195836-NN86G2`, `err-20261008T195836-X3VV9S` + post-refactor prompt summary in `systems/eval-harness/stage3/jarvis.md` | Complete. Residual: personal-block exit instruction (David's edit) |
| 7 | No formal agent manifest / scoping | `agents/manifest.md` (11 agents, roles, owned steps, boundaries, conflict resolution; David documented as human operator) | Complete |
| 8 | Adversarial review isolation undocumented | `agents/adversarial-isolation.md` (isolation mechanics, Ralph coverage, catches evidence plan) | Complete; catch examples accumulate in data window |
| 9 | No CHANGELOG, version tags, release history | `CHANGELOG.md` (v0.1.0 → v1.5.0 from 1,063 commits) + annotated tags v0.1.0, v0.5.0, v1.0.0, v1.5.0; v2.0.0 tagged at resubmission | Complete |

## Cover note points (Harper, Phase 6)

1. Candidate set rationalized to 4 used workflows; weekly-review dropped (0 eval records ever, never-started state). Usage data in `projects/workflow-rationalization-memo-2026-10-08.md`.
2. Naming corrections to the report: David is the human operator, not an agent; Jarvis is the Master agent itself; Ralph is an agent (boot verification, `agents/ralph.md` exists first-class).
3. The report's cited "manual model invocation" phrase lived in `workflows/error-improvement/workflow.md`, not in a candidate workflow; fixed there and candidates were rewritten spawn-first regardless.
4. Data honesty levers: `owning_agent` attribution (fixes the `general-purpose` label pollution the report's file-list analysis would have hit), `token_source` (windowed vs lenient_fallback per-step token attribution), success-rate tiers (strict vs completed-with-degradation, session-exit aborts excluded and counted separately).
5. Enforcement honesty (from BT-03/BT-04): at BT-03/BT-04 time the coordinator-purity and gated-skill controls were procedural only. **Hardened 2026-10-08:** coordinator-direct git writes now have technical enforcement — the PreToolUse git-gate transparently redirects raw git writes onto the authorized `ies-git` wrapper (which enforces the git skill's rules mechanically and audits every operation and refusal; evidence: `projects/stage-4-evidence/bypass-tests/BT-05-git-redirect-verification-2026-10-08.md`). Remaining procedural-only: direct domain-data inspection and inline specialist execution (spawn-first rules + per-step verifiers as the net); escape via `sh -c`/subprocess remains possible and is disclosed.
6. The four new `workflows/*-verification/` directories (morning-briefing, daily-review, plaud-ingest, shutdown-cleanup) are Ralph's verification sub-workflows (siblings of the pre-existing `boot-verification/`), not new candidate workflows; the 4-candidate rationalization still holds. shutdown-cleanup was additionally brought to the full candidate instrumentation standard on 2026-10-08 (verifiers for all 5 steps, guardrail checkpoint, adversarial verification, `git status` forbidden → lock-free lists, commit routed through the ies-git wrapper) even though it is not a Stage 4 candidate, because it is the session-exit workflow and David directed compliance.
7. Guardrail timing honesty: per-step verifiers fire at sub-agent completion (iterating completed steps), not literally mid-run between step N and N+1; the checkpoints that must gate mid-run (boot 06.5, morning-briefing 03b, daily-review 03b, and the new verification steps) do call guardrail-checkpoint.py in-step, which is the mid-run blocking path.

## Remaining to ship (data window, ~10 days)

- 3-5 instrumented runs per candidate workflow with `token_source=windowed` per-step audit trails (export to `systems/eval-harness/audit-exports/`).
- 10+ run success-rate recompute restricted to instrumented runs, with unexplained-abort verification (boot 7, plaud-ingest 11).
- Fresh measured runs to close Stage 3 threshold gaps (chief, harper, knox, rigby, jarvis J2; plus first-ever instrumentation for ralph, galen, shep, quinn, sterling, chase).
- Phase 4A adversarial catch examples recorded structurally.
- v2.0.0 tag + resubmission delivery to Tim via Teams.
