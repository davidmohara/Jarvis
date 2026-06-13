---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: haiku
---

<!-- system:start -->
# Step 03: Triage & Approval

## MANDATORY EXECUTION RULES

1. You MUST NOT proceed to Step 4 without explicit controller approval of the Apply Now list.
2. You MUST set `status: awaiting-approval` in state.yaml before surfacing the approval prompt.
3. You MUST surface Needs Your Call items in the same session — not deferred to later.
4. You MUST record which specific fixes were approved (by id or description) in state.yaml.
5. Deprioritize items are surfaced for awareness only — no approval needed for them.

---

## EXECUTION PROTOCOL

**Agent:** Rigby
**Input:** `patterns_found` from state.yaml (Step 2 output)
**Output:** Three buckets, controller approval, `approved_fixes` written to state.yaml

---

## YOUR TASK

### 1. Bucket all proposed fixes

For each pattern or individual entry with `fix_status: proposed`, assign a bucket:

**Apply Now** — Clear-cut, low-risk, single-file fixes with obvious correct behavior:

| Pattern Type | Fix Type | Example |
|-------------|----------|---------|
| Same `tool-misuse` 3+ times | Rule addition to agent file | "Always use M365 MCP, not Apple Mail" |
| Same `format-violation` 3+ times | Convention rule in SYSTEM.md | "No em-dashes in any output" |
| Same `missed-context` 3+ times | Add source to agent's Data Requirements | "Read clay-contacts before speaker ID" |
| Same `process-skip` 3+ times | Checkpoint in workflow step | "Must reconcile before cleanup" |
| Same `assumption-error` 3+ times | "Verify before assuming" rule | "Pull calendar before scheduling questions" |
| Individual major severity, self-contained fix | Rule or skill update | Single occurrence but high-stakes |
| Eval-correlated pattern | Elevate to Apply Now regardless of tier | Double-confirmed by eval failures |

**Needs Your Call** — Requires judgment, behavioral changes, or infrastructure:

| Pattern Type | Why It Needs Your Call |
|-------------|----------------------|
| `routing-error` patterns | Requires routing table changes — how aggressive? |
| `hallucination` patterns | Requires deciding which sources to distrust or add |
| `over-engineering` / `under-delivery` | Calibration preference — only you know the right level |
| Multi-agent behavioral changes | Affects how multiple agents work — coordination decision |
| Capability gaps (missing tool, missing MCP) | Infrastructure investment decision |
| Patterns where multiple fixes are plausible | Need your call on which direction |

**Deprioritize** — Low signal, isolated incidents, or not worth system overhead:

| Condition | Reason |
|-----------|--------|
| Single occurrence, minor severity, no recurrence | Noise, not signal |
| Already addressed by a broader Apply Now fix | Covered by a more general rule |
| Context-specific one-off that can't be systematized | Not generalizable |

### 2. Draft the specific fix for each Apply Now item

For each Apply Now item, draft the exact change that will be made:
- **Rule addition**: exact text of the rule, exact file and section it goes in
- **Skill update**: exact edit — what line(s) change, what they change to
- **Workflow checkpoint**: exact step and exact new requirement

This is what the controller is approving. Vague descriptions ("improve the boot process") are not acceptable — the approval must be for specific, bounded changes.

### 3. Present for approval

Set `status: awaiting-approval` in state.yaml.

Present in this format:

```
## Error Fix Approval — [N] Apply Now, [M] Needs Your Call, [P] Deprioritize

### Apply Now ([N] fixes)

These are ready to apply. Reply `approve` to proceed with all, or call out any you want to skip/modify.

[For each fix:]
**[N]. [Fix description]**
- Addresses: [pattern description] ([X] occurrences, [severity])
- File: `[target file]`
- Change: [exact text being added/changed]

---

### Needs Your Call ([M] items)

These need your direction before I can act on them.

[For each:]
**[N]. [Pattern description]** — [X] occurrences
- What keeps happening: [description]
- Options: [Option A] | [Option B] | [skip for now]

---

### Deprioritize ([P] items — FYI only)

[Brief list — 1 line each]
```

Wait for the controller's response. Accept:
- `approve` or `approve all` → approve entire Apply Now list
- `approve [N, M, ...]` → approve specific numbered items
- Modified item feedback → revise that item and re-present for that item only
- Needs Your Call answers → capture the decision, add to `approved_fixes` if actionable

### 4. Record approval in state.yaml

Update state.yaml after approval:

```yaml
  approval_received: true
  approved_fixes:
    - fix_id: fix-001
      description: "Add M365-only rule to jarvis-inbox SKILL.md"
      target_file: "skills/jarvis-inbox/SKILL.md"
      change_type: rule
      entry_ids: ["err-20260401-007", "err-20260412-003"]
    - ...
  needs_your_call_decisions:
    - pattern: "routing-error / master doing Harper's work"
      decision: "Apply routing gate — see Step 4 for implementation"
```

Update `status: in-progress` and `current-step: step-04-apply`.

---

## INSTRUMENTATION

After writing the approval to state.yaml, append this step's timing:

```yaml
  step_timings:
    - step: step-03-triage
      started: <ISO-8601 UTC when this step began>
      completed: <ISO-8601 UTC now>
```

---

## CONTEXT BOUNDARIES

- Step 3 ends when the controller has approved a fix list (even if empty)
- An empty approval ("nothing to apply") is valid — move to Step 5 for compact check
- Needs Your Call decisions that result in actionable fixes get added to `approved_fixes`
- Needs Your Call items with no decision stay in `proposed` — surfaced in next cycle

## SUCCESS METRICS

- All proposed fixes bucketed
- Specific change drafted for each Apply Now item
- Controller approval received
- Approved fix list recorded in state.yaml

## FAILURE MODES

| Failure | Action |
|---------|--------|
| No proposed fixes found | Report: "No proposed fixes — log is clean. Proceeding to verify and compact." Skip to Step 5. |
| Controller provides partial approval | Apply only approved items. Record which were skipped and why. |
| Controller asks to defer everything | Set all to `deferred`, skip Step 4, proceed to Step 5 for compact. |

## NEXT STEP

[Step 04 — Apply](step-04-apply.md)
<!-- system:end -->
