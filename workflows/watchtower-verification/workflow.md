---
name: watchtower-verification
description: Adversarial verification of a watchtower weekly run. Ralph cross-checks the run's standing-intelligence claims (themes, drafts, tweets, proposals, drafts sent to #content) against the sources and the record before the run is declared complete.
agent: ralph
model: sonnet
---

<!-- system:start -->
# Watchtower Verification Workflow

**Goal:** Confirm that the weekly run's standing-intelligence claims match what actually happened: every theme traces to source items, every draft that was reported sent was really delivered to `#content`, the tweet and proposal counts are true, and Watchtower never claims to have published to a platform it does not publish to.

**Agent:** Ralph, Verification Agent

**Architecture:** Single-step adversarial pass. Ralph receives the weekly manifest (step outputs, state, seen ledger, draft sources) and returns a verdict table. The caller acts on the results; Ralph never fixes anything.

**Adversarial lens (watchtower):** Standing-intelligence accounting. The producing agent (Knox) summarizes what it synthesized, drafted, proposed, and sent; Ralph re-derives each claim from the recorded evidence: the step outputs, `workflows/watchtower/state.yaml`, `workflows/watchtower/seen.jsonl`, and the draft/angle sources. This is the watchtower lens in `agents/adversarial-isolation.md`.

## Lens checklist (what Ralph checks that the producer structurally cannot)

1. **Themes trace to sources:** every theme in `weekly_themes` names `source_items` that correspond to real gathered/seen items - no theme asserted with no source.
2. **Draft accounting:** every draft in `draft_paths` is one of the themes' content angles, and every theme with a content angle has a draft (or a logged skip); the `blog-ideas.md` candidate rows match the drafts.
3. **Tweet accounting:** `weekly_tweets` count and `angle_types` reconcile; no tweet overlaps a blog angle.
4. **Source proposals are real:** `proposed_count`/`batch_number` match what is actually appended in `proposed-sources.md`, and none duplicate an active source.
5. **No false publishing claims:** Watchtower does NOT publish to LinkedIn/Twitter/any platform - it sends drafts to Slack `#content`. Any claim of "published"/"posted" beyond the `#content` send is a finding; and every draft reported in `drafts_sent` must have a matching `#content` delivery with a recorded pre-publish review.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->

---

<!-- system:start -->
## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|--------------|
| Weekly manifest | Step output paths + run-date | Passed from Knox as accumulated-context |
| Step outputs | `workflows/watchtower/steps/weekly-step-0{1,2,2b,3,4,5,6}-*.md` frontmatter `outputs` | File system read |
| Workflow state | `workflows/watchtower/state.yaml` | File system read |
| Seen ledger | `workflows/watchtower/seen.jsonl` | File system read |
| Draft register | `reference/blog-ideas.md` | File system read |
| Proposal file | `workflows/watchtower/proposed-sources.md` | File system read |

### Verdict table format

| Item | Run claim | Recorded evidence | Verdict |
|------|-----------|-------------------|---------|
| (one row per claim) | (what the summary asserts) | (what the record shows) | ✅ Verified / ⚠️ Unverified |

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
