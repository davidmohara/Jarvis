<!-- system:start -->
### 6. Source the feature image

Identify the single most important high-level keyword from the post (e.g., "leadership", "resilience", "cost", "writing" — conceptual, not literal). Search Unsplash:

> **IMPORTANT:** `mcp__workspace__web_fetch` has a provenance restriction — it only fetches URLs that appeared in a prior user message or web_fetch result. Direct fetches to `unsplash.com/s/photos/...` will fail. Always use the two-step process below.

1. **Run a WebSearch** for: `unsplash {keyword} landscape photo site:unsplash.com/photos`
2. From the search results, pick a free (non-Unsplash+) photo URL — look for results where the title says "Free ... Image on Unsplash". Avoid results that mention "Unsplash+" or "premium".
3. **Fetch the photo page** with `mcp__workspace__web_fetch` using the exact URL returned by the search — this unlocks it for the provenance check.
4. From the fetched page, extract the photo ID from the `og:image` or `twitter:image` meta tag. The ID appears as `photo-{PHOTO_ID}` in the URL.
5. Construct the Unsplash CDN URL:
```
https://images.unsplash.com/photo-{PHOTO_ID}?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid={IXID}&ixlib=rb-4.1.0&q=80&w=2000
```
Use the ixid from the meta tag URL if available; omit the ixid parameter if not — it's optional.

**Image selection rules:**
- Must be landscape-oriented (wider than tall). No portrait-oriented images. Ever.
- Must be thematically aligned with the post's core concept — not just generically "professional." A post about auditing should show paperwork, spreadsheets, or financial review. A post about purpose/fulfillment should show open space, horizon, or journey imagery. A post about AI governance should show systems/infrastructure. Match the metaphor, not just the industry.
- **If the post is geographically specific (names a city, region, or country in the title or hook), the image search query MUST include that location name.** A generic city skyline is not acceptable for a post about Dallas or DFW — search for "unsplash dallas skyline landscape photo site:unsplash.com/photos" or equivalent. After selecting a candidate, inspect the photo's title and description on the fetched Unsplash page to confirm the location matches before accepting. (err-20260915T154324-4DLWA4)
- Avoid portraits of people as the primary subject
- Must be free (no Unsplash+ license required)
- If the first candidate is premium (Unsplash+), portrait, or geographically wrong, discard it and try the next search result — do not settle

> **MANDATORY — verify orientation from the actual pixels, never from the title, alt text, or search category.** Unsplash titles like "a long road with a mountain in the background" or category tags do not reliably indicate orientation — the same photo can be a portrait crop. (See err-20260715T195437-E6MUV6: a "long road / mountain" photo was used and turned out to be 2000x3000, portrait, because the title was trusted instead of the image.)
>
> Before accepting any candidate, fetch it and check real width vs. height via Desktop Commander:
> ```python
> import requests
> from io import BytesIO
> from PIL import Image
> r = requests.get(candidate_url, timeout=20)
> w, h = Image.open(BytesIO(r.content)).size
> assert w > h, f"portrait ({w}x{h}) — discard and try next candidate"
> ```
> If `w <= h`, discard the candidate and move to the next search result. Do not construct the final CDN URL or use the image in Ghost until this check passes.

Upload to Ghost CDN:
```
mcp__ghost-blog__upload_image_from_url(
  url="{unsplash_url}",
  filename="{post-slug}",
  purpose="image"
)
```

Use the returned Ghost CDN URL for both `feature_image` and `twitter_image`.

---
<!-- system:end -->
