---
id: remarkable-push
name: reMarkable Agent Delivery
owning_agent: rigby
model: haiku
context: inline
trigger_keywords:
  - push to remarkable
  - send to remarkable
  - remarkable delivery
  - deliver to remarkable
  - remarkable push
  - push pdf
---

<!-- system:start -->
# reMarkable Agent Delivery Skill

**This skill is the only authorized path for agent-initiated document delivery to the reMarkable tablet.** Any agent that generates a deliverable PDF and needs to push it to the reMarkable must use this skill. Do not write raw rmapi commands outside this skill. No exceptions.

This skill covers agent-driven delivery (e.g., call prep at the end of `client-meeting-prep`, podcast prep at the end of podcast workflows). For interactive/ad hoc uploads initiated conversationally, use `.claude/skills/remarkable-upload/SKILL.md` instead.
<!-- system:end -->

---

## Prerequisites

- `rmapi` installed on host Mac at `/opt/homebrew/bin/rmapi`
- rmapi authenticated (`.rmapi` config file present at `~/.rmapi`)
- Source PDF exists at a persistent Mac path (not a temp VM path)
- All rmapi commands run via `mcp__Control_your_Mac__osascript` — never via Bash in the VM

---

## Naming Convention

Deliverable PDFs pushed to the reMarkable follow the **human-readable deliverable naming standard** from SYSTEM.md Output Naming Conventions:

**Rule: No dates. No slugs. No underscores. Human-readable words with spaces.**

The name on the tablet is the filename without the `.pdf` extension. Name it the way you'd label a folder on your desk.

| Document Type | Pattern | Example |
|---|---|---|
| Call prep / meeting prep | `Person Name Company Call Prep.pdf` | `Austin Ledesma Solace Call Prep.pdf` |
| 1:1 prep | `Person Name.pdf` | `Scott McMichael.pdf` |
| Podcast episode prep | `Episode N.pdf` | `Episode 7.pdf` |
| Client brief or 1-pager | `Account Name Topic.pdf` | `CBRE Confluent 1-Pager.pdf` |
| Board / general meeting | `Meeting Name.pdf` | `Q3 Board Update.pdf` |
| Strategy or planning doc | `Topic Description.pdf` | `One Texas Strategy.pdf` |

**Never use** the IES source file's slug as the display name. Source files like `2026-08-10-austin-ledesma-solace.md` produce deliverables named `Austin Ledesma Solace Call Prep.pdf` — not `2026-08-10-austin-ledesma-solace-call-prep.pdf`.

---

## Path Routing Rules

Route based on document type and context. **Never create a new folder without David's explicit instruction.**

| Document Type | Target Path |
|---|---|
| Call prep / external meeting prep (prospects, partners, vendors) | `/Meetings` |
| 1:1 prep for a direct report (Devlin, Don, Kevin, Robyn, Scott, Tim) | `/Improving/One-on-ones/{person}` |
| Client account material (LTSA, McKesson, ORIX, OZK, Siemens, UTB, Veritas) | `/Improving/Accounts/{client}` |
| Partner meeting material (Confluent, Microsoft, etc.) | `/Improving/Partners/{partner}` |
| Podcast episode prep | `/Improving/Podcast/Episodes` |
| General Improving internal | `/Improving` |
| Terra Arma board docs | `/Terra Arma` |
| Terra Arma 1:1 (Rick Webb, Sean Brown) | `/Terra Arma/One-on-ones/{person}` |
| UTB board meeting | `/UTB/Board Meeting` |
| YPO material | `/YPO` (or sub-folder per context) |
| Ambiguous — no clear match | Surface 3-5 candidate folders ranked by relevance; ask David before pushing |

**Default fallback**: If a meeting is with an external person who is not a named client account contact, use `/Meetings` — even if they have an account folder. Move to `/Improving/Accounts/{client}` only after the prospect becomes a paying client.

---

## Execution Steps

