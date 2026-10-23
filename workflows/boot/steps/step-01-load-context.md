---
status: complete
started-at: '2026-10-09T15:47:07Z'
completed-at: '2026-10-09T15:47:07Z'
---

# Step 01: Load Context

**Executed inline by Master, not as a spawned subagent** — this is the one deliberate exception in boot's dispatch model (see `workflow.md` EXECUTION section). This step's job is loading Master's own operating identity into Master's live session; a subagent can't deposit context into a session it isn't part of. Every step after this one runs as a spawned subagent.

Read in order:
1. agents/master.md
2. SYSTEM.md
3. identity/MEMORY.md
4. identity/VOICE.md
5. identity/GOALS_AND_DREAMS.md
6. identity/RESPONSIBILITIES.md
7. identity/AUTOMATION.md
8. identity/MISSION_CONTROL.md
9. agents/routing.md

Record files_loaded and missing_files in outputs.

Spawn Knox (fire-and-forget), gated on a once-daily marker:

1. Check `data/.knox-last-run`. If the file exists and its contents are today's date (YYYY-MM-DD), skip the spawn: Knox already ran today. Record `knox_spawn: skipped-already-ran-today` and continue.
2. Otherwise spawn:
```
Agent: Knox — run workflows/plaud-ingest/workflow.md. Background, don't wait.
```
3. Write today's date to `data/.knox-last-run` when spawning.

Record knox_spawn status. Dispatch then follows `workflow.md`'s EXECUTION section: spawn the dedicated calendar subagent (step-01.5, tight brief, block on it), then spawn the main boot subagent (steps 01.2 through 08).
