---
date: 2026-07-13
topic: Systemic Compliance Executive Brief PDF
status: complete
---

# Systemic Compliance Executive Brief

Converted `accounts/Systemic Compliance/sc-platform-executive-brief.html` to a branded PDF.

## Final Output
- `accounts/Systemic Compliance/sc-platform-executive-brief.pdf` — 5-page PDF, 500KB
- `accounts/Systemic Compliance/sc-platform-executive-brief.html` — source HTML (updated with all fixes)

## Changes Made to HTML
- Replaced `--teal: #0f9d8f` with Improving Blue `#005596` throughout
- Added `@media print` CSS: forced 3-col goals grid, 2-col risk/brief grids, fixed diagram box widths to prevent overflow
- Footer: "Systemic Compliance Platform Strategy Brief / Prepared by Improving · Confidential" + real Improving logo (base64 PNG from improving-brand skill assets)

## PDF Generation
- Chrome headless via osascript: `file://` URI pointing to OneDrive copy of HTML
- Flags: `--no-pdf-header-footer --no-margins`
- Source HTML must be on Mac filesystem (not /tmp/) for Chrome to access it

## Key Lessons
- PowerBI DOM virtualization requires physical scrolling to load all rows — can't programmatically switch slicers
- `sc-executive-brief-branded.html` in IES root is a temp working copy for Chrome; source of truth is in `accounts/Systemic Compliance/`
- Improving logo: `skills/improving-brand/assets/logos-png/logo-full-blue.png` — base64-encode and embed; external URLs redirect to HTML