### Pre-Push Checklist (run before every `rmapi put`)

1. **Filename check.** Human-readable words, spaces not underscores, no date prefix. Matches the naming convention above.
2. **Persistent path check.** Source is at a stable Mac path under `/Users/davidohara/` — not a `/tmp` path from a prior osascript call.
3. **Overwrite check.** Run `rmapi ls /TargetPath` first. If the same basename already exists, ask David whether to replace (delete + re-put) or keep both. Never silently create a duplicate.
4. **Source exists check.** Verify the file exists before invoking rmapi.

### Step 1 — Verify source file exists

For paths under `CloudStorage` (TCC-restricted), use Finder to verify:

```applescript
tell application "Finder"
    exists file "Document.pdf" of folder (POSIX file "/Users/davidohara/path/to/folder/" as alias)
end tell
```

For paths under `/tmp` or other shell-readable locations:

```applescript
do shell script "test -f '/path/to/Document.pdf' && echo OK || echo MISSING"
```

If MISSING: stop and report the path. Do not proceed.

### Step 2 — Determine target path and verify folder exists

```applescript
do shell script "/opt/homebrew/bin/rmapi ls '/TargetPath' 2>&1"
```

If the folder is missing, stop and surface the issue — **do not create new folders without David's explicit instruction**.

### Step 3 — Check for existing file with same name

Parse the `rmapi ls` output from Step 2. If a file with the same basename exists, ask David before proceeding.

### Step 4 — Rename PDF to human-readable name if needed

If the source PDF uses a slug name, copy it to the correct display name first:

```applescript
do shell script "cp '/path/to/2026-08-10-austin-ledesma-solace-call-prep.pdf' '/path/to/Austin Ledesma Solace Call Prep.pdf'"
```

Use the same directory as the source. The renamed file is what gets pushed.

### Step 5 — Push to reMarkable

```applescript
do shell script "/opt/homebrew/bin/rmapi put '/Users/davidohara/full/path/to/Austin Ledesma Solace Call Prep.pdf' '/Meetings' 2>&1"
```

**Note:** `rmapi put` does not overwrite. To replace an existing file with the same name: run `rmapi rm '/TargetPath/Document'` (no `.pdf` extension in the rmapi path) first, then re-put.

### Step 6 — Verify the upload landed

```applescript
do shell script "/opt/homebrew/bin/rmapi ls '/TargetPath' 2>&1"
```

Confirm the display name appears in the listing.

### Step 7 — Report result

On success: confirm the document name, the folder it was placed in, and that it will sync to the tablet.

On failure: report the rmapi error output verbatim and which step failed.

---

## Handling a Corrupted rmapi Config

If any rmapi call fails with an error containing `failed to parse /Users/davidohara/.rmapi`:

1. Remove the corrupted file:
   ```applescript
   do shell script "rm -f /Users/davidohara/.rmapi"
   ```
2. Retry the rmapi command that originally failed.
3. If retry fails with "not logged in" or asks for a one-time code: stop. Report to David that `.rmapi` was corrupted and removed, and that he needs to run `rmapi` once from a terminal to re-register. Do not attempt to write or fabricate the config file.

---

## Cleanup

If you copied the source PDF to a new display name (Step 4), delete the temporary renamed copy after a successful push if it is outside the IES tree (e.g., in a session outputs folder). If it is inside the IES tree, leave it — it may be the intended deliverable location.

---

## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/remarkable-push-latest.json
```

Content:
```json
{
  "skill": "remarkable-push",
  "agent": "rigby",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}
```

Set `trigger` to `"workflow"` if called from a workflow step, `"scheduled"` if from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the push completed with degraded output (e.g., wrong folder used), `"failure"` if it could not run at all.

**Eval-harness exception:** If running in eval-harness plan-only mode (`eval-mode: plan-only` in the prompt), do not write this signal file. Only genuine production runs should write it.


<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill remarkable-push
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/remarkable-push.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->
