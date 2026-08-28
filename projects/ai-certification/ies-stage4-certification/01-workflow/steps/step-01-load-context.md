---
status: complete
started-at: "2026-08-25T16:11:15Z"
completed-at: "2026-08-25T16:12:30Z"
outputs:
  files_loaded: "[redacted for certification submission — internal business/schedule detail, not relevant to guardrail/workflow mechanism]"
  missing_files: "[redacted for certification submission — internal business/schedule detail, not relevant to guardrail/workflow mechanism]"
  knox_spawn: "[redacted for certification submission — internal business/schedule detail, not relevant to guardrail/workflow mechanism]"
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

Spawn Knox immediately (fire-and-forget):
```
Agent: Knox — run workflows/plaud-ingest/workflow.md. Background, don't wait.
```

Record knox_spawn status. Continue to step-01.5.
