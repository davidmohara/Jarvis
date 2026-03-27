# Agent Conventions

<!-- system:start -->
Shared protocols that apply to every IES agent. Read this file at the start of every task, immediately after reading your own agent file.

---

## Error Reporting Protocol

All agents are responsible for surfacing self-detected errors back to Master so they can be logged to `systems/error-tracking/error-log.json`. Master owns the log write — agents report, Master records.

### When to Report

Report an error when you:
- Catch yourself mid-execution having used the wrong tool, wrong source, or wrong approach
- Realize output you already produced was incorrect (wrong data, wrong format, bad assumption)
- Skip a required step and then catch it before or after the fact
- Detect a routing mistake — you handled something that should have gone to a different agent

### Explicit Corrections from the Executive

When David corrects any behavior — routing, data, process, tone, anything — **Master must log the correction to `systems/error-tracking/error-log.json` immediately in that same response.** This is not optional and does not require a second prompt. Use `"source": "explicit"` in the entry. The correction is logged first, then the conversation continues. This rule applies regardless of which agent was active when the correction occurred.

Do **not** report minor self-corrections that are trivially part of normal reasoning (e.g., rewriting a sentence). Report errors that would matter if they had shipped uncorrected.

### How to Report

At the end of your response or handoff, include a `## Self-Corrections` block if any errors occurred. Omit the block entirely if there are nothing to report — don't add it just to say "none."

```
## Self-Corrections

- **Category**: [data-accuracy | tool-misuse | routing-error | format-violation | missed-context | assumption-error | process-skip | hallucination | over-engineering | under-delivery]
- **Failure mode**: [lazy-search | stale-cache | wrong-assumption | sloppy-read | bad-conversion | tool-ignorance | context-blindness | pattern-mismatch | scope-creep | protocol-skip]
- **Severity**: [minor | moderate | major]
- **What happened**: [one sentence — what went wrong]
- **Corrected to**: [one sentence — what the right answer was]
```

Multiple errors get multiple bullet groups under the same `## Self-Corrections` heading.

Master will pick up this block, log each entry to the error tracking system, and strip the block before delivering output to the controller. The controller never sees raw error reports unless patterns are surfaced during reviews.

### Severity Guide

| Level | Use when |
|-------|----------|
| `minor` | Caught immediately, no impact on output quality |
| `moderate` | Required real correction effort; output would have been wrong |
| `major` | Could have led to a bad decision, missed commitment, or external impact |

---

## Output Format Conventions

Every agent that produces a deliverable must select the right output format. The format hierarchy below applies to all agents and skills — no agent should invent its own format preference.

### Format Hierarchy

When choosing a format for any deliverable, prefer the highest-applicable format in this order:

| Priority | Format | Extension | When to Use |
|----------|--------|-----------|-------------|
| 1 | **Single-page HTML** | `.html` | Default for dashboards, reports, briefings, analysis, anything David will view on screen. Self-contained — inline CSS/JS, no external dependencies. Interactive elements (filters, toggles, collapsible sections) are encouraged. |
| 2 | **Markdown** | `.md` | Knowledge artifacts destined for Obsidian, reMarkable, or long-term reference. Meeting notes, prep sheets, strategy docs, anything that lives in the vault. Also use for content drafts that will be edited further. |
| 3 | **PDF** | `.pdf` | Client-facing deliverables, documents requiring fixed layout, or items explicitly requested as PDF. See tool selection rules below. |
| 4 | **Office formats** | `.pptx` / `.docx` / `.xlsx` | Only when the output must be editable by others in that format (e.g., a deck for a client to modify, a spreadsheet with formulas). Never use as a default. |

### Decision Logic

**Will David view this on screen?** → HTML
**Will this go to Obsidian, reMarkable, or the knowledge vault?** → Markdown
**Will this be sent to a client or printed with fixed layout?** → PDF
**Does someone else need to edit this in Office?** → Office format
**Is the user explicitly requesting a specific format?** → Honor the request — it overrides the hierarchy

### Knowledge Management Override

Any output destined for the knowledge layer — Obsidian vault, reMarkable sync, meeting notes, transcript summaries, decision records — **always uses Markdown** regardless of the general hierarchy. Markdown is the lingua franca of the knowledge system. Knox will not ingest HTML or PDF into the vault.

### HTML Standards

- **Single file.** All CSS and JS inline. No external dependencies except CDN libraries (cdnjs.cloudflare.com).
- **Responsive.** Must render well on both desktop and mobile.
- **Print-friendly.** Include a `@media print` block for clean printing when relevant.
- **No localStorage or sessionStorage.** Use in-memory state only.

### Markdown Standards

- **YAML frontmatter** on every markdown file that enters the vault (source, date, tags at minimum).
- **Wikilinks** (`[[Target]]`) for cross-references within Obsidian.
- **No HTML inside markdown** unless absolutely necessary for a table or layout that markdown can't express.
<!-- system:end -->

<!-- personal:start -->
### PDF Tool Selection

Use the right PDF tool based on audience:

| Audience | Tool | When |
|----------|------|------|
| **Client-facing** | `improving-pdf` skill (branded) | Proposals, case studies, client deliverables, anything external with Improving's name on it |
| **David's own use** | `reportlab` (clean/compact) | Personal briefs, internal reference — no branding overhead. Tight margins, small fonts, zero images. |

The `improving-pdf` tool embeds base64 brand assets on every page and renders via Chromium — large files with visual chrome. For David's personal docs, use reportlab with content only, as compact as possible.

### Output Naming Conventions

**Source files (markdown — for the system):**

| Type | Pattern | Example |
|------|---------|---------|
| Meeting prep | `meetings/YYYY-MM-DD-slug.md` | `meetings/2026-02-20-cbre-confluent.md` |
| Decision | `decisions/YYYY-MM-DD-slug.md` | `decisions/2026-02-05-pricing-change.md` |
| Review | `reviews/daily/YYYY-MM-DD.md` | `reviews/daily/2026-02-20.md` |
| Grouped output | `meetings/subfolder/Name.md` | `meetings/podcast-prep/Episode 7.md` |

**Deliverable files (HTML, PDF, PPTX — for reading/sharing):**

Human-readable names. **No dates in filenames** unless the date is part of the document's identity. Optimized for screen, email, or print.

| Type | Pattern | Example |
|------|---------|---------|
| Meeting 1-pager | `Topic Name.html` | `CBRE Confluent 1-Pager.html` |
| Dashboard | `Dashboard Name.html` | `Pipeline Health.html` |
| Client brief | `Account Name Brief.pdf` | `Contoso Strategy Brief.pdf` |
| Presentation | `Deck Title.pptx` | `Board Update Q1.pptx` |

**Rule of thumb:** If it's going to be read by a human, name it the way you'd label a folder on your desk — short, clear, no ISO dates.
<!-- personal:end -->
