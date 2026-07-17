---
status: complete
started-at: "2026-07-17T09:15:48-05:00"
completed-at: "2026-07-17T09:20:00-05:00"
outputs:
  files_loaded: [SYSTEM.md, identity/MEMORY.md, identity/VOICE.md, identity/GOALS_AND_DREAMS.md, identity/RESPONSIBILITIES.md, identity/AUTOMATION.md, identity/MISSION_CONTROL.md, identity/INTEGRATIONS.md, identity/SECURITY.md]
  missing_files: []
  knox_spawn: "spawned — fire-and-forget with model: haiku, running plaud-ingest workflow in background (agent afe654b5bb6f5e1fd)"
---

<!-- system:start -->
# Step 01: Load Context

## MANDATORY EXECUTION RULES

1. You MUST read SYSTEM.md fully before proceeding. No boot without the operating manual.
2. You MUST read all 6 identity files listed below. No skipping, no assuming from memory.
3. Reading is sequential — complete each file before moving to the next.
4. If a file is missing, note it explicitly and continue. Do NOT halt boot over a missing file.
5. Do NOT proceed to step-02 until all files have been read (or their absence noted).

---

## EXECUTION PROTOCOL

**Agent:** Master
**Input:** Project root file system
**Output:** Full operating context loaded into active session memory

---

## CONTEXT BOUNDARIES

- Read each file in full. Do not skim.
- Do not act on content from these files yet — this step is context loading only.
- Do not surface briefing content to the controller during this step.

---

## YOUR TASK

1. **Read `SYSTEM.md`** — the full operating manual, file map, and conventions for IES.

2. **Read identity files in order:**
   1. `identity/MEMORY.md` — who David is, what he's built, personal history and context
   2. `identity/VOICE.md` — Jarvis personality configuration, communication style
   3. `identity/GOALS_AND_DREAMS.md` — vision, long-term objectives, Lifebook connection
   4. `identity/RESPONSIBILITIES.md` — role, accountabilities, key people, reporting structure
   5. `identity/AUTOMATION.md` — standing permissions, trust tiers, automation rules
   6. `identity/MISSION_CONTROL.md` — mission framing, strategic context, north star

3. **For each file read:** Confirm internally that the file was read. If a file is missing or unreadable, record the failure in outputs:
   ```yaml
   outputs:
     missing_files: [identity/VOICE.md]
     files_loaded: [SYSTEM.md, identity/MEMORY.md, ...]
   ```

4. **Spawn Knox immediately (fire-and-forget) — NON-SKIPPABLE:**

   This step is mandatory. There is no environment, mode, or tool-availability excuse that permits skipping it. If you are tempted to skip it, that is a protocol violation — log it and do it anyway.

   Immediately after reading identity files, spawn Knox as a background Agent using the Agent tool:

   > "Knox — run `workflows/plaud-ingest/workflow.md` in full. Read the workflow, run the STATE CHECK, and execute all steps as written. This is a background task — do not wait for confirmation before starting."

   Record the spawn in outputs:
   ```yaml
   outputs:
     knox_spawn: spawned — fire-and-forget
   ```
   Do NOT wait for Knox. Continue to the next step immediately.

   **If the Agent tool is unavailable:** Record `knox_spawn: failed — Agent tool unavailable` in outputs, surface it explicitly in the boot briefing, and offer to run Plaud ingest manually as an alternative. This is the ONLY valid reason to not spawn Knox — and it still requires surfacing to David, not silent skipping.

5. **Update step frontmatter:** Set `status: complete` and `completed-at` with current timestamp.

6. **Update state.yaml:** Set `current-step: step-01.2-unified-data-pull.md` (chain to consolidated data pull).

---

## SUCCESS METRICS

- SYSTEM.md read in full
- All 6 identity files read (or absences explicitly noted)
- No file silently skipped
- Knox spawned as a background Agent immediately after identity files are read
- Outputs recorded in step frontmatter

## FAILURE MODES

| Failure | Action |
|---------|--------|
| SYSTEM.md missing | Note the failure. Proceed from memory of system structure. Flag prominently in boot output. |
| One or more identity files missing | Note each missing file by name. Continue with remaining files. Surface missing files in the boot briefing. |
| File unreadable (permissions error) | Log as failed — [reason]. Treat same as missing. |
| Knox NOT spawned (any reason other than Agent tool unavailable) | This is a protocol violation. Log immediately to error-tracking. Do not rationalize. Do not blame the environment. Spawn Knox now. |
| Agent tool unavailable | Record failure in outputs. Surface in boot briefing. Offer to run Plaud ingest manually. This is the only acceptable reason for Knox not running. |

---

## NEXT STEP

Read fully and follow: `step-01.5-unified-calendar-pull.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
