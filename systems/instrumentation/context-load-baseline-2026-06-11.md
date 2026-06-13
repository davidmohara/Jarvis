---
type: instrumentation
subject: Cold-load context size baseline
date: 2026-06-11
purpose: Before/after measurement for SYSTEM.md reduction (boot section, operations section, task management layer, knowledge layer, OmniFocus integration, workflow/step conventions, model routing, file map)
---

# Context Load Baseline — 2026-06-11

## Cold-Load Files (read every session)

| File | Lines | Bytes |
|------|-------|-------|
| SYSTEM.md | 1,517 | 70,252 |
| agents/master.md | 801 | 53,197 |
| CLAUDE.md | 61 | 3,461 |
| identity/AUTOMATION.md | 58 | 3,163 |
| identity/CONTENT-VOICE.md | 95 | 10,031 |
| identity/GOALS_AND_DREAMS.md | 67 | 5,383 |
| identity/INTEGRATIONS.md | 91 | 5,266 |
| identity/MEMORY.md | 198 | 11,995 |
| identity/MISSION_CONTROL.md | 66 | 2,589 |
| identity/RESPONSIBILITIES.md | 67 | 2,175 |
| identity/SECURITY.md | 28 | 1,703 |
| identity/VOICE.md | 60 | 3,573 |
| identity/writing-rules.md | 33 | 2,128 |
| **TOTAL** | **3,142** | **174,916** |

## SYSTEM.md Section Breakdown (targeted for removal/extraction)

| Section | Lines | Action |
|---------|-------|--------|
| File Map | 68 | Trim to key dirs, rest → reference/ |
| Boot section | 112 | Delete — superseded by workflows/boot/ |
| Operations section | 421 | Delete — superseded by workflows + skills |
| Task Management Layer | 120 | Delete — describes retired file-based task architecture |
| Knowledge Layer | 210 | Extract → reference/knowledge-layer.md |
| Workflow/Step conventions | 49 | Extract → reference/workflow-conventions.md |
| Model Routing | 54 | Spawn rule stays; defaults + guidance → reference/model-routing.md |
| OmniFocus Integration | 58 | Extract → skills/omnifocus-tasks/SKILL.md |
| **Total targeted** | **1,092** | |

## Notes

- model routing: spawn rule (system block) stays in SYSTEM.md — must fire before any Agent call. Agent defaults table and step-level guidance move to reference/.
- File Map: keep ~10 lines of key directories inline, move full tree to reference/file-map.md
- Jarvis Operating Rules personal block (~80 lines): KEEP — session-critical behavioral rules with logged error history
- Skill Loading Protocol (~40 lines): KEEP — hidden .claude/skills/ warning has 3+ logged violations
- Connector Capability Resolution (~30 lines, system block): KEEP — agents need this at runtime
- General Conventions, Output Naming, Shutdown Cleanup, Appendix: KEEP

## After Snapshot

| File | Lines | Bytes |
|------|-------|-------|
| SYSTEM.md | 506 | 27,102 |
| agents/master.md | 801 | 53,197 |
| CLAUDE.md | 61 | 3,461 |
| identity/* (unchanged) | 763 | 47,806 |
| **TOTAL** | **2,131** | **131,566** |

## Actual Savings

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| SYSTEM.md lines | 1,517 | 506 | **-1,011 (-67%)** |
| SYSTEM.md bytes | 70,252 | 27,102 | **-43,150 (-61%)** |
| Total cold-load lines | 3,142 | 2,131 | **-1,011 (-32%)** |
| Total cold-load bytes | 174,916 | 131,766 | **-43,150 (-25%)** |

## Extracted to reference/ (lazy-load only)

| File | Lines | Bytes |
|------|-------|-------|
| reference/file-map.md | 73 | 5,565 |
| reference/knowledge-layer.md | 209 | 8,738 |
| reference/workflow-conventions.md | 50 | 2,161 |
| reference/model-routing.md | 25 | 1,155 |
