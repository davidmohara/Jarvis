#!/usr/bin/env python3
"""
Add skill-run signal section to skills that don't have it.
"""

import re
from pathlib import Path

# Derive IES_ROOT from this script's location
IES_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = IES_ROOT / ".claude" / "skills"

def has_skill_run_signal(skill_file: Path) -> bool:
    """Check if a skill file already has skill-run signal section."""
    try:
        content = skill_file.read_text(encoding="utf-8")
        return "SKILL COMPLETE" in content and "skill-runs" in content
    except Exception:
        return False

def add_skill_run_signal(skill_file: Path):
    """Add skill-run signal section to a skill file."""
    try:
        content = skill_file.read_text(encoding="utf-8")
        skill_name = skill_file.parent.name
        agent = skill_name.split("-")[0] if "-" in skill_name else "unknown"

        # Check if already has the signal
        if has_skill_run_signal(skill_file):
            print(f"  Skipping {skill_file.name} - already has skill-run signal")
            return

        # Find the Input section or end of file
        input_pattern = r'(<!-- system:start -->\n## Input\n\n\$ARGUMENTS\n<!-- system:end -->)'
        match = re.search(input_pattern, content)

        if match:
            insertion_point = match.end()
            signal_section = f"""

<!-- system:start -->
## SKILL COMPLETE

After the skill's final output is delivered, write the skill-run signal file so the eval harness captures this execution:

```
systems/eval-harness/skill-runs/{skill_name}-latest.json
```

Content:
```json
{{
  "skill": "{skill_name}",
  "agent": "{agent}",
  "trigger": "manual",
  "started": "<ISO-8601 timestamp when this skill began>",
  "completed": "<ISO-8601 timestamp when this skill finished>",
  "status": "success",
  "tool_failures": 0,
  "error_ids": []
}}
```

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action.
<!-- system:end -->"""
            updated_content = content[:insertion_point] + signal_section + content[insertion_point:]
            skill_file.write_text(updated_content, encoding="utf-8")
            print(f"  ✓ Added skill-run signal to {skill_file.name}")
        else:
            print(f"  Skipping {skill_file.name} - no Input section found")
    except Exception as e:
        print(f"  ✗ Failed to update {skill_file.name}: {e}")

def main():
    """Add skill-run signals to all skills that don't have them."""
    print("Adding skill-run signals to skills...\n")

    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue

        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        add_skill_run_signal(skill_file)

    print("\nDone!")

if __name__ == "__main__":
    main()
