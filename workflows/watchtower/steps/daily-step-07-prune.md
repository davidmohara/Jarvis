---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

<!-- system:start -->
# Daily Step 07: Prune Dormant Sources

## MANDATORY EXECUTION RULES

1. Write `status: in-progress` and `started-at` to this file's frontmatter before doing anything else.
2. Dormancy trigger: "no item SURFACED" (cleared awareness_floor) — NOT "feed silent." Noisy feeds that never clear the floor are dormant.
3. Never delete a retired source. Move it to `dormant-sources.yaml` — record kept for revival and audit.
4. Zero retirements is a valid outcome. Still update `source-activity.json` and write outputs.
5. Write retirements to `accumulated-context.retirements_today` for step-06 to include.
6. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | haiku |
| Input | `source-activity.json`, `sources.yaml`, `dormant-sources.yaml`, today's date |
| Output | Updated `source-activity.json`; retired sources moved to `dormant-sources.yaml`; `accumulated-context.retirements_today` written |

---

## YOUR TASK

**1. Read ledger and registry.** Read `workflows/watchtower/source-activity.json` (get `added`, `last_surfaced` per source) and `workflows/watchtower/sources.yaml` (current active list).

**2. Update last_surfaced.** For each item in `accumulated-context.scored_items` where `keep: true`: set its source's `last_surfaced` to today in `source-activity.json`. Write the updated file.

**3. Evaluate dormancy.** For each active source:
```
baseline = max(last_surfaced, added)   # use added if last_surfaced is null
days_since_surfaced = today - baseline
```
If `days_since_surfaced >= 21`: source is dormant — retire it.

**4. Retire dormant sources** (atomic pair — do not remove from sources.yaml until dormant file write succeeds):

a. Remove from `sources.yaml`.

b. Append to `dormant-sources.yaml` under `dormant:` with added fields:
   ```yaml
   retired: <today YYYY-MM-DD>
   reason: "no item cleared awareness_floor in 21 days"
   ```
   Carry all original fields.

c. Remove from `source-activity.json` (dormant sources not tracked).

d. Add source name to `accumulated-context.retirements_today`.

**5. Write outputs:**
```yaml
outputs:
  sources_evaluated: <int>
  sources_retired: <int>
  retired_names: []
  ledger_updated: true
```

---

**On failure:** `source-activity.json` unreadable → log, skip retirement check entirely; `sources.yaml` write fails → log, surface "Source prune failed — manual review needed"; `dormant-sources.yaml` write fails → log, do NOT remove from `sources.yaml` (atomic pair violated).

---

## NEXT STEP

Step order: **step-05-capture → step-07-prune → step-06-report**

Step-06 reads `accumulated-context.retirements_today` written by this step.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
