---
name: dream-cycle-verification
description: Adversarial verification of a dream-cycle memory consolidation. Ralph cross-checks the cycle's archived/promoted/compressed claims against the actual memory files and the dream log, and confirms zero silent drops of working-memory entries.
agent: ralph
model: sonnet
---

<!-- system:start -->
# Dream Cycle Verification Workflow

**Goal:** Confirm that the cycle's consolidation claims match what actually happened to the memory files: nothing reported archived is still sitting in working/, no promoted or high-salience entry was deleted, every compressed source has a digest entry before it disappeared, and the dream.log entry is true.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the consolidation manifest (step outputs, state, dream.log, the real memory trees) and returns a verdict table. The caller acts on the results; Ralph never fixes anything.

**Adversarial lens (dream-cycle):** Memory-conservation accounting. The producing agent (Jarvis) summarizes what it believes it archived, promoted, and compressed; Ralph re-derives each claim from the recorded evidence: the step frontmatter outputs, `workflows/dream-cycle/state.yaml`, `memory/dream.log`, and the real `memory/working/` and `memory/episodic/` trees. This is the dream-cycle lens in `agents/adversarial-isolation.md`.

## Lens checklist (what Ralph checks that the producer structurally cannot)

1. **Zero silent drops:** every file the cycle reported archived is gone from `memory/working/` and present in `memory/episodic/` (or accounted for in a digest); no working-memory entry vanished without being named in a step output.
2. **Promoted preserved:** no entry with `salience.promoted: true` or `salience.score >= 2` was deleted by compression - the exclusion rule held.
3. **Compression ordering:** every compressed source has a matching `### ` digest entry written before the source file was removed.
4. **Semantic targets exist:** every `cluster_actions[].target` in step-03 exists under `memory/semantic/`.
5. **Log is true:** the dream.log entry for this run matches the step outputs (counts, session_id, run date) - no overstated summary.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|--------------|
| Consolidation manifest | Step output paths + run-date + controller summary | Passed from Jarvis as accumulated-context |
| Step outputs | `workflows/dream-cycle/steps/step-0{1,2,3,4,5}-*.md` frontmatter `outputs` | File system read |
| Workflow state | `workflows/dream-cycle/state.yaml` | File system read |
| Dream log | `memory/dream.log` (read the tail) | File system read |
| Working memory | `memory/working/` (current contents) | File system read |
| Episodic memory | `memory/episodic/` and `memory/episodic/digests/` | File system read |

### Verdict table format

| Item | Cycle claim | Recorded evidence | Verdict |
|------|-------------|-------------------|---------|
| (one row per claim) | (what the summary asserts) | (what the files show) | ✅ Verified / ⚠️ Unverified |

### Output

- Verdict table + one-line summary
- Mark ⚠️ on any claim the record does not support
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
