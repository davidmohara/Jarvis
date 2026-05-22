---
name: remarkable-upload
description: Upload PDF or EPUB files to reMarkable tablet. Use when the user wants to send a document to their reMarkable, upload a PDF/EPUB, or put a file on their tablet.
model: haiku
---

<!-- personal:start -->
# reMarkable Upload

Upload PDF and EPUB files to the reMarkable tablet via the cloud API using `rmapi`.

## Plan-Only Mode

If the prompt contains the phrase "do not execute" or `eval-mode: plan-only`, do not run any rmapi, Finder, or osascript commands. Instead, produce a markdown plan describing the commands you would issue, in order, with the exact target folder, rationale, and the inputs you would pass to each. Save the plan to the requested output path and stop. Do not call rmapi or osascript under any circumstances when in plan-only mode.

This branch exists so the skill can be exercised by the Rigby eval loop without producing real uploads to the tablet.

## Critical: Execution Environment

This skill runs inside a Linux VM, but `rmapi` is installed on the **host Mac** at `/opt/homebrew/bin/rmapi`. All rmapi commands must be executed via the `osascript` MCP tool (Control your Mac), not via Bash.

The workspace folder in the VM (`/sessions/*/mnt/IES/...`) maps to a OneDrive-synced folder on the Mac. Due to macOS TCC (privacy) restrictions, shell commands run via `osascript` cannot directly read files from OneDrive CloudStorage paths. However, **Finder has full filesystem access** and can copy files without permission issues.

### The File Bridge Pattern

To get files from the workspace to rmapi:

1. **Use Finder to copy files to /tmp** (Finder bypasses TCC restrictions):
```applescript
tell application "Finder"
    set srcFolder to POSIX file "/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/path/to/folder/" as alias
    set destFolder to POSIX file "/tmp/" as alias
    duplicate file "filename.pdf" of folder srcFolder to folder destFolder with replacing
end tell
```

2. **Run rmapi from /tmp**:
```applescript
do shell script "/opt/homebrew/bin/rmapi put '/tmp/filename.pdf' '/target/folder' 2>&1"
```

If files were generated in the current session and exist in the VM workspace, the Mac-side path is:
`/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/` + the relative path from the workspace mount.

### When the Source Is Already at /tmp

If the source file is already under `/tmp` (or any path `do shell script` can read directly without TCC restrictions), **skip the Finder bridge step entirely** and invoke `rmapi put` against the source path directly. The Finder copy is only required when crossing the TCC boundary from `CloudStorage/`. Document this skip in your action log so the user can confirm the path was already shell-readable.

### Batch Uploads

For multiple files, copy all source files via Finder in **one combined AppleScript block** containing multiple `duplicate` statements, then upload each via **separate `rmapi put` invocations** (one osascript call per file). Looping inside a single osascript invocation is less reliable than separate calls.

**Partial-failure handling:** If a file in the middle of a batch fails (rmapi error, file-not-found, auth expired), do not abort the remaining files. Continue with the rest. At the end, report a single summary listing which files uploaded successfully and which failed, with the failure reason for each. The user can retry only the failed ones.

## Trigger Phrases

- "upload [file] to remarkable"
- "send this to my remarkable"
- "put [file] on my remarkable"
- "send [file] to my tablet"

## Folder Structure

The tablet is organized by domain. **Always route uploads to the correct folder based on context.** If the user specifies a folder, use it. Otherwise, infer the best location from the filename, content, and conversation context.

```
/
├── Books/                        ← books, ebooks, long-form reading
├── Improving/                    ← anything related to Improving (David's company)
│   ├── Accounts/                 ← client/account-specific materials
│   │   ├── Archive/
│   │   ├── LTSA/
│   │   ├── McKesson/
│   │   ├── ORIX/
│   │   ├── OZK/
│   │   ├── Siemens/
│   │   ├── United Texas Bank/
│   │   └── Veritas/
│   ├── Dallas/                   ← Dallas office materials
│   ├── Houston/                  ← Houston office materials
│   ├── One-on-ones/              ← 1:1 meeting prep and notes
│   │   ├── Devlin Liles/
│   │   ├── Don McGreal/
│   │   ├── Kevin Baker/
│   │   ├── Robyn Fuentes/
│   │   ├── Scott McMichael/
│   │   └── Tim Rayburn/
│   ├── Partners/                 ← partner company materials
│   │   └── Confluent QBR/
│   └── Podcast/                  ← podcast prep and episode materials
│       └── Episodes/
├── Journal/                      ← devotionals, personal journals
│   ├── Bible Daily/
│   ├── Joshua workbook/
│   └── Personal/
├── Meetings/                     ← general meeting notes and prep
├── Projects/                     ← project-specific materials
│   └── Design Templates/
├── Terra Arma/                   ← Terra Arma (board member role)
│   ├── One-on-ones/
│   │   ├── Rick Webb/
│   │   └── Sean Brown/
│   └── [board docs at root]
├── UTB/                          ← United Texas Bank (board member role)
│   ├── Audit & Compliance/
│   └── Board Meeting/
└── YPO/                          ← Young Presidents' Organization
    ├── Board/
    │   ├── Fort Worth Gold/
    │   ├── Lone Star Gold/
    │   └── Louisiana Gold/
    └── Forum/
```

## Routing Rules

Use these rules to determine the target folder. First match wins:

