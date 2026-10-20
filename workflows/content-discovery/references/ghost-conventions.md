<!-- personal:start -->
# GHOST BLOG CONVENTIONS

These are locked. Do not deviate.

## Author
- Always: David O'Hara — ID `68a3465b9e3561027e745c51`

## Images
- **Source:** Unsplash. Search for a thematic image matching the post's core concept.
- **URL format:** `https://images.unsplash.com/photo-{id}?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid={ixid}&ixlib=rb-4.1.0&q=80&w=2000`
- **feature_image:** Unsplash URL at w=2000
- **twitter_image:** Same URL as feature_image
- **og_image:** Leave null (Ghost generates automatically)
- **How to set:** Use `mcp__ghost-blog__upload_image_from_url` to upload the Unsplash image to Ghost's CDN first, then use the returned Ghost URL for both feature_image and twitter_image. If the upload fails, use the Unsplash URL directly — Ghost accepts external URLs for feature_image.
- **Finding Unsplash images:** `mcp__workspace__web_fetch` has a provenance restriction and cannot directly fetch `unsplash.com/s/photos/...` search pages. Use WebSearch first to find a photo URL, then web_fetch the specific photo page to extract the image ID. Full protocol in step-01-discover.md Step 6.

## Tags — LOCKED LIST (no new tags ever)
Select 1-3 that best match the post content. IDs are required for the Ghost API.

> **Ghost API format — CRITICAL:** Tags must be passed as objects, not bare strings.
> ✅ `[{"id": "637ea17e92f3300211b1b23a"}]` — links existing tag
> ❌ `["637ea17e92f3300211b1b23a"]` — creates a new tag named after the ID string

| Tag Name | ID | Slug |
|----------|-----|------|
| quotes | 637ea17e92f3300211b1b232 | quotes |
| leadership | 637ea17e92f3300211b1b233 | leadership |
| thoughts | 637ea17e92f3300211b1b234 | thoughts |
| purpose | 637ea17e92f3300211b1b235 | purpose |
| life | 637ea17e92f3300211b1b236 | life |
| speaking | 637ea17e92f3300211b1b237 | speaking |
| culture | 637ea17e92f3300211b1b238 | culture |
| improving | 637ea17e92f3300211b1b239 | improving |
| business | 637ea17e92f3300211b1b23a | business |
| family | 637ea17e92f3300211b1b23b | family |
| excel | 637ea17e92f3300211b1b23c | excel |
| scrum | 637ea17e92f3300211b1b23d | scrum |
| agile | 637ea17e92f3300211b1b23e | agile |
| life-hack | 637ea17e92f3300211b1b23f | life-hack |
| apps | 637ea17e92f3300211b1b240 | apps-tag |
| startup | 637ea17e92f3300211b1b241 | startup |
| rant | 637ea17e92f3300211b1b242 | rant |
| math | 637ea17e92f3300211b1b245 | math |
| trust | 637ea17e92f3300211b1b246 | trust |
| systems thinking | 637ea17e92f3300211b1b247 | systems-thinking |
| conscious capitalism | 637ea17e92f3300211b1b248 | conscious-capitalism |
| sleep | 637ea17e92f3300211b1b249 | sleep |
| mental health | 637ea17e92f3300211b1b24a | mental-health |
| reading | 63c81c6d24f5700210f5ff40 | reading |
| productivity | 63e690387be05d0210064e74 | productivity |
| home projects | 63ebffad2b325802108f5dc5 | home-projects |
| growth | 6400ce1602619502100d3829 | growth |
| fun | 64134647b7e99a0210e5ef27 | fun |
| drone | 64134647b7e99a0210e5ef28 | drone |
| money | 641347f9b7e99a0210e5ef3c | money |
| health | 6414657b52d80f02106903de | health |
| wellness | 6414657b52d80f02106903df | wellness |
| functional medicine | 649470141bafd60209f035d9 | functional-medicine |
| thinking | 64c16e007b788102090a5064 | thinking |
| communication | 64c16e007b788102090a5065 | communication |
| Writing | 66354da2f8a84d01391b72e9 | writing |
| AI | 68fbc4d89e3561027e745c91 | ai |
| technology | 68fbc4d89e3561027e745c92 | technology |

**GATE 2 (Content Schema Validation) checks the drafted post against tag-list membership, word count, voice rules, and the four-arc-element requirement above before any Ghost API call.**

## Post Status Flow
1. This workflow (content-discovery) creates the post with `status: draft` — never published on creation.
2. Publishing is external: David publishes, schedules, or deletes drafts directly in Ghost. Content-discovery (step-01 Step 1a, daily) and content-approval (on demand) resync `pending-drafts.json` against live Ghost state to reflect it — no workflow publishes on his behalf.
<!-- personal:end -->
