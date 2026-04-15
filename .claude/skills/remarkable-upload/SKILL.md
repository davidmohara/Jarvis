---
name: remarkable-upload
description: Upload PDF or EPUB files to reMarkable tablet. Use when the user wants to send a document to their reMarkable, upload a PDF/EPUB, or put a file on their tablet.
model: haiku
---

<!-- personal:start -->
# reMarkable Upload

Upload PDF and EPUB files to the reMarkable tablet via the cloud API using `rmapi`.

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

### Batch Uploads

For multiple files, copy all files via Finder in one AppleScript block, then upload each via separate rmapi calls. This is more reliable than trying to loop within a single osascript invocation.

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
| No clear match | Ask the user where to put it |

## Workflow

1. **Identify the file(s)** to upload. Accept file path(s) from the user or from conversation context (e.g., files just generated). Confirm they exist in the VM workspace and are PDF or EPUB.

2. **Determine the target folder** using the routing rules above. If the user specified a destination, use it. Otherwise, infer from context and confirm with the user if ambiguous.

3. **Verify the target folder exists** on the tablet:
```applescript
do shell script "/opt/homebrew/bin/rmapi ls '/target/folder' 2>&1"
```

4. **Create the folder if needed**:
```applescript
do shell script "/opt/homebrew/bin/rmapi mkdir '/Improving/Accounts/NewClient' 2>&1"
```

5. **Copy files from OneDrive to /tmp via Finder** (required to bypass TCC):
```applescript
tell application "Finder"
    set srcFolder to POSIX file "/Users/davidohara/Library/CloudStorage/OneDrive-Improving/IES/relative/path/" as alias
    set destFolder to POSIX file "/tmp/" as alias
    duplicate file "Document.pdf" of folder srcFolder to folder destFolder with replacing
end tell
```

6. **Upload each file with rmapi**:
```applescript
do shell script "/opt/homebrew/bin/rmapi put '/tmp/Document.pdf' '/target/folder' 2>&1"
```

7. **Verify the upload landed**:
```applescript
do shell script "/opt/homebrew/bin/rmapi ls '/target/folder' 2>&1"
```

8. **Report the result** back to the user. On success, confirm the document name, the folder it was placed in, and that it will sync to the tablet.

## Notes

- Only PDF and EPUB files are supported.
- `rmapi` is installed on the **host Mac** at `/opt/homebrew/bin/rmapi` — never try to run it from Bash in the VM.
- All rmapi and Finder commands must go through the `osascript` MCP tool (Control your Mac).
- The Finder copy step is mandatory — `do shell script` cannot read from OneDrive CloudStorage due to macOS privacy restrictions, but Finder can.
- The document name on the tablet will be the filename without extension.
- When in doubt about routing, ask the user rather than guessing wrong.
<!-- personal:end -->

