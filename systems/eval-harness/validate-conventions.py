#!/usr/bin/env python3
"""
validate-conventions.py — linter for reference/capability-conventions.md.

Usage:
  python3 systems/eval-harness/validate-conventions.py                    # report mode, whole repo
  python3 systems/eval-harness/validate-conventions.py --target <path>     # report mode, one artifact
  python3 systems/eval-harness/validate-conventions.py --target <path> --mode build-gate

Modes:
  report (default) — print all findings, exit 0. Used by workflows/skill-optimize and the sweep.
  build-gate       — FAIL-class findings exit non-zero. Used by rigby-capability-build's lint step.

Rules and severity classes are defined in reference/capability-conventions.md.
Size WARNs can be excused in systems/eval-harness/conventions-exceptions.json
(match on path + rule id; expired review_after re-raises the finding as warn).

Output: structured findings, one JSON object per line, to stdout.
Summary counts to stderr. Exit codes: 0 clean/report, 1 usage error,
2 FAIL-class findings in build-gate mode.
"""

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST_PATH = ROOT / "skills" / "_manifest.jsonl"
EXCEPTIONS_PATH = ROOT / "systems" / "eval-harness" / "conventions-exceptions.json"
ERROR_ENTRIES_DIR = ROOT / "systems" / "error-tracking" / "entries"

SIZE_GUIDES = {
    "size.skill_body": ("SKILL.md", 500, 5000),
    "size.workflow_md": ("workflow.md", 150, None),
    "size.step_file": ("step", 200, None),
    "size.agent_file": ("agent", 400, None),
    "size.script": (".py", 300, None),
}
# Imperative-start heuristic: common command verbs. This is a WARN-class
# heuristic, not a grammar check — anything missing shows up in the sweep.
VERB_START = re.compile(
    r"^(use|build|create|make|write|generate|pull|run|check|verify|audit|analyze|review|"
    r"process|extract|find|match|draft|send|monitor|manage|interpret|plan|package|install|"
    r"submit|track|log|record|tag|search|sync|upload|download|read|turn|surface|deep|show|"
    r"extend|apply|close|report|walk|guide|coach|route|validate|handle|push|navigate|"
    r"execute|capture|convert|compare|score|grade|summarize|interpret|scan|resolve|"
    r"normalize|aggregate|collect|confirm|prepare|update|add|remove|delete|edit|move|"
    r"copy|fetch|retrieve|store|save|load|list|enumerate|count|measure|test|benchmark|"
    r"polish|refine|improve|optimize|compact|archive|restore|revert|rollback|register|"
    r"authenticate|connect|disconnect|configure|setup|deploy|publish|post|notify|alert|"
    r"prompt|remind|brief|prep|review|cross-reference|cross reference|"
    r"get|identify|query|trigger|scrape|fire|link|receive|enroll|activate)", re.I)
IMPORT_RE = re.compile(r"^(?:from\s+([\w.]+)\s+import\s+[\w.(]|import\s+([\w.]+(?:\s*,\s*[\w.]+)*))", re.M)
# local packages inside IES never need a PEP 723 dependency declaration
LOCAL_PACKAGES = {"scripts", "systems", "skills", "agents", "utils", "hook_utils", "step_outputs", "step_audit", "scoring", "score_eval", "assertion_checks", "token_usage", "apply_ruling", "mcp_client"}
STDLIB = set(sys.stdlib_module_names) if hasattr(sys, "stdlib_module_names") else set()

USAGE_ERROR, EXEC_FAIL = 1, 2


def err(msg):
    print(f"ERROR: {msg}\nExpected: see --help\nTry: python3 systems/eval-harness/validate-conventions.py --help", file=sys.stderr)
    sys.exit(USAGE_ERROR)


def finding(severity, rule, path, message):
    rel = path.relative_to(ROOT) if str(path).startswith(str(ROOT)) else path
    return {"severity": severity, "rule": rule, "path": str(rel), "message": message}


def rel_path(path):
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_frontmatter_text(text):
    if not text.startswith("---"):
        return None, text
    lines = text.split("\n")
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            body = "\n".join(lines[i + 1:])
            fm_block = "\n".join(lines[1:i])
            return fm_block, body
    return None, text


