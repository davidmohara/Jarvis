---
name: remarkable-sync
description: "Sync handwritten notes from reMarkable tablet to Obsidian as markdown. Use when the user says 'sync my remarkable', 'pull my remarkable notes', 'download remarkable', 'remarkable to obsidian', or any request to get handwritten notes off their tablet. Also trigger when the user asks about recent notes they wrote on the tablet, or wants to find something they jotted down on the reMarkable."
---

<!-- personal:start -->
# reMarkable Sync

Pull new and updated handwritten notes from the reMarkable tablet, transcribe them using Claude's vision, and save as markdown to the Obsidian vault — mirroring the tablet's folder structure.

## Dispatch: Run as Sub-Agent

**Do NOT run this skill inline.** When triggered, dispatch the entire workflow below to a general-purpose sub-agent using the Agent tool. This keeps the sync's heavy I/O and vision calls out of the main conversation context.

```
Agent(
  subagent_type: "general-purpose",
  description: "Sync reMarkable to Obsidian",
  prompt: "<paste full workflow below>"
)
```

The sub-agent will write a sync report to `/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/reports/remarkable_sync_report.md`. When it returns, read the report and give David a summary.

---

## Critical: Execution Environment

This skill runs inside a Linux VM, but all reMarkable and filesystem operations happen on the **host Mac** via the `osascript` MCP tool (Control your Mac). The tools involved:

| Tool | Location | Purpose |
|------|----------|---------|
| `rmapi` | `/opt/homebrew/bin/rmapi` | reMarkable cloud API — list, download, stat |
| `rmc` | `/opt/homebrew/bin/rmc` | Convert .rm stroke files → SVG |
| `rsvg-convert` | `/opt/homebrew/bin/rsvg-convert` | Convert SVG → PNG for vision |

**Never** run these from Bash in the VM. Always use `osascript`.

## Paths

| What | Path |
|------|------|
| Obsidian vault | `/Users/davidohara/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian/` |
| Remarkable folder in Obsidian | `{vault}/Remarkable/` |
| Sync manifest | `{vault}/Remarkable/.sync_manifest.json` |
| Working directory for downloads | `/tmp/remarkable-sync/` |

## Workflow

### 1. Prepare workspace

```applescript
do shell script "rm -rf /tmp/remarkable-sync && mkdir -p /tmp/remarkable-sync"
```

### 2. Walk the reMarkable tree

Recursively list folders and files on the tablet. For each file, get its `stat` metadata to check `ModifiedClient` timestamp.

```applescript
do shell script "/opt/homebrew/bin/rmapi ls / 2>&1"
```

Folders to sync (these contain handwritten content):

- `/Improving/` and all subfolders
- `/Meetings/`
- `/Projects/`
- `/Terra Arma/`
- `/UTB/`
- `/YPO/` (except `/YPO/Forum/` — skip that subfolder)
- Root-level files (`[f]` entries in `/`)

**Skip these:**
- `/Books/` — uploaded PDFs for reading, not handwritten notes
- `/Journal/` — personal journal, excluded from sync
- `/YPO/Forum/` — private forum notes, excluded from sync
- `/trash/`

For each directory, parse `rmapi ls` output. Lines starting with `[d]` are directories (recurse into them). Lines starting with `[f]` are files (check for changes).

### 3. Detect changes

Load the sync manifest from Obsidian:

```applescript
do shell script "cat '/Users/davidohara/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian/Remarkable/.sync_manifest.json' 2>&1"
```

If it doesn't exist, treat everything as new. The manifest structure:

```json
{
  "last_sync": "2026-03-06T10:00:00Z",
  "files": {
    "/Meetings/Wesley Randall": {
      "modified": "2026-01-19T15:30:00Z",
      "synced": "2026-02-01T10:00:00Z",
      "page_count": 1
    }
  }
}
```

For each file found in the tree walk, run `rmapi stat`:

```applescript
do shell script "/opt/homebrew/bin/rmapi stat '/path/to/file' 2>&1"
```

