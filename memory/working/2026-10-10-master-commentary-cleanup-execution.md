---
title: Commentary cleanup, all phases executed
agent: master
date: 2026-10-10
session: 2026-10-10 commentary cleanup audit + full execution
tags: [cleanup, phases-a-f, eval-harness, hooks]
duration_minutes: 180
importance: 9
session_id: "2026-10-10-commentary-audit"
agent-source: master
---

David directed the full commentary cleanup (audit was same-day, plan approved with 4 decisions). All phases executed, committed, and pushed to origin/main same day.

## Phase ledger (commits)

1. Content family fix (decision 2, all three content workflows live): content-pipeline rewritten as gated orchestrator; committed via the concurrent Rigby session's sweeps plus e24d73f7 (ghost script deletion).
2. Phase A, residue and dead weight (800c6c2e): 168 files, ~1,180 net lines; 21 relocation files under memory/working/; galen real health values placeholder-ized; broken references fixed (evolution-deployment, comp-tracker).
3. Phase F, hook-based eval capture (cccbcddc): 246 files, ~7,250 stamped lines deleted (SKILL COMPLETE / GRADE THIS RUN / STEP COMPLETION TRACKING); new machinery: systems/eval-harness/skill_capture.py + .claude/hooks/eval-skill-invoke.py (PostToolUse on Skill tool) + finalize in eval-turn-stop.py + settings.json matcher; tests in .claude/hooks/tests/test_skill_capture.py; add-skill-signals.py and add-step-tracking.py converted to read-only guard validators. Skill-run capture is live from the NEXT session start (hooks load at session start).
4. Phase B, boilerplate centralization (35b54c86): 100 files, ~2,060 net lines; new shared protocols reference/state-check-protocol.md, adversarial-verify-protocol.md, plan-only-mode-protocol.md, buyer-persona-sources.md; Activation protocol and error-logging consolidated into agents/conventions.md.
5. Phase C+D (f5058fb3): personal-block cleanup (~330 net lines, reference/omnifocus-binding.md + structured-reasoning-binding.md) and the leak-closure rules (agents/conventions.md "Instructional File Hygiene" section; capability-build template now teaches the clean pattern; SYSTEM.md:88 amended to rule-not-story).

Total: ~11,900 lines removed from instructional files this session. Boot-recurring set (CLAUDE.md, SYSTEM.md, agents/, identity/) reduced ~300 lines; every skill invocation no longer loads ~35 lines of stamped tail; every workflow run no longer loads duplicated STATE CHECK / working-memory / adversarial scaffolds.

## Verification record

Marker balance: 0 imbalances across skills/ (64 files), .claude/skills/ (112), workflows (74 workflow.md + 295 steps), agents, identity. Guard validators: PASS (176 skill files, 295 step files). Capture-chain tests: PASS. Residual err-narrative scan: clean. Frontmatter: intact everywhere (5 pre-existing no-frontmatter skills unchanged). Skill registry: fully live with correct descriptions.

## Open items (David's call or follow-up)

1. Frontmatter state fields (status/started-at/completed-at) remain in step files; step-complete.py reads them. Full migration to state.yaml belongs with the concurrent eval-harness instrumentation work (deliberately not done to avoid collision).
2. eval-signal-write skill is superseded by hooks; retire it (delete or stub) when David confirms.
3. Three verifier-side step-01-verify.md scaffolds (content-*-verification) are a distinct pattern from the caller-side adversarial-verify protocol; left as-is, candidate for a verifier-protocol reference.
4. Departed-EA references (Ilse Perez) in identity/INTEGRATIONS.md and AUTOMATION.md; personnel data, David to confirm replacement.
5. Concurrent Rigby session commits to this repo; its junk-messageed HEAD commit 4e51ed5b ("--amend") is cosmetic damage in history (left alone deliberately).
6. The three content-*-verification workflows are entirely personal-wrapped (no system blocks): evolution-invisible. Structural, flagged.
