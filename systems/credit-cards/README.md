# Credit Card Rewards Tracking System

**Owner**: Jarvis (automated)
**Controller**: David O'Hara
**Created**: 2026-02-14

## Files

| File | Purpose |
|------|---------|
| `card-registry.json` | Master record of all cards — rewards structures, benefits, fees, YNAB IDs |
| `benefits-tracker.json` | Real-time benefit usage, deadlines, ROI tracking per card |
| `optimization-guide.json` | Which card to use for each spending category + portfolio gaps |
| `README.md` | This file — system overview and operating procedures |

## How Jarvis Operates This System

### Data Sources
- **YNAB MCP** (4 cards): Amex Blue, Citi AAdvantage, Discover, Chase Sapphire — pull via API
- **Chrome login** (2 cards): Amex Platinum, Atlas Visa Infinite — ask David to log in, then Jarvis drives Chrome via AppleScript JS execution to read activity, benefits, and rewards pages directly
- **Statement parsing** (fallback): Upload PDF/XLSX statements if Chrome isn't available

### Chrome Capabilities
Jarvis can control Chrome via AppleScript JavaScript execution:
- Read page text content from any tab
- Switch between tabs
- Navigate to URLs
- Click buttons, fill forms, scroll pages
- Extract transaction data and benefit usage from issuer dashboards

**Setup required**: Chrome → View → Developer → Allow JavaScript from Apple Events (already enabled)

**Workflow for non-YNAB cards**: David logs in → tells Jarvis to read → Jarvis extracts data and updates tracker files

### Proactive Alerts
1. **Monthly**: Benefits usage check — flag unused credits before they expire
2. **Monthly**: Review card-linked offers on Chase Sapphire, Amex Platinum, and Amex BCP. Cross-reference against recent transaction history. Add any offers for vendors David uses. Flag high-value offers.
3. **Quarterly**: Discover 5% activation reminder + category optimization review
4. **Pre-travel**: Card selection guidance (FTX fees, lounge access, insurance)
5. **Before large purchases**: Best card recommendation + check for active card-linked offer
6. **Annual fee renewal**: ROI check 30 days before each renewal

### Review Cadence
- Monthly: Pull YNAB data, read Chrome dashboards, update benefits tracker, surface optimization opportunities
- Quarterly: Full portfolio review — ROI per card, category analysis, gap identification
- Annually: Renewal decisions — keep/cancel/product-change recommendations

### Key Numbers
- **Total annual fees (gross)**: $1,950 ($1,085 Amex Plat + $770 Citi + $95 Amex BCP)
- **Total annual fees (out-of-pocket)**: $865 (Amex Plat fully reimbursed by YPO Lone Star)
- **Total available credits**: $2,844/yr (Amex Plat $2,484 + Citi $360)
- **Break-even**: Already exceeded — $0 OOP for Amex Plat with $2,484 in credits
