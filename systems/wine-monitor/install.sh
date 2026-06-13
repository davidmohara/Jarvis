#!/usr/bin/env bash
# Install cron jobs for Last Bottle Wine Monitor
# All times are Central Time (America/Chicago)
#
# Schedule:
#   10:55 AM  — Start daemon (covers all windows through midnight)
#   12:01 AM  — Kill any lingering daemon
#
# The daemon self-adjusts polling frequency:
#   Hour of Power (1-3 PM):  every 2 min
#   Pinot / International:    every 3 min
#   Steals & Deals:           every 5 min
#   Skeleton Crew:            every 10 min
#   Between windows:          every 15 min

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MONITOR="${SCRIPT_DIR}/monitor.py"
PYTHON="$(command -v python3)"
LOGFILE="${SCRIPT_DIR}/data/monitor.log"

if [ -z "$PYTHON" ]; then
    echo "ERROR: python3 not found"
    exit 1
fi

# Cron entries (CT timezone)
CRON_START="55 10 * * * cd ${SCRIPT_DIR} && TZ=America/Chicago ${PYTHON} ${MONITOR} --daemon >> ${LOGFILE} 2>&1 &"
CRON_KILL="1 0 * * * pkill -f 'monitor.py --daemon' 2>/dev/null || true"

# Marker so we can identify our lines
MARKER="# jarvis-wine-monitor"

# Remove existing entries
crontab -l 2>/dev/null | grep -v "${MARKER}" | crontab - 2>/dev/null || true

# Add new entries
(crontab -l 2>/dev/null; echo "${CRON_START} ${MARKER}"; echo "${CRON_KILL} ${MARKER}") | crontab -

echo "Cron jobs installed:"
crontab -l | grep "${MARKER}"
echo ""
echo "Monitor will start daily at 10:55 AM CT and run through midnight."
echo "To start now: python3 ${MONITOR} --daemon &"
echo "To test:      python3 ${MONITOR} --test"
