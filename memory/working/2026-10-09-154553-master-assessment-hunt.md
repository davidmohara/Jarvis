---
type: working
task_id: "session"
session_id: "master-2026-10-09-154553"
agent-source: master
created: 2026-10-09T15:45:53-05:00
expires: 2026-10-11T15:45:53-05:00
status: active
context: "Bootcamp assessment hunt — AI Adoption Maturity Assessment location — 2026-10-09"
---

# AI Adoption Maturity Assessment — where it actually lives (2026-10-09)

- David corrected a bad reference in AI-Bootcamp/Pre-Work.md line 130 (logged err-20261009T203817-J2YY3F): it points to ../AI-Deep-Learning-Program/Resources/Measures-and-Assessments/AI-Adoption-Maturity-Assessment.md, which is a REFERENCE POINTER page, not the instrument. Git history (AI-Course-Development repo) confirms the file was born as a pointer in commit e099e50 and never contained questions.
- The full 21-question, 7-dimension instrument exists embedded in: /Users/davidohara/develop/improving/AI-Course-Development/AI-Self-Directed-Learning/Module-4-Completion/Exercise-16-Completion-Self-Assessment.md, Step 5 ("AI Adoption Stage Evaluation", line ~178+), mirrored at /Users/davidohara/develop/improving/courses/AI-Self-Directed-Learning/Module-4-Completion/. Scoring A=1..D=4, total 21-84.
- The embedded instrument uses Improving's company-wide AI Adoption Model vocabulary ("The Trust Evolution: 8 Stages of AI Maturity"): dimensions include Prompt Engineering & AI Interaction, Task Agents, Workflow Orchestration. The DLP pointer page describes DIFFERENT DLP-v2 dimensions (Skill Craft, EC Discipline, Python Evaluation, Iteration, Adversarial Thinking, Adoption, Custom Harness Awareness) — a DLP-v2-specific instrument was never authored as a file.
- No standalone "Trust Evolution" document exists on disk (mdfind + repo grep + vault grep all negative).
- Bootcamp docs referencing the assessment: AI-Bootcamp/Pre-Work.md:130 (bad link), @Overview.md, Bootcamp-2-Week-Compression-Plan.md, Week-2 materials.

## Resolution update (David, 2026-10-09)

- The Exercise-16 embedded instrument was NOT the assessment either (err-20261009T205404-DLR9HZ). The real AI Adoption Maturity Assessment is a separate facilitator-provided document, not a repo file.
- Fixed AI-Bootcamp/Pre-Work.md Section 5: link removed, now reads that the facilitator provides the assessment directly and it is intentionally not in the repository.
- Remaining refs to the pointer page are legitimate (RELEASE-NOTES.md history; DLP-v2-Gap-Analysis.md:111, whose "reference by path" guidance produced the bad link and is now known-outdated).

## Exit ticket removal (David, 2026-10-09)

- Removed all exit-ticket references from the 4 PDF source files (@Overview.md, Week-1.md x7, Week-2.md x7; Pre-Work.md was already clean) and regenerated all 14 PDFs via generate_pdfs.py (improving-pdf). Zero remaining hits in PDF sources.
- NOT touched (out of scope, still reference exit tickets): Trainer/Training-Weeks/Bootcamp-Week-1.deck.md + Bootcamp-Week-2.deck.md (slide sources, ~15 hits), Concept-Coverage-Matrix.md (2), Bootcamp-2-Week-Compression-Plan.md (1).

## Decks cleaned too (David, 2026-10-09)

- Exit tickets also removed from Bootcamp-Week-1.deck.md (7 hits: 5 day-separator slide lines, 1 lecture bullet, 2 speaker-notes sentences rewritten) and Bootcamp-Week-2.deck.md (6 hits: 5 day-separator lines, 1 speaker-notes sentence). Both PPTX rebuilt via build_decks.py (51 and 47 slides).
- Remaining exit-ticket references, intentionally untouched (internal planning docs, not participant materials): Concept-Coverage-Matrix.md (2), Bootcamp-2-Week-Compression-Plan.md (1).
