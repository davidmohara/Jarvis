---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
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

4. **Update step frontmatter:** Set `status: complete` and `completed-at` with current timestamp.

5. **Update state.yaml:** Set `current-step: step-02-gather-data.md`.

---

## SUCCESS METRICS

- SYSTEM.md read in full
- All 6 identity files read (or absences explicitly noted)
- No file silently skipped
- Outputs recorded in step frontmatter

## FAILURE MODES

| Failure | Action |
|---------|--------|
| SYSTEM.md missing | Note the failure. Proceed from memory of system structure. Flag prominently in boot output. |
| One or more identity files missing | Note each missing file by name. Continue with remaining files. Surface missing files in the boot briefing. |
| File unreadable (permissions error) | Log as failed — [reason]. Treat same as missing. |

---

## NEXT STEP

Read fully and follow: `step-02-gather-data.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
