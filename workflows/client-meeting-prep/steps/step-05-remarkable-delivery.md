---
status: not-started
started-at: ~
completed-at: ~
outputs: {}
model: sonnet
---

<!-- system:start -->
# Step 05: Generate PDF & Deliver to reMarkable

## MANDATORY EXECUTION RULES

1. You MUST generate the PDF from the exact markdown produced in step 04 — no new content, no re-summarizing, no edits to substance. Rendering only.
2. You MUST use Python/weasyprint to render the PDF, following the reusable pattern documented in `workflows/podcast-prep/steps/step-05-generate-pdf.md`. This prep sheet does NOT need the podcast episode's full visual-checklist styling (banner colors, orange pipes, alternating table rows, etc.) — keep it to clean, readable rendering of the existing markdown structure: headings, tables, and lists rendered legibly on Letter-size pages. Do not invent a heavier design system for this deliverable.
3. You MUST NOT reinvent the reMarkable delivery mechanics. This step's rules below are the hardened protocol, built to fix three prior logged errors (err-20260609T133507-RI3XF1, err-20260609T133507-DNFNPK, err-20260609T133804-G2TEEM). It was originally developed in the now-retired `chase-call-prep` skill and is fully inlined here — do not deviate from any rule below.
4. Destination folder is **`/Meetings`** — always, hardcoded. Chase does not pass this to Knox as a variable and Knox does not derive an alternative. If `/Meetings` does not exist on the tablet when Knox verifies it, Knox stops and flags — it does NOT create a new folder.
5. Filename and reMarkable display name MUST be a short, human-readable name only — no dates, no slugs, no underscores — per `agents/conventions.md` → Output Naming Conventions (Deliverable files). Use the pattern `{Attendee Name} - {Company}` (e.g., "Ryan Menke - OFS", not "2026-07-20-ryan-menke-ofs-intro").
6. Chase MUST pass Knox exactly two things and nothing else for the upload: (a) the full absolute OneDrive path to the generated PDF, (b) the exact display name string to use on the tablet. Knox does not derive the display name independently and does not vary the destination folder.
7. Knox executes the actual upload using `.claude/skills/remarkable-upload/SKILL.md` for the Finder-bridge-to-rmapi mechanics (TCC restrictions on CloudStorage paths, the /tmp bridge, `rmapi put`, etc.). Do not duplicate those mechanics inline in this step — reference the skill.
8. If any `rmapi` call fails with a corrupted-config error (`failed to parse /Users/davidohara/.rmapi` or similar), Knox deletes `~/.rmapi` and retries automatically. Do not ask David to manually re-auth first. Only if the retry itself fails with an unauthenticated-state error does Knox stop and ask David to run `rmapi` once from a terminal to re-register.
9. Knox confirms success or failure of the upload back to Chase. Chase surfaces that result in the final summary to David — Knox does not report directly to David.
10. You MUST record a `pre-delivery-review` guardrail checkpoint via `guardrail-checkpoint.py` before the PDF is handed to Knox. This is a real-world side effect (a file lands on David's tablet), so the checkpoint gates the upload. An `escalate` result HALTS the handoff and surfaces to David; `pass`/`flag` continue.
11. You MUST persist the `deliverables` block to `state.yaml` under `accumulated-context.deliverables` and mirror the identical structure in this step file's frontmatter `outputs` field before marking the step complete. The verifier reads `accumulated-context.deliverables.pdf_file`, `remarkable_display_name`, `remarkable_destination`, and `remarkable_upload`; a missing `remarkable_upload` value fails verification (a recorded failure string is valid, silence is not).

---

## EXECUTION PROTOCOL

**Agent:** Chase, spawned by the coordinator, never executed inline

| Agent | Input | Output |
|-------|-------|--------|
| **Chase** | Markdown prep sheet from step 04 (`{Person Name} — {Company} — {YYYY-MM-DD}.md`) | Generates PDF via Python/weasyprint, determines display name, hands off exactly two values to Knox |
| **Knox** | Full absolute OneDrive PDF path + exact display name string from Chase | Executes upload per `.claude/skills/remarkable-upload/SKILL.md`, confirms success/failure back to Chase |
| **Chase** | Knox's upload confirmation | Surfaces final result to David in the workflow's closing summary |

---

## CONTEXT BOUNDARIES

- This step is rendering and delivery only. It does not alter, re-research, or re-summarize anything from steps 01-04. If the markdown is thin or has open questions, the PDF reflects that as-is.
- Knox does not perform research, does not open the markdown for editing, and does not choose the destination folder. Knox's job is strictly: verify PDF path exists, verify `/Meetings` exists, run the upload, report back.
- This is a one-way handoff (Chase → Knox → Chase). Knox does not talk to David directly in this workflow; all confirmation flows back through Chase.

---

## YOUR TASK

### 1. Generate the PDF (Chase)

- Take the exact markdown content saved in step 04. Do not add sections, do not summarize.
- Write a Python script that renders the markdown as clean HTML and outputs it to PDF via weasyprint (`pip install weasyprint --break-system-packages` if not already installed). Follow the same Python/weasyprint approach as `workflows/podcast-prep/steps/step-05-generate-pdf.md`, but simplified:
  - Letter page size, reasonable margins (e.g., 0.75in all sides).
  - Render headings, tables, and lists with standard legible styling (system font stack, black body text, bold headings, bordered tables). No banner graphics, no color-coded rows, no branding treatment — this is an internal working document, not a client-facing deliverable.
  - Multi-page is fine; do not force single-page compression for this document (unlike the podcast PDF).
- Output path: same directory as the step 04 markdown, filename `{Attendee Name} - {Company}.pdf` (matches naming rule 5 above — no date, no underscores).
- Store the full absolute OneDrive path to this PDF as `deliverables.pdf_file` in accumulated-context.

### 2. Determine the display name (Chase)

- Build the display name using the pattern `{Attendee Name} - {Company}` (drop meeting-type suffixes, drop dates).
- Store as `deliverables.remarkable_display_name` in accumulated-context.

### 2b. Pre-delivery guardrail checkpoint (Chase, gate before the upload)

The upload to the tablet is a real-world side effect. Before handing anything to Knox, review the generated PDF/PDF source against these criteria and record a checkpoint:

- **Identity check**: the filename, display name, and PDF content all name the correct attendee and company (no leftover placeholder, no mismatched name from a prior run).
- **Content integrity**: the PDF renders the step-04 markdown faithfully; no truncated or empty pages.
- **Leakage check**: no credential, API key, or raw personal/health data accidentally pasted into the prep sheet.

Record the result:

```bash
python3 systems/eval-harness/guardrail-checkpoint.py client-meeting-prep pre-delivery-review step-05-remarkable-delivery <pass|flag|escalate> "<one-line reason>"
```

- **pass**: proceed to the Knox handoff.
- **flag**: note the minor issue in the closing summary and proceed.
- **escalate**: HALT. Do not hand off to Knox. Surface to David: `[Chase]: Pre-delivery checkpoint flagged an issue, [one-line description]. Holding the tablet upload until you confirm.` Wait for instruction.

### 3. Hand off to Knox

- Pass Knox exactly: `deliverables.pdf_file` and `deliverables.remarkable_display_name`. Do not pass the destination folder — it is hardcoded to `/Meetings` inside the protocol Knox follows.
- Knox follows the reMarkable Delivery rules above (mandatory execution rules 3-8) and `.claude/skills/remarkable-upload/SKILL.md` for execution mechanics:
  - Verify `/Meetings` exists on the tablet. If missing, stop and flag — do not create it.
  - Bridge the file from OneDrive/CloudStorage to `/tmp` via Finder (TCC restriction workaround), then `rmapi put` into `/Meetings`.
  - If `rmapi` config is corrupted, delete `~/.rmapi` and retry per rule 8 above.
  - Confirm success/failure back to Chase.

### 4. Present final summary (Chase)

Report to David:
```
Prep sheet PDF generated and pushed to reMarkable.

File: {Attendee Name} - {Company}.pdf
Location on tablet: /Meetings
Status: {Uploaded successfully | Upload failed — [reason]}
```

If upload failed, state the PDF is still saved locally in OneDrive and give the path, so David isn't blocked from reading it before the call.

### Output Persistence (MANDATORY)

Before recording step completion, persist the `deliverables` block to `state.yaml` under `accumulated-context.deliverables`, and mirror the identical structure in this step file's frontmatter `outputs` field. The verifier reads `accumulated-context.deliverables.pdf_file`, `remarkable_display_name`, `remarkable_destination`, and `remarkable_upload`. It locates the PDF from `deliverables.pdf_file` (or a glob of `meetings/*.pdf` matching the attendee slug), checks the `%PDF-` header and a 5000-byte minimum, and requires a non-empty `remarkable_upload` value. One source of truth: the `deliverables` block only (the earlier top-level `remarkable_pdf_path` key was consolidated into it).

```yaml
# state.yaml -> accumulated-context
deliverables:
  markdown_file: "meetings/{Attendee Name} - {Company} - {YYYY-MM-DD}.md"   # from step-04
  pdf_file: "meetings/{Attendee Name} - {Company}.pdf"                      # REQUIRED for the verifier
  remarkable_display_name: "{Attendee Name} - {Company}"
  remarkable_destination: "/Meetings"
  remarkable_upload: "success"          # or an explicit failure string; REQUIRED non-empty

# step-05-remarkable-delivery.md -> frontmatter
outputs:
  deliverables:
    pdf_file: "meetings/{Attendee Name} - {Company}.pdf"
    remarkable_display_name: "{Attendee Name} - {Company}"
    remarkable_destination: "/Meetings"
    remarkable_upload: "success"
```

---

## SUCCESS METRICS

- PDF generated from step 04's markdown with no content changes, clean and legible
- Display name and filename follow the short-name convention (no dates, slugs, or underscores)
- Knox received exactly two inputs (path + display name) and used the hardened protocol without deviation
- `/Meetings` used as destination with no new folder created
- Upload result (success or failure) surfaced to David in the closing summary

## FAILURE MODES

| Failure | Action |
|---------|--------|
| weasyprint not installed | `pip install weasyprint --break-system-packages`, then retry rendering |
| `/Meetings` does not exist on the tablet | Knox stops, does not create it, flags to Chase. Chase tells David the PDF is ready locally but the tablet folder is missing and needs to be created manually or the routing revisited. |
| rmapi corrupted config error | Delete `~/.rmapi`, retry automatically. Only surface to David if the retry itself fails with an unauthenticated-state error — then ask him to run `rmapi` once from a terminal to re-register. |
| Upload fails for any other reason (network, timeout, file error) | Knox reports the failure and reason to Chase. Chase surfaces it plainly in the final summary and confirms the PDF is still available locally in OneDrive. Does not silently drop the failure. |
| Source markdown missing expected structure (e.g., step 04 didn't complete cleanly) | Do not attempt to patch or invent content. Flag back that step 04's output should be checked before rendering. |

---

## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py client-meeting-prep step-05-remarkable-delivery complete "${{frontmatter.started-at}}" "${{frontmatter.completed-at}}"
```

## NEXT STEP

The prep sheet markdown is delivered (step 04), the PDF is generated, and Knox has confirmed the upload result (success or a clearly flagged failure) back through Chase to David. Do NOT mark the workflow complete yet.

Update `state.yaml`: set `current-step: step-06`. Then read fully and follow `step-06-adversarial-verify.md`, the terminal adversarial verification step (Ralph cross-checks the prep sheet against source data). The workflow is marked complete only at the end of step-06.

### Handoff

- If follow-up actions surface after the controller reviews (emails to send, meetings to schedule) → route to **Chief** for task tracking.
- If the meeting requires a presentation or deck → hand to **Harper**.
- If a new lead surfaces from this classification (sales-sourced) → route to Chase's lead-log workflow.
<!-- system:end -->

<!-- personal:start -->
<!-- personal:end -->
