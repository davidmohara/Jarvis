#!/usr/bin/env python3
"""
assertion_checks.py — canonical structural/content/quality assertion evaluator.

Single source of truth for Tier 2 assertion checking, shared by:
  - .claude/hooks/post-tool-use.py       (fires on the skill-run signal-file write)
  - .claude/hooks/eval-agent-stop.py     (fires on SubagentStop)
  - systems/eval-harness/grade_skill_run.py (synchronous, invoked as a skill's final step)

Previously this logic was implemented twice (once per hook) and had drifted
(e.g. eval-agent-stop.py's `min_count` vs post-tool-use.py's `min_steps` key
for `step_count_gte`, and eval-agent-stop.py had bias/safety + tool_was_called
checks post-tool-use.py lacked). This module is the union of both, so every
check type works identically no matter which caller invokes it.

Assertion file format (systems/eval-harness/assertions/{name}.json):
{
  "name": "<skill-or-workflow-name>",
  "type": "skill" | "workflow",
  "assertions": [
    {
      "id": "unique-id",
      "check": "<check-type>",
      "category": "structure" | "content" | "quality",   # optional, defaults to "structure"
      "description": "human-readable description",
      ... check-specific fields ...
    }
  ]
}

Every check function takes (assertion: dict, eval_record: dict, ies_root: Path,
transcript_path: str | None) and returns (passed: bool | None, extra: dict).
`passed=None` means "skipped" (not evaluable at this call site) and must set
extra["skipped"]=True and extra["reason"].
"""

import re
import json
from pathlib import Path

# Canonical manifest agent roster + label normalization live in step_audit.py
# (Stage 3 Phase 0). Import them so routing-attribution checks agree with the
# harness on what an "agent" is; fall back to a local copy if the module is
# not importable at this call site (e.g. a stripped-down test harness).
try:
    from step_audit import MANIFEST_AGENTS as _MANIFEST_AGENTS
    from step_audit import normalize_agent_label as _normalize_agent_label
except Exception:  # pragma: no cover - defensive fallback
    _MANIFEST_AGENTS = (
        "master", "chief", "chase", "knox", "shep", "quinn",
        "harper", "rigby", "sterling", "galen", "ralph",
    )

    def _normalize_agent_label(agent):
        if not agent:
            return None
        a = str(agent).strip().lower()
        if a in ("master", "jarvis"):
            return "master"
        return a if a in _MANIFEST_AGENTS else None


def extract_frontmatter_block(content: str) -> str:
    """Strip leading/trailing `---` YAML frontmatter markers."""
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return content
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:i])
    return "\n".join(lines[1:])


# Default banned-phrase pattern set shared by banned_phrases_absent — kept
# here so individual assertion files don't each hand-roll the same regex.
DEFAULT_BANNED_PHRASES = [
    r"—",                 # em-dash (org-wide style rule: no em-dashes)
    r"lorem ipsum",
    r"\bTODO\b",
    r"\bPLACEHOLDER\b",
    r"\[insert\b",
    r"\[TBD\]",
    r"\bFIXME\b",
]


def _glob(ies_root: Path, pattern: str, newest_only: bool = False):
    """Resolve a glob pattern relative to ies_root. When newest_only is set,
    a pattern that matches many historical files (e.g. output directories
    with no skill-run-scoped naming, accumulated over months) is narrowed to
    just the single most-recently-modified match — so content/quality checks
    evaluate against THIS run's output, not the entire directory's history."""
    matches = list(ies_root.glob(pattern))
    if newest_only and len(matches) > 1:
        matches = [max(matches, key=lambda m: m.stat().st_mtime)]
    return matches


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _load_yaml(path: Path, yaml_module):
    try:
        return yaml_module.safe_load(extract_frontmatter_block(_read_text(path))) or {}
    except Exception:
        return {}


def _load_json(path: Path):
    try:
        return json.loads(_read_text(path))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Check implementations — existing check types (union of both prior copies)
# ---------------------------------------------------------------------------

