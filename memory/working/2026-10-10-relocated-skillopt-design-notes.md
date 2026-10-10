# Relocated: skill-optimize SkillOpt design-limitation rationale

Origin: `workflows/skill-optimize/steps/step-05-score-candidate.md` CONTEXT BOUNDARIES section (removed 2026-10-10 during Phase A commentary cleanup).
Date relocated: 2026-10-10.
Reason: design rationale / adaptation note, not instructional content. The step's operative scoring rule remains in-file.

---

Note: In a full SkillOpt implementation, you would re-run the skill with the candidate version and collect new trajectories. In IES, we use existing records as the held-out validation set because Jarvis runs in a real-work context where synthetic re-runs aren't practical. This is a pragmatic adaptation — the signal is weaker but the gate still prevents regression.
