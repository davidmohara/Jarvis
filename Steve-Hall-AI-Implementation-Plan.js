const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel,
  BorderStyle, WidthType, ShadingType, PageNumber, PageBreak,
  TabStopType, TabStopPosition
} = require("docx");

// Colors
const BLUE = "1B4F72";
const LIGHT_BLUE = "D6EAF8";
const DARK_GRAY = "2C3E50";
const MEDIUM_GRAY = "5D6D7E";
const LIGHT_GRAY = "F2F3F4";
const ACCENT = "E67E22";
const GREEN = "27AE60";

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

function spacer(size = 120) {
  return new Paragraph({ spacing: { before: size, after: size }, children: [] });
}

function heading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 200 },
    children: [new TextRun({ text, font: "Arial", size: 32, bold: true, color: BLUE })]
  });
}

function heading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 160 },
    children: [new TextRun({ text, font: "Arial", size: 26, bold: true, color: DARK_GRAY })]
  });
}

function heading3(text) {
  return new Paragraph({
    spacing: { before: 200, after: 120 },
    children: [new TextRun({ text, font: "Arial", size: 22, bold: true, color: MEDIUM_GRAY })]
  });
}

function bodyText(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 60, after: 60, line: 300 },
    children: [new TextRun({ text, font: "Arial", size: 21, color: "333333", ...opts })]
  });
}

function bulletItem(text, level = 0) {
  return new Paragraph({
    numbering: { reference: "bullets", level },
    spacing: { before: 40, after: 40, line: 280 },
    children: [new TextRun({ text, font: "Arial", size: 21, color: "333333" })]
  });
}

function phaseHeader(phase, title, complexity, timeline) {
  const headerBorder = { style: BorderStyle.SINGLE, size: 1, color: BLUE };
  const headerBorders = { top: headerBorder, bottom: headerBorder, left: headerBorder, right: headerBorder };
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [6000, 3360],
    rows: [
      new TableRow({
        children: [
          new TableCell({
            borders: headerBorders,
            width: { size: 6000, type: WidthType.DXA },
            shading: { fill: BLUE, type: ShadingType.CLEAR },
            margins: { top: 100, bottom: 100, left: 160, right: 120 },
            children: [new Paragraph({
              children: [
                new TextRun({ text: phase + ": ", font: "Arial", size: 24, bold: true, color: "FFFFFF" }),
                new TextRun({ text: title, font: "Arial", size: 24, color: "FFFFFF" })
              ]
            })]
          }),
          new TableCell({
            borders: headerBorders,
            width: { size: 3360, type: WidthType.DXA },
            shading: { fill: BLUE, type: ShadingType.CLEAR },
            margins: { top: 100, bottom: 100, left: 120, right: 160 },
            verticalAlign: "center",
            children: [new Paragraph({
              alignment: AlignmentType.RIGHT,
              children: [
                new TextRun({ text: complexity + " | ", font: "Arial", size: 20, color: LIGHT_BLUE }),
                new TextRun({ text: timeline, font: "Arial", size: 20, bold: true, color: "FFFFFF" })
              ]
            })]
          })
        ]
      })
    ]
  });
}

