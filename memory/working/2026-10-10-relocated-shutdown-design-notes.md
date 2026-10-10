# Relocated: shutdown-cleanup dispatch-model design notes

Origin: `workflows/shutdown-cleanup/workflow.md` EXECUTION section (removed 2026-10-10 during Phase A commentary cleanup; in-file version reduced to the one-sentence dispatch instruction).
Date relocated: 2026-10-10.
Reason: pasted design-review argument and boot-constraint reasoning, not instructional content. The operative rule (every step runs as a spawned sub-agent, no inline exception) remains in-file.

---

**Boot-constraint reasoning (was workflow.md ~78):** Checked step-01 (`step-01-purge-artifacts.md`) specifically against boot's constraint (does it load `agents/master.md`/`SYSTEM.md`/identity files into Master's *own* live session?): no — it purges temp-file patterns and runs the IES root-check, neither of which requires anything to land in Master's live context. By the time shutdown-cleanup runs, Master's own identity was already loaded once, earlier in the session, at boot. None of the 4 steps here have that constraint, so unlike boot there is no reason for any of them to run inline.

**Eval-record hook rationale (was workflow.md ~85):** This gives shutdown-cleanup a real `SubagentStart`/`SubagentStop` pair, same as boot. `.claude/hooks/eval-turn-start.py` opens the eval record independently of this (on `UserPromptSubmit`, matched against `agents/master.md`'s real trigger phrases — "exit", "log off", "end session" — not the words "shutdown" or "cleanup", which never actually appear in how this workflow gets invoked); `.claude/hooks/eval-turn-stop.py` closes it once `state.yaml` reaches `status: complete`.
