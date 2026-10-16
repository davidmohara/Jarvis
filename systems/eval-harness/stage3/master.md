---
agent: master
prompt-definition: agents/master.md
artifact-date: 2026-10-08
status: draft
---

# Stage 3 Artifact: Master (Coordinator)

Master is the coordinator agent. "Jarvis" is the name of the IES system as a
whole, not an agent — eval records that carry a `jarvis` label canonicalize to
`master` for reporting (David's correction, 2026-10-16,
err-20261016T123345-KNNL1T). Master is the always-on orchestrator: the default
interface the controller (David, the human operator) talks to, and the router
that dispatches work to specialist agents. Eval records carry this agent under
two labels, `master` and `jarvis`; both are the same identity and are reported
together below as `master`.

## Prompt Definition

**Path:** `agents/master.md` (frontmatter name: `Master`; instance name `Jarvis`
lives in the personal block). Owning role: agent routing, session boot, task
capture, status dashboards, prioritization, delegation, decision frameworks,
identity-aware context.

**Summary:** Master is the coordinator layer. It reads every agent definition and
workflow purpose, boots the session by loading identity files and live data, and
routes each controller request to the right specialist without the controller
naming one. It does not specialize; it coordinates and holds the executive
function. The routing table lives in `agents/routing.md` and is loaded once at
boot.

**Refreshed 2026-10-08 (post Phase 1 coordinator-purity refactor):** the
coordinator is now formally spawn-first. `agents/master.md` and
`agents/routing.md` carry Hard Stops forbidding direct git operations (git only
via `skills/git/SKILL.md` under Rigby), direct domain-data inspection (spawn the
owning agent, e.g., Knox for plaud staging), and inline execution of specialist
tasks. Every candidate-workflow step file names its owning agent and runs as a
spawned sub-agent; the one documented inline exception is boot step-01 (context
must land in the coordinator's session). The formal agent roster and boundaries
live in `agents/manifest.md`. J2's A/B evidence (post-refactor boot with a
routing-assertion hook) is scheduled in the Phase 4 data window; both cited
violations now have remediation log entries
(`err-20261008T195836-0BTS1J`, `err-20261008T195836-NN86G2`).

## Quality Criteria

| # | Criterion | Measurable pass/fail threshold |
|---|-----------|-------------------------------|
| J1 | Boot completes with live data | Boot run writes a boot eval record with `status: success` and all mandatory boot steps recorded; pass = 100% of boot runs |
| J2 | Routing correctness (no coordinator direct-execution) | Zero routing-error or process-skip entries in the error log where the coordinator executed a specialist task itself; pass = 0 such entries per 30-day window |
| J3 | Structural assertion pass rate | Boot and coordination runs pass >= 90% of harness structural assertions |
| J4 | Tier 3 grade | Grade B or better on graded coordination runs; pass = >= 80% of graded runs |

## Measured Results

Recomputed from `systems/eval-harness/runs/*.json` on 2026-10-16 using the
attribution layer (`step_audit.resolve_record_agent` + `merge_reporting_agent`),
which merges the `master`/`jarvis` label split and recovers records whose
workflow/name resolves to a master-owned workflow. Repro:

```
python3 -c "import json,glob,sys;sys.path.insert(0,'systems/eval-harness');from step_audit import resolve_record_agent,merge_reporting_agent as M;r=[json.load(open(f)) for f in glob.glob('systems/eval-harness/runs/*.json')];print(len([d for d in r if M(resolve_record_agent(d))=='master']))"
```

- **Total records: 139** (attribution-aware). Raw labels: `master` 53, `jarvis`
  61 (both canonicalize to `master`), plus 25 whose workflow/name resolves to a
  master-owned workflow (boot, dream-cycle, git, omnifocus) while the raw label
  was something else — `general-purpose` 19, `knox` 4, `claude` 2.
- **Status distribution (139):** success 94, aborted 26, partial 9, failure 4,
  complete 3, incomplete 3. Strict success rate (success/complete) = 97/139 =
  69.8%; mech (strict + partial, session-exit aborts excluded) = 105/135 = 77.8%.
- **Structural assertions:** 243/369 passed = 65.9% across 139 records. The
  `jarvis`-labelled dream-cycle runs (59 records) carry many assertions per run
  and pull the combined rate down; on coordination runs only (excl. dream-cycle)
  the rate is 176/199 = 88.4%.
- **Tier 3 grades:** 16 graded (A 4, B 7, D 4, F 1) = 11/16 = 68.8% grade-pass
  (A/B). On coordination runs only (excl. dream-cycle): 6/11 = 54.5%.
- **Boot runs (J1):** 54 boot records — success 17, complete 3, partial 8,
  failure 4, aborted 19, incomplete 3. Strict 37.0%, mech 54.0%.
- **Assertion trend (all master records):** 2026-08 67% (n=35), 2026-09 62%
  (n=88), 2026-10 85% (n=14).
- **Error log:** 274 entries canonicalize to `master` (`master` 181 + `jarvis`
  92 + one `master/galen`), 130 with an applied systemic fix, 82 proposed.

**Honesty note:** J1 as literally written (100% of boot runs succeed) is **not
met**: boot strict success is 37.0% and mech 54.0% across 54 boot records, with
19 session-exit aborts. J2 remains partially measured: two routing/process-skip
violations are on record (`err-20260611T113806-g0pfoq`,
`err-20260716T220729-FNAAP8`) and both are cited by the Stage 5 report. J3/J4 use
harness assertions and Tier 3 grades as proxies: J3 is 65.9% combined / 88.4% on
coordination runs only (below the 90% bar), J4 is 68.8% / 54.5% (below the 80%
bar). The two-label split (`master` vs `jarvis`) is now merged in reporting, and
the attribution layer recovered 25 previously-unattributed records into the
master rollup.

## Iteration History

**Iteration 1: coordinator direct-execution of a specialist workflow.**
Baseline: `err-20260611T113806-g0pfoq` (2026-06-11, moderate, process-skip) boot
checked the plaud staging folder directly instead of spawning Knox to run
plaud-ingest; 49 transcripts left uningested. Hypothesis: the boot step lacked an
explicit "spawn Knox" instruction, so the coordinator improvised a directory
listing. Change: boot protocol required running the plaud-ingest workflow, not
just checking for files. Measured: boot runs from 2026-08 onward spawn Knox for
plaud ingest (boot step records show a Knox sub-agent spawn).

**Iteration 2: coordinator executing shutdown cleanup itself.**
Baseline: `err-20260716T220729-FNAAP8` (2026-07-16, moderate, routing-error) on
the "wrap up the day" signal the coordinator attempted git/file cleanup directly
instead of spawning Rigby for the shutdown-cleanup workflow. Hypothesis: the
routing table entry for infrastructure work was not enforced at the exit path.
Change: exit path routed to Rigby via `workflows/shutdown-cleanup/workflow.md`.
Measured: assertion pass rate on the `master` label rose from 68% (2026-08) to
94% (2026-09) and 90% (2026-10); the coordinator-purity refactor is Phase 1 and
this criterion (J2) gets its formal A/B test there.

**Iteration 3 (in flight, Phase 1).** Baseline: the Stage 5 report's three cited
coordinator-purity violations plus the `systems/ies-channel/ies-channel.py:145`
subprocess call. Hypothesis: coordinator step files contain direct-execution
paths. Change: full refactor so every step spawns a named sub-agent. Measured:
iteration evidence pending, fresh A/B run required. The run needed is a
post-Phase-1 boot with a routing-assertion hook that fails if the coordinator
executes a specialist task directly.
