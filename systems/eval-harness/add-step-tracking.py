#!/usr/bin/env python3
"""
Add step tracking calls to all workflow step files.
This script automatically updates step files to call record-step.py at completion.
"""

import re
from pathlib import Path

# Derive IES_ROOT from this script's location
IES_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS_DIR = IES_ROOT / "workflows"

def add_step_tracking_to_step(step_file: Path, workflow_name: str):
    """Add record-step.py call to a step file."""
    try:
        content = step_file.read_text(encoding="utf-8")
        step_name = step_file.stem  # e.g., "step-01-capture"

        # Check if already has the tracking call
        if "record-step.py" in content:
            print(f"  Skipping {step_file.name} - already has tracking")
            return

        # Find the NEXT STEP section
        next_step_pattern = r'(## NEXT STEP\s*\n\s*Read fully and follow: `[^`]+`)'
        match = re.search(next_step_pattern, content)

        if not match:
            print(f"  Skipping {step_file.name} - no NEXT STEP section found")
            return

        # Insert the tracking call before NEXT STEP
        tracking_call = f"""
## STEP COMPLETION TRACKING

Record step completion for eval harness:

```bash
python3 systems/eval-harness/record-step.py {workflow_name} {step_name} complete "${{{{frontmatter.started-at}}}}" "${{{{frontmatter.completed-at}}}}"
```

"""
        insertion_point = match.start()
        updated_content = content[:insertion_point] + tracking_call + content[insertion_point:]

        step_file.write_text(updated_content, encoding="utf-8")
        print(f"  ✓ Updated {step_file.name}")

    except Exception as e:
        print(f"  ✗ Failed to update {step_file.name}: {e}")

def main():
    """Process all workflow step files."""
    print("Adding step tracking to all workflow steps...")

    for workflow_dir in WORKFLOWS_DIR.iterdir():
        if not workflow_dir.is_dir():
            continue

        steps_dir = workflow_dir / "steps"
        if not steps_dir.exists():
            continue

        workflow_name = workflow_dir.name
        print(f"\nProcessing workflow: {workflow_name}")

        for step_file in steps_dir.glob("*.md"):
            if step_file.name.startswith("step-"):
                add_step_tracking_to_step(step_file, workflow_name)

    print("\nDone!")

if __name__ == "__main__":
    main()
