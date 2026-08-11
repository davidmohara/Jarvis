---
date: 2026-08-11
type: correction
subject: Plaud ingest error — Robyn Fuentes incorrectly listed as attendee
file_id: b41015b6c997f774fc349a5ee9be51fe
---

# Correction: 2026-08-10 Plaud Ingest (file_id b41015b6c997f774fc349a5ee9be51fe)

## What Was Wrong

Knox incorrectly listed Robyn Fuentes as an attendee in the plaud-ingest output for the 2026-08-10 recording. The calendar event ("Texans Suite Menu Review", 4:00–4:30 PM CT) had only two confirmed attendees: David O'Hara and Alice Mburu. Robyn's name appeared briefly in the raw Plaud transcript (one line at 00:19 and one at 07:09), which the ingest agent picked up and incorrectly promoted to full attendee status.

## What Was Fixed

1. **Vault note** (`zzPlaud/YPO/2026-08-10 Hospitality Plan for UTB YPO Events Pending Budget Approval.md`):
   - Removed Robyn Fuentes from the Attendees section
   - Rewrote Summary to remove "David, Alice, and Robyn" — now reads "David and Alice"
   - Updated H1 title to include "Texans Suite Menu Review" as the calendar-verified event name
   - Removed duplicate Attendees section created by a failed patch operation
   - Raw transcript left verbatim (Robyn's transcript lines are factual record of what Plaud captured)

2. **Monday tasks** (IDs: 12776900082, 12776920269, 12776903744, 12776916886): Verified clean — none referenced Robyn. No updates needed.

## Root Cause

Plaud transcript attribution picked up ambient voice lines from Robyn and promoted them to attendee status. The calendar event is the authoritative source for attendee lists; transcript speaker detection is unreliable for brief/ambient lines. Knox should cross-reference calendar attendees before listing participants in any ingest output.

## Lesson

Always validate ingest-detected attendees against the confirmed calendar event before writing to vault or creating downstream tasks.
