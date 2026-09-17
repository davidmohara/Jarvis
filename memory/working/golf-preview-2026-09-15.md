# Golf Preview Fallback — 2026-09-15

**Generated:** 2026-09-15 00:04 CT (Slack delivery unavailable; fallback written)

## Target Weekend: Sept 25–27, 2026

- **Friday, Sept 25:** Conditional — Calendar unavailable
- **Saturday, Sept 26:** Conditional — Calendar unavailable
- **Sunday, Sept 27:** Conditional — Calendar unavailable

## Data Source Issues

⚠️ **Calendar:** M365 connector offline — could not verify conflicts
⚠️ **Weather:** API unreachable — could not fetch forecast

## Recommendation

**No viable booking recommendation can be made this week.** Both the calendar conflict check and weather forecast are required to generate confident golf window recommendations, and both systems are unavailable.

**Action required:** Manual review before the golf-booking workflow runs at midnight.

1. Check your calendar for conflicts on **Sept 25–27** (especially Friday afternoon travel, Saturday/Sunday dinner plans)
2. Check the **Frisco TX weather** forecast for that weekend
3. Reply to this message with preferred date/time, or golf-booking will not book

**Fallback booking:** If you have a preferred window in mind, just reply to this summary and we'll book it.

---

*This is a degraded run of the golf preview workflow — both primary data sources unavailable. File exists: `workflows/golf-booking/preview-output.json` (empty options, documented reason).*
