#!/usr/bin/env python3
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
import os

margin = 0.6 * inch
output_path = "/sessions/vigilant-quirky-wright/mnt/IES/meetings/Systemic Compliance.pdf"
doc = SimpleDocTemplate(
    output_path,
    pagesize=letter,
    leftMargin=margin,
    rightMargin=margin,
    topMargin=margin,
    bottomMargin=margin,
)

story = []
styles = getSampleStyleSheet()

header_style = ParagraphStyle(
    'CustomHeader',
    parent=styles['Heading1'],
    fontSize=11,
    textColor=colors.black,
    spaceAfter=6,
    fontName='Helvetica-Bold',
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=9,
    textColor=colors.black,
    spaceAfter=4,
    leading=11,
    alignment=TA_JUSTIFY,
)

bullet_style = ParagraphStyle(
    'CustomBullet',
    parent=styles['BodyText'],
    fontSize=9,
    textColor=colors.black,
    spaceAfter=3,
    leading=11,
    leftIndent=15,
)

story.append(Paragraph("Meeting at a Glance", header_style))
glance_items = [
    "<b>Meeting:</b> Systemic Compliance, LLC — Kick-off: Fractional AI-Driven Consulting",
    "<b>Date:</b> Tuesday, June 30, 2026 | In-person",
    "<b>Setup:</b> David running solo",
    "<b>Attendees:</b> Kevin Graham (President/Founder, SC), Robin Graham (Kevin's wife, may be present), David O'Hara (Improving, Regional Director), Stephen Johnson (Improving VP, Houston)",
    "<b>Purpose:</b> Align on engagement scope, establish working relationship, discuss roadmap for turning SC.ORB into a scalable, sellable asset",
]
for item in glance_items:
    story.append(Paragraph(item, body_style))
story.append(Spacer(1, 0.15 * inch))

story.append(Paragraph("Their Company &amp; Product", header_style))
company_text = [
    "Systemic Compliance, LLC — founded early 2025 by Kevin Graham.",
    "Product: SC.ORB — AI-driven compliance tool built on Claude/Cowork (MVP stage). Two compliance domains:",
    "• <b>OQ (Operator Qualification):</b> Federal requirement under 49 CFR 192/195. Pipeline operators must qualify workers performing covered tasks. SC.ORB helps determine qualification status and maintain defensible records.",
    "• <b>API RP 1173 / PSMS:</b> Currently voluntary but PHMSA's March 2025 Federal Register filing signals shift toward mandatory. This is Kevin's regulatory tailwind.",
    "Team includes former PHMSA inspectors, accident investigators, pipeline operators, regulatory committee members — 175+ years combined pipeline safety experience.",
    "Kevin's backstory: Founded Veriforce 1998, sold 2009. Watched it go through Thoma Bravo (2019, 6x growth through M&amp;A) then Apax Partners (2024). Drifted from pipeline-operator-specific expertise into generic contractor management. He came back to build what he would have built if PE hadn't taken it elsewhere.",
]
for text in company_text:
    story.append(Paragraph(text, body_style))
story.append(Spacer(1, 0.15 * inch))

story.append(Paragraph("Technical Conversation to Own (4 Dimensions)", header_style))
tech_items = [
    "<b>1. Auditability:</b> Every SC.ORB determination needs an immutable audit trail. PHMSA inspectors and attorneys will ask: what did the system decide, on what basis, who was responsible? Anthropic's Compliance API (launched Aug 2025) streams audit events into enterprise SIEM systems — the infrastructure layer SC.ORB needs to build toward.",
    "<b>2. Model Independence:</b> SC.ORB is currently tightly coupled to Claude. Production-grade needs a model-agnostic abstraction layer. Improving's role: design that architecture early.",
    "<b>3. Accuracy Defensibility:</b> The sales weapon. Independent graders evaluate SC.ORB outputs against known-correct determinations. SME kickback rates tracked and published. Edge cases documented and tested. No OQ/PSMS competitor has this. Kevin's domain credibility makes it believable; Improving's eval architecture makes it verifiable.",
    "<b>4. Regulatory Defensibility:</b> PHMSA's OQ rule requires operators to explain every covered task determination. AI as advisor with human sign-off, not sole decision-maker. SC.ORB flags, recommends, documents — qualified human approves.",
]
for item in tech_items:
    story.append(Paragraph(item, body_style))
story.append(Spacer(1, 0.15 * inch))

story.append(Paragraph("The Strategic Fork", header_style))
fork_items = [
    "Keep and Scale: Build production-grade, auditable, deployable platform. Longer engagement, growing scope.",
    "Harvest IP: Package IP for acquirers. Shorter, focused engagement around productization and go-to-market narrative.",
    "The Question: When you think about what you want this to become — are you building something you want to run for the next decade, or building something you want to prove out and put in the right hands?",
    "Framing: Don't push Kevin toward either path. Kevin sold once — he knows what the PE treadmill costs. Pitch Improving as the partner who helps him build the right thing, not the biggest thing.",
]
for item in fork_items:
    story.append(Paragraph("• " + item, bullet_style))
story.append(Spacer(1, 0.15 * inch))

story.append(Paragraph("Questions to Ask", header_style))
questions = [
    'What made you decide this was the right time to come back? — lets him tell the story',
    'When you think about SC in 5 years, what does success look like for you personally? — surfaces keep vs. sell without asking directly',
    'Are you evaluating other advisory partners, or are we your primary choice? — ask during open discussion, not early',
    'What does SC.ORB currently do well, and where does it break down under pressure? — shows homework, credibility check',
]
for q in questions:
    story.append(Paragraph("• " + q, bullet_style))
story.append(Spacer(1, 0.15 * inch))

story.append(Paragraph("Objections &amp; Handles", header_style))
objections = [
    '<b>"We\'ve built a lot already":</b> Acknowledge IP and momentum. Improving accelerates, doesn\'t replace.',
    '<b>"Not sure on keep vs. sell":</b> That uncertainty is exactly why now is right. Help them see both paths clearly.',
    '<b>"What\'s the ROI?":</b> De-risking a multi-million-dollar outcome. Improving\'s fee is a fraction of the IP value.',
    '<b>"Won\'t this slow us down?":</b> Fractional advisory works at your pace. You own all decisions.',
]
for item in objections:
    story.append(Paragraph(item, body_style))
story.append(Spacer(1, 0.15 * inch))

story.append(Paragraph("Competitive Landscape", header_style))
competitors = [
    "Veriforce (Kevin's former company — now Apax-owned, drifted from pipeline-specific focus)",
    "EWN, ITS, Compliance Services Inc. — traditional SaaS, no AI layer",
    "TRC Companies and large consultancies — services-heavy, no software-plus-ops model",
    "Kevin's Moat: 175+ years domain expertise + AI-native product. No competitor has both.",
]
for comp in competitors:
    story.append(Paragraph("• " + comp, bullet_style))
story.append(Spacer(1, 0.15 * inch))

story.append(Paragraph("Watch Items", header_style))
watch = [
    "Don't position Improving as a scale accelerator — position as the partner who helps Kevin build the right thing this time.",
    "PHMSA regulatory shift (ANPRM June 2025, Federal Register March 2025) is Kevin's tailwind — use it to frame urgency on the keep-and-scale path.",
    "Robin Graham is Kevin's wife and may be present — not a primary decision driver.",
]
for item in watch:
    story.append(Paragraph("• " + item, bullet_style))

doc.build(story)

file_size = os.path.getsize(output_path)
print("PDF built successfully. File size: {:,} bytes ({:.1f} KB)".format(file_size, file_size / 1024))
