---
type: working-archive
task_id: "dream-cycle-2026-06-26"
session_id: "dream-cycle-2026-06-26-030941"
agent-source: jarvis
created: 2026-06-26T08:16:30Z
expires: 2026-06-27T08:00:00Z
status: archived
context: "Dream cycle 2026-06-26 — tapered run; surface YAML corruption discovery from prior promotion writes."
date: 2026-06-26
source_file: memory/working/dream-summary-2026-06-26.md
tags:
  - dream-summary
  - omnifocus
  - semantic-promotion
  - dream-cycle
  - lessons
  - rigby
  - jarvis
related_people: []
salience:
  score: 10
  promoted: true
  last-promoted-check: "2026-06-29"
---
# Dream Cycle Summary — 2026-06-26

Routine run, light counts as expected after yesterday's backlog flush.

**Step-01 (working memory):** Zero archives. The only expired file (`2026-06-19-000000-golf-booking-confirmed.md`) had `status: completed` rather than `status: active`, so it was correctly skipped per the rules. 72 already-archived stragglers, 13 unparseable, 9 not-expired.

**Step-02 (salience scoring):** 133 episodic entries scored. Window 2026-05-27 → 2026-06-26, 61 in-window. Distribution: 0:12, 2:3, 5:1, 6:3, 8:7, 9:8, 10:99.

**Step-03 (semantic promotion):** Zero candidates. Yesterday's 116-entry promotion flushed the backlog; everything with `salience.score >= 3` already has `salience.promoted: true`. Expected behavior.

**Step-04 (compression):** Skipped. Oldest episodic entry is 69 days old; 90-day threshold not yet hit.

**Step-05 (logging):** Dream log appended; LESSONS.md updated with 3 newly threshold-breaching error combos.

## Notable finding — YAML corruption from prior promotion writes

While building the entry list for step-02, pyyaml failed to parse ~120 of 133 episodic frontmatters. Root cause: yesterday's semantic-promotion writes inserted `promoted: true` indented under `related_people: null`, which produces invalid YAML. The dream cycle recovered today via a regex-based tag/date extractor, so scoring and the salience write both succeeded. But future cycles should not rely on the fallback.

Recommend Rigby tighten the frontmatter mutation in step-03's promotion code path (likely in the script that sets `salience.promoted: true`). The fix is mechanical: the `promoted: true` field belongs under `salience:`, not under `related_people:`. A correctness pass over the corrupted files is also warranted.

## Lessons added today

- `assumption-error / wrong-assumption` — 3 occurrences in 30d
- `format-violation / wrong-assumption` — 3 occurrences in 30d
- `format-violation / protocol-skip` — 3 occurrences in 30d
