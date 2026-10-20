<!-- system:start -->
# Quality Gates 1 and 2 (content-discovery step-01)

Both gates are HARD and BLOCKING. Run them exactly as written.

## GATE 1 — Source Integrity

**Purpose:** Everything downstream — routing, drafting, dedup — depends on this pull actually having reached the right channel and returned real data. A silent tunnel failure or wrong-channel response must not be treated as "no new content."

| Check | Expected | On failure |
|-------|----------|------------|
| Command exit / stdout is non-empty | Non-empty JSON string returned | **STOP.** Do not conclude "no messages" — this looks like a tool/network failure. Retry via `mcp__Desktop_Commander__start_process` per MANDATORY EXECUTION RULE 0 before reporting. |
| Response parses as valid JSON | `json.loads` succeeds | **STOP.** Report the raw response and abort this run. Do not attempt to draft from unparseable output. |
| `ok` field is `true` | `{"ok": true, ...}` | **STOP.** If `ok: false`, capture the `error` field verbatim and report failure per FAILURE MODES below. Do not retry blindly more than once. |
| `messages` field is present and is a list (possibly empty) | `isinstance(messages, list)` | **STOP.** A missing or non-list `messages` field means the API contract broke or the wrong endpoint/channel was hit. |
| Channel ID in the request matches C0B160MA3EK | Literal string match against the command issued | **STOP.** If the channel ID was altered anywhere upstream, abort — do not draft from the wrong channel's content. |
| No garbage/binary payload in message `text` fields | Spot-check: at least the first message's `text` is printable UTF-8 | **STOP.** A garbled payload indicates a transport-layer problem (see err-20260715T182916-FSMOJK class of failures); do not attempt to parse it as content. |

An empty `messages` array (`{"ok": true, "messages": []}`) is a legitimate PASS — it means no new content in the last 24 hours, not a failure. Proceed to exit cleanly per the MESSAGE ROUTER's "no messages route" rule.

Log the result:
```
[Gate 1] Channel: C0B160MA3EK
[Gate 1] Response ok: true|false
[Gate 1] Messages returned: N
[Gate 1] PASS — proceeding to message routing.
```

If it fails, log `[Gate 1] FAIL — <check name>` and follow FAILURE MODES ("read.py fails") before any further processing.

## GATE 2 — Content Schema Validation


Run after Step 6 (image sourced) and before Step 7 (Ghost draft creation). This formalizes the rules in `workflows/content-discovery/references/digest-format.md` and workflow.md's BLOG VOICE & FORMAT section into an explicit checklist rather than leaving them as inline prose that's easy to skip under time pressure.

Applies to both the URL PATH and the DIGEST PATH (per DIGEST PATH Step E, the digest path merges in here).

**Two of these checks require judgment this gate does not delegate away:** whether the four
post-arc elements are actually present in the prose, and whether the draft reads as David's
own angle rather than a source recap. Make those calls yourself by reading the draft, set them
as plain booleans (`has_hook`, `has_story`, `has_insight`, `has_challenge`, `is_source_recap`),
then call `skills/schema-validator/SKILL.md` to mechanically check everything else against
those booleans plus the objective fields:

```yaml
data:
  word_count: <int>
  has_hook: <bool>
  has_story: <bool>
  has_insight: <bool>
  has_challenge: <bool>
  is_source_recap: <bool>          # your own read — true means FAIL
  body: "<full draft text>"
  tags: [{"id": "..."}, ...]
  meta_title: "<...>"
  meta_description: "<...>"
  feature_image_landscape: <bool>  # from Step 6's w > h check
  feature_image_set: <bool>
  feature_image_geo_confirmed: <bool>  # true if post is not geo-specific, OR if geo-specific and image location verified
  has_internal_link_if_required: <bool>  # true if no published related post exists, OR if one exists and a lexical link node was inserted
  is_voice_original: <bool>  # your own read — true means the post makes a distinct argument in David's voice, not a paraphrase of the digest
schema_spec:
  word_count: { min: 300, max: 500 }   # or {min: 1500, max: 2000} for IMPROVING BLOG PATH only
  tags: { field: "tags", allowed_list: [<locked-list tag ids from workflow.md>], format: "object_with_id" }
  em_dash_check: { field: "body", enabled: true }
  custom_checks:
    - { field: "has_hook", rule: "must_be_true" }
    - { field: "has_story", rule: "must_be_true" }
    - { field: "has_insight", rule: "must_be_true" }
    - { field: "has_challenge", rule: "must_be_true" }
    - { field: "is_source_recap", rule: "must_be_false" }
    - { field: "is_voice_original", rule: "must_be_true" }
    - { field: "meta_title", rule: "max_length", value: 70 }
    - { field: "meta_description", rule: "max_length", value: 155 }
    - { field: "feature_image_landscape", rule: "must_be_true" }
    - { field: "feature_image_set", rule: "must_be_true" }
    - { field: "feature_image_geo_confirmed", rule: "must_be_true" }
    - { field: "has_internal_link_if_required", rule: "must_be_true" }
```

