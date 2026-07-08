#!/bin/bash
# Status line formatter for Claude Code
# Combines git info with session context data from stdin

input=$(cat)

# Extract session data from JSON
model=$(echo "$input" | jq -r '.model.display_name // "Claude"')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // 0')
context_size=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')

# Format context window size as human readable
context_window=$(
  size=$context_size
  if [ "$size" -ge 1000000 ]; then
    echo "$((size / 1000000))M"
  elif [ "$size" -ge 1000 ]; then
    echo "$((size / 1000))k"
  else
    echo "$size"
  fi
)

# Get git information from current directory
cwd=$(echo "$input" | jq -r '.cwd // "."')
cd "$cwd" 2>/dev/null || exit 1

# Get git branch and tracking branch
git_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
git_tracking=$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null | sed 's|origin/||' || echo "")

if [ -n "$git_tracking" ]; then
  git_info="$git_branch ($git_tracking)"
else
  git_info="$git_branch"
fi

# Get file status counts
modified=$(git diff --name-only 2>/dev/null | wc -l | tr -d ' ')
staged=$(git diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')
untracked=$(git ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')

# Format output like the screenshot
printf "%s | %s 📝, %s 🟢 | 🎯 %.1fk tokens (%d%%) | 🧠 %s (%s)" \
  "$git_info" \
  "$modified" \
  "$staged" \
  "$(echo "scale=1; $(echo "$input" | jq -r '.context_window.total_input_tokens // 0') / 1000" | bc 2>/dev/null || echo 0)" \
  "$used_pct" \
  "$model" \
  "$context_window"
