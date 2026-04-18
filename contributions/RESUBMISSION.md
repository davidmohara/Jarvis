# Resubmission Queue

DB was wiped on redeploy 2026-04-18. All pending submissions lost. This file is the authoritative resubmission checklist — work top to bottom when the fix is confirmed in place.

**Status legend:** `READY` = package files verified on disk. `NEEDS PACKAGE` = files on disk but not yet assembled. `UPDATED` = content changed since original submission.

---

## 1. Connector — plaud-connector-1.0.0

**Type:** Connector  
**Original submission ID:** `cmo4dqchr00001tqg8iqhi8t9` (lost)  
**Status:** READY  
**Package:** `contributions/plaud-connector-1.0.0/`  

All package files verified present. No changes since original submission.

**Submit via:**
```
Skill: rigby-package-submit
Package: contributions/plaud-connector-1.0.0
Endpoint: POST /api/connectors
```

---

## 2. Evolution — Cowork Scheduled Tasks

**Type:** System evolution  
**Original DB ID:** `cmnsu3kgw000s1tn52nehirmk` (lost)  
**Status:** UPDATED — `scheduled-tasks.json` has grown from 3 to 5 tasks since original submission  
**Evolution classification:** system

**Files to include:**
| File | Action |
|------|--------|
| `config/scheduled-tasks.json` | add (updated — now includes wine-monitor and ies-channel tasks) |
| `.claude/skills/rigby-scheduled-setup/SKILL.md` | add |

**Note:** Submit the current state of scheduled-tasks.json (5 tasks). The evolution is additive — receiving instances won't have this file yet.

**Submit via:**
```
Skill: rigby-evolution-package → rigby-evolution-upload
```

---

## 3. Evolution — Root Audit

**Type:** System evolution  
**Original DB ID:** `cmnry2y6r000p1tn5dtymavwh` (lost)  
**Status:** UPDATED — `rigby-root-audit` skill was merged into `rigby-integrity` after original submission  
**Evolution classification:** system

**Files to include (updated from original):**
| File | Action |
|------|--------|
| `.claude/skills/rigby-integrity/SKILL.md` | add (replaces `rigby-root-audit` — root audit capability is now integrated here along with full integrity scanning) |
| `workflows/daily-review/steps/step-04-root-audit.md` | add |
| `agents/rigby.md` | merge (Root Audit + Integrity added to Task Portfolio) |
| `workflows/daily-review/steps/step-03-update-system.md` | merge (chains to step-04-root-audit) |

**Note:** The original submission named the standalone `rigby-root-audit` skill. That skill was absorbed into `rigby-integrity` (commit `6ec2db8`). Submit `rigby-integrity` instead — it is a superset. Strip personal blocks per standard evolution packaging rules.

**Submit via:**
```
Skill: rigby-evolution-package → rigby-evolution-upload
```

---

## 4. Evolution — Error Tracking System Agent Integration

**Type:** System evolution  
**Status:** NEEDS PACKAGE — all 12 files on disk, never assembled into a package  
**Evolution classification:** system

**Files to include:**
| File | Action |
|------|--------|
| `skills/rigby-error-analysis/SKILL.md` | add |
| `agents/conventions.md` | merge |
| `agents/master.md` | merge |
| `agents/rigby.md` | merge |
| `agents/chief.md` | merge |
| `agents/chase.md` | merge |
| `agents/quinn.md` | merge |
| `agents/shep.md` | merge |
| `agents/harper.md` | merge |
| `agents/knox.md` | merge |
| `workflows/daily-review/steps/step-03-update-system.md` | merge |
| `.claude/skills/quinn-weekly-review/SKILL.md` | merge |

**Note:** This is the large multi-agent update. Will likely need to split into 2-3 packages due to the ~35-40KB API payload limit (same as the original April 9 submission). Suggested split:
- Package A: core files (error-log.json, schema.md, rigby-error-analysis, conventions.md, master.md)
- Package B: agent files (chief, chase, quinn, shep, harper, knox, rigby)
- Package C: workflow + weekly-review integration

**Submit via:**
```
Skill: rigby-evolution-package → rigby-evolution-upload (×3 packages)
```

---

## 5. Evolution — IES v2.0 (Tiered Memory + Dream Cycle + Skill Manifest)

**Type:** System evolution (NEW — never submitted)  
**Status:** NEEDS PACKAGE  
**Evolution classification:** system  
**Built:** 2026-04-18, commit `d620fed`

**Files to include:**
| File | Action |
|------|--------|
| `memory/working/README.md` | add |
| `memory/episodic/README.md` | add |
| `memory/semantic/README.md` | add |
| `memory/personal/README.md` | add |
| `memory/LESSONS.md` | add |
| `skills/dream-cycle/SKILL.md` | add |
| `systems/scheduled-tasks/dream-cycle.json` | add |
| `skills/_manifest.jsonl` | add |
| `skills/_index.md` | add |
| `SYSTEM.md` | merge (Knowledge Layer section, boot sequence, Skill Loading Protocol) |

**Note:** Personal files (`memory/personal/`, `memory/dream.log`) excluded — personal classification. SYSTEM.md is 54KB+ and may hit payload limit; if so, split off into its own package.

**Submit via:**
```
Skill: rigby-evolution-package → rigby-evolution-upload
```

---

## Submission Order

Submit in this order — later submissions may reference components from earlier ones:

1. **Connector** — plaud-connector-1.0.0
2. **Evolution** — Error Tracking System Agent Integration (foundational, others reference it)
3. **Evolution** — Cowork Scheduled Tasks
4. **Evolution** — Root Audit
5. **Evolution** — IES v2.0

---

## Verification After Each Submission

After each submission, update `submissions.json` with:
- New submission ID (will be a new cuid — the old IDs are gone)
- Timestamp
- Status: `pending`
