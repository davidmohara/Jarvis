#!/usr/bin/env bash
# IES Channel Daemon — install script
# Sets up Python dependency and verifies config before first run.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IES_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$IES_ROOT/config/.env"

echo "=== IES Channel Daemon — Install ==="
echo "IES root: $IES_ROOT"
echo ""

# 1. Verify claude binary
if which claude &>/dev/null; then
  echo "  ✓ claude binary found: $(which claude) ($(claude --version 2>&1))"
else
  echo "  ✗ claude not found — is Claude Code installed?"
  exit 1
fi
echo ""

# 2. Check SLACK_BOT_TOKEN
if grep -q "SLACK_BOT_TOKEN=xoxb-" "$ENV_FILE" 2>/dev/null; then
  echo "  ✓ SLACK_BOT_TOKEN found in config/.env"
else
  echo "  ⚠ SLACK_BOT_TOKEN missing or not set in config/.env"
  echo "    Add: SLACK_BOT_TOKEN=xoxb-your-token"
fi

# 3. Check required channel config
if grep -q "IES_CHANNEL_ID=" "$ENV_FILE" 2>/dev/null; then
  echo "  ✓ IES_CHANNEL_ID found in config/.env"
else
  echo "  ⚠ IES_CHANNEL_ID not set in config/.env"
  echo "    Add: IES_CHANNEL_ID=C0YOUR_CHANNEL_ID"
fi

if grep -q "IES_OWNER_USER_ID=" "$ENV_FILE" 2>/dev/null; then
  echo "  ✓ IES_OWNER_USER_ID found in config/.env"
else
  echo "  ⚠ IES_OWNER_USER_ID not set in config/.env"
  echo "    Add: IES_OWNER_USER_ID=U0YOUR_USER_ID"
fi

# 4. Create data directory
mkdir -p "$SCRIPT_DIR/data"
echo "  ✓ data/ directory ready"
echo ""

# 5. Dry run
echo "→ Running test poll (--test mode, no API calls or posts)..."
python3 "$SCRIPT_DIR/ies-channel.py" --test
echo ""
echo "=== Install complete ==="
echo ""
echo "To start the daemon:"
echo "  python3 $SCRIPT_DIR/ies-channel.py"
echo ""
echo "Or configure as a scheduled task in Cowork via /schedule"
