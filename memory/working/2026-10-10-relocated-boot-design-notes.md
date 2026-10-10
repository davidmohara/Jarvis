# Relocated content: boot eval-record mechanics

- Origin: workflows/boot/workflow.md (dispatch section, ~line 46)
- Date: 2026-10-10
- Reason: Phase A cleanup. Design rationale for how boot's dispatch pattern interacts with the eval harness is not an instruction; it belongs with the harness schema, not in the boot workflow file. Phase F (harness decoupling) supersedes this mechanism anyway.

## Original text

This dispatch pattern is what gives boot a real `SubagentStart`/`SubagentStop` pair to hang an eval record on. It is not, on its own, what makes the eval record exist. That is `.claude/hooks/eval-turn-start.py` (opens the record on `UserPromptSubmit`, independent of whether steps run inline or spawned) and `.claude/hooks/eval-turn-stop.py` (closes it out on `Stop` once `state.yaml` reaches `status: complete`). Both mechanisms are complementary: the turn-level hooks guarantee an eval record exists at all; running steps 2-12 as a real subagent additionally gives per-subagent model/token/cost data in the record's `subagents[]` array. See `systems/eval-harness/schema.md` for the full field reference.
