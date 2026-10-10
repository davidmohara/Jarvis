<!-- personal:start -->
# OmniFocus Binding

Canonical binding for the OmniFocus task-management system. Workflow steps that refer to "the task management system" or "the task management API" mean OmniFocus, and point here instead of restating this.

**Reads** go through the `omnifocus-data` skill (`skills/omnifocus-data/SKILL.md`). Do not hand-write queries.

**Writes** (create, move, assign, flag, complete) go through the `omnifocus-tasks` skill (`skills/omnifocus-tasks/SKILL.md`), which is gate-enforced on project and tag.

**Never** write raw OmniFocus AppleScript for task creation outside the `omnifocus-tasks` skill.

Pointer form used by each step:

> Reads and writes follow `reference/omnifocus-binding.md`.
<!-- personal:end -->