def check_file_exists(a, eval_record, ies_root, transcript_path, yaml_module=None):
    matches = _glob(ies_root, a.get("path", ""), a.get("newest_only", False))
    return len(matches) > 0, {}


def check_file_min_bytes(a, eval_record, ies_root, transcript_path, yaml_module=None):
    matches = _glob(ies_root, a.get("path", ""), a.get("newest_only", False))
    min_bytes = a.get("min_bytes", 0)
    if not matches:
        return False, {}
    return all(m.stat().st_size >= min_bytes for m in matches), {}


def check_file_contains(a, eval_record, ies_root, transcript_path, yaml_module=None):
    matches = _glob(ies_root, a.get("path", ""), a.get("newest_only", False))
    regex = a.get("pattern", "")
    if not matches:
        return False, {}
    for m in matches:
        if re.search(regex, _read_text(m), re.IGNORECASE):
            return True, {}
    return False, {}


def check_file_not_contains(a, eval_record, ies_root, transcript_path, yaml_module=None):
    matches = _glob(ies_root, a.get("path", ""), a.get("newest_only", False))
    regex = a.get("pattern", "")
    if not matches:
        return True, {}  # no file = nothing to contain = passes
    for m in matches:
        if re.search(regex, _read_text(m), re.IGNORECASE):
            return False, {}
    return True, {}


def check_yaml_field_equals(a, eval_record, ies_root, transcript_path, yaml_module=None):
    matches = _glob(ies_root, a.get("path", ""), a.get("newest_only", False))
    field = a.get("field", "")
    value = a.get("value")
    if not matches or yaml_module is None:
        return False, {}
    data = _load_yaml(matches[0], yaml_module)
    return data.get(field) == value, {}


def check_json_field_not_equals(a, eval_record, ies_root, transcript_path, yaml_module=None):
    """A named field in a JSON file must NOT equal a given value (e.g. status
    != "failure"). Pre-existing gap: used in 119 assertions/{name}.json files
    but never implemented in either legacy hook copy of run_assertions — every
    one of those checks silently fell through to "unknown check type" and was
    excluded from assertions_checked/assertions_passed. Implemented here for
    the first time.
    """
    matches = _glob(ies_root, a.get("path", ""), a.get("newest_only", False))
    field = a.get("field", "")
    value = a.get("value")
    if not matches:
        return False, {"reason": "file not found"}
    data = _load_json(matches[0])
    if data is None:
        return False, {"reason": "file is not valid JSON"}
    return data.get(field) != value, {}


def check_step_count_gte(a, eval_record, ies_root, transcript_path, yaml_module=None):
    # Accept either key: eval-agent-stop.py historically used `min_count`,
    # post-tool-use.py used `min_steps`. Support both so either convention works.
    min_steps = a.get("min_count", a.get("min_steps", 0))
    completed_steps = [
        s for s in eval_record.get("steps", [])
        if s.get("status") in ("success", "complete")
    ]
    return len(completed_steps) >= min_steps, {}


def check_guardrail_checkpoint_ran(a, eval_record, ies_root, transcript_path, yaml_module=None):
    checkpoint_name = a.get("checkpoint_name")
    guardrails = eval_record.get("guardrails", [])
    if checkpoint_name:
        return any(g.get("name") == checkpoint_name for g in guardrails), {}
    return len(guardrails) >= 1, {}


def check_duration_lte(a, eval_record, ies_root, transcript_path, yaml_module=None):
    max_duration = a.get("max_duration_seconds", a.get("max_seconds", float("inf")))
    actual = eval_record.get("duration_seconds", 0)
    return actual <= max_duration, {}


def check_tool_was_called(a, eval_record, ies_root, transcript_path, yaml_module=None):
    tool_pattern = a.get("tool_pattern", "")
    if not tool_pattern:
        return None, {"skipped": True, "reason": "no tool_pattern specified"}
    if not transcript_path:
        return None, {"skipped": True, "reason": "tool_was_called not available at this call site (no transcript)"}
    try:
        content = Path(transcript_path).read_text(errors="replace")
        return re.search(tool_pattern, content) is not None, {}
    except Exception as e:
        return None, {"skipped": True, "reason": f"could not read transcript: {e}"}


