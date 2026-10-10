---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 07: Adversarial Verification - Eval-Record Analysis Claims vs the Records

## EXECUTION PROTOCOL

**Agent:** Rigby, spawned by the coordinator, never executed inline. Rigby spawns Ralph.
**Input:** Step 01-06 outputs, `workflows/system-eval/state.yaml`, `systems/eval-harness/runs/*.json`, the analysis report in `systems/eval-harness/grading/`
**Output:** Ralph's verdict table; an `adversarial-verification` guardrail result recorded; verdict summary written to state.yaml

## PARAMETERS

- Verification workflow: `workflows/system-eval-verification/workflow.md`
- Lens: eval-record analysis claims vs the records themselves (counts, grades, findings traced to files)
- Manifest:
  - step-outputs: `workflows/system-eval/steps/step-0{1,2,3,4,5,6}-*.md` frontmatter outputs
  - state: `workflows/system-eval/state.yaml`
  - eval-records-dir: `systems/eval-harness/runs/`
  - analysis-report: `<report_path from state.yaml accumulated-context.analysis>`
  - run-date: `<YYYY-MM-DD>`
- Ralph task: Cross-check this run's grades, assertion counts, and analysis findings against the eval records themselves and return your verdict table.
- Guardrail call: `python3 systems/eval-harness/guardrail-checkpoint.py system-eval adversarial-verification step-06-dashboard <pass|flag|escalate> "<one-line reason>"`
- Escalate triggers: a finding the records do not support, a grade with no evidentiary basis, or a self-grading violation

## YOUR TASK

Read and follow `reference/adversarial-verify-protocol.md` in full, then apply the parameters above.

Workflow-specific notes:
- This step runs after step-06's dashboard regeneration and record closure (terminal verification).
- On `escalate`: system-eval is fully autonomous with no controller approval gate, but an escalation overrides that. Set `state.yaml` to `aborted` with a note naming the specific claim(s) at issue, and surface it in the closing summary the next time a controller session reviews the dashboard.
- On `pass` or `flag`: update this step's frontmatter and deliver the one-line verification result in the closing summary (`state.yaml` was already set complete by step-06; this step does not re-open it).

---

## NEXT STEP

End of run. system-eval is complete once the adversarial verdict is recorded.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
