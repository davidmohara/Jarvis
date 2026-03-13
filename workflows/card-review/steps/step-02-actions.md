---
step: 2
name: actions
description: Present action items and get David's decisions
next: step-03-update.md
---

# Step 2: Action Items & Decisions

## Process

### 1. Present Action Items

From the audit, surface all action items grouped by urgency:

**🔴 Expiring This Month**
- Credits that reset or expire at month-end
- Card-linked offers about to expire
- Rotating category activation deadlines

**🟡 Attention Needed**
- Credits with $0 usage
- Spend threshold pace concerns
- Annual fee renewals within 90 days

**🟢 Optimization Opportunities**
- New card-linked offers to add
- Category shifts (e.g., Discover Q2 categories announced)
- Portfolio gap recommendations

### 2. Get David's Decisions

For each action item, ask David:
- "Want me to add these card-linked offers?"
- "Should we schedule the Resy/lululemon/hotel credit usage?"
- "Any planned large purchases this month I should factor into threshold tracking?"

### 3. Check Data Freshness

Review `last_updated` field across all data files. If any file is >30 days stale:
- Flag it: "Card data is [X] days old. Want to do a site walkthrough to refresh?"
- If David says yes → trigger `card-walkthrough` workflow

## Completion

Proceed to `step-03-update.md`
