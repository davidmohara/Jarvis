#!/bin/bash
# extract_from_chrome.sh — Extract a Plaud transcript from Chrome and save to Obsidian
#
# Usage: ./extract_from_chrome.sh <file_id> <title> <date> <duration>
#
# Requires: Chrome open with Plaud Web logged in, python3 available
#
# Example:
#   ./extract_from_chrome.sh 69679aaa94a5fd286f686f68444f3999 \
#     "DRC Event Strategy" "2026-02-24" "38m 21s"

set -e

FILE_ID="$1"
TITLE="$2"
DATE="$3"
DURATION="$4"
OBSIDIAN_PLAUD="/Users/davidohara/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian/zzPlaud"
TMP_JSON="/tmp/plaud_${FILE_ID}.json"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CHUNK_SIZE=10000

if [ -z "$FILE_ID" ] || [ -z "$TITLE" ] || [ -z "$DATE" ] || [ -z "$DURATION" ]; then
    echo "Usage: $0 <file_id> <title> <date> <duration>"
    exit 1
fi

# Ensure output directory exists
mkdir -p "$OBSIDIAN_PLAUD"

echo "Fetching transcript for: $TITLE ($DATE)..."

# Step 1: Fetch file detail and transcript via Chrome JS
osascript -e '
tell application "Google Chrome"
    set jsCode to "
        (async () => {
            try {
                var token = localStorage.getItem('"'"'tokenstr'"'"');
                var resp = await fetch('"'"'https://api.plaud.ai/file/detail/'"$FILE_ID"''"'"', {
                    headers: { '"'"'Authorization'"'"': token }
                });
                var data = await resp.json();
                var cl = data.data.content_list;
                var transItem = cl.find(c => c.data_type === '"'"'transaction'"'"');
                var transResp = await fetch(transItem.data_link);
                var transData = await transResp.json();
                var el = document.getElementById('"'"'jarvis-data'"'"');
                if (!el) { el = document.createElement('"'"'div'"'"'); el.id = '"'"'jarvis-data'"'"'; el.style.display = '"'"'none'"'"'; document.body.appendChild(el); }
                el.setAttribute('"'"'data-len'"'"', JSON.stringify(transData).length);
                el.textContent = JSON.stringify(transData);
            } catch(e) {
                var el = document.getElementById('"'"'jarvis-data'"'"');
                if (!el) { el = document.createElement('"'"'div'"'"'); el.id = '"'"'jarvis-data'"'"'; el.style.display = '"'"'none'"'"'; document.body.appendChild(el); }
                el.textContent = '"'"'ERROR: '"'"' + e.message;
            }
        })();
    "
    execute active tab of front window javascript jsCode
end tell
'

sleep 3

# Step 2: Get total length
TOTAL_LEN=$(osascript -e '
tell application "Google Chrome"
    execute active tab of front window javascript "document.getElementById('"'"'jarvis-data'"'"').getAttribute('"'"'data-len'"'"')"
end tell
')

echo "Transcript size: ${TOTAL_LEN} chars. Chunking transfer..."

# Step 3: Transfer in chunks
rm -f "$TMP_JSON"
OFFSET=0
while [ "$OFFSET" -lt "$TOTAL_LEN" ]; do
    END=$((OFFSET + CHUNK_SIZE))
    CHUNK=$(osascript -e "
tell application \"Google Chrome\"
    execute active tab of front window javascript \"document.getElementById('jarvis-data').textContent.substring($OFFSET, $END)\"
end tell
")
    if [ "$OFFSET" -eq 0 ]; then
        printf '%s' "$CHUNK" > "$TMP_JSON"
    else
        printf '%s' "$CHUNK" >> "$TMP_JSON"
    fi
    OFFSET=$END
done

# Step 4: Validate JSON
python3 -c "import json; data=json.load(open('$TMP_JSON')); print(f'Valid JSON: {len(data)} utterances')"

# Step 5: Convert and save
OUTPUT_FILE="${OBSIDIAN_PLAUD}/${DATE} ${TITLE}.md"
python3 "$SCRIPT_DIR/plaud_to_markdown.py" "$TMP_JSON" "$TITLE" "$DATE" "$DURATION" --output "$OUTPUT_FILE"

echo "Saved to: $OUTPUT_FILE"

# Step 6: Cleanup
rm -f "$TMP_JSON"
echo "Done."
