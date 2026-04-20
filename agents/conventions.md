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

## Working Memory Write Protocol

Working memory is the input funnel for the dream cycle. If nothing is written, nothing compounds between sessions.

**Who writes:** Master owns the working memory write. When a sub-agent returns meaningful output, Master writes the entry as part of Agent Output Handling (see `agents/master.md`). Individual agents do NOT need to write their own working memory entries during normal operation. The only exceptions are:
- **Boot sequence:** The morning-briefing step-04 writes the boot entry directly (Master is executing, not receiving sub-agent output)
- **Scheduled tasks:** Workflows that run without Master (e.g., Cowork scheduled tasks) must embed the write in their final step file

### Schema (REQUIRED fields)

```yaml
---
type: working
task_id: "todo-2026-04-17-001"         # OmniFocus or IES task ID (use "session" if no task)
session_id: "chief-2026-04-17-091532"   # {agent}-{YYYY-MM-DD}-{HHmmss}
agent-source: chief | chase | quinn | shep | harper | rigby | knox | galen | sterling
created: 2026-04-17T09:15:32           # Local time, no Z suffix
expires: 2026-04-19T09:15:32           # created + 2 days
status: active | archived              # ONLY these two values
context: "Brief description of what this captures"
---
```

### Rules

1. **Filename**: `YYYY-MM-DD-HHmmss-{type}-{subject-slug}.md` (e.g., `2026-04-20-083000-session-boot-morning-briefing.md`)
2. **session_id format**: `{agent}-{YYYY-MM-DD}-{HHmmss}` — must match the agent that wrote the entry and the timestamp of creation. No abbreviations, no workflow names, no suffixes like `-final` or `-v2`.
3. **status values**: Only `active` or `archived`. Never `complete`, `done`, or any other value.
4. **Timestamps**: Local time (from Mac via osascript), ISO 8601, no Z suffix. Never UTC.
5. **TTL**: Entries expire 2 days after creation. The dream cycle handles archival and promotion.
6. **Body content**: Free-form markdown. Include what was produced, what data sources were used, key findings, and any flags.
7. **One entry per significant deliverable**: A boot briefing gets one entry. A meeting prep gets a separate entry. Don't bundle unrelated work into one file.

### When NOT to Write

- Trivial responses (answering a quick question, confirming a capture)
- Pure routing actions (Master spawning a sub-agent)
- File reads with no synthesis or output

---

## Tiered Memory Access Rules

The memory system has four tiers. Every agent must respect these boundaries:

| Tier | Path | Who Reads | Who Writes |
|------|------|-----------|------------|
| **working** | `memory/working/` | Any agent | Any agent |
| **episodic** | `memory/episodic/` | Any agent | Any agent (during task execution) |
| **semantic** | `memory/semantic/` | Any agent | **Dream cycle ONLY** |
| **personal** | `memory/personal/` | Any agent (boot) | Controller / Rigby only |

**HARD RULE: `memory/semantic/` is read-only for all agents except the dream cycle.** No agent may create, modify, or append to files in `memory/semantic/`. Violation of this rule will be logged as `category: tool-misuse`, `failure_mode: protocol-skip`.

### Read Priorities at Boot

1. `memory/personal/` — always loaded (identity, objectives, preferences)
2. `memory/semantic/` — always loaded (distilled patterns from dream cycle)
3. `memory/episodic/` — queried on demand by agents during task execution
4. `memory/working/` — queried on demand; volatile, TTL 2 days

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

---

## Slack Notification Protocol

When any agent produces output that David needs to see — a completed report, a scheduled task result, a lead alert, a prep brief, a pipeline update — **do not invoke the master-slack skill directly.** The skill lives with Master. Agents pass the message payload back to Master; Master sends it.

### How It Works

1. **Agent completes its task** and has output ready to send to Slack.
2. **Agent includes a `## Slack Notification` block** at the end of its response, containing the formatted message payload.
3. **Master reads the block**, invokes the master-slack skill (`agents/master.md` → `.claude/skills/master-slack/SKILL.md`), and sends the message.
4. **Master strips the block** before delivering the response to David. He never sees the raw payload.

### The Handoff Block Format

```
## Slack Notification
channel: jarvis
message: |
  *[Report Title — Date]*
  • [key finding or action item]
  • [key finding or action item]
  • [key finding or action item]
```

Use `channel: dm` instead of `channel: jarvis` for urgent or private items only.

### When to Include a Notification

| Trigger | Channel | What to Send |
|---------|---------|-------------|
| Scheduled task completes | jarvis | Task name, key findings, action items |
| Morning briefing delivered | jarvis | Headline summary (calendar, top priority, flags) |
| Pipeline review complete | jarvis | Revenue summary, risk flags |
| Lead alert (post-call, unassigned 4+ days) | jarvis | Lead name, days since call, recommended AM |
| Prep brief ready | jarvis | Meeting name, time, one-line context |
| Overdue commitment surfaced | dm | Who, what, how late |
| System error or boot failure | dm | What failed, what was skipped |

### What Agents Must NOT Do

- **Never invoke `mcp__Desktop_Commander__start_process`** to call the Slack bot script directly. That capability belongs to Master only.
- **Never silently complete a scheduled task** without a `## Slack Notification` block. Silent completions are failures.
- **Never DM unless the item is urgent or private.** Default is always #jarvis.

### Message Formatting Rules

1. Tight. Headline + 3-5 bullets. David reads it in 10 seconds.
2. Slack markdown: `*bold*`, `_italic_`, bullets with `•`.
3. Lead with the most important thing — not a greeting, not a summary of what you did.
4. Max 5000 chars per message. Split into multiple blocks if needed.
5. Use real line breaks in the message block — never literal `\n`.
<!-- personal:end -->