def check_bias_coverage_check(a, eval_record, ies_root, transcript_path, yaml_module=None):
    bias = eval_record.get("assessment", {}).get("bias_assessment", {})
    if not bias.get("applicable", False):
        return True, {}
    return bias.get("demographic_coverage_verified", False), {}


def check_adversarial_cases_present(a, eval_record, ies_root, transcript_path, yaml_module=None):
    bias = eval_record.get("assessment", {}).get("bias_assessment", {})
    if not bias.get("applicable", False):
        return True, {}
    return bias.get("adversarial_inputs_tested", False), {}


def check_safety_threshold_gte(a, eval_record, ies_root, transcript_path, yaml_module=None):
    bias = eval_record.get("assessment", {}).get("bias_assessment", {})
    if not bias.get("applicable", False):
        return True, {}
    min_score = a.get("min_score", 0.70)
    safety_grade = eval_record.get("assessment", {}).get("grading", {}).get("safety_grade")
    grade_map = {"A": 1.0, "B": 0.8, "C": 0.6, "D": 0.4, "F": 0.0}
    if safety_grade is None:
        return True, {}  # not yet graded — defer, don't fail
    return grade_map.get(safety_grade, 0.0) >= min_score, {}


def check_bias_not_detected(a, eval_record, ies_root, transcript_path, yaml_module=None):
    bias = eval_record.get("assessment", {}).get("bias_assessment", {})
    if not bias.get("applicable", False):
        return True, {}
    return not bias.get("bias_detected", False), {}


# ---------------------------------------------------------------------------
# New check types — deterministic content + quality proxies
# ---------------------------------------------------------------------------

def check_count_matches_source(a, eval_record, ies_root, transcript_path, yaml_module=None):
    """Regex match count in output file(s) compares to match count in a source file.

    Fields: output_path, source_path, pattern (applied to both), comparator
    ("gte"|"eq", default "gte").
    """
    out_matches = _glob(ies_root, a.get("output_path", ""), a.get("newest_only", False))
    src_matches = _glob(ies_root, a.get("source_path", ""), a.get("newest_only", False))
    pattern = a.get("pattern", "")
    comparator = a.get("comparator", "gte")
    if not out_matches or not src_matches or not pattern:
        return False, {"reason": "missing output/source file or pattern"}

    src_count = len(re.findall(pattern, _read_text(src_matches[0]), re.IGNORECASE))
    out_count = len(re.findall(pattern, _read_text(out_matches[0]), re.IGNORECASE))

    if comparator == "eq":
        passed = out_count == src_count
    else:
        passed = out_count >= src_count
    return passed, {"source_count": src_count, "output_count": out_count}


def check_list_items_covered(a, eval_record, ies_root, transcript_path, yaml_module=None):
    """Every bullet/line extracted from a source file (by item_pattern) must
    appear (as a substring, case-insensitive, whitespace-normalized) somewhere
    in the output file. Catches dropped items during summarization/rewriting.

    Fields: output_path, source_path, item_pattern (regex with one capture
    group giving the item text), min_chars_to_match (default 12 — guards
    against trivially short fragments matching everywhere).
    """
    out_matches = _glob(ies_root, a.get("output_path", ""), a.get("newest_only", False))
    src_matches = _glob(ies_root, a.get("source_path", ""), a.get("newest_only", False))
    item_pattern = a.get("item_pattern", "")
    min_chars = a.get("min_chars_to_match", 12)
    if not out_matches or not src_matches or not item_pattern:
        return False, {"reason": "missing output/source file or item_pattern"}

    src_text = _read_text(src_matches[0])
    out_text = re.sub(r"\s+", " ", _read_text(out_matches[0])).lower()

    items = [m.group(1).strip() for m in re.finditer(item_pattern, src_text, re.MULTILINE)]
    items = [i for i in items if len(i) >= min_chars]
    if not items:
        return None, {"skipped": True, "reason": "no items extracted from source with item_pattern"}

    missing = []
    for item in items:
        normalized = re.sub(r"\s+", " ", item).lower()
        if normalized not in out_text:
            missing.append(item)

    passed = len(missing) == 0
    return passed, {"total_items": len(items), "missing_count": len(missing), "missing_sample": missing[:3]}


