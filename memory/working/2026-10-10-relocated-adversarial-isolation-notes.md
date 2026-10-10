Origin: agents/adversarial-isolation.md, "## Evidence of catches" section.
Date: 2026-10-10 (Phase A commentary cleanup).
Reason: run-log status narrative, not an instruction; relocated out of the boot-loaded agent file to keep it strictly instructional.

## Evidence of catches

Honest status: Ralph's documented catches are thin so far. The boot run records are few and were historically misattributed in the harness's agent field (attribution fix in Phase 2 scope). The Phase 4A wiring changes this structurally: each of the four workflows now records an `adversarial-verification` guardrail result on every run (assertions `boot-004`, `morning-008`, `daily-007`, `plaud-002`), so a run that skips adversarial verification fails a recorded assertion rather than passing silently, and catch examples accumulate as machine-readable evidence during the Phase 4 data window rather than only as narrative.
