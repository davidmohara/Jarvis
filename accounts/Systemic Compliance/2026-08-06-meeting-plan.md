# SC.IMS — Aug 6 Session Checklist
## GitHub Artifact Upload + Eval Harness Planning

**Goal:** Get every Claude artifact Kevin has built into GitHub during this session, then use what's there to plan the eval harness design. Starting with the upload grounds the conversation in what actually exists, not what we think exists.

**Ownership in the room:**
- Kevin = sole operator of all Claude artifacts (engines, prompts, data, uploads)
- Mehmet = SC.ORB platform and code side only
- Robin = organizational conscience — keeps Kevin honest on what's shipped vs. aspirational
- David = uploads Kevin's artifacts to GitHub as Kevin identifies them

---

## Part 1: GitHub Setup & Upload (30 min)
*Do this first — everything else builds on what's in the repo*

### Setup (5 min)
- [ ] Repo created, Ben and David have access before upload begins
- [ ] Agree on folder structure: `/gap-analysis`, `/moc-ripple`, `/competence-architect`, `/two-register-reconciliation`, `/data-corpora`, `/prompt-templates`
- [ ] Scope the exclusions now: anything with client-identifiable data or raw operator procedures goes in a separate `/review-before-committing` folder rather than blocking the upload

### Upload — Engine by Engine (25 min)
*Kevin pulls up Claude, calls out each artifact, David uploads*

- [ ] **Gap Analysis** — Claude Project or thread? Prompt templates, system instructions, any uploaded input files that aren't client-specific
- [ ] **MOC Ripple** — same
- [ ] **Competence Architect** — same; flag where the anonymized training corpus lives and whether it can go in the repo
- [ ] **Two-Register Reconciliation** — same
- [ ] **Panama Canal Placer** — same
- [ ] Anything living outside Claude (local files, Word docs, Google Docs) — Kevin shares screen or transfers to David, David commits it

**Don't leave Part 1 until the repo has at least one artifact from every engine. Partial is fine; empty is not.**

---

## Part 2: Engine-by-Engine Detail (40 min — ~8 min per engine)
*Now that artifacts are in GitHub, walk through what each one actually does*

### For each engine, get:
- [ ] Exact inputs Kevin provides each run — which files, what format, uploaded fresh each time or stored in the Project?
- [ ] What the output looks like — document, spreadsheet, JSON, freeform text?
- [ ] Where the logic lives — fixed system prompt, Kevin's manual steering mid-conversation, or a mix?
- [ ] Whether the output is deterministic — same inputs, same output on rerun?
- [ ] Any manual corrections Kevin routinely makes to the output before it goes anywhere (these are undocumented business rules)

### Gap Analysis specific
- [ ] How does peer benchmarking work — is the benchmark corpus a file Kevin uploads, or baked into the prompt?
- [ ] What triggers a run — client engagement, ad hoc, scheduled?

### MOC Ripple specific
- [ ] What triggers a MOC run — new regulation, operator document change, both?
- [ ] Where does the ripple map/audit trail dossier go after generation?

### Competence Architect specific
- [ ] Does one run produce all 4 training formats, or is each format a separate prompt/run?
- [ ] Where does the anonymized training corpus live — uploaded file, Claude Project knowledge, or elsewhere?
- [ ] Who reviews output before it goes to a client — Kevin, Robin, SME?

### Two-Register Reconciliation specific
- [ ] What are the two registers and what format are they in today?
- [ ] What does the reconciliation check for — orphans, date pins, both?

---

## Part 3: Where the Data Lives (15 min)
*Kevin leads — these answers feed directly into Ben's eval harness design*

- [ ] The regulatory requirements graph (~750 entities, ~1,066 links) — spreadsheet, Claude Project files, a database, something else?
- [ ] The anonymized training corpus — file format, rough size, where stored?
- [ ] The peer benchmarking corpus — same
- [ ] State overlays and enforcement index — standalone files or folded into the main register?
- [ ] What actually gets refreshed and how often — not the aspirational answer, the real one

---

## Part 4: Tacit Knowledge (5 min)
*Kevin only — Robin keep him from underselling this*

- [ ] What phrasing or sequencing has Kevin learned makes outputs significantly better? (The muscle-memory stuff he does without thinking — that's the undocumented logic that breaks silently in migration)
- [ ] Any consistent corrections he makes after generation — even small ones?

---

## Closing (5 min)
- [ ] Confirm Ben has enough to begin the eval harness design
- [ ] Name the single biggest unknown that would block the design — assign an owner
- [ ] Next touchpoint — date and format

---

**Watch for:** Kevin describing what an engine *should* do rather than what it *does* today. When that happens, redirect to "show me the file" or "what did you upload last time you ran it." The gap between Kevin's mental model and what's actually in Claude is the whole risk in this migration.
