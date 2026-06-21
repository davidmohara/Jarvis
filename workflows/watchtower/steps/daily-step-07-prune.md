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
2. The dormancy trigger is "no item SURFACED" (cleared awareness_floor) — NOT "feed silent." A source that publishes noise without clearing the floor still counts as dormant.
3. Never delete a retired source. Move it to `dormant-sources.yaml` — the record is kept for revival and audit.
4. If zero sources are retired today: still update `source-activity.json` (step-03 may have written new last_surfaced dates) and write outputs. Zero retirements is a valid outcome.
5. Surface retirements in today's report (write to `accumulated-context.retirements_today` for step-06 to include).
6. Write `status: complete`, `completed-at`, and `outputs` when done.

---

## EXECUTION PROTOCOL

| Field | Value |
|-------|-------|
| Agent | Knox |
| Model | haiku |
| Input | `source-activity.json`, `sources.yaml`, `dormant-sources.yaml`, today's date |
| Output | Updated `source-activity.json`; any retired sources moved to `dormant-sources.yaml` and removed from `sources.yaml`; `accumulated-context.retirements_today` written |

---

## CONTEXT BOUNDARIES

- Scope: dormancy check and source lifecycle only. No gathering, scoring, or summarizing.
- Dormancy window: 21 consecutive days. Measured as `today - max(last_surfaced, added) >= 21`.
  - Using `max(last_surfaced, added)` means new sources get a full 21-day grace period from their add date even if they never surface anything.
  - `last_surfaced: null` means the source has never surfaced an item — treat as never surfaced; apply add date as the baseline.
- Only retire sources with `status: active` in `sources.yaml`. Paused sources are not evaluated.

---

## YOUR TASK

### 1. Read ledger and registry

Read `workflows/watchtower/source-activity.json` — get `added` and `last_surfaced` for each source.

Read `workflows/watchtower/sources.yaml` — get current active source list.

### 2. Update last_surfaced from today's run

Step-03 (score) marks items with their source name. For each item in `accumulated-context.scored_items` where `keep: true` (cleared awareness_floor):
- Find the matching entry in `source-activity.json` by `source_name`.
- Set `last_surfaced` to today's date (overwrite if today is later than current value).

Write the updated `source-activity.json`.

### 3. Evaluate dormancy for each active source

For each active source:

```
baseline = max(last_surfaced, added)   # use added if last_surfaced is null
days_since_surfaced = today - baseline
```

If `days_since_surfaced >= 21`:
- The source is dormant. Proceed to retirement.

### 4. Retire dormant sources

For each source flagged dormant:

a. **Remove the entry from `sources.yaml`** (move it, do not leave a stub).

b. **Append to `dormant-sources.yaml`** under the `dormant:` list with these added fields:
   ```yaml
   retired: <today YYYY-MM-DD>
   reason: "no item cleared awareness_floor in 21 days"
   ```
   Carry all original fields (name, url, rss, gather_method, topic, trust, added, notes if present).

c. **Remove the entry from `source-activity.json`** (dormant sources are not tracked; they are not polled).

d. **Add to `accumulated-context.retirements_today`** (list of retired source names, for step-06 report).

### 5. Write outputs

```yaml
outputs:
  sources_evaluated: <int>
  sources_retired: <int>
  retired_names: []   # list of names, or empty list
  ledger_updated: true
```

---

## SUCCESS METRICS

- `source-activity.json` reflects today's run results.
- Any source dormant >= 21 days has been moved to `dormant-sources.yaml` and removed from `sources.yaml`.
- Dormancy trigger is awareness_floor-based (surfaced items), not raw feed activity.
- `accumulated-context.retirements_today` written (empty list is valid).

---

## FAILURE MODES

| Failure | Action |
|---------|--------|
| `source-activity.json` unreadable | Log warning; skip retirement check; do not retire sources without ledger data |
| `sources.yaml` write fails | Log; surface to David: "Source prune failed — manual review of source-activity.json needed." |
| `dormant-sources.yaml` write fails | Log; do not remove from sources.yaml until the dormant file write succeeds (atomic pair) |

---

## NEXT STEP

End of daily run. This step runs after `daily-step-06-report.md` — or, more precisely, step-06 reads `accumulated-context.retirements_today` that this step writes, so the order is:

**step-05-capture → step-07-prune → step-06-report**

Step-06 includes any retirements surfaced by this step in today's terminal report.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