def check_word_count_range(a, eval_record, ies_root, transcript_path, yaml_module=None):
    """Word count of output file(s) falls within [min_words, max_words]."""
    matches = _glob(ies_root, a.get("path", ""), a.get("newest_only", False))
    min_words = a.get("min_words", 0)
    max_words = a.get("max_words", float("inf"))
    if not matches:
        return False, {}
    text = _read_text(matches[0])
    count = len(text.split())
    return (min_words <= count <= max_words), {"word_count": count}


def check_banned_phrases_absent(a, eval_record, ies_root, transcript_path, yaml_module=None):
    """file_not_contains against DEFAULT_BANNED_PHRASES (or a custom list),
    checked as separate patterns rather than one combined regex so the
    result can report which phrase(s) were found.
    """
    matches = _glob(ies_root, a.get("path", ""), a.get("newest_only", False))
    phrases = a.get("phrases", DEFAULT_BANNED_PHRASES)
    if not matches:
        return True, {}
    found = []
    for m in matches:
        text = _read_text(m)
        for phrase in phrases:
            if re.search(phrase, text, re.IGNORECASE):
                found.append(phrase)
    passed = len(found) == 0
    return passed, ({"found_phrases": found} if found else {})


def check_json_path_exists(a, eval_record, ies_root, transcript_path, yaml_module=None):
    """A dotted field path must exist in a JSON file, optionally fanning out
    over an array with a trailing `[]` segment.

    This is the field-path check that naive `file_contains` assertions should
    have used. A whole-file substring match cannot tell an entry's real field
    from the same token appearing in the file's own boilerplate (e.g. the
    reminders registry's `_instructions` header literally contains the words
    "action_prompt" and "routing.agent", so `file_contains "action_prompt"`
    passed against an EMPTY reminders array). Parsing the JSON and walking the
    path checks the actual entry structure instead.

    Fields: path (JSON file, glob-resolved), field_path (dotted; a segment
    ending in `[]` fans out over a list — e.g. `reminders[].routing.agent`),
    min_matches (default 1).
    """
    matches = _glob(ies_root, a.get("path", ""), a.get("newest_only", False))
    field_path = a.get("field_path", "")
    min_matches = a.get("min_matches", 1)
    if not matches:
        return False, {"reason": "file not found"}
    data = _load_json(matches[0])
    if data is None:
        return False, {"reason": "file is not valid JSON"}

    segments = [seg for seg in field_path.split(".") if seg != ""]
    if not segments:
        return False, {"reason": "empty field_path"}

    nodes = [data]
    for seg in segments:
        is_list = seg.endswith("[]")
        key = seg[:-2] if is_list else seg
        nxt = []
        for node in nodes:
            if not isinstance(node, dict) or key not in node:
                continue
            value = node[key]
            if is_list:
                if isinstance(value, list):
                    nxt.extend(value)
            else:
                nxt.append(value)
        nodes = nxt
        if not nodes:
            break

    count = len(nodes)
    return count >= min_matches, {"matched": count}


def check_numeric_field_in_range(a, eval_record, ies_root, transcript_path, yaml_module=None):
    """A named field in a JSON file (or eval_record itself when path omitted)
    falls within [min, max]. Generalizes "PDF must be exactly 1 page" style
    checks once the producing step writes that number out as JSON.

    Fields: path (optional — omit to read from eval_record), field (dotted
    path, e.g. "a.b.c"), min, max.
    """
    field = a.get("field", "")
    min_v = a.get("min", float("-inf"))
    max_v = a.get("max", float("inf"))

    if a.get("path"):
        matches = _glob(ies_root, a["path"])
        if not matches:
            return False, {}
        data = _load_json(matches[0])
        if data is None:
            return False, {}
    else:
        data = eval_record

    value = data
    for part in field.split("."):
        if not isinstance(value, dict) or part not in value:
            return False, {"reason": f"field '{field}' not found"}
        value = value[part]

    try:
        value = float(value)
    except (TypeError, ValueError):
        return False, {"reason": f"field '{field}' is not numeric: {value!r}"}

    return (min_v <= value <= max_v), {"value": value}


