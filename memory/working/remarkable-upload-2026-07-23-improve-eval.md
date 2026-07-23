---
date: 2026-07-23
type: skill-run
skill: remarkable-upload
eval_id: eval-20260723T155130-2N7J2L
grade: A
prior_baseline: eval-20260630T203949-E747AF
---

# remarkable-upload — intentional improvement eval

## What changed in the skill
- **Persistent Staging Rule** — ban `/tmp` across separate osascript calls; put from IES absolute paths (fixes E747AF failure mode).
- **Pre-Push Checklist** — filename convention, pdftoppm visual gate for session-generated PDFs, overwrite intent.
- Workflow put steps rewritten around checklist + persistent path.

## Eval result (plan-only, GeniusSpark Meeting Prep → `/Meetings`)
| Config | Assertions | Grade suggestion |
|--------|------------|------------------|
| with_skill (improved) | 8/8 | A |
| old_skill (snapshot) | 5/8 | C |
| prior live baseline E747AF | 2/2 structural, execution D | D |

Shareable comparison: `var/level-3-skill/remarkable-upload-comparison.html`
