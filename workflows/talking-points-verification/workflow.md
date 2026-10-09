---
name: talking-points-verification
description: Adversarial verification of a talking-points run. Ralph traces each delivered point back to a real source (knowledge-layer entries, agent-domain data, or provided context) so no point is unsourced.
agent: ralph
model: sonnet
---

<!-- system:start -->
# Talking Points Verification Workflow

**Goal:** Confirm that every delivered talking point is grounded: each point's supporting evidence traces to a real source (a knowledge-layer entry, an agent-domain data pull, or explicitly provided context), the executive's position is one they actually hold, and no statistic, quote, or claim is invented. No unsourced claims.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the deliverable manifest (the delivered points, the workflow's accumulated-context, the voice profile, and the source material) and returns a verdict table. The caller acts on the results; Ralph never fixes anything.

**Adversarial lens (talking-points):** Points traced to source strategy/notes. The producing agent (Harper) generates points with a `source_reference` for each; Ralph re-derives each point's evidence from the named source and checks that the point is not asserted without one. This is the talking-points lens in `agents/adversarial-isolation.md`.

## Lens checklist (what Ralph checks that the producer structurally cannot)

1. **Every point is sourced:** each talking point's supporting evidence traces to a real source (knowledge layer, agent domain, or provided context). A point with no source is a finding.
2. **No invented evidence:** statistics, quotes, and specific claims in the points are backed by the source, not fabricated.
3. **Positions are real:** a position attributed to the executive matches what the sources show they actually hold.
4. **Format matches the event type:** the delivered format (meeting / panel / media / internal-comms) matches the event_type recorded in step-01, with no mixed formats.
5. **Q&A is present and grounded:** the anticipated questions and responses are present and tied to the topic and audience, not generic filler.
6. **Voice calibration:** phrasing reads in the executive's voice (per `identity/VOICE.md`) rather than a generic professional register.

<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|--------------|
| Deliverable | The delivered `{...}-talking-points.md` | File system read |
| Workflow state | `workflows/talking-points/state.yaml` accumulated-context | File system read |
| Voice profile | `identity/VOICE.md` | File system read |
| Source material | Knowledge-layer entries / agent-domain data the points cite | From the manifest |

### Verdict table format

| Item | Point claim | Source evidence | Verdict |
|------|-------------|-----------------|---------|
| (one row per point) | (what the point asserts) | (what the source shows) | ✅ Verified / ⚠️ Unverified |

### Output

- Verdict table + one-line summary
- Mark ⚠️ on any point the source does not support
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## EXECUTION

Single step: `steps/step-01-verify.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
