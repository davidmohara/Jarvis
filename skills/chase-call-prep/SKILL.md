# Skill: Call & Meeting Prep (RETIRED)

**Skill ID:** `chase-call-prep`
**Status:** Deprecated 2026-07-20 — do not use, do not trigger.

---

## This skill has been retired

David consolidated external call/meeting prep onto a single canonical capability: the **`client-meeting-prep`** workflow.

**Successor:** `workflows/client-meeting-prep/workflow.md`

Reasons for consolidation:
- Two capabilities existed for the same job (this skill's five-section template vs. the workflow's email-first, evidence-gated template). David decided the workflow is canonical.
- The workflow's step-02 establishes reason-for-call from actual email/calendar evidence *before* any web research — a hardening this skill never had, built after `err-20260720T144623-LSBA9A` (a prep sheet built from web research and calendar data alone produced a wrong title, an invented sales narrative, and a wrong reason for the call).
- This skill's useful pieces were carried forward rather than lost:
  - Its "Company Overview" section and source-priority guidance (website → web search → CRM → Clay supplemental-only) now live in `workflows/client-meeting-prep/steps/step-03-research-company-and-attendee.md` and render in `steps/step-04-build-prep-sheet.md`.
  - Its "Depth by context" distinction (full research vs. brief refresh) now lives as `contact_depth` (first-touch vs. repeat-meeting), set in `steps/step-02-source-of-truth-email.md`.
  - Its hardened reMarkable Delivery protocol is fully inlined in `workflows/client-meeting-prep/steps/step-05-remarkable-delivery.md`.

**If you were routed here:** stop, and instead read and follow `workflows/client-meeting-prep/workflow.md` in full via Chase.

Do not resurrect this file's old five-section template (Background-History / Company Overview / Improving's Position / Proposed Agenda / Talking Points). It is superseded.


<!-- system:start -->
## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/chase-call-prep-latest.json
```

Content:
```json
{
  "skill": "chase-call-prep",
  "agent": "chase",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action, immediately followed by the grading step below.
<!-- system:end -->

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill chase-call-prep
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/chase-call-prep.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->
