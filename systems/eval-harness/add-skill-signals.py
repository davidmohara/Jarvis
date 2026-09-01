#!/usr/bin/env python3
"""
Add skill-run signal section to skills that don't have it.
"""

import re
from pathlib import Path

# Derive IES_ROOT from this script's location
IES_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIRS = [IES_ROOT / ".claude" / "skills", IES_ROOT / "skills"]

def has_skill_run_signal(skill_file: Path) -> bool:
    """Check if a skill file already has skill-run signal section."""
    try:
        content = skill_file.read_text(encoding="utf-8")
        return "SKILL COMPLETE" in content and "skill-runs" in content
    except Exception:
        return False

def has_grading_step(skill_file: Path) -> bool:
    """Check if a skill file's SKILL COMPLETE section already invokes grade_skill_run.py."""
    try:
        content = skill_file.read_text(encoding="utf-8")
        return "grade_skill_run.py" in content
    except Exception:
        return False

def grading_section(skill_name: str) -> str:
    """The eval-harness grading step, inserted right after the signal-file write."""
    return f"""

<!-- system:start -->
## GRADE THIS RUN

Immediately after writing the skill-run signal file above, run the deterministic grader as your actual final action:

```bash
python3 systems/eval-harness/grade_skill_run.py --skill {skill_name}
```

This prints a compact block: a structure/content/quality assertion breakdown, a deterministic % score, and a pass/fail gate status, computed from `systems/eval-harness/assertions/{skill_name}.json` (Tier 2 — 100% deterministic, no model judgment). It always exits 0, even when no assertion file exists yet (it will say so) or when checks fail.

Include that printed block verbatim (or lightly reformatted to match your closing summary's style) in your final response to the operator — the deterministic grade must always reach the person reading the output, not just the eval record on disk. A qualitative (Tier 3) grade is added separately later via the end-of-day `rigby-eval-grade` sweep; do not attempt to compute or claim a qualitative grade yourself here.
<!-- system:end -->"""

def add_skill_run_signal(skill_file: Path):
    """Add skill-run signal + grading section to a skill file. Idempotent —
    safe to re-run across all skills: adds whichever piece (signal, grading,
    or both) is missing, and does nothing if both are already present."""
    try:
        content = skill_file.read_text(encoding="utf-8")
        skill_name = skill_file.parent.name
        agent = skill_name.split("-")[0] if "-" in skill_name else "unknown"

        if re.search(r'description:\s*["\']?RETIRED', content):
            print(f"  Skipping {skill_file.name} - RETIRED stub, not instrumented")
            return

        already_has_signal = has_skill_run_signal(skill_file)
        already_has_grading = has_grading_step(skill_file)

        if already_has_signal and already_has_grading:
            print(f"  Skipping {skill_file.name} - already has signal + grading")
            return

        if already_has_signal and not already_has_grading:
            # Upgrade path: signal section exists (from a prior run of this
            # script, in one of several historical template variants — some
            # wrapped in <!-- system:start/end -->, some plain markdown).
            # The one constant across every variant is the closing sentence
            # of the signal-write instructions, so anchor on that instead of
            # a structural marker.
            anchor = "This write is always the final action"
            anchor_idx = content.find(anchor)
            if anchor_idx == -1:
                print(f"  Skipping {skill_file.name} - could not locate SKILL COMPLETE closing sentence")
                return
            # Insert right after the sentence's closing period.
            period_idx = content.find(".", anchor_idx)
            insertion_point = period_idx + 1 if period_idx != -1 else anchor_idx + len(anchor)
            updated_content = content[:insertion_point] + grading_section(skill_name) + content[insertion_point:]
            skill_file.write_text(updated_content, encoding="utf-8")
            print(f"  ✓ Added grading step to {skill_file.name}")
            return

        # Neither present — insert both together after the Input section.
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

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action, immediately followed by the grading step below.
<!-- system:end -->"""
            updated_content = content[:insertion_point] + signal_section + grading_section(skill_name) + content[insertion_point:]
            skill_file.write_text(updated_content, encoding="utf-8")
            print(f"  ✓ Added skill-run signal + grading to {skill_file.name}")
        else:
            # Fallback for skills that don't use the standard system-wrapped
            # "## Input\n\n$ARGUMENTS" block (e.g. personal-block-only skills,
            # or lightweight utility skills with no Input section at all):
            # append both sections at end of file.
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

Set `trigger` to `"boot"` if called from a boot workflow, `"scheduled"` if called from a scheduled task, `"manual"` otherwise. Set `status` to `"partial"` if the skill completed with degraded output, `"failure"` if it could not run at all. Use the actual start time of this skill execution for `started`. This write is always the final action, immediately followed by the grading step below.
<!-- system:end -->"""
            updated_content = content.rstrip("\n") + "\n" + signal_section + grading_section(skill_name) + "\n"
            skill_file.write_text(updated_content, encoding="utf-8")
            print(f"  ✓ Added skill-run signal + grading to {skill_file.name} (appended at EOF - no standard Input block)")
    except Exception as e:
        print(f"  ✗ Failed to update {skill_file.name}: {e}")

def main():
    """Add skill-run signals to all skills that don't have them."""
    print("Adding skill-run signals + grading steps to skills...\n")

    for skills_dir in SKILLS_DIRS:
        if not skills_dir.exists():
            continue
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue

            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue

            add_skill_run_signal(skill_file)

    print("\nDone!")

if __name__ == "__main__":
    main()