function useCaseTable(rows) {
  const hdrBorder = { style: BorderStyle.SINGLE, size: 1, color: BLUE };
  const hdrBorders = { top: hdrBorder, bottom: hdrBorder, left: hdrBorder, right: hdrBorder };

  const headerRow = new TableRow({
    children: [
      new TableCell({
        borders: hdrBorders, width: { size: 2800, type: WidthType.DXA },
        shading: { fill: LIGHT_BLUE, type: ShadingType.CLEAR },
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        children: [new Paragraph({ children: [new TextRun({ text: "Use Case", font: "Arial", size: 20, bold: true, color: BLUE })] })]
      }),
      new TableCell({
        borders: hdrBorders, width: { size: 4360, type: WidthType.DXA },
        shading: { fill: LIGHT_BLUE, type: ShadingType.CLEAR },
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        children: [new Paragraph({ children: [new TextRun({ text: "Description", font: "Arial", size: 20, bold: true, color: BLUE })] })]
      }),
      new TableCell({
        borders: hdrBorders, width: { size: 2200, type: WidthType.DXA },
        shading: { fill: LIGHT_BLUE, type: ShadingType.CLEAR },
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        children: [new Paragraph({ children: [new TextRun({ text: "Data Required", font: "Arial", size: 20, bold: true, color: BLUE })] })]
      })
    ]
  });

  const dataRows = rows.map((r, i) => new TableRow({
    children: [
      new TableCell({
        borders, width: { size: 2800, type: WidthType.DXA },
        shading: i % 2 === 0 ? { fill: LIGHT_GRAY, type: ShadingType.CLEAR } : undefined,
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        children: [new Paragraph({ children: [new TextRun({ text: r[0], font: "Arial", size: 20, bold: true, color: DARK_GRAY })] })]
      }),
      new TableCell({
        borders, width: { size: 4360, type: WidthType.DXA },
        shading: i % 2 === 0 ? { fill: LIGHT_GRAY, type: ShadingType.CLEAR } : undefined,
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        children: [new Paragraph({ spacing: { line: 260 }, children: [new TextRun({ text: r[1], font: "Arial", size: 20, color: "333333" })] })]
      }),
      new TableCell({
        borders, width: { size: 2200, type: WidthType.DXA },
        shading: i % 2 === 0 ? { fill: LIGHT_GRAY, type: ShadingType.CLEAR } : undefined,
        margins: { top: 60, bottom: 60, left: 120, right: 120 },
        children: [new Paragraph({ spacing: { line: 260 }, children: [new TextRun({ text: r[2], font: "Arial", size: 20, color: MEDIUM_GRAY })] })]
      })
    ]
  }));

  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2800, 4360, 2200],
    rows: [headerRow, ...dataRows]
  });
}

