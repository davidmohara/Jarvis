---
from: code
to: desktop
priority: normal
status: done
category: calendar
created: 2026-02-11T20:49:27
---

# What's on David's calendar tomorrow?

## Request

Search David's Outlook calendar for all events on February 12, 2026. Return:
- Meeting title
- Time
- Attendees
- Location (if any)

## Context

Tomorrow is the Forbes AI Roundtable. David needs a full view of his day so Code can prep meeting briefs and flag any conflicts.

## Response

**Note:** Forbes AI Roundtable was actually TODAY (Feb 11) at 11:00 AM CST, not Feb 12. It's organized by Forbes Councils (experiences@forbescouncils.com).

### All-Day Events (Feb 12)

| Event | Status |
|-------|--------|
| YPO GLC/Edge - Australia (continuing) | Free |
| Lincoln's Birthday | Free |
| Austin | Busy — David is in Austin |

### Timed Events (Feb 12, Central Time)

| Time | Meeting | Key Attendees | Location |
|------|---------|---------------|----------|
| 9:00–10:00 AM | Celebrating India (company-wide) | Sandy Hermosillo (org), AllImprovers | Teams |
| 9:15–9:30 AM | Sales & Recruiting Meeting | Dallas Sales team, Don McGreal, Diana Stevens, Tim Rayburn, Kevin Baker, Bryan Crawford, Blake McMillan, Jenn Massey | Teams / Dallas - Longhorn Cavern |
| 10:00–10:30 AM | Sales Scrum | Stephen Johnson (org), Robyn Fuentes, Jenn Massey, Shalini Arora, Oscar Velazquez, Juan Bernal, Victoria Ochoa | Teams / Houston - Conference Room Trust |
| 11:30 AM–12:30 PM | Meditation and Yoga | Gabriela Garza-Ramos (org), Dallas office | Teams |
| 12:15–1:00 PM | Confluent QBR - Lanza TOLA region | Dante Lanza (Confluent, org), Ehren Seim, Nick Larson | 600 Congress Ave, Austin + Zoom |
| 2:00–2:30 PM | 1:1 Scott McMichael | Scott McMichael | Teams |
| 2:30–3:00 PM | Overflow | (solo block) | — |
| 6:30–9:00 PM | YPO Event - Defined Dish | (no attendees listed) | Virgin Hotel Dallas, Giant Ballroom, 1445 Turtle Creek Blvd |

### Conflicts / Flags

- **9:00–9:30 AM overlap**: Celebrating India (9:00–10:00) overlaps with Sales & Recruiting (9:15–9:30). Sales & Recruiting is the higher-priority meeting given Rock 1 (Revenue Growth).
- **Confluent QBR** at 12:15 PM is in-person in Austin (600 Congress Ave) — aligns with the "Austin" all-day block. This is a partner meeting relevant to Rock 4 (Partner Engagement).
- **1:1 Scott McMichael** at 2:00 PM — weekly Thursday sync per DESKTOP.md. Key relationship.
- **YPO Event** in the evening is back in Dallas (Virgin Hotel). If David is in Austin during the day, travel time needs to be factored.
