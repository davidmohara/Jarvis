---
name: jarvis-inbox
description: >
  Process items from the "Jarvis" folder in the Improving account of Apple Mail —
  David's agent inbox for routing tasks, references, and action items to the IES system.
  Trigger on boot (morning briefing), during daily review, or when David says "check my
  Jarvis folder", "process my inbox", or "anything in the Jarvis folder?"
agent: chief
---

# Jarvis Inbox — Mail Folder Processing

## Purpose

David forwards or moves emails to a **"Jarvis"** folder in Apple Mail (Improving account)
when he wants the IES system to process them. Chief scans this folder, classifies each
item, routes it to the right agent or system, and reports what was processed.

## How It Works

### 1. Scan the Folder

Pull all items from the Jarvis mailbox via AppleScript:

```applescript
tell application "Mail"
  set improvingAcct to null
  repeat with a in every account
    if name of a contains "Improving" then set improvingAcct to a
  end repeat
  set jarvisMB to mailbox "Jarvis" of improvingAcct
  set msgs to messages of jarvisMB
  -- iterate msgs, collect id, subject, sender name+address, date received, content
end tell
```

If the folder is empty, report "Jarvis inbox is empty" and exit.

### 2. Classify Each Item

For each email, determine its type and routing:

| Signal | Classification | Route To |
|--------|---------------|----------|
| Lead, prospect, company intro, "met this person at..." | **Lead / Contact** | Chase — add to lead tracker or Clay |
| Article, resource, "read this", FYI, newsletter | **Knowledge / Reference** | Knox — file in Obsidian vault |
| Task, follow-up, reminder, "don't forget to..." | **Action Item** | Chief — create OmniFocus task |
| Meeting request, scheduling, calendar | **Calendar** | Chief — handle directly |
| Draft request, "write this", content idea | **Comms / Content** | Harper — queue for drafting |
| Coaching, 1:1 context, team feedback | **People / Coaching** | Shep — add to person file |
| Wine order confirmation (Last Bottle, etc.) | **Wine / Invintory** | Chief — call `invintory_add_delivery` for each wine ordered. Extract: wine name, producer, vintage, qty, price per bottle, order number (→ notes), order date, ETA if given. Then archive. |
| Invoice, receipt, order confirmation | **Administrative** | Chief — file or note, no action unless flagged |
| Unclear or multi-category | **Triage** | Surface to David with recommendation |

### 3. Process Each Item

For each classified item:

1. **Extract the actionable content**: subject, sender, key details, any attachments noted
2. **Execute the routing**:
   - **Chase items**: Note in working memory for lead review. If a new contact, suggest adding to Clay.
   - **Knox items**: Summarize and note for Obsidian filing. If it's an article URL, capture the link and title.
   - **Chief items**: Create an OmniFocus task with context from the email.
   - **Harper items**: Note the request with context for the next drafting session.
   - **Shep items**: Note the person and context for the next 1:1 prep.
   - **Wine / Invintory items**: Call `invintory_add_delivery` for each wine line item. Default destination: Classic. For Marathon shipping orders (Last Bottle), set expected_date ~6 weeks out.
   - **Administrative**: Log and move on unless David flagged it.
3. **Archive the email**: After successful processing, move the email out of the Jarvis
   folder via AppleScript:

   ```applescript
   tell application "Mail"
     set improvingAcct to null
     repeat with a in every account
       if name of a contains "Improving" then set improvingAcct to a
     end repeat
     set archiveMB to mailbox "@Archive" of improvingAcct
     move theMessage to archiveMB
   end tell
   ```

   To move all processed messages at once (more efficient):
   ```applescript
   -- collect all non-triage messages first, then:
   repeat with m in msgsToArchive
     move m to archiveMB
   end repeat
   ```

4. **Exception — Triage items**: Do NOT archive emails classified as **Triage** (unclear
   or needing David's input). Leave these in the Jarvis folder until David decides.
   Once David gives direction and the item is processed, archive it then.

### 4. Report

Present a concise summary:

```
Jarvis inbox — [N] items processed:

→ Chase: [description] (from: [sender])
→ Knox: [description] (from: [sender])
→ Chief: Created task "[task name]"
→ Invintory: Added [N] deliveries — [wine names]
→ [item needing your input]: [description] — [recommendation]

[N] items still need your call: [list if any]
```

## Deduplication

The archive step is the primary dedup mechanism — once processed, the email leaves the
Jarvis folder entirely, so subsequent scans never see it again. The only items that
persist in the folder are **Triage** items awaiting David's decision. If a Triage item
has been sitting for more than 2 sessions without resolution, re-surface it with a nudge.

## When to Run

| Trigger | Context |
|---------|---------|
| Morning briefing (boot) | Scan as part of Phase 2 parallel data gathering |
| Daily review | Scan before capture step — surface anything David sent during the day |
| On demand | "Check my Jarvis folder", "anything in my inbox?", "process Jarvis" |

## Failure Modes

| Failure | Action |
|---------|--------|
| Apple Mail AppleScript unavailable | Report "Can't reach Mail — skipping Jarvis inbox" and proceed |
| Folder empty | Report "Jarvis inbox is empty" — this is normal, not an error |
| Classification unclear | Surface the item to David with your best guess and let him decide |
| Email has attachments | Note the attachment names but don't attempt to download — flag for David if action-dependent |
