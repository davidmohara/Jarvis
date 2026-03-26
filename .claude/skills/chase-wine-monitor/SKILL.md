---
name: chase-wine-monitor
description: Monitor Last Bottle Wines for flash deals matching David's taste profile
context: fork
agent: general-purpose
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - WebFetch
---

<!-- system:start -->
You are running the Last Bottle Wine Monitor for David O'Hara.

## What This Does
Polls lastbottlewines.com for flash wine offers and scores them against David's taste profile. Alerts via Slack when a match is found.

## How to Run

### Single poll (check what's live right now):
```bash
python3 /home/user/Jarvis/systems/wine-monitor/monitor.py
```

### Test mode (see scores without sending alerts):
```bash
python3 /home/user/Jarvis/systems/wine-monitor/monitor.py --test
```

### Start daemon (continuous monitoring through drop windows):
```bash
python3 /home/user/Jarvis/systems/wine-monitor/monitor.py --daemon &
```

### Install cron for automatic daily monitoring:
```bash
bash /home/user/Jarvis/systems/wine-monitor/install.sh
```

## Taste Profile
Located at `/home/user/Jarvis/systems/wine-monitor/taste-profile.json`. Edit to adjust varietal preferences, region weights, minimum alert score (default: 15), max price ($250), and cult producer list.

## Drop Windows (Central Time)
| Time | Theme | Poll Rate |
|------|-------|-----------|
| 11:00 AM | Pinot Noir Hour | Every 3 min |
| 1:00 PM | Hour of Power | Every 2 min |
| 3:00 PM | Steals & Deals | Every 5 min |
| 5:00 PM | International | Every 3 min |
| 6:00 PM | Skeleton Crew | Every 10 min |

When David asks to check wines, run --test mode and report results. When asked to start monitoring, run --daemon mode.
<!-- system:end -->
