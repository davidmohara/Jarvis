#!/usr/bin/env python3
"""
Rebuild Systemic Compliance call prep PDF with Improving brand colors.
Uses ReportLab for styled PDF output.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, pt
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.enum.text import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime

# Improving brand colors
IMPROVING_BLUE = HexColor("#0077C8")
LIGHT_BLUE_TINT = HexColor("#E8F4FC")
NEAR_BLACK = HexColor("#1A1A1A")
WHITE = HexColor("#FFFFFF")

# Page setup
PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 0.6 * inch
CONTENT_WIDTH = PAGE_WIDTH - (2 * MARGIN)

def build_pdf():
    """Build the complete PDF document."""

    doc = SimpleDocTemplate(
        "/sessions/vigilant-quirky-wright/mnt/IES/meetings/Systemic Compliance.pdf",
        pagesize=letter,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
    )

    # Define styles
    styles = getSampleStyleSheet()

    # Section header style
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=WHITE,
        spaceAfter=12,
        spaceBefore=6,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
    )

    # Body text style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=9,
        textColor=NEAR_BLACK,
        spaceAfter=8,
        leading=11,
        alignment=TA_JUSTIFY,
    )

    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=16,
        textColor=IMPROVING_BLUE,
        spaceAfter=24,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
    )

    story = []

    # Title
    story.append(Paragraph("Systemic Compliance Call Prep", title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Section 1: Meeting at a Glance
    story.append(create_section_header("1. Meeting at a Glance", section_header_style))

    glance_data = [
        ["Meeting", "Systemic Compliance, LLC — Kick-off: Fractional AI-Driven Consulting"],
        ["Date", "Tuesday, June 30, 2026 | In-person | David running solo"],
        ["Attendees", "Kevin Graham (President/Founder, SC), Robin Graham (Kevin's wife, may be present), David O'Hara (Improving, Regional Director), Stephen Johnson (Improving VP, Houston)"],
        ["Purpose", "Align on engagement scope, establish working relationship, discuss roadmap for turning SC.ORB into a scalable, sellable asset"],
    ]

    glance_table = Table(glance_data, colWidths=[1.2*inch, CONTENT_WIDTH-1.2*inch])
    glance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), IMPROVING_BLUE),
        ('TEXTCOLOR', (0, 0), (0, -1), WHITE),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 9),
        ('TEXTCOLOR', (1, 0), (1, -1), NEAR_BLACK),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [WHITE, LIGHT_BLUE_TINT]),
        ('GRID', (0, 0), (-1, -1), 1, IMPROVING_BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))

    story.append(glance_table)
    story.append(Spacer(1, 0.3 * inch))

    # Section 2: Their Company & Product
    story.append(create_section_header("2. Their Company & Product", section_header_style))

    company_text = """
Systemic Compliance, LLC — founded early 2025 by Kevin Graham. Product is SC.ORB — AI-driven compliance tool built on Claude/Cowork (MVP stage). Two compliance domains:
<br/><br/>
<b>OQ (Operator Qualification):</b> 49 CFR 192/195. Pipeline operators must qualify workers performing "covered tasks." SC.ORB determines qualification status and maintains defensible records.
<br/><br/>
<b>API RP 1173 / PSMS:</b> Currently voluntary but PHMSA's March 2025 Federal Register filing signals shift toward mandatory. Kevin's regulatory tailwind.
<br/><br/>
<b>Team:</b> Former PHMSA inspectors, accident investigators, pipeline operators, regulatory committee members — 175+ years combined experience.
<br/><br/>
<b>Kevin's backstory:</b> Founded Veriforce 1998, sold 2009. Watched it go Thoma Bravo (2019) → Apax Partners (2024), grow 6x through M&A, drift from pipeline-specific expertise into generic contractor management. Came back to build it right.
    """

    story.append(Paragraph(company_text, body_style))
    story.append(Spacer(1, 0.3 * inch))

    # Section 3: Technical Conversation to Own
    story.append(create_section_header("3. Technical Conversation to Own", section_header_style))

    tech_points = [
        ("<b>1. Auditability</b> — Every SC.ORB determination needs an immutable audit trail. PHMSA inspectors and attorneys will ask: what did the system decide, on what basis, who was responsible? Anthropic's Compliance API (Aug 2025) streams audit events into enterprise SIEM systems — the infrastructure layer SC.ORB needs.", body_style),
        ("<b>2. Model independence</b> — SC.ORB is tightly coupled to Claude. Production-grade needs a model-agnostic abstraction layer. Improving's role: design that architecture early.", body_style),
        ("<b>3. Accuracy defensibility</b> — The sales weapon. Independent graders, SME kickback rates tracked and published, edge cases documented. No OQ/PSMS competitor has this. Kevin's domain credibility makes it believable; Improving's eval architecture makes it verifiable.", body_style),
        ("<b>4. Regulatory defensibility</b> — PHMSA requires operators to explain every covered task determination. AI as advisor with human sign-off, not sole decision-maker. SC.ORB flags, recommends, documents — qualified human approves.", body_style),
    ]

    for text, style in tech_points:
        story.append(Paragraph(text, style))
        story.append(Spacer(1, 0.08 * inch))

    story.append(Spacer(1, 0.2 * inch))

    # Section 4: The Strategic Fork
    story.append(create_section_header("4. The Strategic Fork", section_header_style))

    fork_text = """
