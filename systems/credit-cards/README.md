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

### Active Capabilities (Chase Agent)

| Capability | Trigger | Workflow | Description |
|------------|---------|----------|-------------|
| **Which Card?** | "card", "which card for X?", "buying [item]" | `workflows/card-which/` | Full-optimization card selection: category match, rotating categories, caps, spend thresholds, card-linked offers, active credits. Returns best card + reasoning. |
| **Monthly Benefits Review** | 1st of month @ 9 AM (scheduled) or "card review" | `workflows/card-review/` | Audit all benefit extraction. Dashboard of used/remaining credits, expiring deadlines, rotating category status, spend threshold pace, card-linked offer savings. Surfaces action items. |
| **Site Walkthrough** | "card walkthrough" or prompted after stale data flag | `workflows/card-walkthrough/` | Guided walkthrough of each card portal with David. Reads pages via Chrome, extracts current data, compares to stored values, updates all data files. |

### Proactive Alerts
1. **Monthly (scheduled)**: Full benefits review — credit usage audit, expiring credits, rotating category check, spend threshold pace, card-linked offer review
2. **Monthly (after review)**: Site walkthrough prompt when data is >30 days stale
3. **On purchase**: Best card recommendation with full optimization (category, caps, thresholds, offers, credits)
4. **Pre-travel**: Card selection guidance (FTX fees, lounge access, insurance)
5. **Annual fee renewal**: ROI check 30 days before each renewal — routed to Chief for briefing

### Review Cadence
- **Monthly**: Scheduled benefits review (1st of month) + portal walkthrough to refresh data
- **Quarterly**: Rotating category activation + full portfolio ROI review
- **Annually**: Renewal decisions — keep/cancel/product-change recommendations

### Key Numbers
- **Total annual fees (gross)**: $1,950 ($1,085 Amex Plat + $770 Citi + $95 Amex BCP)
- **Total annual fees (out-of-pocket)**: $865 (Amex Plat fully reimbursed by YPO Lone Star)
- **Total available credits**: $2,844/yr (Amex Plat $2,484 + Citi $360)
- **Break-even**: Already exceeded — $0 OOP for Amex Plat with $2,484 in credits
