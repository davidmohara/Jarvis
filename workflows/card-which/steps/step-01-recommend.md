---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
---

---
step: 1
name: recommend
description: Analyze the purchase and return the optimal card with full reasoning
---

# Step 1: Recommend Best Card

## Process

### 1. Identify the Purchase Category

Parse the user's input to determine:
- **Vendor** (if named) — check for active card-linked offers
- **Category** — map to one of the categories in `optimization-guide.json`
- **Amount** (if stated) — relevant for spend thresholds and large-purchase bonuses
- **Location** — domestic vs. international (affects FTX fee cards)

### 2. Check Category Match

Read `optimization-guide.json` → `card_selection_guide.categories`. Find the matching category. Note the `best_card` and `runner_up`.

### 3. Check Rotating Categories

Read `card-registry.json` → `discover-it.rotating_categories`. Is the current quarter's category relevant? Is it activated?

If the purchase falls into Discover's active rotating category AND is under the $1,500/quarter cap, Discover at 5% may beat the default recommendation.

### 4. Check Annual/Quarterly Caps

For cards with spending caps:
- **Amex BCP grocery**: $6,000/year at 6%, then drops to 1%. Read `benefits-tracker.json` to check YTD grocery spend.
- **Discover rotating**: $1,500/quarter at 5%. Check quarter spend to date.

If a cap is hit or close, switch to runner-up.

### 5. Check Spend Thresholds

Read `benefits-tracker.json` → `spend_threshold_tracker`:
- **Amex Plat $75K**: If David is behind pace, consider routing discretionary spend to Plat to close the gap (unlocks Centurion guest access + Sky Club).
- Only recommend this if the purchase is large enough to matter AND the category earn rate difference is small (e.g., 1x vs. 1x — no loss).

### 6. Check Card-Linked Offers

Read `benefits-tracker.json` → `card_linked_offers` for all cards. Search for the vendor name. If an active offer exists:
- Factor the cashback/credit into the total return calculation
- If the offer is on a different card than the category winner, calculate which yields more:
  - Category card earn rate vs. offer card earn rate + offer bonus

### 7. Check Active Credits

Read `benefits-tracker.json` → `benefits_usage`. Does this purchase qualify for an existing credit?
- Dining at a Resy restaurant → Amex Plat Resy credit ($100/quarter)
- Grubhub → Citi $10/mo credit
- Lyft → Citi $10/mo credit (after 3 rides)
- Streaming → Amex BCP 6% + possible Amex Plat digital entertainment credit
- Lululemon → Amex Plat $75/quarter credit

If a credit applies, it may override the category recommendation.

### 8. International Check

If the purchase is international or online from a foreign merchant:
- **NEVER** use Amex BCP (2.7% FTX fee)
- Prefer: Citi AAdvantage, Amex Plat, or Atlas (all no FTX)

## Output Format

```
**Use: [Card Name]**
- Earn rate: [X% / Xx]
- Why: [1-sentence reason]
- Stacking: [any card-linked offer or credit that applies]
- Note: [any cap warning, threshold opportunity, or alternative]
```

Keep it tight. David doesn't want a dissertation — he wants a card name and a reason.

## Completion

No file updates needed. This is a read-only decision.
