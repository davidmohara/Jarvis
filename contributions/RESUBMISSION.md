# Resubmission Queue

DB was wiped on redeploy 2026-04-18. All pending submissions lost. This file is the authoritative resubmission checklist.

**Status legend:** `READY` = package files verified on disk. `NEEDS PACKAGE` = files on disk but not yet assembled. `UPDATED` = content changed since original submission. `SUBMITTED` = resubmitted successfully. `DENIED (error)` = admin denied; submitted in error.

---

## 1. Connector — plaud-connector-1.0.0 ✓

**Type:** Connector  
**Original submission ID:** `cmo4dqchr00001tqg8iqhi8t9` (lost)  
**Status:** SUBMITTED — connector ID `cmo5912gu00081tqvw4trq7a8`, submitted Apr 19, 2026, status `pending`

---

## 2. Evolution — Cowork Scheduled Tasks ✓

**Type:** System evolution  
**Original DB ID:** `cmnsu3kgw000s1tn52nehirmk` (lost)  
**Status:** SUBMITTED — production ID `a3040a94`, submitted Apr 19, 2026  
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

## 3. Evolution — Root Audit ✓

**Type:** System evolution  
**Original DB ID:** `cmnry2y6r000p1tn5dtymavwh` (lost)  
**Status:** SUBMITTED — production ID `1c318b9f`, submitted Apr 19, 2026. (Duplicate `9ca24702` denied by admin. `err-20260418-001`.)  
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

## 4. Evolution — Error Tracking System Agent Integration ✓

**Type:** System evolution  
**Status:** SUBMITTED — Package A and Package B both uploaded Apr 19, 2026  
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

## 5. Evolution — IES v2.0 (Tiered Memory + Dream Cycle + Skill Manifest) ✓

**Type:** System evolution  
**Status:** SUBMITTED (cleaned) — evolution ID `2c1e25b7-1143-404a-971e-5916ec2e8292`, DB ID `cmo6357lg000a1tqv0ejdgypd`, Apr 19, 2026  
**Previous submission:** `cmo597t7x00091tqvl1uukdl0` denied — personal refs + path traversal  
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

1. **Connector** — plaud-connector-1.0.0 — SUBMITTED (`cmo5912gu00081tqvw4trq7a8`, Apr 19)
2. **Evolution** — Error Tracking System Agent Integration — SUBMITTED (Pkg A + B, Apr 19)
3. **Evolution** — Cowork Scheduled Tasks — SUBMITTED (`a3040a94`, Apr 19)
4. **Evolution** — Root Audit — SUBMITTED (`1c318b9f`, Apr 19)
5. **Evolution** — IES v2.0 — SUBMITTED (`cmo597t7x00091tqvl1uukdl0`, Apr 19)

---

## Verification After Each Submission

After each submission, update `submissions.json` with:
- New submission ID (will be a new cuid — the old IDs are gone)
- Timestamp
- Status: `pending`
