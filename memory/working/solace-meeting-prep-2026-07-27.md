---
date: 2026-07-27
session: cowork
type: work-summary
tags: [solace, meeting-prep, crm, energy, remarkable]
---

# Solace Meeting Prep — Session Summary

## What was built
- `Solace-MeetingPrep-2026-07-28.md` — full meeting prep sheet for tomorrow's Solace × Improving onsite
- `One Texas - Energy Accounts Prioritized v2.xlsx` — rebuilt energy accounts spreadsheet with CRM-verified activity data
- `Solace Meeting Prep.pdf` — pushed to reMarkable at `/Meetings`

## Key findings

### CRM Energy Accounts
- None of the original 18 CRM-exported energy accounts have activity in the past 2 years. The original export was a cold list.
- 14 CRM-active TOLA energy accounts identified via Dynamics 365 OData API (imp_lastactivitydate filter).
- Top accounts with closed-won history: NRG Energy, CP Chem, Newmont USA, EnergyHub, Venture Global LNG, ExxonMobil, Oceaneering, CPower, American Airlines, Charles Schwab.

### Solace Agenda (from Austin Ledesma, received today)
- Scope is broader than energy: also covers transportation/logistics (Alaska Airlines, Avelo Airlines), enterprise tech
- Named joint accounts: HP Inc. (TIBCO replacement), AT&T (legacy modernization), ExxonMobil (SAP + agentic AI), SLB (SAP + agentic AI)
- Other Solace customers to discuss: Halliburton, Baker Hughes, Charles Schwab
- Prospects: Kinetik (UNS), Alaska Airlines (TIBCO displacement), Avelo Airlines (SWIM)

### Improving's Energy Proof Points (for the room tomorrow)
- **NRG Energy**: AI DLP Program ($1.6M Apr 2026), multi-year Agile coach, SAP BDC — deepest energy relationship
- **CP Chem**: 3+ embedded consultants, ongoing since 2023, still active Jun 2026 — best proof of team delivery
- **Energy Worldnet**: Agentic AI workshop + AI Deep Learning Program + deal closed TODAY (Jul 27) — freshest AI credential
- **Newmont USA**: $3M+ SAP analytics engagement, Newcrest integration — strongest data/analytics story
- **EnergyHub**: Annual embedded Java/Python team renewals ~$500K/yr — steady managed team model
- **American Airlines**: Large Java/full-stack Loyalty team, $7.6M SOW, multi-year — strong non-energy story for transportation block

## Technical notes
- Dynamics 365 accessed via OData API through authenticated Chrome tab (Entra SSO workaround)
- Correct field for last activity: `imp_lastactivitydate` (not standard `lastactivitydate`)
- rmapi config was corrupted; cleared ~/.rmapi and re-authenticated successfully
