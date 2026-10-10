# Relocated: system-eval dashboard Chart.js patch history

Origin: `workflows/system-eval/steps/step-06-dashboard.md` section 2a (removed 2026-10-10 during Phase A commentary cleanup; the operative safety-net clause was folded into the sed step itself).
Date relocated: 2026-10-10.
Reason: dated patch/changelog note, not instructional content. The sed command and its purpose remain in-file.

---

**Note (2026-07-08):** `generate-dashboard.py` was patched to emit the approved Chart.js 4.5.0 tag directly. This sed command is a no-op on freshly generated dashboards but is kept as a safety net in case an older version of the script is used.
