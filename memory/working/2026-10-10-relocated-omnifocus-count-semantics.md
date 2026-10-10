# Relocated: OmniFocus count semantics

- Origin: skills/omnifocus-data/SKILL.md, section "Counts mean open work, not rows"
- Date: 2026-10-10
- Reason: Measured transcript and debugging detail removed from the skill during the commentary cleanup; the rule stays in the skill as a 3-line summary plus Invariant 4.

## Counts mean open work, not rows

`total_uncompleted` counts real open tasks: no project-root rows, and nothing
inside an archived folder. This matters more than it sounds.

`count of (flattened tasks whose completed is false)` (the obvious
implementation, and the one this skill originally shipped) returns **258** on
this database. The honest number is **136**, and the 122-row gap is two
separate traps:

- **`flattened tasks` includes each project's root row.** 49 of them here,
  each carrying `completed: false`. The MCP's task query returns these too,
  which is why project names show up in task listings; the script subtracts
  them.
- **Archiving a folder in OmniFocus does not complete its tasks.** The 21
  projects inside the hidden `Archive` folder hold 73 tasks that stay
  `completed: false` forever. OmniFocus's own UI treats them as dropped, and
  so does the MCP.

Measured 2026-09-16: `258 = 136 open + 73 archived + 49 project roots`.

Two consequences worth knowing. A consumer that reads `total_uncompleted` as
"how much work is on my plate" was previously reading a number ~90% too high.

The second is `projects`. AppleScript's `status is active status` returns **30**
active projects; the honest answer is **27**. The three extras (`Find new
doctor`, `Build measuring board`, `Personal`) are marked active but sit inside
the archive, so they are not real targets for new work. The AppleScript path
now excludes them the same way the MCP does, because this command feeds the
project-assignment gate in `omnifocus-tasks`: a gate that offers an archived
project as a target is worse than no gate.

`inbox_uncompleted`, `flagged_uncompleted`, `overdue_uncompleted`,
`completed_today` and `due_within_7` are unaffected: no project root has a due
date or a flag, so both backends already agreed on them.
