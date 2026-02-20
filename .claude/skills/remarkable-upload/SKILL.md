---
name: remarkable-upload
description: Upload PDF or EPUB files to reMarkable tablet. Use when the user wants to send a document to their reMarkable, upload a PDF/EPUB, or put a file on their tablet.
context: fork
agent: general-purpose
allowed-tools:
  - "Bash(*)"
---

# reMarkable Upload

Upload PDF and EPUB files to the reMarkable tablet via the cloud API using `rmapi`.

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

1. **Identify the file** to upload. Accept a file path from the user. If the path is relative, resolve it from the current working directory. Confirm the file exists and is a PDF or EPUB.

2. **Determine the target folder** using the routing rules above. If the user specified a destination, use it. Otherwise, infer from context and confirm with the user if ambiguous.

3. **Create the folder if needed**. If the target subfolder doesn't exist yet (e.g., a new client account):

```bash
rmapi mkdir "/Improving/Accounts/NewClient"
```

4. **Upload with rmapi**:

```bash
rmapi put "<absolute-file-path>" "<target-folder>"
```

5. **Report the result** back to the user. On success, confirm the document name, the folder it was placed in, and that it will sync to the tablet.

## Notes

- Only PDF and EPUB files are supported.
- `rmapi` is installed at `/opt/homebrew/bin/rmapi` and handles cloud auth automatically.
- Use `rmapi ls <folder>` to verify a folder exists before uploading.
- Use `rmapi mkdir <folder>` to create a new folder if needed.
- The document name on the tablet will be the filename without extension.
- When in doubt about routing, ask the user rather than guessing wrong.
