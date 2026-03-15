# IES Evolution History

This file logs all system evolutions applied to this IES installation. Each entry records what changed, when, and what personal blocks were preserved.

---

## Format

Each evolution entry follows this structure:

```
## Evolution Name (version) — Applied YYYY-MM-DD

**Evolution ID:** unique-id
**Applied:** ISO timestamp
**Snapshot:** snapshot-id
**Applied by:** user or system

### Files Changed
- List of files modified with action types

### Conflicts
- Any conflicts encountered and how resolved

### Personal Blocks Preserved
- Files with personal blocks and where they were preserved

### Status
- Success or warnings/errors
```

---

## Quinn Strategy Builder — Applied 2026-03-01

**Type:** System evolution
**Applied by:** Manual (David + Jarvis session)

### Summary

Added strategy-building capability to Quinn agent. Fills the creation-phase gap in Quinn's portfolio — previously all Quinn tasks (rocks, alignment, initiatives, leadership-prep) were tracking/reviewing. Strategy Builder is the first generative task: coaches users through rigorous strategy development using the kernel methodology (diagnosis → guiding policy → coherent actions).

### Files Changed

- `skills/quinn-strategy/SKILL.md` — added (new skill, 200 lines)
- `skills/quinn-strategy/references/strategy-framework.md` — added (extended reference, 230+ lines)
- `agents/quinn.md` — merged (Strategy Builder added to Capabilities metadata and Task Portfolio in system block; personal blocks preserved)
- `.claude/skills/quinn-strategy/SKILL.md` — added (shared skill registration)

### Conflicts

None.

### Personal Blocks Preserved

- `agents/quinn.md`: All existing personal blocks preserved (tool bindings, quarterly objectives reference)
- `skills/quinn-strategy/SKILL.md`: Personal blocks contain concrete tool bindings only (M365 MCP, Obsidian, OmniFocus, etc.)
- `.claude/skills/quinn-strategy/SKILL.md`: Personal blocks contain concrete tool bindings only

### Source Material

- *Good Strategy Bad Strategy* by Richard Rumelt (PDF summary)
- Lenny's Newsletter podcast episode with Rumelt (1:49:16 transcript)
- Lenny's Newsletter article on Rumelt's strategy framework

### Notes

- Methodology is Rumelt-derived but skill is branded as generic strategy building — not Rumelt-specific
- "Action agenda" framing used throughout instead of "strategy" — per Rumelt's own recommendation
- Future consideration: workflow version combining strategy building with RAPID decision framework

---

## Error Tracking System — Applied 2026-03-15

**Evolution ID:** 5b830712-192d-42f0-bd1e-65c083ad4278
**Type:** System evolution
**Applied:** 2026-03-15T00:00:00Z
**Applied by:** Manual (David + Jarvis session)

### Summary

Silent error and correction tracking system with pattern analysis and tiered fix proposals. Captures explicit corrections from the executive and self-detected errors during agent execution. Logs are invisible during normal operations; patterns surface through existing review cadences (daily count via Chief, full analysis via Quinn weekly review) and proactive threshold alerting (3+ occurrences). Split ownership: Master captures, Rigby analyzes, Chief/Quinn surface.

### Files Changed

- `systems/error-tracking/error-log.json` — added (structured log with entries array and pattern tracking)
- `systems/error-tracking/schema.md` — added (10 error categories, 10 failure modes, 3 severity levels, pattern structure)
- `.claude/skills/rigby-error-analysis/SKILL.md` — added (pattern detection, statistics, tiered fix proposals)
- `agents/master.md` — merged (Error Capture Protocol added to system block; error analysis routing added to Agent Routing table)
- `agents/rigby.md` — merged (Error Analysis added to Task Portfolio, Data Requirements, and Handoff Behavior in system blocks)
- `SYSTEM.md` — merged (Error Accountability expanded with logging step; Error Tracking System reference section added)
- `workflows/daily-review/steps/step-03-update-system.md` — merged (error count added to System State template; error tracking pull step added)
- `.claude/skills/quinn-weekly-review/SKILL.md` — merged (System Improvement Review step added; System Health section added to weekly report)

### Conflicts

None.

### Personal Blocks Preserved

- `agents/master.md`: All existing personal blocks preserved (Jarvis voice overlay, bridge operations, boot/exit additions, output naming, purge patterns)
- `agents/rigby.md`: All existing personal blocks preserved (release watch task, architecture note)
- `.claude/skills/quinn-weekly-review/SKILL.md`: Personal calibration block preserved

### Architecture Decisions

- **Split ownership over new agent**: Master captures because it sees all interactions. Rigby analyzes because it owns system evolution infrastructure. No new agent needed.
- **Tiered fix proposals**: Tier 1 (auto-propose) for clear-cut fixes like repeated tool misuse. Tier 2 (data-only) for ambiguous patterns requiring executive judgment.
- **Threshold alerting at 3**: Balances signal vs. noise. One mistake is a one-off. Two is a coincidence. Three is a pattern.
- **System classification**: Core error categories, failure modes, and analysis logic are framework-agnostic. Any IES instance benefits from self-improvement tracking.

### Notes

- Error log starts empty — entries accumulate as sessions run
- The `quinn-weekly-review` integration is classified as personal (skill is personal) even though the error tracking system itself is system-classified
- Future consideration: training module generation from recurring patterns (Rigby → training system handoff exists but no auto-generation yet)
