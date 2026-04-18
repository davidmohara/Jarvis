#!/bin/bash
# scripts/migrate-to-tiered-memory.sh
# Run from: /path/to/jarvis/
# Migrates context/ files to the tiered memory/ structure.
# Does NOT delete context/ — rollback is: restore context/ references in SYSTEM.md.
set -e

echo "[migrate] Starting IES memory layer migration..."

# Phase 1: Create new directory structure
mkdir -p memory/working memory/episodic/meetings memory/episodic/people
mkdir -p memory/episodic/projects memory/episodic/decisions memory/episodic/coaching
mkdir -p memory/episodic/digests memory/semantic/relationships
mkdir -p memory/semantic/operational memory/semantic/domain memory/personal
echo "[migrate] Directory structure created."

# Phase 2: Migrate existing context/ files to memory/personal/
for f in context/org.md context/principles.md context/quarterly-objectives.md context/vision.md; do
  if [ -f "$f" ]; then
    base=$(basename "$f")
    dest="memory/personal/$base"
    if [ ! -f "$dest" ]; then
      python3 - "$f" "$dest" << 'PYEOF'
import sys, os
from datetime import date

src, dst = sys.argv[1], sys.argv[2]
with open(src) as fh:
    content = fh.read()

subject = os.path.basename(src).replace('.md', '')
if not content.startswith('---'):
    header = f"---\ntype: personal\nsubject: \"{subject}\"\nlast-updated: {date.today()}\npromoted: never\n---\n\n"
    content = header + content
else:
    if 'type: personal' not in content:
        content = content.replace('---\n', f'---\ntype: personal\npromoted: never\nlast-updated: {date.today()}\n', 1)

with open(dst, 'w') as fh:
    fh.write(content)
PYEOF
      echo "[migrate] Moved $f -> $dest"
    else
      echo "[migrate] Skipped $f (already exists at $dest)"
    fi
  fi
done

# Phase 3: Migrate any existing context/meetings/, context/people/ etc. if present
for subdir in meetings people projects decisions coaching; do
  if [ -d "context/$subdir" ] && [ "$(ls -A context/$subdir 2>/dev/null)" ]; then
    cp -rn context/$subdir/. memory/episodic/$subdir/ 2>/dev/null || true
    echo "[migrate] Migrated context/$subdir/ -> memory/episodic/$subdir/"
  fi
done

# Phase 4: Initialize dream.log and LESSONS.md if not present
if [ ! -f memory/dream.log ]; then
  echo "# Dream Log" > memory/dream.log
  echo "Initialized: $(date +%Y-%m-%d)" >> memory/dream.log
  echo "[migrate] Initialized memory/dream.log"
fi

if [ ! -f memory/LESSONS.md ]; then
  echo "# Global Lessons" > memory/LESSONS.md
  echo "[migrate] Initialized memory/LESSONS.md"
fi

echo "[migrate] Done."
echo "[migrate] context/ files preserved as backup. Verify agent references then optionally remove."
echo "[migrate] SYSTEM.md has been updated with memory/ paths — no manual updates needed."
