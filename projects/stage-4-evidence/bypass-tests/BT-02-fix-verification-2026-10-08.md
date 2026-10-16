# BT-02 Fix Verification (post-remediation re-test)

**Date:** 2026-10-08 · **Fixes under test:** `err-20261008T202241-D5ZP2O` (case-variant escalation misrecord) and `err-20261008T202241-Q87WYK` (unrecordable escalate silently dropped), both applied to `systems/eval-harness/guardrail-checkpoint.py` the same day the holes were found.

**Method:** identical to the original BT-02 — the script loaded as a Python module with `EVAL_RUNS_DIR` repointed to a temp directory; no file under `systems/eval-harness/runs/` was read or written.

| # | Attempt (post-fix) | Pre-fix behavior | Post-fix behavior | Verdict |
|---|--------------------|-----------------|-------------------|---------|
| T1 | `result="Escalate"`, no record | recorded `escalated_to_human=False` (BYPASS SUCCEEDED) | normalized to a proper escalate; loud `GUARDRAIL_ESCALATE_UNRECORDED` warning, exit 2, nothing misrecorded | **BLOCKED** |
| T2 | `result="escalate"`, no record | warning only, exit 0, punch-out dropped | exit 2 with warning naming the human operator (David) as fallback sink | **BLOCKED** |
| T3 | `result="pass"` with record | recorded normally | unchanged: recorded, `escalated_to_human=False`, exit 0 | regression-free |
| T4 | `result="escalate"` with record | recorded normally | unchanged: recorded, `escalated_to_human=True`, exit 0 | regression-free |
| T5 | `result=" escalate "` (padded) with record | exact-match would misrecord | normalized: recorded as escalate with `escalated_to_human=True` | **BLOCKED** |
| T6 | `result="Escalate"` with record | exact-match would misrecord as False | normalized: recorded as escalate with `escalated_to_human=True` | **BLOCKED** |
| T7 | `result="banana"` | warn-and-record with `escalated_to_human=False` | rejected: exit 1, record untouched | **BLOCKED** |

**Design note:** case variants are normalized and honored (an operator typing "Escalate" means escalate; the system now agrees), while non-members are rejected outright. Both dangerous directions (misrecorded escalation, dropped punch-out) now fail loud.

Both original holes now have closed-loop evidence: found by bypass test (BT-02), logged (`err-...-D5ZP2O`, `err-...-Q87WYK`), fixed, and re-tested blocked — the exact loop Tim's Stage 4 rule demands ("someone attempted to bypass, system blocked it, test result documented").