The "no bullet points / no headers in body" check for sub-500-word posts is a structural scan
of `body` this skill's generic rule set doesn't cover directly — run it yourself (or add it as
`format_rules`/`custom_checks` on a future edit if it recurs elsewhere) and fold the result
into `errors` manually if it fails, same STOP treatment as any other Gate 2 failure below.

| Check | Expected | On failure |
|-------|----------|------------|
| Word count | 300-500 words (URL/digest post path) or 1,500-2,000 words (IMPROVING BLOG PATH only) | **STOP.** Trim or expand before proceeding. Do not send an out-of-range draft to Ghost. |
| Four post-arc elements present | Hook, Story/Observation, Insight, Challenge/Takeaway all identifiable in the draft | **STOP.** If any is missing, write it now per the "Missing sections" rule in `workflows/content-discovery/references/digest-format.md` (using CONTENT-VOICE.md), then re-check. |
| No em-dashes | Zero occurrences of `—`, `–` used as a dash, or `--` | **STOP.** Replace with commas, periods, or parentheses. Re-scan the full draft, not just the flagged sentence. |
| No bullet points / no headers in body (post under 500 words) | Prose only | **STOP.** Convert to prose. |
| Not a source recap / not a paraphrase | Draft reads as David's reaction/angle, not "According to [source]..." AND does not simply restate the digest's argument in different words. Put the post and the digest side by side — if they make the same points in the same order with the same framing, `is_voice_original` is false. (`is_source_recap` false + `is_voice_original` true both required.) (err-20260915T154324-LFMX48) | **STOP.** Rewrite from David's own angle. The digest is the stimulus, not the script. Change the framing, not just the words. |
| Tags are from the locked list | Every tag id in the draft's tag selection appears in workflow.md's LOCKED LIST table | **STOP.** Do not proceed with an off-list tag. Re-select from the locked list. |
| Tag format is object-with-id | Selected tags represented as `[{"id": "..."}]`, never bare strings | **STOP.** Fix format before the Ghost API call — bare strings create junk tags (see workflow.md's CRITICAL note). |
| meta_title ≤ 70 chars, meta_description ≤ 155 chars | Character counts checked | **STOP.** Trim before proceeding. |
| Feature image is landscape and CDN-uploaded (or verified fallback per FAILURE MODES) | `w > h` confirmed in Step 6; `feature_image` is set | **STOP.** Do not create the Ghost post without a validated image or an explicit, logged fallback. |
| Feature image geography matches post (if geo-specific) | If the post names a city/region, the image is confirmed to depict that location (checked via photo title/description on the Unsplash page). If the post is not geo-specific, this check auto-passes. | **STOP.** Discard the candidate and re-run Step 6 with a location-specific search query. (err-20260915T154324-4DLWA4) |
| Internal links present (if related published post exists) | If the post references or clearly relates to a published Ghost post, a lexical link node is built into the lexical body before this gate. If no related published post exists, this check auto-passes. | **STOP.** Resolve the referenced post URL from `get_posts` and insert the lexical link node now, before calling the Ghost API. Plain-text references are not acceptable. (err-20260915T154324-VTPMUJ) |

Log the result (reading `errors`/`warnings` back from the skill's response):
```
[Gate 2] Word count: N (limit: 300-500 or 1500-2000)
[Gate 2] Post-arc elements present: Hook ✓ Story ✓ Insight ✓ Challenge ✓
[Gate 2] Em-dash scan: clean
[Gate 2] Voice original (not source paraphrase): ✓
[Gate 2] Tags: {tag names} — all on locked list, object format confirmed
[Gate 2] Image: landscape confirmed, CDN url set
[Gate 2] Image geography: {confirmed match to {city} | n/a — post not geo-specific}
[Gate 2] Internal links: {lexical link node inserted for "{prior post title}" | n/a — no related published post}
[Gate 2] PASS — proceeding to Ghost draft creation.
```

If `schema-validator` returns `valid: false`, log `[Gate 2] FAIL — <errors list>` and remediate
(fix the draft, or correct the boolean you fed in if your own judgment call was wrong on
re-read) before re-running the gate. Do not call the Ghost API with a draft that hasn't passed
Gate 2 (`valid: true`).

---
<!-- system:end -->