def fm_get(fm_block, key):
    """Return a frontmatter value, unwrapping YAML block scalars (> / |) and quotes."""
    m = re.search(rf"^{key}:\s*(.*)$", fm_block or "", re.M)
    if not m:
        return None
    inline = m.group(1).strip().strip("\"'")
    if inline in (">", "|", ">-", "|-", ">+", "|+"):
        # block scalar: join indented continuation lines
        lines = fm_block.split("\n")
        start = next(i for i, l in enumerate(lines) if re.match(rf"^{key}:", l))
        block = []
        for l in lines[start + 1:]:
            if l.startswith(("  ", "\t")) or (block and not l.strip()):
                block.append(l.strip())
            elif not l.strip() and not block:
                continue
            else:
                break
        return " ".join(x for x in block if x)
    return inline


def load_exceptions():
    if not EXCEPTIONS_PATH.exists():
        return []
    try:
        return json.loads(EXCEPTIONS_PATH.read_text()).get("exceptions", [])
    except json.JSONDecodeError as e:
        err(f"cannot parse {EXCEPTIONS_PATH}: {e}")


def exception_for(exceptions, path, rule):
    """Return ('acknowledged'|'warn', entry) if an exception matches path+rule."""
    rel = rel_path(path)
    today = date.today()
    for e in exceptions:
        if e.get("path") == rel and e.get("rule") == rule:
            ra = e.get("review_after")
            if ra:
                try:
                    if datetime.fromisoformat(ra).date() < today:
                        return "warn", e  # decayed
                except ValueError:
                    pass
            return "acknowledged", e
    return None, None


def manifest_ids():
    ids = set()
    if MANIFEST_PATH.exists():
        for line in MANIFEST_PATH.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                ids.add(json.loads(line).get("id"))
            except json.JSONDecodeError:
                pass
    return ids


def skills_with_error_history():
    """Skills named in error-log `related_skill` fields (the Gotchas trigger)."""
    skills = set()
    if not ERROR_ENTRIES_DIR.exists():
        return skills
    for p in ERROR_ENTRIES_DIR.glob("*.json"):
        try:
            data = json.loads(p.read_text())
            for key in ("related_skill", "related_skills"):
                v = data.get(key)
                if isinstance(v, str):
                    skills.add(v)
                elif isinstance(v, list):
                    skills.update(v)
        except (json.JSONDecodeError, OSError):
            continue
    return skills


# ---------------------------------------------------------------------------
# Rule checks
# ---------------------------------------------------------------------------

def check_size(path, text, exceptions):
    name = path.name
    lines = len(text.splitlines())
    tokens = len(text.encode()) // 4
    rel = rel_path(path)
    if name == "SKILL.md":
        rule = "size.skill_body"
    elif name == "workflow.md":
        rule = "size.workflow_md"
    elif path.suffix == ".py":
        rule = "size.script"
    elif "workflows" in path.parts and path.suffix == ".md":
        rule = None  # set below: only files inside a steps/ directory are step files
        if "steps" in path.parts:
            rule = "size.step_file"
    elif "agents" in path.parts and path.suffix == ".md":
        rule = "size.agent_file"
    else:
        return []
    if rule is None:
        return []
    _, line_guide, token_guide = SIZE_GUIDES[rule]
    reasons = []
    if line_guide and lines > line_guide:
        reasons.append(f"{lines} lines > {line_guide}")
    if token_guide and tokens > token_guide:
        reasons.append(f"~{tokens} tokens > {token_guide}")
    if not reasons:
        return []
    status, entry = exception_for(exceptions, path, rule)
    if status == "acknowledged":
        return [finding("acknowledged", rule, path,
                        f"over size guide ({'; '.join(reasons)}) — exception recorded, "
                        f"review after {entry.get('review_after', 'unknown')}")]
    note = " (exception decayed — review_after passed)" if status == "warn" else ""
    return [finding("warn", rule, path, f"over size guide: {'; '.join(reasons)}{note}")]