# ---------------------------------------------------------------------------
# Stage 3 Phase 1 check types — routing attribution, Tier-3 deferral, and
# YAML field/list checks. These close the measurement gaps for criteria that
# had zero assertion coverage (see
# projects/stage-5-submission/stage3-compliance-plan.md, Phase 1).
#
# Mirror note: every function below is duplicated (kept in parity) in
# .claude/hooks/eval-turn-stop.py's inline run_assertions(), which does not
# import this module. Add new check types in BOTH places.
# ---------------------------------------------------------------------------

GRADE_ORDER = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}


def _frontmatter_field(text: str, field: str):
    """Read one top-level frontmatter scalar by regex, without needing PyYAML."""
    lines = (text or "").split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(rf"^{re.escape(field)}\s*:\s*(.+?)\s*$", line)
        if m:
            return m.group(1).strip().strip("'\"")
    return None


def _manifest_ownership(ies_root: Path) -> dict:
    """Parse agents/manifest.md's agent table -> {agent: owns_cell_text}.

    The 'Owns (workflow steps, skills)' column is the coordinator-vs-specialist
    routing contract Master J2 is scored against."""
    text = _read_text(ies_root / "agents" / "manifest.md")
    owners = {}
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 4:
            continue
        m = re.match(r"\*\*([A-Za-z]+)\*\*", cells[0])
        if not m:
            continue
        agent = m.group(1).strip().lower()
        if agent in _MANIFEST_AGENTS:
            owners[agent] = cells[3]
    return owners


def _manifest_boot_step_ranges(owners: dict):
    """[(agent, lo, hi)] parsed from phrases like 'boot steps 02-06' / 'boot step-08'."""
    ranges = []
    for agent, owns in owners.items():
        for m in re.finditer(
            r"boot steps?\s+(\d+(?:\.\d+)?)\s*(?:[-–]\s*(\d+(?:\.\d+)?))?",
            owns or "",
        ):
            lo = float(m.group(1))
            hi = float(m.group(2)) if m.group(2) else lo
            ranges.append((agent, lo, hi))
    return ranges


def _workflow_step_owner_map(ies_root: Path) -> dict:
    """basename -> set of owning agents, by scanning workflows/<name>/steps/*.md
    and reading each workflow's `agent:` frontmatter. A step file that lives in
    a specialist-owned workflow belongs to that specialist."""
    step_owners = {}
    wf_dir = ies_root / "workflows"
    if not wf_dir.is_dir():
        return step_owners
    for wf in wf_dir.iterdir():
        if not wf.is_dir():
            continue
        wf_md = wf / "workflow.md"
        if not wf_md.is_file():
            continue
        owner = _normalize_agent_label(_frontmatter_field(_read_text(wf_md), "agent"))
        steps_dir = wf / "steps"
        if not steps_dir.is_dir():
            continue
        for sf in steps_dir.glob("*.md"):
            step_owners.setdefault(sf.name, set()).add(owner or wf.name)
    return step_owners


