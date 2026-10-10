Origin file: skills/chase-call-prep/SKILL.md
Relocated: 2026-10-10
Reason: RETIRED-skill migration map (why the skill was consolidated and where each useful piece moved). Plan intended memory/episodic/; staged here per this cleanup task's relocation rule.

Reasons for consolidation:
- Two capabilities existed for the same job (this skill's five-section template vs. the workflow's email-first, evidence-gated template). David decided the workflow is canonical.
- The workflow's step-02 establishes reason-for-call from actual email/calendar evidence *before* any web research — a hardening this skill never had, built after `err-20260720T144623-LSBA9A` (a prep sheet built from web research and calendar data alone produced a wrong title, an invented sales narrative, and a wrong reason for the call).
- This skill's useful pieces were carried forward rather than lost:
  - Its "Company Overview" section and source-priority guidance (website → web search → CRM → Clay supplemental-only) now live in `workflows/client-meeting-prep/steps/step-03-research-company-and-attendee.md` and render in `steps/step-04-build-prep-sheet.md`.
  - Its "Depth by context" distinction (full research vs. brief refresh) now lives as `contact_depth` (first-touch vs. repeat-meeting), set in `steps/step-02-source-of-truth-email.md`.
  - Its hardened reMarkable Delivery protocol is fully inlined in `workflows/client-meeting-prep/steps/step-05-remarkable-delivery.md`.
