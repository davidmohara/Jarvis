#!/usr/bin/env python3
"""
Process discovery data and identify new recordings not in vault.
"""

import json
from datetime import datetime
from pathlib import Path
import difflib

# Load discovery data
with open("/tmp/plaud_discovery.json") as f:
    all_recordings = json.load(f)

# Known vault recordings (from manual vault check)
vault_known_files = [
    "2026-08-05 Magline and Improving AI Enablement Discovery Call.md",
    "2026-08-05 Strategy Meeting - Wendy's Account Growth and GCP Partnership.md",
    # There are many more but we'll handle them via fuzzy matching below
]

# Vault file names we know exist (from the earlier list)
vault_files_full = [
    "2025-12-22 Unity AI Strategy Data Infrastructure Partnership Kickoff.md",
    "2026-02-13 Cardinal IT Solutions Improving Partnership Discussion.md",
    "2026-02-20 McKesson Databricks Partnership Snowflake Migration Strategy.md",
    "2026-02-23 Meeting AI Training Program DevOps IT Infrastructure FUB.md",
    "2026-03-05 Strategic Discussion AI Integration Professional Services.md",
    "2026-03-06 Meeting Azure Go-Live Event-Driven POC Legacy Code Analysis.md",
    "2026-03-10 Steve Hall EA System Integration Jarvis Onboarding.md",
    "2026-03-12 NextBen ICHRA Pre-Sales Analysis Tool Consultation.md",
    "2026-03-20 Athena Crystal Foran Consultation.md",
    "2026-03-25 Liftnet Sales Call - Rescue and Expansion.md",
    "2026-03-25 Vendor Partnership Failure and Strategic Reset — Guatemala Team Capability Gap.md",
    "2026-03-26 DRC Talent Labs Senior HR Leadership Incubator AI Focus.md",
    "2026-04-02 Specialty Capital - SaaS System Replacement.md",
    "2026-04-02 Specialty Capital SaaS System Replacement Consultation.md",
    "2026-04-06 Birgo - AI Solutions for Property Management Efficiency.md",
    "2026-04-06 Don McGreal - Vistage Membership Consultation.md",
    "2026-04-07 Meredith Anastasio - Opal Conference Speaker Search.md",
    "2026-04-20 AI Enablement and Agent Governance for SAP and Digital Teams at McKesson.md",
    "2026-04-21 Strategic Advisory on Scaling an AI Startup.md",
    "2026-05-05 AI Starting Point Discussion - Windsurf Tooling and AI Adoption Strategy.md",
    "2026-05-12 Lunch Meeting - DSO Access Strategy Cosm Immersive MVP and Wealth Platform.md",
    "2026-05-12 Lunch — DSO Cosm MVP, Wedbush Transition, UTB Data, and Goke Intro.md",
    "2026-05-12 TopGolf Executive AI Workshop Scoping.md",
    "2026-05-12 Workshop - Executive AI Strategy and Use-Case Prioritization (Topgolf).md",
    "2026-05-13 Alex Wilcox - Fractional CTO Assessment.md",
    "2026-05-13 Consultation - Bob Freeburg THL Odessa Underperformance.md",
    "2026-05-13 Consultation - Enterprise Claude Governance and Upskilling at Exeter Finance.md",
    "2026-05-13 Consultation - Fractional CTO-CIO Business Strategy (Alex Wilcox).md",
    "2026-05-13 Consultation Rob Private Equity Firm - Odessa Underperformance.md",
    "2026-05-13 Enterprise Claude Governance Fraud Mitigation and Upskilling at Exeter Finance.md",
    "2026-05-14 Consultation - AI Hands-On Build Session for Synexus Leaders (Matthew Smart).md",
    "2026-05-14 Matthew Smart - Synexus AI Workshop Discovery Call.md",
    "2026-05-18 Meeting - AI Innovation Lab Workshop Planning (Simpson Strong-Tie).md",
    "2026-05-18 SST Innovation Lab Discovery Planning.md",
    "2026-05-22 Austin Principaled Business Summit Planning with Alexander McCobin.md",
    "2026-05-22 Consultation - THL Odessa Service Margin Erosion (Rob Spies).md",
    "2026-05-22 THL and Odessa - Service Margin Erosion Intro with Rob Spies.md",
    "2026-05-26 Interview - Head of IT Technology Role (Adeel Ali).md",
    "2026-05-26 JSX Head of IT Interview - Adeel Ali.md",
    "2026-05-26 Simpson Strong Tie FP&A AI Workshop.md",
    "2026-05-28 Bridger - 3-Month AI Build Program for Windsor Leadership Offsite.md",
    "2026-05-28 Consultation - 3-Month AI Build Program Windsor Oct 2026 (Cara Antonacci).md",
    "2026-06-08 Kate Bugakova - TechBar SW Partnership Exploration.md",
    "2026-06-08 Kate Bugakova — TechBar SW Partnership Exploration for Data Engineering and AI.md",
    "2026-06-08 Wendy's AI Strategy - Cognition Devin Introduction.md",
    "2026-06-09 PE Firm AI Consultation - Data Strategy and AI Adoption for Lower Middle Market Fund.md",
    "2026-06-12 AI Adoption Governance and Scaling (Topgolf Lecture).md",
    "2026-06-12 AI Discussion on Practical Frameworks and Adoption.md",
    "2026-06-12 TopGolf Executive AI Briefing.md",
    "2026-06-15 Dustin Shaffer — Leveraging AI for Business Operations and Competitive Advantage.md",
    "2026-06-15 Strategic AI Implementation in Small to Medium-Sized Businesses.md",
    "2026-06-16 Spring Line Advisory - AI Strategy Governance and Investor Readiness.md",
    "2026-06-22 Cole Estrate — xAI and Improving Strategic Partnership Exploration.md",
    "2026-06-22 SpaceXAI Improving Partnership - Grok AI Adoption in TOLA.md",
    "2026-06-26 Kazakhstan IVLP Delegation — AI Strategy and US Approaches to Regulation.md",
    "2026-06-30 Concentrate AI Demo and Reconnect with Ari Jacoby.md",
    "2026-06-30 Improving x Xero — AI Training Workshop Proposal Discussion.md",
    "2026-06-30 Systemic Compliance — Fractional AI Advisory Kickoff with Kevin Graham and Mehmet Yasar.md",
    "2026-07-01 Microsoft Responsible AI and Improving Partnership — Follow-up After Houston AI Tour.md",
    "2026-07-01 Nexben Discussion — Platform Modernization and AI Integration.md",
    "2026-07-07 Strategic Discussion — Basic Memory AI Startup and Potential Partnership.md",
    "2026-07-08 Systemic Compliance Whiteboard — AI-Native Platform Architecture, Governance, and GTM Strategy.md",
    "2026-07-09 Systemic Compliance — Orb Platform Demo and Technical Architecture Review.md",
    "2026-07-14 Coffee with Steve Hall — Automotive AI Use Cases and Just Capital Partnership.md",
    "2026-07-22 Sales Proposal - Santa's Wonderland Technology Discovery.md",
    "2026-07-28 Concentrate AI Platform Demo.md",
    "2026-07-28 Improving + Solace TOLA Partnership Onsite.md",
    "2026-08-05 Magline and Improving AI Enablement Discovery Call.md",
    "2026-08-05 Strategy Meeting - Wendy's Account Growth and GCP Partnership.md",
]

