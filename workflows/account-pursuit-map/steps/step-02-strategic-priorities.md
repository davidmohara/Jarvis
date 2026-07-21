---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 02: Stated Strategic Priorities — Primary Sources Only

## MANDATORY EXECUTION RULES

1. You MUST source every stated priority strictly from primary sources: 10-K/10-Q filings, investor day materials, press releases, and earnings call transcripts. This section is factual grounding, not speculation.
2. You MUST cite every claim. Every priority statement in the output must trace to a specific source (filing name/date, investor day deck, press release URL, earnings call date).
3. You MUST NOT infer or invent a strategic priority that isn't stated somewhere in a primary source. If you believe something is a priority based only on secondary news coverage or general industry pattern-matching, label it explicitly as inference, not as a stated priority, and keep it out of the primary priorities list.
4. You MUST organize findings into 3-5 named priority themes. Do not present an unstructured list of quotes — synthesize into themes the way the Schwab and Constellation reference plans do (e.g., "AI at Scale," "Data Platform Modernization").
5. Do NOT proceed to step 03 until priority themes are drafted with citations for every substantive claim.

---

## EXECUTION PROTOCOL

**Agent:** Chase
**Input:** Confirmed entity from step 01
**Output:** 3-5 named, cited strategic priority themes — stored in accumulated-context for step 03 and step 05

---

## CONTEXT BOUNDARIES

- Primary sources only for this section: 10-K, 10-Q, investor day presentations/transcripts, official press releases, earnings call transcripts (company IR site, SEC EDGAR, or reputable transcript aggregators quoting the call directly).
- General news commentary, analyst opinion pieces, and trade press are not acceptable as the sole source for a "stated priority" claim — they may corroborate but not originate one.
- If the company is private (no 10-K/10-Q), rely on press releases, any public investor communications, executive public statements (conference talks, published interviews), and company website strategic messaging — note the reduced source set explicitly.
- 3-5 themes is a target, not a hard rule — fewer than 3 well-cited themes beats 5 padded ones.

---

## YOUR TASK

### 1. Pull primary source materials

- SEC EDGAR or company IR site: most recent 10-K and any 10-Q filed since.
- Company investor relations site: most recent investor day deck/transcript, if one exists.
- Company newsroom: press releases from the last 12-18 months, prioritizing anything tied to strategy, technology, M&A, or major initiatives.
- Earnings call transcripts: most recent 2-4 quarters, searching for forward-looking strategic statements (not just financial results).

### 2. Extract and organize into named priority themes

- Read across all pulled sources and group recurring, stated priorities into 3-5 named themes.
- For each theme, capture: the theme name, a synthesis paragraph describing what the company has said about it, and the specific citations supporting it.
- Record:
  ```yaml
  strategic_priorities:
    themes:
      - name: "{Theme name, e.g., 'AI at Scale — Client-Facing and Internal'}"
        summary: "{2-4 sentence synthesis of what the company has stated, with inline reference to which source(s) support each claim}"
        sources:
          - "{Source title/date — URL}"
      - name: "{Theme 2}"
        summary: "..."
        sources: [...]
    source_set: "10-K + investor day + press releases + earnings calls" | "{Note if reduced, e.g., 'Private company — press releases and public statements only, no 10-K/10-Q available'}"
  ```

### 3. Flag anything that looked like a priority but isn't citable

- If secondary coverage suggests a priority that no primary source confirms, do not include it in `strategic_priorities.themes`. Instead note it separately:
  ```yaml
  uncited_signals:
    - signal: "{What secondary coverage suggested}"
      source: "{Where you saw it}"
      note: "Not corroborated by a primary source — flagged for awareness, not treated as a stated priority."
  ```

---

## SUCCESS METRICS

- 3-5 named priority themes produced, each with a citation trail
- Every substantive claim in each theme traces to a primary source
- No priority asserted without a citable primary source backing it
- Reduced source availability (e.g., private company) explicitly noted rather than silently worked around

## FAILURE MODES

| Failure | Action |
|---------|--------|
| No 10-K/10-Q available (private company) | Note explicitly in `source_set`. Rely on press releases and public executive statements. Do not fabricate financial-filing-style claims. |
| Fewer than 3 clear themes findable | Present what's genuinely supportable. Note: "Limited primary-source material available — {N} themes identified with strong citation support." Do not pad to hit a target count. |
| Investor day materials not public / paywalled | Note the gap. Rely on earnings call transcripts and press releases for forward-looking statements instead. |
| Conflicting statements across sources (e.g., strategy shifted between quarters) | Note the most recent statement as authoritative, but flag the shift explicitly — a strategy pivot is itself useful context for the pursuit. |
| Secondary news repeatedly suggests a priority with no primary-source backing | Log it under `uncited_signals`, not the main themes list. Do not let volume of secondary coverage substitute for a primary citation. |

---

## NEXT STEP

Read fully and follow: `step-03-competitive-positioning-and-leadership.md`
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
