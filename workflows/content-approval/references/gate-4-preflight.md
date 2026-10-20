<!-- system:start -->
## QUALITY GATE 4 — Publishing Pre-flight (HARD, BLOCKING)

Run immediately before the Ghost publish call. This formalizes the checks discovery's GATE 2 already ran at draft-creation time — re-run here because time has passed since drafting and an editorial edit (Section 6d) may have touched the post since, so the pre-publish state needs its own independent check rather than trusting the draft-time gate.

Fetch the current post via `mcp__ghost-blog__get_post(post_id="{ghost_post_id}", formats="lexical")`, then call `skills/schema-validator/SKILL.md`:

```yaml
data:
  status: "{post.status}"
  lexical_non_empty: <bool>          # your own check: does lexical have paragraph nodes
  feature_image: "{post.feature_image}"
  tags: {post.tags}                  # real tag objects as returned, not bare strings
  slug: "{post.slug}"
  obsidian_note_found: <bool>        # from the vault-sync protocol above
schema_spec:
  required_fields:
    - "feature_image"
    - "slug"
  custom_checks:
    - { field: "status", rule: "must_equal", value: "draft" }
    - { field: "lexical_non_empty", rule: "must_be_true" }
    - { field: "obsidian_note_found", rule: "must_be_true" }
  tags: { field: "tags", allowed_list: [<locked-list tag ids from workflows/content-discovery/references/ghost-conventions.md>], format: "object_with_id" }
```

| Check | Expected | On failure |
|-------|----------|------------|
| `post.status == "draft"` | Confirmed still a draft, not already published/scheduled (re-confirms Step 1's Ghost Status Verification, since time has passed) | **STOP.** If status changed since Step 1, do not publish — re-run Step 1 sync and re-classify. |
| `lexical` is non-empty | Has paragraph nodes | **STOP.** Do not publish a post with empty body content. Notify David and do not proceed. |
| `feature_image` is set | Non-null, non-empty URL | **STOP.** Do not publish without a feature image. If an editorial edit removed it, re-run the Step 6 image protocol from content-discovery's step-01. |
| `tags` show real tag names (not bare ID strings) and every tag is on the locked list | Cross-check against the LOCKED LIST table in `workflows/content-discovery/references/ghost-conventions.md` | **STOP.** If tags are malformed or off-list, fix via Ghost Admin API PUT before publishing. Never publish with a junk tag. |
| `slug` is present and non-empty | Ghost auto-generates on creation; confirm it wasn't cleared by a prior edit | **STOP.** If missing, this indicates a corrupted post — notify David rather than guessing a slug. |
| Obsidian note found (from the protocol above) or its failure was surfaced per Step 4 of that protocol | No silent skip | **STOP** if the note is missing and the warning wasn't prepended — do not publish without vault sync being at least attempted and reported. |

Log the result (reading `errors` back from the skill's response for anything that failed):
```
[Gate 4] Post: "{title}" ({ghost_post_id})
[Gate 4] Status: draft (confirmed) | lexical: non-empty | feature_image: set | tags: {names} (locked-list confirmed) | slug: {slug}
[Gate 4] PASS — proceeding to publish.
```

If `schema-validator` returns `valid: false` (or the direct status check above fails), log
`[Gate 4] FAIL — <errors list>` and remediate (or halt and notify David per FAILURE MODES)
before calling the publish endpoint.

---

**Step 2b: Publish Pre-Flight Guardrail Checkpoint (HARD, BLOCKING)**

Publishing a post to driventodevelop.com is this workflow's one irreversible external action.
After GATE 4 passes and before the publish call, record a guardrail checkpoint so the run's
eval record carries the review result:

```bash
python3 systems/eval-harness/guardrail-checkpoint.py content-approval publish-preflight step-01-approve <pass|flag|escalate> "<one-line reason>"
```

- **No issue found** → `pass`. Proceed to publish.
- **A minor issue you can point to that does not block the publish** (e.g., a warning carried
  from the Obsidian sync) → `flag`, note it, and proceed. Surface the flag in the `[PUBLISHED]`
  Slack message.
- **A leaked secret in the post body, a wrong author, an off-list tag, a missing feature image,
  or a publish that would bypass GATE 4** → `escalate`. Halt. Do NOT call the publish endpoint.
  Surface to David: `[Harper]: Publishing pre-flight checkpoint flagged an issue for "{title}", [description]. Holding the publish until you confirm.` Wait for instruction.

If `guardrail-checkpoint.py` cannot write (no in-progress eval record), note the gap in the
`[PUBLISHED]` Slack message and proceed only if GATE 4 found nothing — otherwise escalate
verbally. This is distinct from a step failure; do not mark step-01 failed because of an
escalation here.

---

**Step 3: Publish to Ghost, then verify — via `skills/delivery-router/SKILL.md`**

Gate 5 (delivery verification) and the publish call itself are now one skill call, because
"call the API" and "confirm it actually took" are exactly what `delivery-router`'s `ghost`
backend already does as a single unit (call `update_post`, then re-fetch and check the result
— see that skill's Process section) — keeping them as two separate manual steps here would
just be re-implementing what the skill already owns.

```yaml
content: "{ghost_post_id}"          # ghost backend keys off config.post_id; content is informational here
destinations:
  - backend: "ghost"
    required: true
    config:
      post_id: "{ghost_post_id}"
      target_status: "published"
      expected_host: "driventodevelop.com"
```

The skill's `ghost` backend handles the concurrent-edit wait/retry protocol internally (2s
retry, then 5s retry, matching what this step used to do manually) before falling through to
its general 3-attempt budget. Read `delivery_status[0]` for the outcome:

- `success: true` → `.id` is `post.url` from the verified re-fetch. This **is** Gate 5 passing
  — proceed straight to notifying David (Step 5 below). Do not re-run a separate verification
  fetch; the skill already did it and only reports `success: true` if the re-fetch confirmed
  `status == target_status`, `url` resolves to `expected_host`, and `published_at` is set.
- `success: false` → treat as both the publish failing and Gate 5 failing (the skill does not
  distinguish "the call failed" from "the call succeeded but didn't verify" in its retry
  loop — by the time it reports failure, every attempt including verification has been
  exhausted). Read `.error` for what to tell David. Keep `pending-drafts.json` status as
  "approved" (not "pending") per the concurrent-edit handling this replaces, and follow
  FAILURE MODES below.

---
<!-- system:end -->
