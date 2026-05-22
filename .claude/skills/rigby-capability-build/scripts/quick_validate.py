#!/usr/bin/env python3
"""
Quick validation for IES skills.

Adapted from anthropics/skills/skill-creator. The Anthropic original enforced a
strict closed allowlist of frontmatter keys and required PyYAML. IES skills use
a wider variety of frontmatter keys (context, agent, model, owning_agent,
trigger_keywords, ...) and multiline description scalars (>-, |), so we relax
both: parse only what we need to verify, accept any additional keys, and avoid
the YAML dependency.

Checks performed:
  - SKILL.md exists at the given path
  - Frontmatter is present and well-formed (--- delimiters)
  - `name:` and `description:` are present
  - Name follows kebab-case (lowercase, hyphens, digits)
  - Name length <= 64 chars
  - Description does not contain angle brackets
  - Description length <= 1024 chars

Returns (True, "...") on success or (False, "<reason>") on the first failure.
"""

import re
import sys
from pathlib import Path


_FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---', re.DOTALL)


def _extract_field(frontmatter_text, field):
    """Return the value of a top-level field from frontmatter text, or None.

    Handles three shapes:
      field: value on one line
      field: "quoted value"
      field: >-                  (folded — joins continuation lines)
        first line
        second line
      field: |                   (literal — joins with newlines)
        first line
        second line

    Stops at the next top-level key (line starting in column 0 with `key:`).
    """
    pattern = re.compile(rf'^{re.escape(field)}:[ \t]*(.*)$', re.MULTILINE)
    m = pattern.search(frontmatter_text)
    if not m:
        return None

    first = m.group(1).strip()
    rest_start = m.end()
    rest = frontmatter_text[rest_start:]

    if first in (">", ">-", ">+", "|", "|-", "|+"):
        joiner = " " if first.startswith(">") else "\n"
        lines = []
        for raw in rest.splitlines():
            if not raw.strip():
                continue
            if raw[:1] in (" ", "\t"):
                lines.append(raw.strip())
                continue
            if re.match(r'^[A-Za-z_][\w-]*:', raw):
                break
            lines.append(raw.strip())
        value = joiner.join(lines)
    else:
        value = first

    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]
    return value


def validate_skill(skill_path):
    skill_path = Path(skill_path)

    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, f"SKILL.md not found at {skill_md}"

    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found (file does not start with ---)"

    match = _FRONTMATTER_RE.match(content)
    if not match:
        return False, "Invalid frontmatter format (missing closing ---)"
    frontmatter_text = match.group(1)

    name = _extract_field(frontmatter_text, 'name')
    if not name:
        return False, "Missing 'name' in frontmatter"
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"Name '{name}' should be kebab-case (lowercase letters, digits, hyphens)"
    if name.startswith('-') or name.endswith('-') or '--' in name:
        return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
    if len(name) > 64:
        return False, f"Name is too long ({len(name)} chars). Maximum is 64."

    description = _extract_field(frontmatter_text, 'description')
    if not description:
        return False, "Missing 'description' in frontmatter"
    if '<' in description or '>' in description:
        return False, "Description cannot contain angle brackets (< or >)"
    if len(description) > 1024:
        return False, f"Description is too long ({len(description)} chars). Maximum is 1024."

    return True, "Skill is valid!"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.quick_validate <skill_directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
