#!/bin/sh
# git-credential-helper.sh
# Rotation-proof credential helper for Cowork sandbox.
# Reads credentials from .git-credentials in the same directory as this script.
# The ! prefix in credential.helper means git calls: <script> <action>
# We only need to handle "get" — other actions (store, erase) are no-ops.

ACTION="$1"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CREDS_FILE="$SCRIPT_DIR/.git-credentials"

if [ "$ACTION" != "get" ]; then
  exit 0
fi

if [ ! -f "$CREDS_FILE" ]; then
  # No credentials file — exit cleanly, git will prompt interactively
  exit 0
fi

# Read stdin to get protocol and host
while IFS= read -r line || [ -n "$line" ]; do
  key="${line%%=*}"
  val="${line#*=}"
  case "$key" in
    protocol) protocol="$val" ;;
    host) host="$val" ;;
  esac
done

# Search credentials file for matching entry
# Format: https://username:token@host
while IFS= read -r cred || [ -n "$cred" ]; do
  [ -z "$cred" ] && continue
  # Extract host from credential URL
  cred_host="${cred##*@}"
  cred_host="${cred_host%%/*}"
  if [ "$cred_host" = "$host" ]; then
    # Extract user:pass
    userpass="${cred#*://}"
    userpass="${userpass%@*}"
    username="${userpass%%:*}"
    password="${userpass#*:}"
    printf 'username=%s\npassword=%s\n' "$username" "$password"
    exit 0
  fi
done < "$CREDS_FILE"

exit 0
