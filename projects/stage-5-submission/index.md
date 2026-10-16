# Stage 5 Submission Evidence Index

**Created:** 2026-10-08 (Phase 6 prep) · **Use:** pre-submission self-audit. Walk Tim's 9 findings in his own vocabulary and confirm each row's evidence exists before the bundle ships. Status column updated as the data window closes.

| # | Tim's finding (his vocabulary) | Evidence artifact | Status |
|---|-------------------------------|-------------------|--------|
| 1 | Guardrails incomplete, not all adversarial | Phase 4A wiring: deterministic per-step verifiers (`workflows/<wf>/verify/step-*.py` dispatched by step-complete.py) at every transition of all 4 candidates, boot step-06.5 now machine-checked (freshness + briefing currency + credential scan + checkpoint-presence), Ralph-spawned adversarial verification with lens checklists for all 4 (`workflows/*-verification/`, guardrail `adversarial-verification`, assertions boot-004/morning-008/daily-007/plaud-002). Real catches recorded structurally: `projects/stage-4-evidence/adversarial-catches/` (5 entries as of 2026-10-16) | Complete |
| 2 | Punch-out mechanisms not bypass-tested | `projects/stage-4-evidence/bypass-tests/` (BT-01..BT-04 matrix + logs; BT-02 found 2 real holes, both fixed same day with closed-loop re-test evidence in `BT-02-fix-verification-2026-10-08.md`) | Complete |
| 3 | No end-to-end success rate for any workflow | `projects/stage-4-evidence/success-rate-baseline-2026-10-08.{md,csv}` (daily-review 98%, morning-briefing 94%, plaud-ingest ~89% pending no-op verification, boot 75%); final numbers from the instrumented data window | Baseline done; final numbers pending data window |
| 4 | Per-step input tokens, output tokens, cost missing | `systems/eval-harness/step_audit.py` + `export-step-audit.py` (CSV/JSON, per-step model/tokens/cost/owning_agent/token_source); 3-5 instrumented runs per candidate to export via `export-step-audit.py --runs <ids> --out systems/eval-harness/audit-exports` | Instrumentation done; instrumented runs pending data window |
| 5 | No Stage 3 artifacts for component agents | `systems/eval-harness/stage3/<agent>.md` x11 (prompt definition, 4 criteria each, attribution-aware measured results with repro commands, iteration histories). Full plan: `stage3-compliance-plan.md` (Phases 0-3 executed 2026-10-16: attribution layer, assertion wiring for 16 previously unmeasured criteria, 7 measured runs, recompute). Final measured verdicts below | Attribution-aware recompute done; final graded-run window closes 2026-10-21 |

**Stage 3 verdicts (2026-10-16, attribution-aware recompute; thresholds untouched):**

| Agent | Records (after attribution recovery) | Strict success | Criteria verdict |
|---|---|---|---|
| master | 151 | 69.8% | J1-J4 below bars; J2 routing sentinel (boot-009) now active |
| chief | 97 | 67.0% | C4 52.4% overall, 66.7% excluding scheduled runs — below 80% both ways |
| chase | 12 | 33.3% | H1-H3 now have assertions; graded runs accumulating |
| harper | 23 | 88.9% | P3 69.4%, P4 71.4% — below bars |
| knox | 101 | 62.1% | K3 73.9% below 90%; K4 flipped to 74.2% below 80% after 15 recovered graded records surfaced |
| quinn | 8 | 100% (n=8) | First runs landed 2026-10-16 |
| ralph | 16 | 50.0% | First attribution 2026-10-16; assertions wired, graded runs pending |
| rigby | 86 | 81.6% | R3 86.5% below 90%; R4 70.0% below 80% |
| shep | 12 | 66.7% | First assertion-bearing runs 2026-10-16 |
| sterling | 7 | 75.0% | First assertion-bearing runs 2026-10-16 |
| galen | 5 | 100% (n=5) | First records ever 2026-10-16 (attribution fix unblocked) |

