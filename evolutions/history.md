# IES Evolution History

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
