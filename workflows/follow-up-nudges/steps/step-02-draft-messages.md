---
model: sonnet
---

<!-- system:start -->
# Step 02: Draft Tone-Calibrated Follow-Up Messages

## MANDATORY EXECUTION RULES

1. You MUST draft a message for every item identified in step 01.
2. You MUST determine tone level using the calibration rules below — not instinct.
3. You MUST offer 2-3 tone variants for each item so the executive can choose.
4. You MUST adjust for relationship seniority: cap at Level 2 for superiors unless executive explicitly escalates.
5. Do NOT send any message in this step. That is step 03.

---

## EXECUTION PROTOCOL

**Agent:** Shep
**Input:** Ranked nudge candidates from step 01 (with days overdue, relationship context, past patterns)
**Output:** Draft messages for each item (2-3 tone variants each), stored in working memory

---

## CONTEXT BOUNDARIES

- Tone calibration is the core value of this workflow. A blunt escalation message to a VP who is one day late is a management mistake. A gentle nudge to a direct report who is 10 days late and has a pattern of ignoring follow-ups fails the executive.
- Reference the past patterns from the knowledge layer. If prior nudges to this person were ignored, start higher on the tone scale.
- Message content must always reference the specific delegation: what was asked, when it was due.

---

## YOUR TASK

### Tone Calibration

For each item, determine the appropriate tone level:

**Step 1 — Base level from days overdue:**

- 1-3 days overdue → Level 1 (Gentle reminder)
- 4-7 days overdue → Level 2 (Firm follow-up)
- 8+ days overdue → Level 3 (Escalation)

**Step 2 — Adjust for relationship seniority:**

- Direct report → use base level; escalate to Level 3 if pattern of lateness
- Peer → cap at Level 2 unless executive explicitly requests escalation
- Superior → cap at Level 2; never send Level 3 without explicit executive authorization

**Step 3 — Adjust for past pattern from knowledge layer:**

- `reliable` → stay at base level or go one level down if only 1-2 days late
- `occasionally-late` → use base level
- `frequently-late` → go one level up from base level
- `unknown` → use base level, note the unknown pattern to the executive

### Draft Message Format

For each item, draft 2-3 variants at adjacent tone levels. Present all variants for the executive to choose from:

```text
[Person Name] — [Task] — [N] days overdue

Variant A (Level [N] — [tone name]):
"[Draft message — specific reference to task and due date. Tone calibrated to level.]"

Variant B (Level [N+1] — [tone name]):
"[Draft message — slightly firmer. Same specifics, escalated urgency.]"
```

**Message content guidelines:**

- Always name the specific delegation: "the [task description] I asked you to handle"
- Always include the original due date or how many days it is past due
- Level 1: "Just checking in..." / "Wanted to make sure this is still on your radar..."
- Level 2: "I need an update on [X] by [date]..." / "This was due [date] and I haven't heard back..."
- Level 3: "[X] is [N] days overdue and [state the impact]. I need your response by [date]..."

---

## SUCCESS METRICS

- Tone level determined for every item using the calibration rules
- 2-3 message variants drafted per item
- Messages include specific delegation reference and due date
- Seniority adjustment applied to all messages

## FAILURE MODES

| Failure | Action |
|---------|--------|
| Relationship seniority unknown | Treat as peer. Cap at Level 2. Flag to executive: "Seniority unknown — defaulting to peer-level tone." |
| Past pattern data unavailable | Use base tone level from days overdue. Note: "No past follow-up history for this person." |
| Item is both overdue and stale | Use the higher tone indicator of the two. Note both conditions in the message draft. |

---

## NEXT STEP

Read fully and follow: `step-03-review-and-send.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
