# State Check Protocol

Canonical resume/abort check for workflow runs. Every `workflows/<name>/workflow.md` replaces its inline STATE CHECK block with this pointer:

> Read and follow `reference/state-check-protocol.md` before any execution. Workflow name: `<name>`; agent: `<agent>`.

Substitute `<name>` and `<agent>` for the workflow referencing this protocol.

---

## Procedure

1. Read `state.yaml` in the workflow's own directory.

2. If `status: in-progress`:
   - You are resuming a previous run. Do NOT start over.
   - Read `current-step` to find where to continue.
   - Load `accumulated-context`: data already gathered. Do not re-pull it.
   - Check that step's frontmatter: if `status: in-progress`, re-execute it; if `status: not-started`, begin it fresh.
   - Notify the controller: "[<agent>]: Resuming <name> from [current-step]."

3. If `status: not-started` or `status: complete`:
   - Fresh run. Initialize `state.yaml`: set `status: in-progress`, generate `session-id`, write `session-started` and `original-request`, set `current-step: step-01`.
   - Begin at step-01.

4. If `status: aborted`:
   - Surface to controller: "[<agent>]: <name> was previously aborted at [current-step]. Resume or start fresh?"
   - Wait for instruction.
