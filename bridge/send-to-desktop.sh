#!/bin/bash
# Wrapper to run send-to-desktop.swift using the swift interpreter
# (which already has accessibility permissions)
#
# Usage:
#   bridge/send-to-desktop.sh "Your prompt here"
#   bridge/send-to-desktop.sh --file /path/to/prompt.txt

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
swift "$SCRIPT_DIR/send-to-desktop.swift" "$@"
