<!-- system:start -->
## QUALITY GATE 4 — Speaker Identification Completeness (SOFT, LOGGED, DOES NOT REPLACE THE AWAITING-INPUT PAUSE)

This gate formalizes what "unresolved speaker" means and makes it an explicit, tracked flag.
It does **not** change the interactive-pause behavior in the workflow's STATE CHECK item 3 or
in step 3 of YOUR TASK above (pause, ask the controller in one consolidated message, resume
on response) — that behavior is preserved exactly as-is. This gate documents and carries the
condition forward; it does not gate progression to step-04 (the existing pause already does
that when needed) and it never silently drops the pause.

**Definition of "unresolved speaker"** for this gate's purposes: any generic label (e.g.
"Speaker 1", "Speaker 2") that survives all three resolution passes above — registered-speaker
embedding match, self-ID transcript scan, and the full calendar search discipline (matched
event attendees, adjacent events, recurring 1:1 pattern) — with no confident match to a real
name. This is exactly the set that ends up in `pending-speaker-mappings` before controller
escalation.

**What this gate does:**

1. After step 2 (auto-resolution) completes and before step 3 (controller escalation, if
   needed), take a snapshot of whatever remains in `pending-speaker-mappings` and write it,
   per-recording, into a new `accumulated-context.unresolved_speakers` list — same shape as
   `pending-speaker-mappings` (file_id, recording, unresolved labels, note) — so this
   condition is visible in state even after the controller eventually resolves it and
   `pending-speaker-mappings` is cleared back to `[]`.
2. If the controller later resolves some or all of them, update the corresponding
   `unresolved_speakers` entries to reflect resolution (do not delete the history — mark
   `resolved: true` with the method, e.g. "controller-provided") rather than removing the
   entry outright. This gives a durable record of which speakers needed a human across runs.
3. If nothing is unresolved after auto-resolution, `unresolved_speakers` stays `[]` and
   `gate_4_result: "pass"`.

Log the result:
```
[Gate 4] Unresolved speakers this run: N (across M recordings). Logged to accumulated-context.unresolved_speakers.
```
or
```
[Gate 4] No unresolved speakers — all resolved via embedding match, self-ID, or calendar.
```

Write to `state.yaml` `accumulated-context`:
```yaml
# state.yaml -> accumulated-context
gate_4_result: "pass" | "pass-with-unresolved"
gate_4_unresolved_speakers: [{file_id, recording, unresolved: [...]}, ...]
# Required whenever gate_4_result is "pass-with-unresolved" (or any escalation occurred):
unresolved_speakers: [{file_id, recording, unresolved: [...], evidence: "<calendar lookup result>"}, ...]
escalation-evidence: "<calendar event time + attendees checked + why insufficient; transcript self-ID scan result>"
```
`escalation-evidence` and a non-empty `unresolved_speakers` are what
`plaud-k4-escalation-evidence` / `plaud-sp-004/005` read — leave them empty (`[]`
and `null`) on a fully auto-resolved run, and the evidence check passes vacuously.

---
<!-- system:end -->
