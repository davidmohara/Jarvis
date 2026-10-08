---
agent: jarvis
prompt-definition: agents/master.md
artifact-date: 2026-10-08
status: draft
---

# Stage 3 Artifact: Jarvis (Master / Coordinator)

Jarvis is the Master agent itself, not a separate agent. It is the always-on
orchestrator: the default interface the controller (David, the human operator)
talks to, and the router that dispatches work to specialist agents. Eval records
carry this agent under two labels, `master` and `jarvis`; both are the same
identity and are reported together below.

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

Mined from `systems/eval-harness/runs/*.json` on 2026-10-08. Repro:

```
python3 -c "import json,glob;r=[json.load(open(f)) for f in glob.glob('systems/eval-harness/runs/*.json')];print(len([d for d in r if d.get('agent') in ('master','jarvis')]))"
```

- **Total records: 113** (two labels: `master` 53, `jarvis` 60).
- **`master` status distribution (53):** success 35, aborted 8, complete 2,
  incomplete 2, failure 3, partial 2, in-progress 1.
- **`jarvis` status distribution (60):** success 54, aborted 6. Workflows under
  the `jarvis` label: dream-cycle 52, git 7, remarkable-upload 1.
- **Structural assertions:** master 102/117 passed (87.2%) across 53 records;
  jarvis 76/158 passed (48.1%) across 60 records. Combined 178/275 = 64.7%.
  (Note: the `jarvis`-labelled dream-cycle runs carry many assertions per run,
  which pulls the combined rate down.)
- **Tier 3 grades:** master 9 graded (A 2, B 3, D 3, F 1) = 55.6% grade-pass
  (A/B); jarvis 4 graded (A 2, B 2) = 100% grade-pass. Combined 13 graded,
  9 grade-pass = 69.2%.
- **Assertion trend (master label):** 2026-08 68% (n=15) to 2026-09 94% (n=31)
  to 2026-10 90% (n=4). See Iteration History.
- **Error log:** 167 entries tagged `master` (72 with an applied systemic fix,
  52 proposed), 86 tagged `jarvis` (50 applied, 21 proposed).

**Honesty note:** J1 (boot success) is measured directly and passes. J2 is
partially measured: two routing/process-skip violations are on record
(`err-20260611T113806-g0pfoq`, `err-20260716T220729-FNAAP8`) and both are cited
by the Stage 5 report. J3/J4 use harness assertions and Tier 3 grades as proxies,
not the named criteria. A fresh instrumented boot run is required to score J2
against its stated threshold. The two-label split (`master` vs `jarvis`) is a
data-quality issue that should be normalized before grading.

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