| Context signal | Target folder |
|---|---|
| User specifies a folder explicitly | Use that folder exactly |
| Book or ebook | `/Books` |
| Improving client/account (LTSA, McKesson, ORIX, OZK, Siemens, UTB, Veritas) | `/Improving/Accounts/{client}` |
| 1:1 prep for a direct report (Devlin, Don, Kevin, Robyn, Scott, Tim) | `/Improving/One-on-ones/{person}` |
| Improving partner material (e.g., Confluent) | `/Improving/Partners/{partner}` |
| Improving podcast content | `/Improving/Podcast` |
| Improving Dallas office | `/Improving/Dallas` |
| Improving Houston office | `/Improving/Houston` |
| General Improving material | `/Improving` |
| Terra Arma board docs | `/Terra Arma` |
| Terra Arma 1:1 (Rick Webb, Sean Brown) | `/Terra Arma/One-on-ones/{person}` |
| UTB board meeting materials | `/UTB/Board Meeting` |
| UTB audit/compliance | `/UTB/Audit & Compliance` |
| General UTB materials | `/UTB` |
| YPO chapter board material | `/YPO/Board/{chapter}` |
| YPO forum material | `/YPO/Forum` |
| General YPO material | `/YPO` |
| Journal or devotional | `/Journal` |
| Meeting prep (general) | `/Meetings` |
| Project materials | `/Projects` |
| No clear match | Surface 3-5 candidate folders and ask (see "Asking when ambiguous" below) |

### Asking When Ambiguous

When the routing rules above don't produce a clear single match, do not ask a bare "where should this go?" question and do not guess. Instead:

1. Identify the **3-5 most plausible candidate folders** from the folder structure, ranked by relevance to the filename and any conversational context.
2. Surface them as an enumerated list with one-line rationale each (e.g., `1. /Improving — "strategy" in the filename matches general Improving material`).
3. Add a final option: `Other (specify path)`.
4. Wait for the user's selection before constructing any rmapi command.

A clarifying question that doesn't pre-narrow the choices wastes a turn. Three-to-five ranked candidates is the right shape.

## Workflow

1. **Identify the file(s)** to upload. Accept file path(s) from the user or from conversation context (e.g., files just generated). Each path must end in `.pdf` or `.epub` — reject any other extension up front.

2. **Verify each source file exists before doing anything else.** Pick the check based on path:
   - **Path under `/tmp` or another shell-readable location:**
     ```applescript
     do shell script "test -f '/tmp/Document.pdf' && echo OK || echo MISSING"
     ```
   - **Path under `/Users/davidohara/Library/CloudStorage/OneDrive-Improving/...` (TCC-restricted):** use Finder to confirm, since `do shell script` cannot read CloudStorage paths.
     ```applescript
     tell application "Finder"
         exists file "Document.pdf" of folder (POSIX file "/Users/.../folder/" as alias)
     end tell
     ```

   If any file in the input list returns missing, **stop and report which paths could not be found**. Do not proceed to rmapi or Finder copy. Ask the user to correct the path or remove the missing file from the batch. Skipping this check causes the Finder copy step to fail mid-batch with a less actionable error.

3. **Determine the target folder** using the routing rules above. If the user specified a destination, use it. Otherwise, infer from context and confirm with the user if ambiguous.

4. **Verify the target folder exists** on the tablet:
```applescript
do shell script "/opt/homebrew/bin/rmapi ls '/target/folder' 2>&1"
```

5. **Create the folder if and only if the verification in step 4 reported it missing.** Do not run mkdir unconditionally — `rmapi mkdir` errors on existing folders, which would abort the upload. Parse the step 4 output: if it lists entries or returns the folder contents, skip step 5. If it returns "entry doesn't exist," "no such directory," or similar, run:
```applescript
do shell script "/opt/homebrew/bin/rmapi mkdir '/Improving/Accounts/NewClient' 2>&1"
```

6. **Copy files from OneDrive to /tmp via Finder** (required to bypass TCC, unless the source is already under /tmp — see "When the Source Is Already at /tmp" above):
```applescript
tell application "Finder"
    set srcFolder to POSIX file "/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/relative/path/" as alias
    set destFolder to POSIX file "/tmp/" as alias
    duplicate file "Document.pdf" of folder srcFolder to folder destFolder with replacing
end tell
```

7. **Upload each file with rmapi**:
```applescript
do shell script "/opt/homebrew/bin/rmapi put '/tmp/Document.pdf' '/target/folder' 2>&1"
```

**Overwrite vs. duplicate behavior:** `rmapi put` does NOT overwrite existing files. If a file with the same name already exists at the target folder, the new upload creates a second entry with a numeric suffix on the tablet. For recurring artifacts (quarterly board decks, weekly devotionals), the user typically wants the new version to replace the old one. **Before uploading a file whose name matches an existing entry**, ask the user whether to replace (run `rmapi rm '/target/folder/Document'` first, then put) or keep both. If unsure, ask.

8. **Verify the upload landed**:
```applescript
do shell script "/opt/homebrew/bin/rmapi ls '/target/folder' 2>&1"
```

9. **Report the result** back to the user. On success, confirm the document name, the folder it was placed in, and that it will sync to the tablet.

## Notes

- Only PDF and EPUB files are supported.
- `rmapi` is installed on the **host Mac** at `/opt/homebrew/bin/rmapi` — never try to run it from Bash in the VM.
- All rmapi and Finder commands must go through the `osascript` MCP tool (Control your Mac).
- The Finder copy step is mandatory when the source is under `CloudStorage/` — `do shell script` cannot read those paths due to macOS privacy restrictions, but Finder can. When the source is already under `/tmp` or another shell-readable path, the Finder bridge is unnecessary.
- `rmapi mkdir` errors if the folder already exists; always gate it on the result of an `rmapi ls` verification.
- `rmapi put` creates a new entry; it does not overwrite. To replace an existing file with the same name, run `rmapi rm` first.
- The document name on the tablet will be the filename without extension.
- When routing is ambiguous, surface 3-5 ranked candidate folders rather than asking a bare "where?" question.
<!-- personal:end -->