def check_skill(path, text, exceptions, manifest, error_skills, findings):
    fm_block, body = parse_frontmatter_text(text)
    desc = fm_get(fm_block, "description") if fm_block else None
    rel = rel_path(path)

    if not fm_block:
        findings.append(finding("fail", "skill.frontmatter", path, "no frontmatter"))
        desc = None
    if desc is None:
        findings.append(finding("fail", "skill.description", path, "no description in frontmatter"))
    elif len(desc) > 1024:
        findings.append(finding("fail", "skill.description_limit", path,
                                f"description is {len(desc)} chars > 1024"))
    elif not VERB_START.match(desc):
        findings.append(finding("warn", "skill.description_imperative", path,
                                "description does not start with a verb (intent, not mechanics)"))

    # manifest registration (library skills only; fork stubs register via their library twin)
    skill_id = path.parent.name
    if manifest and "skills" in path.parts and ".claude" not in path.parts and skill_id not in manifest:
        findings.append(finding("fail", "skill.manifest_registration", path,
                                f"'{skill_id}' not in skills/_manifest.jsonl"))

    # system/personal blocks
    if "<!-- system:start -->" not in text and "<!-- personal:start -->" not in text:
        findings.append(finding("fail", "skill.evolution_blocks", path,
                                "missing <!-- system:start --> / <!-- personal:start --> delineation blocks"))

    # gotchas where error history exists
    if skill_id in error_skills and not re.search(r"^#+\s*Gotchas?\b", body, re.M | re.I):
        findings.append(finding("warn", "skill.gotchas", path,
                                "error history exists for this skill (error-log related_skill) but no Gotchas section"))

    # reference pointers must state when to load
    for m in re.finditer(r"`?((?:references|assets)/[\w\-./]+)`?", body):
        ctx = body[max(0, m.start() - 200):m.end() + 200]
        if not re.search(r"\b(if|when|before|after|for|use|read|load|on)\b", ctx, re.I):
            findings.append(finding("warn", "skill.pointer_when_to_load", path,
                                    f"pointer to {m.group(1)} lacks when-to-load phrasing"))
            break  # one per file; the sweep fixes all instances at once


def check_step(path, text, exceptions, findings):
    fm_block, _ = parse_frontmatter_text(text)
    if fm_block is None:
        findings.append(finding("fail", "step.frontmatter", path, "step file missing frontmatter"))


def check_agent(path, text, exceptions, findings):
    if "<!-- system:start -->" not in text and "<!-- personal:start -->" not in text:
        findings.append(finding("fail", "agent.evolution_blocks", path,
                                "missing <!-- system:start --> / <!-- personal:start --> delineation blocks"))


def check_script(path, text, exceptions, findings):
    rel = rel_path(path)
    # statement-position input() calls only; string/regex literals about the rule are excluded
    if re.search(r"(?m)^[^#'\"\\]*?\binput\(", text):
        status, entry = exception_for(exceptions, path, "script.interactive_input")
        if status == "acknowledged":
            findings.append(finding("acknowledged", "script.interactive_input", path,
                                    "input() call — exception recorded, "
                                    f"review after {entry.get('review_after', 'unknown')}"))
        elif status == "warn":
            findings.append(finding("fail", "script.interactive_input", path,
                                    "bundled script calls input() — must be non-interactive "
                                    "(exception decayed — review_after passed)"))
        else:
            findings.append(finding("fail", "script.interactive_input", path,
                                    "bundled script calls input() — must be non-interactive"))
    mods = set()
    for m in IMPORT_RE.finditer(text):
        mod = m.group(1) or m.group(2) or ""
        top = mod.split(".")[0].split(",")[0].strip()
        if not top or top in STDLIB or top in LOCAL_PACKAGES:
            continue
        # local modules: a sibling file in the same directory is not a dependency
        if (path.parent / f"{top}.py").exists() or (ROOT / f"{top}.py").exists():
            continue
        mods.add(top)
    has_pep723 = re.search(r"#\s*///\s*script", text) and "dependencies" in text
    if mods and not has_pep723:
        findings.append(finding("fail", "script.pep723_dependencies", path,
                                f"non-stdlib imports ({', '.join(sorted(mods))}) without a PEP 723 "
                                f"'# /// script' dependency block"))
    if "argparse" not in text and "sys.argv" in text:
        findings.append(finding("warn", "script.help_flag", path,
                                "script parses sys.argv manually with no argparse --help handling"))


