#!/usr/bin/env python3
"""Systemic Compliance call prep PDF — with Devlin's architecture notes."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY

BLUE = colors.HexColor('#0077C8')
WHITE = colors.white
LIGHT_BLUE = colors.HexColor('#E8F4FC')

margin = 0.6 * inch
PAGE_W = letter[0] - 2 * margin

doc = SimpleDocTemplate(
    "/sessions/vigilant-quirky-wright/mnt/IES/meetings/Systemic Compliance.pdf",
    pagesize=letter,
    leftMargin=margin, rightMargin=margin,
    topMargin=margin, bottomMargin=margin,
)

styles = getSampleStyleSheet()

hdr_inner = ParagraphStyle('HdrInner', parent=styles['Normal'],
    fontSize=10, textColor=WHITE, fontName='Helvetica-Bold', leading=14, alignment=TA_LEFT)
body = ParagraphStyle('Body', parent=styles['BodyText'],
    fontSize=8.5, textColor=colors.black, spaceAfter=3, leading=11, alignment=TA_JUSTIFY)
bullet = ParagraphStyle('Bullet', parent=styles['BodyText'],
    fontSize=8.5, textColor=colors.black, spaceAfter=2, leading=11, leftIndent=12)
label = ParagraphStyle('Label', parent=styles['BodyText'],
    fontSize=8.5, fontName='Helvetica-Bold', textColor=colors.black, leading=11)

def hdr(title):
    p = Paragraph(title, hdr_inner)
    t = Table([[p]], colWidths=[PAGE_W])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BLUE),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    return t

def gap(n=0.08):
    return Spacer(1, n * inch)

def two_col_table(rows, col1=1.4*inch):
    data = [[Paragraph(f'<b>{r[0]}</b>', bullet), Paragraph(r[1], bullet)] for r in rows]
    t = Table(data, colWidths=[col1, PAGE_W - col1])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [WHITE, LIGHT_BLUE]),
    ]))
    return t

story = []

# ── MEETING AT A GLANCE ──────────────────────────────────────────────
story += [hdr("Meeting at a Glance"), gap()]
story += [two_col_table([
    ("Meeting",   "Systemic Compliance, LLC — Kick-off: Fractional AI-Driven Consulting"),
    ("Date",      "Tuesday, June 30, 2026 | In-person | 4:00 PM"),
    ("Status",    "SOW already signed — 16 hours across 3 months. This is a kick-off, not a pitch."),
    ("Attendees", "Kevin Graham (President/Founder, SC), Robin Graham (Kevin's wife, may attend), David O'Hara (Improving, Regional Director), Stephen Johnson (Improving VP, Houston)"),
    ("Purpose",   "Align on engagement scope, establish working rhythm, discuss roadmap for turning SC.ORB into a scalable, sellable asset."),
], col1=0.85*inch), gap()]

# ── THEIR COMPANY & PRODUCT ──────────────────────────────────────────
story += [hdr("Their Company & Product"), gap()]
story.append(Paragraph("Systemic Compliance, LLC — founded early 2025 by Kevin Graham. Product: <b>SC.ORB / SC.IMS</b> — AI-driven compliance tool built on Claude/Cowork (MVP stage). Two domains:", body))
story.append(Paragraph("• <b>OQ (Operator Qualification):</b> 49 CFR 192/195. Operators must qualify workers performing covered tasks. SC.ORB determines qualification status and maintains defensible records.", bullet))
story.append(Paragraph("• <b>API RP 1173 / PSMS:</b> Currently voluntary but PHMSA's March 2025 Federal Register filing signals shift toward mandatory. Kevin's regulatory tailwind.", bullet))
story.append(Paragraph("<b>The real moat (per Devlin):</b> Not the prompts — those are replaceable. The moat is the interconnectivity: <b>peer benchmarking across operators</b> and the <b>contractor equivalency engine</b>. Hard to copy and get stronger as more operators join.", body))
story.append(Paragraph("<b>Kevin's backstory:</b> Founded Veriforce 1998, sold 2009. Watched it go Thoma Bravo → Apax Partners, grow 6x through M&A, drift from pipeline-specific expertise into generic contractor management. Came back to build it right. Team: 175+ years combined pipeline safety experience including former PHMSA inspectors.", body))
story.append(gap())

# ── DEVLIN'S ROADMAP ────────────────────────────────────────────────
story += [hdr("Roadmap to a Sellable Asset (Devlin's 6 Steps)"), gap()]
steps = [
    ("1. Separate model from machine", "Anthropic supplies intelligence; SC's prompts, skills, and agents are theirs and port anywhere. Moving out of Cowork frees the IP from the Anthropic account so every consultant and client isn't living inside one seat."),
    ("2. Turn the crosswalk into a database", "The giant spreadsheet becomes the requirements store. Tag every requirement on the way in. This solves semantic saturation — where the model merges requirements that look alike (e.g., 192.31.4.c stitched with .b). Tagging on ingestion beats it."),
    ("3. Port to deployable framework", "Port skills and agents into a deployable framework, stand up a chat interface over the database. Keep a human making real edits to any AI-generated code so it stays copyrightable."),
    ("4. Build the evaluation harness", "Asking the AI to check its own work fails ~91% of the time. Proof of accuracy must come from outside the model: independent graders, datasets, edge-case test cases for ambiguous input and false-premise detection. This is also the sales weapon — hand a buyer two cases and prove it."),
    ("5. Watch for cognitive surrender", "The more SMEs watch the AI get it right, the less they catch when it doesn't. If a reviewer hasn't kicked anything back in 40 runs, that's a signal, not a clean bill of health. Track the kickback rate."),
    ("6. Move to active governance", "Output can't just be a report. PSMS is Plan-Do-Check-Act — the value is intervention before the compliance mistake, with KPIs trended over time to show improvement at granular level."),
]
story.append(two_col_table(steps, col1=1.5*inch))
story.append(gap())

# ── KSTG SEARCH ARCHITECTURE ────────────────────────────────────────
story += [hdr("KSTG Search Architecture (Know This)"), gap()]
story.append(Paragraph("As the corpus grows past what one model holds reliably, no single search method finds the right requirement. You combine four, traversed together:", body))
kstg = [
    ("Keyword (K)",   "Catches exact citations — the literal 49 CFR 192 reference."),
    ("Semantic (S)",  "Catches meaning and intent — the passage that satisfies a requirement without quoting it."),
    ("Temporal (T)",  "Catches what applied and when — handles grandfathering and effective dates so an asset is judged against the rules that governed it when built."),
    ("Graph (G)",     "Connective tissue — links, equivalencies, and peer relationships that power benchmarking and the contractor equivalency engine."),
]
story.append(two_col_table(kstg, col1=1.1*inch))
story.append(Paragraph("Run only K+S and you keep muddying similar requirements together. Add T+G and the system can tell them apart and reason across them. Same problem Devlin solved for biomedical and food research groups.", body))
story.append(gap())

# ── STRATEGIC FORK ──────────────────────────────────────────────────
story += [hdr("The Strategic Fork"), gap()]
fork = [
    ("Keep & Scale", "Build SC.IMS into value-priced software with consulting wrapped around it, collect long-tail recurring revenue. Moat holds if peer benchmarking and equivalency engine are built — those get stronger as more operators join."),
    ("Harvest IP",   "Harden it, sell into 15–20 bigger midstream players, take cash now. Right call if the moat erodes faster than you want to defend it. A knockoff will be in market by customer 15–20, so this is a 4-year harvest, not a 10-year annuity."),
    ("Both paths",   "Require the same first move: get SC.ORB out of Claude Cowork so it can be owned, audited, and sold."),
]
story.append(two_col_table(fork, col1=1.1*inch))
story.append(Paragraph('<b>The question to ask:</b> "Are you building something you want to run for the next decade, or proving it out and putting it in the right hands?" Don\'t push either direction. Kevin sold once — he knows what the PE treadmill costs.', body))
story.append(gap())

# ── TECHNICAL CONVERSATION TO OWN ───────────────────────────────────
story += [hdr("Technical Conversation to Own"), gap()]
tech = [
    ("Auditability",     "Every SC.ORB determination needs an immutable audit trail. PHMSA inspectors and attorneys will ask: what did the system decide, on what basis, who was responsible? Anthropic's Compliance API (Aug 2025) streams audit events into enterprise SIEM systems — the infrastructure layer SC.ORB needs."),
    ("Model independence","SC.ORB is tightly coupled to Claude. Production-grade needs a model-agnostic abstraction layer. Design it early — Devlin's architecture shows the agent orchestration layer calling the models, with the evaluation harness separate from the model."),
    ("Accuracy defense", "The eval harness is the sales weapon. Independent graders, SME kickback rates tracked and published, edge-case test cases. No OQ/PSMS competitor has this."),
    ("Regulatory defense","PHMSA requires operators to explain every covered task determination. AI as advisor with human sign-off, not sole decision-maker. SC.ORB flags, recommends, documents — qualified human approves."),
]
story.append(two_col_table(tech, col1=1.3*inch))
story.append(gap())

# ── THINGS KEVIN CAN STOP WORRYING ABOUT ────────────────────────────
story += [hdr("Things Kevin Can Stop Worrying About"), gap()]
stop = [
    ("Security",  "Claude Team account = 30-day retention, no training, data-private. The anonymizer is good belt-and-suspenders. The AI-use clause in their agreements is right. They're not putting clients at risk today."),
    ("IP",        "Sounds like a procedural walkthrough — process patent candidate. Counsel needed: someone who has been through the patent process and defended technology IP specifically. (Devlin offered Chris Haslick at Boyer Miller.)"),
    ("Taxes",     "This is R&D. If the work is capitalizable (built the asset, not day-to-day ops), time and development feed the R&D credit. Get the timesheet to Robin and capture it this year if pulling profit."),
]
story.append(two_col_table(stop, col1=1.0*inch))
story.append(gap())

# ── QUESTIONS TO ASK ────────────────────────────────────────────────
story += [hdr("Questions to Ask"), gap()]
qs = [
    ("Vision",      '"When you think about SC in 5 years, what does success look like for you personally?" — surfaces keep vs. sell without asking directly.'),
    ("Decision",    '"Are you leaning toward building a long-term platform or a harvested asset?" — you can ask this directly now that they\'re a client.'),
    ("SC.ORB today",'"What does SC.ORB currently do well, and where does it break down under pressure?" — calibrates where you start the roadmap.'),
    ("Moat check",  '"How far along is the peer benchmarking and equivalency engine?" — this is the actual moat per Devlin; its maturity determines which path makes sense.'),
    ("Kickback rate",'"What\'s your SME override rate been so far?" — tests their eval discipline before you introduce the concept.'),
]
story.append(two_col_table(qs, col1=1.0*inch))
story.append(gap())

# ── OBJECTIONS & HANDLES ─────────────────────────────────────────────
story += [hdr("Objections & Handles"), gap()]
objs = [
    ('"We\'ve built a lot already"', "Acknowledge it. Devlin confirmed: real IP, not yet a sellable asset. Improving closes that gap."),
    ('"Not sure keep vs. sell"',     "That uncertainty is exactly why the roadmap is the same first move regardless. Start there."),
    ('"What\'s the ROI?"',           "De-risking a multi-million-dollar outcome. The fee is a rounding error against the IP value."),
    ('"Won\'t this slow us down?"',  "Fractional advisory at your pace. 16 hours is a light touch — you own all decisions."),
]
story.append(two_col_table(objs, col1=1.4*inch))
story.append(gap())

# ── WATCH ITEMS ──────────────────────────────────────────────────────
story += [hdr("Watch Items"), gap()]
story.append(Paragraph("• SOW is signed. Don't pitch — facilitate. Your job is to establish the working rhythm and start the roadmap conversation.", bullet))
story.append(Paragraph("• Don't position Improving as a scale accelerator. Kevin knows what that treadmill costs. Position as the partner who helps him build the right thing.", bullet))
story.append(Paragraph("• PHMSA regulatory shift (ANPRM June 2025, Federal Register March 2025) is Kevin's tailwind — use it to frame urgency on the keep-and-scale path.", bullet))
story.append(Paragraph("• Robin Graham is Kevin's wife, may be present — not a primary decision driver.", bullet))
story.append(Paragraph("• Devlin's hallucination benchmark post: devlinliles.com/lies-lies-and-statistics — worth reading before the meeting.", bullet))

doc.build(story)

import os
path = "/sessions/vigilant-quirky-wright/mnt/IES/meetings/Systemic Compliance.pdf"
print(f"Done. {os.path.getsize(path)/1024:.1f} KB")
