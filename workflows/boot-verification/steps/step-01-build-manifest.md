---
status: complete
started-at: "2026-10-09T15:55:00Z"
completed-at: "2026-10-09T15:56:00Z"
outputs:
  manifest-tasks: 6
---

<!-- system:start -->
# Step 01: Build Manifest

## MANDATORY EXECUTION RULES

1. You MUST collect the Phase 2 completion report before proceeding. This was passed from Master as context: it contains what each Phase 2 task claimed.
2. You MUST build one manifest entry per Phase 2 task. No task may be omitted.
3. You MUST include the state file, log, and data-file paths for every task that has them. These are known from the boot step definitions: do not leave them blank.
4. Do NOT invent claimed statuses. Use exactly what each task reported in Phase 2.
5. Do NOT proceed to step 02 until the manifest is complete with all six entries.

---

## EXECUTION PROTOCOL

**Agent:** Ralph (boot-verification workflow, spawned by the boot subagent at step-03, never executed inline in the coordinator's session)
**Input:** Phase 2 completion report from accumulated-context
**Output:** Structured task manifest stored in accumulated-context for step 02

---

## CONTEXT BOUNDARIES

- Phase 2 tasks are fixed by the current boot step-02 definition: Morning Briefing Steps 01-02, Task E (Plaud/Knox, spawned in step-01), Task G (72-Hour Look-Ahead), Task H (Email Triage), Task I (Jarvis Inbox), Task J (Boot Reminders).
- Do not add tasks that weren't part of Phase 2. Do not omit tasks that were. Note: Task F (Lead Review) is NOT a boot Phase 2 task post-refactor: do not include it.
- Claimed status comes from Phase 2 reporting: not from re-checking state files here. That's Ralph's job in step 02.
- Data files are the ground truth Ralph cross-checks against. Boot step-01.2 (unified data pull) and step-01.5 (unified calendar pull) write them before Phase 2 runs.

---

## YOUR TASK

### Sequence

1. **Read the Phase 2 completion report** from accumulated-context. This contains what each task claimed: completed, nothing to surface, failed, or in-progress.

2. **Build the manifest**: one entry per task, in this order:

   ```yaml
   manifest:
     - task: "Morning Briefing Steps 01-02"
       claimed-status: "[from Phase 2 report]"
       state-file: "workflows/morning-briefing/state.yaml"
       expected-log: ~
       expected-output: "data/calendar-unified.json"
       data-files:
         - "data/calendar-unified.json"
         - "data/omnifocus-unified.json"

     - task: "E: Plaud Ingest (Knox)"
       claimed-status: "[from Phase 2 report]"
       state-file: "workflows/plaud-ingest/state.yaml"
       expected-log: ~
       expected-output: ~
       verification-note: "Fire-and-forget. Spawned by boot step-01. Ralph marks ➖ when a Knox/plaud-ingest eval record or a fresh plaud-ingest state.yaml exists; do not treat an unfinished background run as a failure."

     - task: "G: 72-Hour Look-Ahead"
       claimed-status: "[from Phase 2 report]"
       state-file: ~
       expected-log: ~
       expected-output: "data/calendar-unified.json"
       data-files:
         - "data/calendar-unified.json"
       verification-note: "No state file. Ralph checks that calendar-unified.json exists, is valid JSON, and carries events for days +1..+3."

     - task: "H: Email Triage"
       claimed-status: "[from Phase 2 report]"
       state-file: ~
       expected-log: ~
       expected-output: "data/email-unified.json"
       data-files:
         - "data/email-unified.json"
       verification-note: "No state file. Ralph checks email-unified.json is present and fresh (written this run), or that an explicit empty-result was reported from a live read."

     - task: "I: Jarvis Inbox"
       claimed-status: "[from Phase 2 report]"
       state-file: ~
       expected-log: "systems/eval-harness/skill-runs/jarvis-inbox-latest.json"
       expected-output: "data/jarvis-inbox-unified.json"
       data-files:
         - "data/jarvis-inbox-unified.json"

     - task: "J: Boot Reminders"
       claimed-status: "[from Phase 2 report]"
       state-file: ~
       expected-log: ~
       expected-output: "data/reminders.json"
       data-files:
         - "data/reminders.json"
       verification-note: "No state file. 'nothing-to-surface' is a valid outcome when data/reminders.json is missing, empty, or has no due entries: but the file's absence must be stated, not silent."
   ```

3. **Store the manifest** in accumulated-context under the key `phase2-manifest`.

4. **Update state.yaml**: set `current-step: step-02`.

---

## SUCCESS METRICS

- Manifest contains all six Phase 2 tasks (Morning Briefing 01-02, E, G, H, I, J)
- Each entry has the correct state-file, log, or data-file path (or explicit null with a verification-note for tasks without one)
- Claimed statuses match what Phase 2 actually reported

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Phase 2 completion report missing from context | Surface to Master: "Phase 2 report not in context: cannot build manifest. Pass the Phase 2 summary as context and re-run." Halt. |
| A task's claimed status is absent | Use "unknown" as claimed-status. Ralph will mark it ⚠️ Unverified: that's the right outcome for a silent task. |

---

## NEXT STEP

Read fully and follow: `step-02-verify.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
