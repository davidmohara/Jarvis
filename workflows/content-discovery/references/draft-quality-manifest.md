<!-- system:start -->
# Draft-Quality Manifest Schema (content-discovery step-01, task 6b)

One JSON object, one entry in `posts` per post drafted this run (URL PATH, DIGEST PATH, and IMPROVING BLOG PATH alike). Write the file even when zero posts were drafted — an empty `posts` list is a valid, passing record:

```json
{
  "run_date": "YYYY-MM-DD",
  "posts": [
    {
      "title": "{Post Title}",
      "body": "{full draft text}",
      "source_text": "{the feeder digest/article text this draft was built from}",
      "is_voice_original": true,
      "feature_image": "{feature_image URL}",
      "image_landscape": true,
      "image_search_query": "{the Unsplash search query used in Step 6}",
      "geo_specific": false,
      "post_city": null,
      "image_geo_confirmed": true,
      "related_published_post": null,
      "internal_links": []
    }
  ]
}
```

Field rules (these are what the eval-harness `draft_quality` assertions read — a missing or non-compliant field FAILS the run):

- `body` and `source_text` are both required — they are the evidence for the voice check. `source_text` is the digest section text or the fetched article's prose the draft was built from.
- `is_voice_original` — your Gate 2 judgment, recorded as a plain boolean. `false` fails the run.
- `image_landscape` — the Step 6 `w > h` pixel check result. `false` fails the run.
- `image_search_query` — the exact query used. When `geo_specific` is `true`, `post_city` is required and the query must contain the city name (err-20260915T154324-4DLWA4).
- `image_geo_confirmed` — `true` when the post is not geo-specific, OR when a geo-specific post's image location was verified. `false` on a geo-specific post fails the run.
- `related_published_post` — the canonical URL of a related published Ghost post, or `null` when none exists.
- `internal_links` — every hyperlink URL built into the draft's lexical body. When `related_published_post` is set, its URL must appear here (err-20260915T154324-VTPMUJ).

Use `mcp__Desktop_Commander__write_file`. This manifest is the machine-readable counterpart to the `[Gate 2]` log lines above; both are required.

---
<!-- system:end -->
