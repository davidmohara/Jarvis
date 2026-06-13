---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Step 01: Build Manifest

## MANDATORY EXECUTION RULES

1. You MUST collect the Phase 2 completion report before proceeding. This was passed from Master as context — it contains what each Phase 2 task claimed.
2. You MUST build one manifest entry per Phase 2 task. No task may be omitted.
3. You MUST include state file paths and log paths for every task that has them. These are known — do not leave them blank.
4. Do NOT invent claimed statuses. Use exactly what each task reported in Phase 2.
5. Do NOT proceed to step 02 until the manifest is complete with all six entries.

---

## EXECUTION PROTOCOL

**Agent:** Master (running this step as part of boot orchestration)
**Input:** Phase 2 completion report from accumulated-context
**Output:** Structured task manifest stored in accumulated-context for step 02

---

## CONTEXT BOUNDARIES

- Phase 2 tasks are fixed: Morning Briefing Steps 01-02, E (Plaud Ingest), F (Lead Review), G (72-Hour Look-Ahead), H (Email Triage), I (Jarvis Inbox).
- Do not add tasks that weren't part of Phase 2. Do not omit tasks that were.
- Claimed status comes from Phase 2 reporting — not from re-checking state files here. That's Ralph's job in step 02.

---

## YOUR TASK

### Sequence

1. **Read the Phase 2 completion report** from accumulated-context. This contains what each task claimed: completed, nothing to surface, failed, or in-progress.

2. **Build the manifest** — one entry per task, in this order:

   ```yaml
   manifest:
     - task: "Morning Briefing Steps 01-02"
       claimed-status: "[from Phase 2 report]"
       state-file: "workflows/morning-briefing/state.yaml"
       expected-log: ~
       expected-output: ~

     - task: "E — Plaud Ingest"
       claimed-status: "[from Phase 2 report]"
       state-file: "workflows/plaud-ingest/state.yaml"
       expected-log: ~
       expected-output: ~

     - task: "F — Lead Review"
       claimed-status: "[from Phase 2 report]"
       state-file: "workflows/lead-review/state.yaml"
       expected-log: ~
       expected-output: ~

     - task: "G — 72-Hour Look-Ahead"
       claimed-status: "[from Phase 2 report]"
       state-file: ~
       expected-log: ~
       expected-output: ~
       verification-note: "No state file. Ralph checks Phase 2 report for actual calendar event data (names, times, attendees)."

     - task: "H — Email Triage"
       claimed-status: "[from Phase 2 report]"
       state-file: ~
       expected-log: ~
       expected-output: ~
       verification-note: "No state file. Ralph checks Phase 2 report for actual email data or explicit empty-result from a live query."

     - task: "I — Jarvis Inbox"
       claimed-status: "[from Phase 2 report]"
       state-file: ~
       expected-log: "systems/eval-harness/skill-runs/jarvis-inbox-latest.json"
       expected-output: ~
   ```

3. **Store the manifest** in accumulated-context under the key `phase2-manifest`.

4. **Update state.yaml**: set `current-step: step-02`.

---

## SUCCESS METRICS

- Manifest contains all six Phase 2 tasks
- Each entry has the correct state-file or log path (or explicit null with a verification-note for tasks without one)
- Claimed statuses match what Phase 2 actually reported

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Phase 2 completion report missing from context | Surface to Master: "Phase 2 report not in context — cannot build manifest. Pass the Phase 2 summary as context and re-run." Halt. |
| A task's claimed status is absent | Use "unknown" as claimed-status. Ralph will mark it ⚠️ Unverified — that's the right outcome for a silent task. |

---

## NEXT STEP

Read fully and follow: `step-02-verify.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
