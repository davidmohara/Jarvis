---
type: decision-rationale
subject: "Error improvement cycle \u2014 2026-03-21 to 2026-05-27"
date: 2026-05-27
tags:
- system-improvement
- error-tracking
- rigby
related-entities:
  projects:
  - ies-system
  accounts: []
  people: []
  meetings: []
agent-source: rigby
salience:
  score: 0
  last-promoted-check: 2026-06-04
  references: []
  promoted: false
---
## Error Improvement Cycle — 2026-03-21 to 2026-05-27

Rigby ran the full error-improvement workflow on 2026-05-27. This was the inaugural run of the newly built workflow. The active log contained 127 entries spanning 2026-03-21 to 2026-05-27, with 8 distinct patterns identified across 6 categories.

No fixes were applied this cycle. All 10 remaining proposed entries were classified as Needs Your Call — they are routing-gate entries (routing-error → protocol-skip pattern, pat-002) where the correct resolution depends on a policy decision about how aggressively Master should enforce routing before answering directly. Until David decides on that policy boundary, these entries remain open and are blocking March 2026 compaction.

The top pattern this cycle was process-skip → protocol-skip (19 occurrences, top agent: chief), reflecting cases where IES agents skipped required protocol steps — primarily boot sequence shortcuts and pre-flight omissions. The second pattern was routing-error → protocol-skip (18 occurrences, top agent: jarvis), representing the routing-gate Needs Your Call cluster. Together these two patterns account for 29% of the active log. The assumption-error → wrong-assumption pattern (13 occurrences, top agent: jarvis) ranked third and is the most directly addressable through skill edits, though no fix proposals surfaced this cycle.

48 entries from April 2026 were archived to a monthly digest (systems/error-tracking/digests/compact-2026-04.json). Source file deletion was blocked by sandbox filesystem permissions during this session and must be completed from the host (e.g., via Desktop Commander or direct shell). The digest is authoritative; the source files are safe to delete once the IES root is accessible outside the sandbox.

Trend: DEGRADING. March had 39 entries, April had 48, and May is on pace to exceed 48. The self-detection rate is approximately 7% — the vast majority of logged errors come from explicit David corrections rather than autonomous detection. This means the actual error rate is likely higher than the log reflects, and improving autonomous detection is a higher-leverage investment than pure fix throughput.

One notable cross-system finding: the morning-briefing workflow shows correlated assertion failures in the eval harness that align with the boot-skip pattern in the error log. This suggests a reinforcing cycle where boot shortcuts lead to degraded briefing quality, which generates more corrections, which appear as errors. Addressing the boot-skip pattern at the process level would likely improve both error rate and eval metrics simultaneously.
