---
date: 2026-06-19
error_reference: err-20260619T121855-S669II
improvement_type: workflow-hardening
category: skill-execution
---

# Workflow Improvement: Golf Booking Step 7 Slack Notification

## Problem Statement

During the June 19, 2026 midnight golf booking run, **Step 7 (Slack notification) was skipped** without error logging or fallback notification.

**Error ID**: err-20260619T121855-S669II  
**Failure Mode**: Skipped mandatory skill invocation  
**Severity**: High (booking confirmed but notification not delivered)

### What Happened

1. Booking completed successfully and was visually verified on ChronoGolf Bookings page
2. Step 7 required invoking master-slack skill to send confirmation to #jarvis
3. Agent assumed skill was unavailable (not in `<available_skills>` list in context)
4. Rather than attempting invocation or logging failure, agent silently skipped Step 7
5. Result: Booking confirmed but no notification sent to David

### Root Cause

- Incorrect assumption that `<available_skills>` context list was exhaustive
- Did not understand that skills can be accessed directly from filesystem: `.claude/skills/` and `skills/` directories
- Did not attempt skill invocation via Skill tool or fallback mechanisms
- No guard rail preventing silent omission of mandatory steps

---

## Solution: Workflow Hardening

All changes apply to `/Users/davidohara/develop/jarvis/skills/golf-booking/SKILL.md`

### 1. Add Explicit Rule 13 to MANDATORY EXECUTION RULES

```markdown
13. **SLACK NOTIFICATION IS MANDATORY (Step 7).** After visual verification 
    confirms the booking is on the Bookings page, ALWAYS invoke master-slack 
    skill to send booking confirmation to #jarvis. Do NOT skip, suppress, or 
    omit this step under any circumstances. If Desktop Commander is unavailable, 
    log the failure explicitly and create a fallback notification. Silence on 
    Step 7 is a critical failure mode.
```

**Impact**: Establishes non-negotiable execution requirement for Step 7

### 2. Replace Step 7 Generic Instructions with Explicit Executable Commands

**Old approach**: "Read and follow `.claude/skills/master-slack/SKILL.md`. Send to #jarvis"

**New approach**: Detailed 5-step protocol (7a–7e):

#### 7a — Invoke master-slack Skill
- Direct Desktop Commander call with mdfind command
- Explicit channel ID (C0AN2PQNXBR)
- 15-second timeout

#### 7b — Message Template
- Pre-formatted Slack markdown with all variable substitutions
- Emoji formatting for scannability
- Booking number included

#### 7c — Critical Rules for Slack Message
- Multi-line string handling (NOT literal `\n`)
- Dollar sign escaping (`\$` not `$`)
- 5000 character limit
- No fluff preamble

#### 7d — Verify Success
- Check for `{"ok": true, "channel": "...", "ts": "..."}` response
- Log timestamp for audit trail
- Explicit error surfacing if `ok: false`

#### 7e — Fallback Protocol
- If Desktop Commander unavailable: **do not skip**
- Log failure with error details
- Create fallback notification in `memory/working/`
- Surface error in task output: "Booking confirmed but Slack notification failed"

**Impact**: Converts ambiguous instruction ("follow SKILL.md") into concrete, step-by-step executable protocol with fallbacks

### 3. Update SUCCESS METRICS

**Added explicit Slack requirement:**

```markdown
- **Slack confirmation sent to #jarvis with all required fields** (Step 7 — MANDATORY)
  - Response includes `"ok": true` and valid `ts` timestamp
  - Message formatted per template with all variable substitutions completed
```

**Added explicit dual-gate completion:**

```markdown
- **No success claimed without: (1) visual confirmation on Bookings page, AND 
  (2) Slack notification delivered**
```

**Impact**: Makes Slack delivery a non-negotiable success criterion, not optional

### 4. Add Slack-Specific Failure Modes

New entries in FAILURE MODES table:

| Failure | Action |
|---------|--------|
| **Slack notification fails (Step 7)** | CRITICAL: Do NOT skip or suppress error. (1) Log failure with details. (2) Create fallback in memory/working/. (3) Surface in task output. (4) Set status: complete but flag `slack_notification_failed: true`. |
| post.py script not found | Use mdfind to search. If not found, log error + create fallback. Do not proceed silently. |
| SLACK_BOT_TOKEN missing | Log error. Follow token setup in master-slack SKILL.md. Do not proceed without token. |

**Impact**: Eliminates silent failures; every Slack error path has explicit handling and escalation

---

## Preventive Measures

### At Workflow Design Level
- Every mandatory step must have explicit rules in MANDATORY EXECUTION RULES
- Every mandatory step must have success metrics
- Every step with external dependencies must have failure modes with no-silence clause

### At Code Review Level
- Check that no mandatory steps are referenced generically ("follow SKILL.md")
- Verify fallback protocols exist for all external tool dependencies
- Ensure no silent skips in failure paths

### At Agent Level
- Never assume a skill is unavailable based on context list alone
- Always attempt invocation before declaring unavailability
- Always log failures; never silently skip mandatory steps
- Fallback is not optional — it's a design requirement

---

## Testing This Fix

**Next golf booking run** (Tuesday, June 25, 2026 at 11:00 PM for July 3–5 weekend):

1. Verify Step 7 executes (check for Desktop Commander call)
2. Verify Slack message appears in #jarvis with booking details
3. Verify response includes `ok: true` and valid timestamp
4. If any failure occurs, verify fallback notification created in memory/working/

**If Step 7 is skipped again**, error will be immediately caught because:
- Rule 13 explicitly states "ALWAYS invoke"
- Success metric requires Slack delivery
- No fallback allows silent omission

---

## Files Changed

- `skills/golf-booking/SKILL.md` — Step 7 expanded from ~20 lines to ~80 lines with explicit protocol and fallbacks
- `systems/error-tracking/entries/err-20260619T121855-S669II.json` — Error logged and corrected
- `workflows/golf-booking/state.yaml` — Status updated to `complete`
- `workflows/golf-booking/preview-output.json` — Booking result recorded

---

## Lessons Learned

1. **Context lists are not exhaustive.** Skills exist on disk and can be invoked directly even if not in the session's `<available_skills>` list.

2. **Mandatory steps need mandatory guards.** Using generic phrases like "read and follow" invites interpretation and skipping. Explicit, executable protocols prevent omission.

3. **Fallbacks are not optional.** If a step is mandatory but has external dependencies, fallback handling must be equally mandatory and explicit.

4. **Silence is a failure mode.** Any step that doesn't report completion or failure is a risk. Add explicit success/failure reporting to every critical path.

---

## Future Applicability

This pattern should be applied to any workflow with mandatory external tool invocations:

- Master-slack notifications
- Calendar event creation
- Email sending
- OmniFocus task creation
- Any step where "tool X is unavailable" should never result in silent skipping

Every such step should have:
1. Explicit rule in MANDATORY EXECUTION RULES
2. Success metric with verification criteria
3. Failure mode with explicit fallback (log + surface + continue or log + surface + abort)
4. No code path that silently omits the step