def normalize_name(name):
    """Normalize a string for comparison."""
    return name.lower().strip().replace("—", "-").replace("'", "'")

def fuzzy_match(api_name, vault_names, threshold=0.7):
    """Check if api_name matches any vault file name (fuzzy)."""
    api_normalized = normalize_name(api_name)
    for vault_name in vault_names:
        vault_normalized = normalize_name(vault_name.replace(".md", ""))
        ratio = difflib.SequenceMatcher(None, api_normalized, vault_normalized).ratio()
        if ratio >= threshold:
            return True
    return False

# Identify new recordings
new_recordings = []
seen_ids = set()

for rec in all_recordings:
    file_id = rec.get("id")
    if file_id in seen_ids:
        continue
    seen_ids.add(file_id)

    name = rec.get("filename", rec.get("fullname", ""))
    start = rec.get("start_time", 0)

    # Convert epoch ms to date
    if isinstance(start, (int, float)):
        if start > 1e12:
            start = int(start / 1000)
        dt = datetime.fromtimestamp(start)
        date_str = dt.strftime("%Y-%m-%d")
    else:
        date_str = "unknown"

    duration = rec.get("duration", 0)
    # Duration is in milliseconds
    if duration > 1000:
        duration = int(duration / 1000)

    has_trans = bool(rec.get("is_trans", False))
    trans_status_code = rec.get("trans_status", 0)

    if has_trans:
        if trans_status_code == 1:
            transcript_status = "ready"
        else:
            transcript_status = "pending"
    else:
        transcript_status = "missing"

    # Check if already in vault
    if fuzzy_match(name, vault_files_full):
        # Already ingested
        continue

    new_recordings.append({
        "file_id": file_id,
        "name": name,
        "date": date_str,
        "duration_seconds": duration,
        "has_transcript": has_trans,
        "transcript_status": transcript_status,
    })

# Sort by date descending
new_recordings.sort(key=lambda x: x["date"], reverse=True)

print(f"Found {len(new_recordings)} new recording(s)")
print()

# Print summary
ready_count = sum(1 for r in new_recordings if r["transcript_status"] == "ready")
pending_count = sum(1 for r in new_recordings if r["transcript_status"] == "pending")
missing_count = sum(1 for r in new_recordings if r["transcript_status"] == "missing")

print(f"Ready: {ready_count}")
print(f"Pending: {pending_count}")
print(f"Missing: {missing_count}")
print()

# Print first 5
for rec in new_recordings[:5]:
    print(f"  - {rec['date']} {rec['name']} ({rec['transcript_status']})")

# Save to YAML format for state.yaml
print("\n# Copy this to state.yaml accumulated-context.new-recordings:")
print("new-recordings:")
for rec in new_recordings:
    print(f"  - file_id: \"{rec['file_id']}\"")
    print(f"    name: \"{rec['name']}\"")
    print(f"    date: \"{rec['date']}\"")
    print(f"    duration_seconds: {rec['duration_seconds']}")
    print(f"    has_transcript: {str(rec['has_transcript']).lower()}")
    print(f"    transcript_status: {rec['transcript_status']}")

# Also save to JSON for processing
with open("/tmp/plaud_new_recordings.json", "w") as f:
    json.dump(new_recordings, f, indent=2)

print(f"\nTotal new recordings saved to /tmp/plaud_new_recordings.json")