<b>Keep and scale:</b> Build production-grade, auditable, deployable platform. Longer engagement, growing scope.
<br/><br/>
<b>Harvest IP:</b> Package IP for acquirers. Shorter, focused engagement around productization and go-to-market narrative.
<br/><br/>
<b>The question to ask:</b> "When you think about what you want this to become — are you building something you want to run for the next decade, or building something you want to prove out and put in the right hands?"
<br/><br/>
Kevin sold once — he knows what the PE treadmill costs. Pitch Improving as the partner who helps him build the right thing, not the biggest thing.
    """

    story.append(Paragraph(fork_text, body_style))
    story.append(Spacer(1, 0.3 * inch))

    # Section 5: Questions to Ask
    story.append(create_section_header("5. Questions to Ask", section_header_style))

    questions = [
        '"What made you decide this was the right time to come back?" — lets him tell the story',
        '"When you think about SC in 5 years, what does success look like for you personally?" — surfaces keep vs. sell without asking directly',
        '"Are you evaluating other advisory partners, or are we your primary choice?" — ask during open discussion, not early',
        '"What does SC.ORB currently do well, and where does it break down under pressure?" — shows homework',
    ]

    for i, q in enumerate(questions, 1):
        story.append(Paragraph(f"<b>{i}.</b> {q}", body_style))
        story.append(Spacer(1, 0.06 * inch))

    story.append(Spacer(1, 0.2 * inch))

    # Section 6: Objections & Handles
    story.append(create_section_header("6. Objections & Handles", section_header_style))

    objections = [
        ('"We\'ve built a lot already"', "Acknowledge IP and momentum. Improving accelerates, doesn't replace."),
        ('"Not sure on keep vs. sell"', "That uncertainty is exactly why now is right. Help them see both paths clearly."),
        ('"What\'s the ROI?"', "De-risking a multi-million-dollar outcome. Improving's fee is a fraction of the IP value."),
        ('"Won\'t this slow us down?"', "Fractional advisory works at your pace. You own all decisions."),
    ]

    obj_data = [[Paragraph(f"<b>{obj}</b>", body_style), Paragraph(handle, body_style)] for obj, handle in objections]

    obj_table = Table(obj_data, colWidths=[1.8*inch, CONTENT_WIDTH-1.8*inch])
    obj_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [WHITE, LIGHT_BLUE_TINT]),
        ('GRID', (0, 0), (-1, -1), 1, IMPROVING_BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))

    story.append(obj_table)
    story.append(Spacer(1, 0.3 * inch))

    # Section 7: Competitive Landscape
    story.append(create_section_header("7. Competitive Landscape", section_header_style))

    competitors = [
        ("<b>Veriforce</b> — Kevin's former company — Apax-owned, drifted from pipeline-specific focus", body_style),
        ("<b>EWN, ITS, Compliance Services Inc.</b> — traditional SaaS, no AI layer", body_style),
        ("<b>TRC Companies and large consultancies</b> — services-heavy, no software-plus-ops model", body_style),
        ("<b>Kevin's moat:</b> 175+ years domain expertise + AI-native product. No competitor has both.", body_style),
    ]

    for text, style in competitors:
        story.append(Paragraph(text, style))
        story.append(Spacer(1, 0.08 * inch))

    story.append(Spacer(1, 0.3 * inch))

    # Section 8: Watch Items
    story.append(create_section_header("8. Watch Items", section_header_style))

    watch_items = [
        "Don't position Improving as a scale accelerator — position as the partner who helps Kevin build the right thing this time.",
        "PHMSA regulatory shift (ANPRM June 2025, Federal Register March 2025) is Kevin's tailwind — use it to frame urgency on the keep-and-scale path.",
        "Robin Graham is Kevin's wife and may be present — not a primary decision driver.",
    ]

    for i, item in enumerate(watch_items, 1):
        story.append(Paragraph(f"<b>{i}.</b> {item}", body_style))
        story.append(Spacer(1, 0.08 * inch))

    # Build PDF
    doc.build(story)
    print(f"PDF created successfully: /sessions/vigilant-quirky-wright/mnt/IES/meetings/Systemic Compliance.pdf")

def create_section_header(text, style):
    """Create a styled section header with background color."""
    # We'll use the Paragraph with a background color via table trick
    # Actually, we'll return a table with colored background for the header
    header_table = Table([[Paragraph(text, style)]], colWidths=[CONTENT_WIDTH])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), IMPROVING_BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    return header_table

if __name__ == '__main__':
    build_pdf()