144 historically unattributed records recovered at read time via transcript mining; historical records never rewritten. Remaining failures are genuine quality measurements, not harness artifacts — they need the instrumented run window (through 2026-10-21) and David's threshold calls, not code.
| 6 | Coordinator purity violations | Phase 1 refactor (42 files, spawn-first Hard Stops, all steps spawn named agents) + remediation log entries `err-20261008T195835-EW45PB`, `err-20261008T195836-0BTS1J`, `err-20261008T195836-NN86G2`, `err-20261008T195836-X3VV9S` + post-refactor prompt summary in `systems/eval-harness/stage3/master.md` | Complete. Residual: personal-block exit instruction (David's edit) |
| 7 | No formal agent manifest / scoping | `agents/manifest.md` (11 agents, roles, owned steps, boundaries, conflict resolution; David documented as human operator) | Complete |
| 8 | Adversarial review isolation undocumented | `agents/adversarial-isolation.md` (isolation mechanics, Ralph coverage, catches evidence plan) + catch log `projects/stage-4-evidence/adversarial-catches/` (5 real catches recorded, 2026-10-16) | Complete; catch log live, thin (see log README) |
| 9 | No CHANGELOG, version tags, release history | `CHANGELOG.md` (v0.1.0 → v1.5.0 from 1,063 commits) + annotated tags v0.1.0, v0.5.0, v1.0.0, v1.5.0; v2.0.0 tagged at resubmission | Complete |

## Cover note points (Harper, Phase 6)

1. Candidate set rationalized to 4 used workflows; weekly-review dropped (0 eval records ever, never-started state). Usage data in `projects/workflow-rationalization-memo-2026-10-08.md`.
2. Naming corrections to the report: David is the human operator, not an agent; Jarvis is the Master agent itself; Ralph is an agent (boot verification, `agents/ralph.md` exists first-class).
3. The report's cited "manual model invocation" phrase lived in `workflows/error-improvement/workflow.md`, not in a candidate workflow; fixed there and candidates were rewritten spawn-first regardless.
4. Data honesty levers: `owning_agent` attribution (fixes the `general-purpose` label pollution the report's file-list analysis would have hit), `token_source` (windowed vs lenient_fallback per-step token attribution), success-rate tiers (strict vs completed-with-degradation, session-exit aborts excluded and counted separately).
5. Enforcement honesty (from BT-03/BT-04): at BT-03/BT-04 time the coordinator-purity and gated-skill controls were procedural only. **Hardened 2026-10-08:** coordinator-direct git writes now have technical enforcement — the PreToolUse git-gate transparently redirects raw git writes onto the authorized `ies-git` wrapper (which enforces the git skill's rules mechanically and audits every operation and refusal; evidence: `projects/stage-4-evidence/bypass-tests/BT-05-git-redirect-verification-2026-10-08.md`). Remaining procedural-only: direct domain-data inspection and inline specialist execution (spawn-first rules + per-step verifiers as the net); escape via `sh -c`/subprocess remains possible and is disclosed.
6. The four new `workflows/*-verification/` directories (morning-briefing, daily-review, plaud-ingest, shutdown-cleanup) are Ralph's verification sub-workflows (siblings of the pre-existing `boot-verification/`), not new candidate workflows; the 4-candidate rationalization still holds. shutdown-cleanup was additionally brought to the full candidate instrumentation standard on 2026-10-08 (verifiers for all 5 steps, guardrail checkpoint, adversarial verification, `git status` forbidden → lock-free lists, commit routed through the ies-git wrapper) even though it is not a Stage 4 candidate, because it is the session-exit workflow and David directed compliance.
7. Guardrail timing honesty: per-step verifiers fire at sub-agent completion (iterating completed steps), not literally mid-run between step N and N+1; the checkpoints that must gate mid-run (boot 06.5, morning-briefing 03b, daily-review 03b, and the new verification steps) do call guardrail-checkpoint.py in-step, which is the mid-run blocking path.

## Remaining to ship (data window closes 2026-10-21)

- 3-5 instrumented runs per candidate workflow with `token_source=windowed` per-step audit trails (export to `systems/eval-harness/audit-exports/`).
- 10+ run success-rate recompute restricted to instrumented runs, with unexplained-abort verification (boot 19, plaud-ingest 11).
- Fresh measured runs to close Stage 3 threshold gaps (chief, harper, knox, rigby, master J2; plus first-ever instrumentation for ralph, galen, shep, quinn, sterling, chase).
- Phase 4A adversarial catch examples recorded structurally.
- v2.0.0 tag + resubmission delivery to Tim via Teams.

## Success rates — apples-to-apples recompute (2026-10-15)

Two methods applied consistently across both periods. "Strict" = status `success` or `complete` only. "Mech" = strict + `partial` (ran to completion with degraded results), session-exit aborts excluded from denominator for mech. The Oct 8 baselines (94%/98%/89%) used the mech method; both are shown here for transparency.

| Workflow | Aug 2026 (recs) | Aug strict | Aug mech | Oct 8-15 (recs) | Oct strict | Oct mech | All-time mech |
|---|---|---|---|---|---|---|---|
| boot | 34 | 35.3% | 58.8% | 14 | 57.1% | 57.1% | 60.9% (64 recs) |
| morning-briefing | 8 | 37.5% | 87.5% | 4 | 50.0% | 100.0% | 95.7% (23 recs) |
| daily-review | 10 | 30.0% | 100.0% | 4 | 100.0% | 100.0% | 98.4% (62 recs) |
| plaud-ingest | 20 | 30.0% | 35.0% | 6 | 100.0% | 100.0% | 60.5% (38 recs) |

Session-exit aborts by period: boot Aug=13, Oct=6; plaud-ingest Aug=11, Oct=0. These are records closed by `close-open-evals.py` when a session ended before the workflow's own completion step ran — not mid-run crashes.

The prior Oct 8 figures (94%/98%/89%) aligned with the mech column for all-time records at that point; the Oct 8-15 window shows meaningful improvement post-remediation. Final submission figures will use windowed instrumented runs only.