Compare `ModifiedClient` from stat against the manifest's `modified` value. A file needs syncing if:
- It's not in the manifest (new file), OR
- Its `ModifiedClient` is newer than the stored `modified` timestamp

### 4. Download changed files

For each file that needs syncing:

```applescript
do shell script "cd /tmp/remarkable-sync && /opt/homebrew/bin/rmapi get '/Path/To/File' 2>&1"
```

This downloads a `.rmdoc` file (a zip archive) to `/tmp/remarkable-sync/`. The file extension is `.rmdoc`, NOT `.zip`.

### 5. Extract and render pages

Each `.rmdoc` contains:
- `{uuid}.content` — JSON metadata with page list and ordering
- `{uuid}/{page-uuid}.rm` — Binary stroke data for each page

**Extract the .rmdoc** (it's a standard zip archive despite the extension):

```applescript
do shell script "cd /tmp/remarkable-sync && unzip -o 'FileName.rmdoc' -d 'FileName_extracted' 2>&1"
```

**Parse the .content file** to get page order:

```applescript
do shell script "cat /tmp/remarkable-sync/FileName_extracted/*.content 2>&1"
```

The `.content` JSON has `cPages.pages` array — each entry has an `id` field. Process pages in array order. The UUID for the document-level directory is in the `.content` filename (before `.content`).

**Important edge cases from testing:**
- A page ID in `cPages.pages` might not have a corresponding `.rm` file — this means the page is blank/unused. Skip it gracefully.
- `pageCount` in the JSON may not match the actual number of page entries in `cPages.pages`. Trust the `cPages.pages` array for ordering, and check for `.rm` file existence before rendering.

**Page count guard**: If a notebook has more than 30 pages, pause and ask David whether to sync it. Notebooks like "Bible Daily" (3000+ pages) should not be auto-synced. If David says yes, ask which page range to sync.

**For each page, convert .rm → SVG → PNG:**

```applescript
do shell script "/opt/homebrew/bin/rmc -f rm -t svg -o '/tmp/remarkable-sync/page_N.svg' '/tmp/remarkable-sync/FileName_extracted/{uuid}/{page-uuid}.rm' 2>&1"
```

```applescript
do shell script "/opt/homebrew/bin/rsvg-convert -f png -d 150 -p 150 -o '/tmp/remarkable-sync/page_N.png' '/tmp/remarkable-sync/page_N.svg' 2>&1"
```

Use 150 DPI for readable text without oversized files. Increase to 200 if transcription quality is poor.

**Blank page detection**: If the resulting PNG is under 2KB, the page is blank (just template lines, no handwriting). Skip it — don't transcribe or include in the markdown output.

### 6. Transcribe with Claude vision

Copy each PNG to the VM workspace (via the OneDrive bridge) so Claude can read it:

```applescript
do shell script "cp /tmp/remarkable-sync/page_N.png '/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/remarkable_temp_page.png' 2>&1"
```

Then read it from the VM:

```
Read /sessions/*/mnt/IES/remarkable_temp_page.png
```

**Transcription rules:**

- Transcribe the handwriting faithfully — don't editorialize or restructure
- Use markdown formatting naturally: `#` for clear headings, `-` for bullet points, `>` for indented/quoted sections
- Preserve the writer's structure — if they used bullets, use bullets; if they wrote in paragraphs, write paragraphs
- Names, dates, and numbers should be transcribed exactly as written
- If something is illegible, use `[illegible]` rather than guessing
- For drawings or diagrams, describe them briefly in italics: *[diagram: org chart showing reporting structure]*
- Add `---` between pages in multi-page documents

### 7. Save to Obsidian

**File path**: Mirror the reMarkable folder structure under `{vault}/Remarkable/`. Examples:

| reMarkable path | Obsidian path |
|-----------------|---------------|
| `/Meetings/Wesley Randall` | `Remarkable/Meetings/Wesley Randall.md` |
| `/Improving/One-on-ones/Don McGreal` | `Remarkable/Improving/One-on-ones/Don McGreal.md` |
| `/Current Actions` | `Remarkable/Current Actions.md` |

Create directories as needed:

```applescript
do shell script "mkdir -p '/Users/davidohara/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian/Remarkable/Meetings' 2>&1"
```

#### Deduplication (critical)

Before writing, check if the target file already exists. If it does:

1. **Read the existing file content** via osascript `cat`.
2. **For each transcribed page/section**, check whether substantially similar content already exists in the file. Compare by date headings (e.g., `### March 19, 2026`) and the first few bullet points. If a section with the same date heading and similar content already exists, **skip it** — do not append duplicate entries.
3. **Only append genuinely new sections** that don't already appear in the file. Use `>>` (append) instead of `>` (overwrite) when adding to an existing file.
4. **Update the YAML frontmatter** (`synced` timestamp and `pages` count) in the existing file rather than replacing the entire file.

If the file does not exist, create it fresh with full YAML frontmatter and all transcribed content.

#### File format

Build the markdown file with YAML frontmatter:

```markdown
---
source: reMarkable
synced: 2026-03-06T10:30:00Z
pages: 1
remarkable_path: /Meetings/Wesley Randall
---

# Wesley Randall

### January 19, 2026

- Defense Conf - Mar/Apr
- JPMorgan Guys & VC Liberty Ventures
...
```

**Title**: Use the document name from the reMarkable as the H1 heading.

#### Writing files

For **new files** (no existing file at the target path):

```applescript
do shell script "cat > '/path/to/file.md' << 'ENDOFFILE'
[full content with frontmatter]
ENDOFFILE"
```

For **existing files** (appending new sections only):

```applescript
do shell script "cat >> '/path/to/file.md' << 'ENDOFFILE'

---

### March 19, 2026

[new section content only]
ENDOFFILE"
```

Then update the `synced` timestamp in the frontmatter using `sed`:

```applescript
do shell script "sed -i '' 's/^synced: .*/synced: 2026-03-19T10:00:00Z/' '/path/to/file.md'"
```

### 8. Update the manifest

After all files are synced, update `.sync_manifest.json` with new timestamps:

```applescript
do shell script "cat > '/Users/davidohara/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian/Remarkable/.sync_manifest.json' << 'ENDOFFILE'
{
  "last_sync": "2026-03-06T10:30:00Z",
  "files": { ... }
}
ENDOFFILE"
```

### 9. Clean up

```applescript
do shell script "rm -rf /tmp/remarkable-sync 2>&1"
```

Also remove any temp PNG from the OneDrive bridge:

```applescript
do shell script "rm -f '/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/remarkable_temp_page.png' 2>&1"
```

### 10. Report

Write a sync report to `/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/reports/remarkable_sync_report.md` via osascript. Include:

- Total files synced (new vs updated)
- Each file: name, folder, page count
- Files skipped (too many pages, errors, blank)
- Any errors encountered

Example:

```
## Remarkable Sync Report — 2026-03-06

**3 files synced** (2 new, 1 updated)

| File | Folder | Pages | Status |
|------|--------|-------|--------|
| Wesley Randall | Meetings | 1 | new |
| Don McGreal | Improving/One-on-ones | 3 | new |
| Current Actions | / | 1 | updated |

**Skipped:** Bible Daily (3000+ pages)
```

The calling agent will read this file and relay the summary to David.

## Error Handling

- **`rmc` warnings about newer format**: These are non-fatal. The conversion usually still works. Proceed and check the output.
- **Empty SVG or blank PNG**: The page might be blank (unused page in a notebook). Skip it and note in the transcription: *[blank page]*
- **`rmapi` auth failure**: Tell David that rmapi needs re-authentication. He can run `/opt/homebrew/bin/rmapi` in Terminal to refresh the token.
- **Timeout on large files**: If a download or conversion hangs, skip that file and report it.

## What This Skill Does NOT Do

- It does not sync PDFs or ebooks back (those were uploaded via `remarkable-upload`)
- It does not modify or delete anything on the reMarkable
- It does not sync the entire Bible Daily notebook (3000+ pages) without explicit permission
- It does not push changes back to the reMarkable — this is a one-way pull
<!-- personal:end -->