def classify_and_check(path, exceptions, manifest, error_skills):
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        return [finding("fail", "io.read", path, str(e))]
    findings = []
    rel_parts = path.parts
    if path.name == "SKILL.md" and ("skills" in rel_parts or ".claude" in rel_parts):
        check_skill(path, text, exceptions, manifest, error_skills, findings)
    elif path.name == "workflow.md":
        pass  # orchestrator; size check only
    elif "workflows" in rel_parts and "steps" in rel_parts and path.suffix == ".md":
        check_step(path, text, exceptions, findings)
    elif "agents" in rel_parts and path.suffix == ".md":
        check_agent(path, text, exceptions, findings)
    if path.suffix == ".py":
        check_script(path, text, exceptions, findings)
    findings.extend(check_size(path, text, exceptions))
    return findings


def build_gate_extra(target, findings):
    """FAIL rules that only apply when validating a newly built artifact."""
    # two-tier: agent-specific skill must ship with its stub
    if target.name == "SKILL.md" and ".claude/skills" in str(target):
        lib_twin = ROOT / "skills" / target.parent.name / "SKILL.md"
        if not lib_twin.exists():
            findings.append(finding("fail", "skill.two_tier_stub", target,
                                    f"agent-specific skill has no library content file at {lib_twin}"))
    return findings


def collect_targets(target_arg):
    if target_arg:
        t = (ROOT / target_arg) if not Path(target_arg).is_absolute() else Path(target_arg)
        if not t.exists():
            err(f"target {target_arg} does not exist (relative to repo root)")
        return [t]
    skip = {".git", "__pycache__", "node_modules", "evolutions", ".obsidian", "dist", ".venv", "vendor"}
    targets = []
    for base in ("skills", ".claude/skills", "workflows", "agents", ".claude/hooks", "systems"):
        base_p = ROOT / base
        if base_p.exists():
            for p in base_p.rglob("*"):
                if p.is_file() and not (skip & set(p.relative_to(ROOT).parts[:-1])):
                    targets.append(p)
    return targets


def main():
    ap = argparse.ArgumentParser(
        description="Lint IES capability artifacts against reference/capability-conventions.md",
        epilog="Examples:\n"
               "  python3 systems/eval-harness/validate-conventions.py\n"
               "  python3 systems/eval-harness/validate-conventions.py --target skills/git/SKILL.md\n"
               "  python3 systems/eval-harness/validate-conventions.py --target .claude/skills/new-skill/SKILL.md --mode build-gate\n")
    ap.add_argument("--target", help="lint a single artifact (path relative to repo root)")
    ap.add_argument("--mode", choices=["report", "build-gate"], default="report",
                    help="report: print findings, exit 0 (default). build-gate: FAIL-class findings exit non-zero.")
    args = ap.parse_args()

    exceptions = load_exceptions()
    manifest = manifest_ids()
    error_skills = skills_with_error_history()

    findings = []
    for t in collect_targets(args.target):
        findings.extend(classify_and_check(t, exceptions, manifest, error_skills))
    if args.mode == "build-gate" and args.target:
        findings.extend(build_gate_extra(
            (ROOT / args.target) if not Path(args.target).is_absolute() else Path(args.target), findings))

    for f in findings:
        print(json.dumps(f))
    fails = sum(1 for f in findings if f["severity"] == "fail")
    warns = sum(1 for f in findings if f["severity"] == "warn")
    acks = sum(1 for f in findings if f["severity"] == "acknowledged")
    print(f"SUMMARY: {fails} fail | {warns} warn | {acks} acknowledged", file=sys.stderr)
    if args.mode == "build-gate" and fails:
        print(f"BUILD GATE: blocked — {fails} FAIL-class finding(s). Fix them; FAIL-class rules have no exceptions.",
              file=sys.stderr)
        sys.exit(EXEC_FAIL)


if __name__ == "__main__":
    main()