def check_step_owner_manifest(a, eval_record, ies_root, transcript_path, yaml_module=None):
    """Master J2 — routing correctness: the coordinator must not own a step that
    belongs to a specialist. Fails when a step carries `owning_agent: master`
    even though the step belongs to a specialist workflow (per
    workflows/<name>/workflow.md's agent frontmatter) or falls in a specialist's
    boot-step range (per agents/manifest.md).

    A step is NOT flagged when master is itself a legitimate owner of that step
    — i.e. the step's own workflow is master-owned (boot's own steps) or the
    manifest assigns it to master. This is the "manifest owner OR workflow
    owner" rule: it catches a specialist workflow's steps (e.g. plaud-ingest
    steps 02-06, owned by knox) being stamped master, without flagging boot's
    own coordinator steps. Returns skipped when the record has no steps.
    """
    steps = eval_record.get("steps") or []
    if not steps:
        return None, {"skipped": True, "reason": "no steps recorded on this record"}

    owners = _manifest_ownership(ies_root)
    boot_ranges = _manifest_boot_step_ranges(owners)
    step_owners = _workflow_step_owner_map(ies_root)

    violations = []
    for s in steps:
        if isinstance(s, dict):
            name = s.get("name") or ""
            owning = _normalize_agent_label(s.get("owning_agent"))
        elif isinstance(s, str):
            name, owning = s, None
        else:
            continue
        if not name:
            continue

        expected = set()
        base = name if name.endswith(".md") else f"{name}.md"
        for o in step_owners.get(base, set()):
            if o and o in _MANIFEST_AGENTS:
                expected.add(o)
        num = re.match(r"^step-(\d+(?:\.\d+)?)", name)
        if num:
            n = float(num.group(1))
            for agent, lo, hi in boot_ranges:
                if lo <= n <= hi:
                    expected.add(agent)

        # Flag only when the step belongs to a workflow/range we can attribute,
        # master is recorded as owner, and master is NOT a legitimate owner.
        if expected and owning == "master" and "master" not in expected:
            violations.append({
                "step": name,
                "owning_agent": "master",
                "expected_owner": sorted(expected)[0],
            })

    passed = len(violations) == 0
    extra = {}
    if violations:
        extra["violation_count"] = len(violations)
        extra["violations"] = violations[:10]
    return passed, extra


def check_grade_threshold(a, eval_record, ies_root, transcript_path, yaml_module=None):
    """Honest alternative for a criterion that can only be judged by Tier 3
    grading (voice quality, strategy-kernel quality). Defers (skipped, not
    failed) when the record carries no grade yet — the same convention
    safety_threshold_gte uses — and compares the grade to `min_grade`
    (default B) once grading has run.

    Fields: min_grade ("A"|"B"|"C"|"D"|"F", default "B").
    """
    grading = (eval_record.get("assessment", {}) or {}).get("grading", {}) or {}
    grade = grading.get("grade")
    min_grade = str(a.get("min_grade", "B")).upper()
    if not grade:
        return None, {
            "skipped": True,
            "reason": "not graded yet — this criterion is only judgeable by Tier 3 "
                      "grading; deferred (not failed) until a grade exists",
        }
    g = GRADE_ORDER.get(str(grade).upper())
    if g is None:
        return False, {"reason": f"unrecognised grade {grade!r}"}
    return g >= GRADE_ORDER.get(min_grade, 3), {"grade": grade, "min_grade": min_grade}


def _yaml_walk(data, field_path):
    """Walk a dotted field path over parsed YAML, fanning out over `[]` segments.
    Returns the list of nodes reached (empty when any segment is missing)."""
    nodes = [data]
    for seg in [x for x in field_path.split(".") if x]:
        is_list = seg.endswith("[]")
        key = seg[:-2] if is_list else seg
        nxt = []
        for node in nodes:
            if not isinstance(node, dict) or key not in node:
                continue
            val = node[key]
            if is_list:
                if isinstance(val, list):
                    nxt.extend(val)
            else:
                nxt.append(val)
        nodes = nxt
        if not nodes:
            break
    return nodes


def check_yaml_path_exists(a, eval_record, ies_root, transcript_path, yaml_module=None):
    """YAML analogue of json_path_exists. A dotted field path must exist in a
    YAML file, fanning out over `[]` array segments.

    Fields: path, field_path (dotted; a segment ending in `[]` fans out),
    min_matches (default 1).
    """
    matches = _glob(ies_root, a.get("path", ""), a.get("newest_only", False))
    if not matches:
        return False, {"reason": "file not found"}
    if yaml_module is None:
        return None, {"skipped": True, "reason": "yaml module unavailable at this call site"}
    data = _load_yaml(matches[0], yaml_module)
    count = len(_yaml_walk(data, a.get("field_path", "")))
    return count >= a.get("min_matches", 1), {"matched": count}


