#!/bin/bash
# IES Pre-Tool-Use Safety Hook
# Blocks a short list of genuinely destructive operations.
# Everything else runs without confirmation.
#
# Exit 2 = blocked. Exit 0 = allowed.

INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('tool_name', ''))
" 2>/dev/null)

# Only inspect Bash calls
if [ "$TOOL_NAME" != "Bash" ]; then
    exit 0
fi

COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('tool_input', {}).get('command', ''))
" 2>/dev/null)

# Extract only the first line / primary command — ignore heredoc body
# This prevents matching blocked patterns that appear as text in commit messages
PRIMARY=$(echo "$COMMAND" | head -1)

# Blocklist — destructive operations that require explicit human confirmation
# Each entry is an extended regex checked against the primary command line only

BLOCKED_PATTERNS=(
    "^git push[[:space:]].*--force"
    "^git push[[:space:]].*[[:space:]]-f([[:space:]]|$)"
    "^git push[[:space:]]+-f([[:space:]]|$)"
    "^git reset[[:space:]]+--hard"
    "^git clean[[:space:]]+-[a-z]*f"
    "^rm[[:space:]]+-[a-z]*r[a-z]*f[[:space:]]*/[^/]"
    "^rm[[:space:]]+-[a-z]*f[a-z]*r[[:space:]]*/[^/]"
    "^rm[[:space:]]+-rf[[:space:]]*$"
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if echo "$PRIMARY" | grep -qE "$pattern"; then
        echo "IES safety hook: blocked pattern '$pattern'" >&2
        echo "This operation requires explicit confirmation. If intentional, David must approve it directly." >&2
        exit 2
    fi
done

exit 0
