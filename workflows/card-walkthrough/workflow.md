---
name: card-walkthrough
description: Monthly guided walkthrough of card issuer portals to update benefit details, discover new offers, and refresh stale data
agent: chase
---

# Card Optimizer — Site Walkthrough

**Goal:** Keep card data fresh. Benefits change, offers rotate, policies update. The only way to stay current is to read the source — the issuer portals themselves.

**Agent:** Chase — Revenue & Pipeline (personal finance domain)

**Architecture:** Sequential per-card walkthrough. David logs in, Chase reads and extracts. Interactive — requires David's participation for login and navigation.

**Cadence:** Monthly, triggered after the benefits review when data is >30 days stale. Can also be triggered manually: "card walkthrough" or "update card benefits."

---

## INITIALIZATION

### Data Sources Required

| Source | What to Pull | Access Method |
|--------|-------------|---------------|
| Amex Platinum portal | Benefits status, credit usage, offers, MR balance | Chrome automation — David logs in |
| Amex BCP portal | Offers, cashback balance, category usage | Chrome automation — David logs in |
| Citi AAdvantage portal | Offers (283+), credit usage, miles balance | Chrome automation — David logs in |
| Chase portal | Offers, UR balance, account status | Chrome automation — David logs in |
| Discover portal | Rotating categories, cashback balance, offers | Chrome automation — David logs in |
| Atlas portal | Benefits status, points balance, dining rate | Chrome automation — David logs in |

### Input

Triggered by:
- "Card walkthrough"
- "Update card benefits"
- "Let's go through the card sites"
- Prompted by Chase after a stale-data flag in the monthly review

---

## EXECUTION

Read fully and follow: `steps/step-01-walkthrough.md`