def check_yaml_list_field_present(a, eval_record, ies_root, transcript_path, yaml_module=None):
    """Every item in a YAML list must carry a named non-empty field — the
    completeness check for verdict tables / manifests where a silent omission
    (an item with no verdict) is the failure mode.

    Fields: path, list_field (dotted path to the list), item_field.
    Returns skipped when the list is empty (nothing to verify, not a failure).
    """
    matches = _glob(ies_root, a.get("path", ""), a.get("newest_only", False))
    if not matches:
        return False, {"reason": "file not found"}
    if yaml_module is None:
        return None, {"skipped": True, "reason": "yaml module unavailable at this call site"}
    data = _load_yaml(matches[0], yaml_module)
    nodes = _yaml_walk(data, a.get("list_field", ""))
    items = nodes[0] if nodes and isinstance(nodes[0], list) else []
    item_field = a.get("item_field", "")
    if not items:
        return None, {"skipped": True, "reason": "list is empty — nothing to verify"}
    missing = [
        i for i, it in enumerate(items)
        if not (isinstance(it, dict) and str(it.get(item_field, "")).strip())
    ]
    return len(missing) == 0, {"total_items": len(items), "missing_count": len(missing)}


def check_yaml_list_counts_gte(a, eval_record, ies_root, transcript_path, yaml_module=None):
    """Accounting check: len(accounted) + len(skipped) >= len(source) across
    dotted YAML list paths. The zero-silent-drops gate (e.g. every staged
    recording is either ingested or explicitly logged as skipped).

    Fields: path, source_field, accounted_field, skipped_field (optional).
    """
    matches = _glob(ies_root, a.get("path", ""), a.get("newest_only", False))
    if not matches:
        return False, {"reason": "file not found"}
    if yaml_module is None:
        return None, {"skipped": True, "reason": "yaml module unavailable at this call site"}
    data = _load_yaml(matches[0], yaml_module)

    def _list(field):
        if not field:
            return []
        nodes = _yaml_walk(data, field)
        return nodes[0] if nodes and isinstance(nodes[0], list) else []

    source = _list(a.get("source_field", ""))
    accounted = _list(a.get("accounted_field", ""))
    skipped = _list(a.get("skipped_field", ""))
    if not source:
        return True, {"source_count": 0, "accounted_count": len(accounted), "skipped_count": len(skipped)}
    passed = (len(accounted) + len(skipped)) >= len(source)
    return passed, {"source_count": len(source), "accounted_count": len(accounted), "skipped_count": len(skipped)}


CHECKS = {
    "file_exists": check_file_exists,
    "file_min_bytes": check_file_min_bytes,
    "file_contains": check_file_contains,
    "file_not_contains": check_file_not_contains,
    "yaml_field_equals": check_yaml_field_equals,
    "json_field_not_equals": check_json_field_not_equals,
    "step_count_gte": check_step_count_gte,
    "guardrail_checkpoint_ran": check_guardrail_checkpoint_ran,
    "duration_lte": check_duration_lte,
    "tool_was_called": check_tool_was_called,
    "bias_coverage_check": check_bias_coverage_check,
    "adversarial_cases_present": check_adversarial_cases_present,
    "safety_threshold_gte": check_safety_threshold_gte,
    "bias_not_detected": check_bias_not_detected,
    # New deterministic content/quality checks:
    "count_matches_source": check_count_matches_source,
    "list_items_covered": check_list_items_covered,
    "word_count_range": check_word_count_range,
    "banned_phrases_absent": check_banned_phrases_absent,
    "numeric_field_in_range": check_numeric_field_in_range,
    "json_path_exists": check_json_path_exists,
    # Stage 3 Phase 1 (mirrored in .claude/hooks/eval-turn-stop.py):
    "step_owner_manifest": check_step_owner_manifest,
    "grade_threshold": check_grade_threshold,
    "yaml_path_exists": check_yaml_path_exists,
    "yaml_list_field_present": check_yaml_list_field_present,
    "yaml_list_counts_gte": check_yaml_list_counts_gte,
}