// Build the document
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: BLUE },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: DARK_GRAY },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
    ]
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [
          { level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
          { level: 1, format: LevelFormat.BULLET, text: "\u25E6", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 1440, hanging: 360 } } } }
        ] },
      { reference: "numbers",
        levels: [
          { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } } }
        ] }
    ]
  },
  sections: [
    // TITLE PAGE
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      children: [
        spacer(2400),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 200 },
          children: [new TextRun({ text: "AI Implementation", font: "Arial", size: 56, bold: true, color: BLUE })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 120 },
          children: [new TextRun({ text: "Project Plan", font: "Arial", size: 56, bold: true, color: BLUE })]
        }),
        spacer(200),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          border: { top: { style: BorderStyle.SINGLE, size: 2, color: ACCENT, space: 8 } },
          spacing: { before: 200, after: 200 },
          children: [new TextRun({ text: "Prepared for Steve Hall", font: "Arial", size: 28, color: DARK_GRAY })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 80 },
          children: [new TextRun({ text: "Prepared by David O\u2019Hara | Improving", font: "Arial", size: 24, color: MEDIUM_GRAY })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { after: 80 },
          children: [new TextRun({ text: "February 2026", font: "Arial", size: 24, color: MEDIUM_GRAY })]
        }),
        spacer(1200),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "CONFIDENTIAL", font: "Arial", size: 20, bold: true, color: ACCENT })]
        }),
      ]
    },
    // MAIN CONTENT
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            border: { bottom: { style: BorderStyle.SINGLE, size: 1, color: BLUE, space: 4 } },
            children: [
              new TextRun({ text: "AI Implementation Plan \u2014 Steve Hall", font: "Arial", size: 16, color: MEDIUM_GRAY }),
              new TextRun({ text: "\tIMPROVING", font: "Arial", size: 16, bold: true, color: BLUE })
            ],
            tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }]
          })]
        })
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            border: { top: { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC", space: 4 } },
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: "Page ", font: "Arial", size: 16, color: MEDIUM_GRAY }),
              new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16, color: MEDIUM_GRAY })
            ]
          })]
        })
      },
      children: [
        // EXECUTIVE SUMMARY
        heading1("Executive Summary"),
        bodyText("This plan outlines a phased AI implementation strategy for Steve Hall\u2019s portfolio of businesses, including automotive dealerships (Denver Bentley, Honda of Paris), an auto finance company, and his foundation\u2019s content operations. The approach is designed to deliver immediate productivity wins while building toward sophisticated strategic agents."),
        spacer(60),
        bodyText("The implementation is structured in five phases, ordered from simplest to most complex. Phase 0 (Data Discovery) is a prerequisite that maps Steve\u2019s current data landscape and determines integration requirements. Each subsequent phase builds on the connectors and tooling established in earlier phases."),
        spacer(60),
        bodyText("The baseline platform is the \u201CImproving Executive System\u201D (IES)\u2014an AI-powered executive operating system similar to what David O\u2019Hara uses daily. It connects to email, calendar, task management, and documents to create a unified command center. Each phase extends this foundation with domain-specific agents and data integrations."),

        // PHASE 0
        new Paragraph({ children: [new PageBreak()] }),
        heading1("Phase 0: Data Discovery & Integration Architecture"),
        bodyText("Before building any agents, we need to understand where Steve\u2019s data lives, how it\u2019s structured, what\u2019s accessible via API, and what requires custom connectors. This phase is the foundation everything else depends on."),
        spacer(60),
        phaseHeader("Phase 0", "Data Discovery", "Foundation", "2\u20133 Weeks"),
        spacer(120),

        heading2("Objectives"),
        bulletItem("Map all data sources across Steve\u2019s portfolio companies and personal operations"),
        bulletItem("Assess API availability, authentication methods, and data formats for each source"),
        bulletItem("Identify gaps where custom connectors or ETL pipelines are needed"),
        bulletItem("Establish a secure data access architecture with appropriate permissions"),
        bulletItem("Produce a Data Landscape Map and Integration Roadmap"),

        heading2("Discovery Areas"),
        heading3("Business & Financial Systems"),
        bulletItem("Dealer Management Systems (DMS) \u2014 which platform? Reynolds & Reynolds, CDK, Tekion?"),
        bulletItem("Accounting / ERP systems across dealerships and auto finance company"),
        bulletItem("Board decks and financial statements \u2014 format, storage location (SharePoint, Google Drive, local?)"),
        bulletItem("Auto finance company loan management and portfolio systems"),
        bulletItem("Acquisition target financial data \u2014 how is it received and stored?"),

        heading3("Communication & Productivity"),
        bulletItem("Email provider(s) \u2014 Gmail, Outlook, or both? Which accounts?"),
        bulletItem("Calendar system(s) \u2014 Google Calendar, Outlook, iCal?"),
        bulletItem("Task management \u2014 current tools? Paper, Todoist, Apple Reminders, Notion?"),
        bulletItem("CRM \u2014 does one exist? Which businesses use it?"),
        bulletItem("Document storage \u2014 Google Drive, Dropbox, OneDrive, local file systems?"),

        heading3("Market & Intelligence Data"),
        bulletItem("Sources for quarterly earnings calls (SEC EDGAR, Bloomberg, FactSet?)"),
        bulletItem("Automotive market data feeds (NADA, Kelley Blue Book, Cox Automotive?)"),
        bulletItem("Interest rate and economic data sources"),
        bulletItem("Competitor tracking \u2014 Sonic, Lithia, others?"),

        heading3("Content & Foundation Operations"),
        bulletItem("Foundation website and content platforms"),
        bulletItem("Current content creation workflow \u2014 who writes, who reviews, where is it published?"),
        bulletItem("Event management tools for Wisdom Dinners"),
        bulletItem("Contractor communication for Dallas renovation \u2014 email, text, project management app?"),

        heading2("Deliverables"),
        bulletItem("Data Landscape Map \u2014 visual diagram of all systems, data flows, and access methods"),
        bulletItem("Integration Feasibility Matrix \u2014 each data source rated by API availability, effort, and priority"),
        bulletItem("Connector Development Backlog \u2014 prioritized list of custom integrations needed"),
        bulletItem("Security & Access Architecture \u2014 authentication strategy, data handling policies"),

        // PHASE 1
        new Paragraph({ children: [new PageBreak()] }),
        heading1("Phase 1: Executive Operating System Foundation"),
        bodyText("Stand up the core AI executive system \u2014 the \u201CSteve Hall Command Center.\u201D This is the same architecture David uses daily, adapted for Steve\u2019s tools and workflows. It provides immediate daily value and becomes the platform for everything else."),
        spacer(60),
        phaseHeader("Phase 1", "Executive OS", "Low Complexity", "3\u20134 Weeks"),
        spacer(120),

        useCaseTable([
          ["Email Response Generation", "AI drafts email responses in Steve\u2019s voice and tone. Reviews, edits, sends. Learns preferences over time.", "Email accounts, sent mail history for voice training"],
          ["To-Do Follow-Up", "AI tracks pending items, sends reminders, flags overdue tasks. Replaces manual list management.", "Current task lists, email commitments, calendar actions"],
          ["Voice-to-Draft", "Dictate strategy thoughts via voice memo; AI produces polished first draft of white papers and memos.", "Voice recording input, document templates"],
          ["Calendar & Scheduling Intelligence", "AI manages scheduling conflicts, prep for meetings, morning briefings with day\u2019s priorities.", "Calendar, contacts, meeting context"]
        ]),

        spacer(120),
        heading2("Implementation Approach"),
        bulletItem("Deploy IES platform with Steve\u2019s email, calendar, and task integrations"),
        bulletItem("Build voice capture workflow (phone dictation \u2192 transcription \u2192 AI draft)"),
        bulletItem("Train AI on Steve\u2019s communication style using sent email corpus"),
        bulletItem("Configure morning briefing routine and end-of-day review"),
        bulletItem("2-week onboarding period with daily tuning"),

        heading2("Success Criteria"),
        bulletItem("Steve uses the system daily for email triage and response drafting"),
        bulletItem("At least 50% of routine emails handled with AI-assisted drafts"),
        bulletItem("Voice-to-draft workflow operational for white paper content"),
        bulletItem("Morning briefing delivered automatically by 6:00 AM"),

        // PHASE 2
        new Paragraph({ children: [new PageBreak()] }),
        heading1("Phase 2: Communication Intelligence & Automation"),
        bodyText("Extend the executive OS with deep email analytics and operational automation. This phase turns Steve\u2019s communication data into actionable intelligence about where his time and attention are going."),
        spacer(60),
        phaseHeader("Phase 2", "Communication Intel", "Medium Complexity", "4\u20136 Weeks"),
        spacer(120),

        useCaseTable([
          ["Email & Time Intelligence", "Analyze email patterns: who Steve communicates with most, response times, topic distribution. Identify misallocated time vs. stated priorities. Coach on communication effectiveness.", "6\u201312 months email history, calendar data, stated priority list"],
          ["Operator Coaching Support", "AI prepares coaching briefs for portfolio company operators. Tracks commitments, surfaces patterns, suggests talking points.", "Operator email threads, meeting notes, KPI data"],
          ["Wisdom Dinner Automation", "Automate invitations, RSVPs, dietary preferences, seating, follow-ups for Steve\u2019s signature dinner events.", "Contact list, venue info, event history, dietary preferences"],
          ["Renovation Project Management", "Coordinate multi-contractor communication, track deliverables, flag delays, consolidate updates.", "Contractor contacts, project timeline, communication threads"]
        ]),

        spacer(120),
        heading2("Key Connectors Required"),
        bulletItem("Email analytics pipeline (read-only access to analyze patterns)"),
        bulletItem("Contact enrichment integration (LinkedIn, company data)"),
        bulletItem("Event management connector (Resy, Evite, or custom)"),
        bulletItem("Project management integration for renovation tracking"),

        heading2("Success Criteria"),
        bulletItem("Monthly \u201CTime Allocation Report\u201D generated automatically"),
        bulletItem("Coaching prep briefs ready 24 hours before operator calls"),
        bulletItem("Wisdom Dinner logistics handled end-to-end with minimal manual input"),

        // PHASE 3
        new Paragraph({ children: [new PageBreak()] }),
        heading1("Phase 3: Content Creation & Market Research"),
        bodyText("Build agents focused on Steve\u2019s foundation content operations and market intelligence needs. These agents consume data from the connectors built in earlier phases and produce polished outputs."),
        spacer(60),
        phaseHeader("Phase 3", "Content & Research", "Medium-High Complexity", "4\u20136 Weeks"),
        spacer(120),

        useCaseTable([
          ["Foundation Content Engine", "Draft white papers, leadership covenants, and Stewardship Mandates in Steve\u2019s voice. Manage editorial calendar and publication workflow.", "Existing publications, brand voice guide, foundation mission docs"],
          ["Market & Competitive Intelligence", "Track real-time shifts in automotive market, interest rate changes affecting auto finance, and competitor moves by Sonic and Lithia.", "Market data feeds, SEC filings, news APIs, competitor websites"],
          ["Sentiment & Regulatory Agent", "Scrape and synthesize quarterly earnings calls for linguistic shifts\u2014how CEOs talk about inventory levels or AI integration vs. previous quarters.", "SEC EDGAR transcripts, NLP models, historical call data"]
        ]),

        spacer(120),
        heading2("Key Connectors Required"),
        bulletItem("SEC EDGAR API for earnings call transcripts"),
        bulletItem("Financial news aggregation (Bloomberg, Reuters, or alternative)"),
        bulletItem("Automotive industry data feeds (Cox Automotive, NADA)"),
        bulletItem("Content management system for foundation publications"),

        heading2("Success Criteria"),
        bulletItem("First AI-assisted white paper published through foundation"),
        bulletItem("Weekly market intelligence brief delivered every Monday"),
        bulletItem("Quarterly earnings analysis available within 48 hours of filings"),

        // PHASE 4
        new Paragraph({ children: [new PageBreak()] }),
        heading1("Phase 4: Financial Intelligence Agents"),
        bodyText("Deploy specialized financial analysis agents that can process complex documents, identify inconsistencies, and surface insights from acquisition targets and portfolio performance data."),
        spacer(60),
        phaseHeader("Phase 4", "Financial Intelligence", "High Complexity", "6\u20138 Weeks"),
        spacer(120),

        useCaseTable([
          ["Financial Reconciliation Agent", "Compare disparate financial reports from acquisition targets. Spot inconsistencies in \u201Cunderperforming but mature\u201D businesses that standard accounting software misses.", "Target company financials, internal benchmarks, industry comparables"],
          ["Shadow Board Agent", "Feed AI board decks, financial statements, and strategic briefs from automotive holdings. AI acts as a skeptical activist investor identifying weak assumptions in growth plans.", "Board decks, financials, strategic plans, industry benchmarks"]
        ]),

        spacer(120),
        heading2("Key Connectors Required"),
        bulletItem("Document ingestion pipeline for financial statements (PDF, Excel, various formats)"),
        bulletItem("Dealership DMS integration for real-time operational data"),
        bulletItem("Benchmarking data sources (NADA guides, industry performance metrics)"),
        bulletItem("Secure document vault for acquisition-sensitive materials"),

        heading2("Implementation Approach"),
        bulletItem("Build financial document parsing pipeline (OCR, table extraction, normalization)"),
        bulletItem("Develop comparison frameworks for cross-company financial analysis"),
        bulletItem("Create \u201Cactivist investor\u201D prompt architecture with industry-specific mental models"),
        bulletItem("Implement human-in-the-loop review for all financial conclusions"),
        bulletItem("Extensive testing with historical data before live deployment"),

        heading2("Success Criteria"),
        bulletItem("Agent successfully identifies known inconsistencies in test financial data"),
        bulletItem("Shadow Board produces actionable challenge questions for next board meeting"),
        bulletItem("Steve trusts the system enough to use it in active acquisition evaluation"),

        // PHASE 5
        new Paragraph({ children: [new PageBreak()] }),
        heading1("Phase 5: Strategic Simulation Agents"),
        bodyText("The most sophisticated phase: multi-agent systems that simulate real-world business scenarios. These require all prior phases to be operational and benefit from the accumulated data and trained models."),
        spacer(60),
        phaseHeader("Phase 5", "Strategic Simulation", "Very High Complexity", "8\u201312 Weeks"),
        spacer(120),

        useCaseTable([
          ["Moat Builder (F&I Simulation)", "Simulate an aggressive AI buyer negotiating against Steve\u2019s dealership F&I processes. Identify where current processes break down before real AI buyers arrive.", "F&I product data, current negotiation scripts, pricing models, deal history"],
          ["Synthetic Negotiation", "Multi-agent simulation: one AI acts as buyer, another as Steve, to practice acquisition pitches. Useful for both buying and selling companies.", "Deal terms, company valuations, industry comps, Steve\u2019s negotiation style"],
        ]),

        spacer(120),
        heading2("Implementation Approach"),
        bulletItem("Build multi-agent orchestration framework"),
        bulletItem("Train buyer/seller personas on industry-specific negotiation patterns"),
        bulletItem("Develop F&I process model from Steve\u2019s dealership data"),
        bulletItem("Create scenario libraries with varying difficulty levels"),
        bulletItem("Implement replay and analysis tools for post-simulation review"),
        bulletItem("Iterate with Steve through live practice sessions"),

        heading2("Success Criteria"),
        bulletItem("F&I simulation identifies at least 3 process vulnerabilities Steve\u2019s team validates"),
        bulletItem("Synthetic negotiation produces practice scenarios Steve considers realistic"),
        bulletItem("Steve uses simulation prep before at least one real acquisition conversation"),

        // TIMELINE & INVESTMENT
        new Paragraph({ children: [new PageBreak()] }),
        heading1("Timeline & Investment Overview"),
        bodyText("The full implementation spans approximately 6\u20139 months, with each phase delivering standalone value. Steve can pause, adjust scope, or accelerate at any phase boundary."),
        spacer(120),

        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2200, 1700, 1700, 2060, 1700],
          rows: [
            new TableRow({
              children: ["Phase", "Duration", "Complexity", "Depends On", "Use Cases"].map((h, i) =>
                new TableCell({
                  borders: { top: { style: BorderStyle.SINGLE, size: 1, color: BLUE }, bottom: { style: BorderStyle.SINGLE, size: 1, color: BLUE }, left: { style: BorderStyle.SINGLE, size: 1, color: BLUE }, right: { style: BorderStyle.SINGLE, size: 1, color: BLUE } },
                  width: { size: [2200, 1700, 1700, 2060, 1700][i], type: WidthType.DXA },
                  shading: { fill: BLUE, type: ShadingType.CLEAR },
                  margins: { top: 60, bottom: 60, left: 100, right: 100 },
                  children: [new Paragraph({ children: [new TextRun({ text: h, font: "Arial", size: 20, bold: true, color: "FFFFFF" })] })]
                })
              )
            }),
            ...([
              ["0: Data Discovery", "2\u20133 weeks", "Foundation", "\u2014", "1"],
              ["1: Executive OS", "3\u20134 weeks", "Low", "Phase 0", "4"],
              ["2: Comms Intel", "4\u20136 weeks", "Medium", "Phase 1", "4"],
              ["3: Content & Research", "4\u20136 weeks", "Med-High", "Phase 0\u20131", "3"],
              ["4: Financial Intel", "6\u20138 weeks", "High", "Phase 0\u20131", "2"],
              ["5: Strategic Sim", "8\u201312 weeks", "Very High", "Phase 0\u20134", "2"],
            ].map((row, ri) => new TableRow({
              children: row.map((cell, ci) => new TableCell({
                borders,
                width: { size: [2200, 1700, 1700, 2060, 1700][ci], type: WidthType.DXA },
                shading: ri % 2 === 0 ? { fill: LIGHT_GRAY, type: ShadingType.CLEAR } : undefined,
                margins: { top: 50, bottom: 50, left: 100, right: 100 },
                children: [new Paragraph({ children: [new TextRun({ text: cell, font: "Arial", size: 20, color: DARK_GRAY })] })]
              }))
            })))
          ]
        }),

        spacer(200),
        bodyText("Note: Phases 2, 3, and 4 can run in parallel after Phase 1 is complete. The timeline above assumes sequential execution. Parallel execution could compress the total timeline to approximately 5\u20137 months."),

        // NEXT STEPS
        new Paragraph({ children: [new PageBreak()] }),
        heading1("Recommended Next Steps"),
        spacer(60),

        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          spacing: { before: 80, after: 40, line: 300 },
          children: [
            new TextRun({ text: "Schedule Data Discovery Kickoff ", font: "Arial", size: 21, bold: true, color: DARK_GRAY }),
            new TextRun({ text: "\u2014 2-hour working session with Steve and his key team members (assistant, finance lead, IT contact). Goal: map the full data landscape and identify quick wins.", font: "Arial", size: 21, color: "333333" })
          ]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          spacing: { before: 80, after: 40, line: 300 },
          children: [
            new TextRun({ text: "Inventory Current Tools & Access ", font: "Arial", size: 21, bold: true, color: DARK_GRAY }),
            new TextRun({ text: "\u2014 Steve provides logins/access to email, calendar, document storage, and financial systems. We assess API availability and integration paths.", font: "Arial", size: 21, color: "333333" })
          ]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          spacing: { before: 80, after: 40, line: 300 },
          children: [
            new TextRun({ text: "Deliver Integration Roadmap ", font: "Arial", size: 21, bold: true, color: DARK_GRAY }),
            new TextRun({ text: "\u2014 Within 2 weeks of kickoff, produce the Data Landscape Map and prioritized connector backlog. This becomes the blueprint for all subsequent phases.", font: "Arial", size: 21, color: "333333" })
          ]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          spacing: { before: 80, after: 40, line: 300 },
          children: [
            new TextRun({ text: "Begin Phase 1 Build ", font: "Arial", size: 21, bold: true, color: DARK_GRAY }),
            new TextRun({ text: "\u2014 Start with email integration and daily briefing. Steve experiences AI value within the first week of Phase 1.", font: "Arial", size: 21, color: "333333" })
          ]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          spacing: { before: 80, after: 40, line: 300 },
          children: [
            new TextRun({ text: "Establish Weekly Review Cadence ", font: "Arial", size: 21, bold: true, color: DARK_GRAY }),
            new TextRun({ text: "\u2014 30-minute weekly check-in to review progress, adjust priorities, and plan next sprint. This ensures the implementation stays aligned with Steve\u2019s evolving needs.", font: "Arial", size: 21, color: "333333" })
          ]
        }),

        spacer(400),
        new Paragraph({
          border: { top: { style: BorderStyle.SINGLE, size: 2, color: BLUE, space: 8 } },
          spacing: { before: 200 },
          children: [new TextRun({ text: "David O\u2019Hara | Regional Director, Texas | Improving", font: "Arial", size: 20, color: MEDIUM_GRAY })]
        }),
        new Paragraph({
          spacing: { before: 40 },
          children: [new TextRun({ text: "david.ohara@improving.com | 214.317.9659", font: "Arial", size: 20, color: MEDIUM_GRAY })]
        }),
      ]
    }
  ]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/sessions/modest-funny-bardeen/mnt/my-os/Steve-Hall-AI-Implementation-Plan.docx", buffer);
  console.log("Document created successfully");
});
