---
status: complete
started-at: "2026-08-23T12:15:00-05:00"
completed-at: "2026-08-23T12:16:00-05:00"
outputs:
  files_loaded: 9
  missing_files: 0
  knox_spawn: "fire-and-forget, background task"
---

# Step 01: Load Context

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