def find_assertion_file(assertions_dir: Path, name: str, agent: str = None) -> "Path | None":
    """Match by workflow/skill name first, then by agent type (legacy fallback)."""
    candidate = assertions_dir / f"{name}.json"
    if candidate.exists():
        return candidate
    if agent:
        candidate = assertions_dir / f"{agent}.json"
        if candidate.exists():
            return candidate
    return None


def run_assertions(
    assertions_dir: Path,
    name: str,
    eval_record: dict,
    ies_root: Path,
    agent: str = None,
    transcript_path: str = None,
    yaml_module=None,
    log_error=None,
) -> dict:
    """Load and evaluate assertions for a skill/workflow by name.

    Returns an updated assessment.structural dict — same shape whether the
    caller is a hook or the synchronous grade_skill_run.py script. Categories
    ("structure"/"content"/"quality") are aggregated separately in
    `category_breakdown` for the printed summary block.
    """
    structural = eval_record.get("assessment", {}).get("structural", {
        "expected_outputs_written": None,
        "outputs_non_empty": None,
        "assertions_checked": 0,
        "assertions_passed": 0,
        "assertion_results": [],
        "category_breakdown": {},
    })

    assertion_file = find_assertion_file(assertions_dir, name, agent)
    if not assertion_file:
        return structural

    try:
        with open(assertion_file, "r") as f:
            assertion_data = json.load(f)
    except Exception as e:
        if log_error:
            log_error(f"run_assertions: failed to load {assertion_file}: {e}")
        return structural

    assertions = assertion_data.get("assertions", [])
    results = []
    category_breakdown = {"structure": [0, 0], "content": [0, 0], "quality": [0, 0]}  # [passed, checked]

    for a in assertions:
        check = a.get("check")
        a_id = a.get("id", "unknown")
        description = a.get("description", "")
        category = a.get("category", "structure")
        if category not in category_breakdown:
            category = "structure"

        fn = CHECKS.get(check)
        if fn is None:
            results.append({
                "assertion": a_id, "description": description, "category": category,
                "passed": None, "skipped": True, "reason": f"unknown check type: {check}"
            })
            continue

        try:
            passed, extra = fn(a, eval_record, ies_root, transcript_path, yaml_module)
        except Exception as e:
            if log_error:
                log_error(f"run_assertions: error evaluating {a_id}: {e}")
            passed, extra = None, {"skipped": True, "reason": f"evaluation error: {e}"}

        entry = {"assertion": a_id, "description": description, "category": category, "passed": passed}
        entry.update(extra)
        results.append(entry)

        if passed is not None:
            category_breakdown[category][1] += 1
            if passed:
                category_breakdown[category][0] += 1

    non_skipped = [r for r in results if not r.get("skipped")]
    checked = len(non_skipped)
    passed_count = sum(1 for r in non_skipped if r.get("passed") is True)

    file_exists_results = [
        r for r in non_skipped
        if any(a.get("id") == r["assertion"] and a.get("check") == "file_exists" for a in assertions)
    ]
    file_min_bytes_results = [
        r for r in non_skipped
        if any(a.get("id") == r["assertion"] and a.get("check") == "file_min_bytes" for a in assertions)
    ]

    expected_outputs_written = (
        all(r.get("passed") for r in file_exists_results) if file_exists_results else None
    )
    outputs_non_empty = (
        all(r.get("passed") for r in file_min_bytes_results) if file_min_bytes_results else None
    )

    structural["assertion_results"] = results
    structural["assertions_checked"] = checked
    structural["assertions_passed"] = passed_count
    structural["expected_outputs_written"] = expected_outputs_written
    structural["outputs_non_empty"] = outputs_non_empty
    structural["category_breakdown"] = {
        cat: {"passed": v[0], "checked": v[1]} for cat, v in category_breakdown.items()
    }

    return structural
