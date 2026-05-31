#!/usr/bin/env python3
"""
Jarvis Skill Library Audit
Usage: python3 skills/rigby-skill-audit/scripts/audit.py [--threshold-days N]

Audits both skill roots:
  skills/           -- library skills (owning_agent, trigger_keywords, etc.)
  .claude/skills/   -- fork skills (context: fork, agent, allowed-tools)

Five report sections:
  1. Structural Validation
  2. Root Coverage
  3. Schema Classification
  4. Token Pressure
  5. Execution Health
"""

import argparse
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip3 install pyyaml", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LIBRARY_ROOT = Path("skills")
FORK_ROOT = Path(".claude/skills")
MANIFEST_PATH = Path("skills/_manifest.jsonl")
SKILL_RUNS_DIR = Path("systems/eval-harness/skill-runs")
WORKFLOWS_DIR = Path("workflows")

LIBRARY_REQUIRED_FIELDS = {"name", "description", "model", "owning_agent", "trigger_keywords", "trigger_agents"}
FORK_REQUIRED_FIELDS = {"name", "description", "model", "context", "agent", "allowed-tools"}

MAX_DESCRIPTION_CHARS = 200
BODY_BLOAT_TOKEN_THRESHOLD = 3000

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(skill_path: Path):
    """Parse YAML frontmatter from a SKILL.md file. Returns (dict|None, error_str|None)."""
    try:
        text = skill_path.read_text(encoding="utf-8")
    except Exception as e:
        return None, f"Cannot read file: {e}"

    if not text.startswith("---"):
        return {}, None  # No frontmatter — treat as empty

    lines = text.split("\n")
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return None, "Unclosed frontmatter (no closing ---)"

    fm_text = "\n".join(lines[1:end_idx])
    try:
        data = yaml.safe_load(fm_text) or {}
        body = "\n".join(lines[end_idx + 1:])
        return data, None, body
    except yaml.YAMLError as e:
        return None, f"YAML parse error: {e}", ""


def token_estimate(text: str) -> int:
    return math.ceil(len(text.encode("utf-8")) / 4)


def git_last_commit_date(skill_path: Path) -> datetime | None:
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci", "--", str(skill_path)],
            capture_output=True, text=True, timeout=5
        )
        raw = result.stdout.strip()
        if not raw:
            return None
        # Format: "2026-05-01 14:32:00 -0500"
        # Parse with timezone
        dt = datetime.fromisoformat(raw.replace(" ", "T", 1))
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def read_run_file(skill_name: str) -> dict | None:
    run_path = SKILL_RUNS_DIR / f"{skill_name}-latest.json"
    if not run_path.exists():
        return None
    try:
        return json.loads(run_path.read_text())
    except Exception:
        return None


def get_run_timestamp(run_data: dict) -> datetime | None:
    """Extract the best available timestamp from a run file."""
    for key in ("completed", "started"):
        val = run_data.get(key)
        if val:
            try:
                dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
                return dt.astimezone(timezone.utc)
            except Exception:
                continue
    return None


def scan_session_jsonl_for_skill(skill_name: str) -> bool:
    """Check ~/.claude session JSONL files for mentions of skill_name."""
    claude_dir = Path.home() / ".claude"
    if not claude_dir.exists():
        return False
    try:
        for jsonl_file in claude_dir.glob("*.jsonl"):
            try:
                content = jsonl_file.read_text(encoding="utf-8", errors="ignore")
                if skill_name in content:
                    return True
            except Exception:
                continue
    except Exception:
        pass
    return False


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

def discover_skills():
    """
    Returns list of dicts:
      {path, root, skill_name_from_dir, frontmatter, parse_error, body, full_text}
    """
    skills = []

    for root_dir, root_label in [(LIBRARY_ROOT, "library"), (FORK_ROOT, "fork")]:
        if not root_dir.exists():
            continue
        for skill_dir in sorted(root_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            if skill_dir.name.startswith("_"):
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue

            result = parse_frontmatter(skill_md)
            if len(result) == 3:
                fm, err, body = result
            else:
                fm, err = result
                body = ""

            try:
                full_text = skill_md.read_text(encoding="utf-8")
            except Exception:
                full_text = ""

            skills.append({
                "path": skill_md,
                "dir": skill_dir,
                "root": root_label,
                "dir_name": skill_dir.name,
                "frontmatter": fm,
                "parse_error": err,
                "body": body,
                "full_text": full_text,
            })

    return skills


# ---------------------------------------------------------------------------
# Section 1: Structural Validation
# ---------------------------------------------------------------------------

def section_structural(skills):
    parse_errors = []
    missing_fields = []
    names_seen = {}  # name -> list of paths

    for s in skills:
        path_str = str(s["path"])
        fm = s["frontmatter"]

        if s["parse_error"]:
            parse_errors.append((path_str, s["parse_error"]))
            continue

        if fm is None:
            parse_errors.append((path_str, "No frontmatter returned"))
            continue

        # Determine expected schema based on root
        if s["root"] == "fork":
            required = FORK_REQUIRED_FIELDS
        else:
            required = LIBRARY_REQUIRED_FIELDS

        missing = required - set(fm.keys())
        if missing:
            missing_fields.append((path_str, sorted(missing)))

        # Also check fork context value
        if s["root"] == "fork" and fm.get("context") != "fork":
            missing_fields.append((path_str, [f"context must equal 'fork' (got: {fm.get('context')!r})"]))

        # Track names for duplicate detection
        name = fm.get("name")
        if name:
            names_seen.setdefault(name, []).append(path_str)

    duplicates = {name: paths for name, paths in names_seen.items() if len(paths) > 1}

    return {
        "parse_errors": parse_errors,
        "missing_fields": missing_fields,
        "duplicates": duplicates,
    }


# ---------------------------------------------------------------------------
# Section 2: Root Coverage
# ---------------------------------------------------------------------------

def section_root_coverage(skills):
    if not MANIFEST_PATH.exists():
        return {"manifest_missing": True, "not_in_manifest": [], "manifest_no_dir": [], "cross_root_conflicts": []}

    # Load manifest
    manifest_entries = []
    manifest_errors = []
    try:
        for i, line in enumerate(MANIFEST_PATH.read_text().splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                manifest_entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                manifest_errors.append(f"Line {i}: {e}")
    except Exception as e:
        return {"manifest_missing": False, "manifest_read_error": str(e),
                "not_in_manifest": [], "manifest_no_dir": [], "cross_root_conflicts": []}

    manifest_ids = {e.get("id") for e in manifest_entries if e.get("id")}
    manifest_paths = {}
    for e in manifest_entries:
        p = e.get("path")
        if p:
            manifest_paths[p] = e

    # Skills on disk
    disk_skill_paths = {str(s["path"]): s for s in skills}
    disk_dir_names = {s["dir_name"] for s in skills}

    # Skills not in manifest — check by path match
    not_in_manifest = []
    for s in skills:
        path_str = str(s["path"])
        # Normalize path for comparison
        found = False
        for mp in manifest_paths:
            if Path(mp).resolve() == s["path"].resolve() or mp == path_str or mp.endswith(str(s["path"])):
                found = True
                break
        # Also try matching by skill id in frontmatter or dir_name
        fm = s["frontmatter"] or {}
        skill_id = fm.get("name") or s["dir_name"]
        if not found:
            for e in manifest_entries:
                if e.get("id") == skill_id or e.get("id") == s["dir_name"]:
                    found = True
                    break
        if not found:
            not_in_manifest.append(str(s["path"]))

    # Manifest entries with no corresponding directory
    manifest_no_dir = []
    for e in manifest_entries:
        entry_path = e.get("path", "")
        entry_id = e.get("id", "")
        # Check if the path exists
        if entry_path and not Path(entry_path).exists():
            # Also check if a directory with that id exists in either root
            lib_dir = LIBRARY_ROOT / entry_id
            fork_dir = FORK_ROOT / entry_id
            if not lib_dir.exists() and not fork_dir.exists():
                manifest_no_dir.append((entry_id, entry_path))

    # Cross-root conflicts: same skill name in both roots
    lib_names = {s["dir_name"] for s in skills if s["root"] == "library"}
    fork_names = {s["dir_name"] for s in skills if s["root"] == "fork"}
    cross_root_conflicts = sorted(lib_names & fork_names)

    return {
        "manifest_missing": False,
        "manifest_errors": manifest_errors,
        "not_in_manifest": not_in_manifest,
        "manifest_no_dir": manifest_no_dir,
        "cross_root_conflicts": cross_root_conflicts,
    }


# ---------------------------------------------------------------------------
# Section 3: Schema Classification
# ---------------------------------------------------------------------------

def section_schema_classification(skills):
    ambiguous = []
    fork_prefix_conflicts = []

    for s in skills:
        fm = s["frontmatter"]
        if not fm:
            continue

        has_owning_agent = bool(fm.get("owning_agent"))
        is_fork_context = fm.get("context") == "fork"

        # Ambiguous: missing BOTH owning_agent AND context:fork
        if not has_owning_agent and not is_fork_context:
            ambiguous.append((str(s["path"]), "missing owning_agent and context:fork"))

        # Fork skill prefix conflict
        if s["root"] == "fork" and has_owning_agent:
            dir_name = s["dir_name"]
            prefix = dir_name.split("-")[0] if "-" in dir_name else dir_name
            explicit_owner = fm.get("owning_agent", "")
            if explicit_owner and explicit_owner != prefix:
                fork_prefix_conflicts.append((
                    str(s["path"]),
                    f"dir prefix '{prefix}' conflicts with owning_agent '{explicit_owner}'"
                ))

    return {
        "ambiguous": ambiguous,
        "fork_prefix_conflicts": fork_prefix_conflicts,
    }


# ---------------------------------------------------------------------------
# Section 4: Token Pressure
# ---------------------------------------------------------------------------

def section_token_pressure(skills):
    skill_tokens = []
    agent_budgets = {}
    description_overages = []
    body_bloat = []

    for s in skills:
        fm = s["frontmatter"] or {}
        full_text = s["full_text"]
        body = s["body"]

        total_tokens = token_estimate(full_text)
        body_tokens = token_estimate(body)

        skill_id = s["dir_name"]
        skill_tokens.append((skill_id, str(s["path"]), total_tokens))

        # Agent budget attribution
        agents_for_skill = set()
        if s["root"] == "library":
            if fm.get("owning_agent"):
                agents_for_skill.add(fm["owning_agent"])
            for a in (fm.get("trigger_agents") or []):
                agents_for_skill.add(a)
        else:
            # Fork: derive from directory prefix
            prefix = skill_id.split("-")[0] if "-" in skill_id else skill_id
            agents_for_skill.add(prefix)
            if fm.get("agent"):
                agents_for_skill.add(fm["agent"])

        for agent in agents_for_skill:
            agent_budgets[agent] = agent_budgets.get(agent, 0) + total_tokens

        # Description length
        desc = fm.get("description", "")
        if desc and len(desc) > MAX_DESCRIPTION_CHARS:
            description_overages.append((str(s["path"]), len(desc)))

        # Body bloat: body > threshold AND matching workflow exists
        workflow_dir = WORKFLOWS_DIR / skill_id
        if body_tokens > BODY_BLOAT_TOKEN_THRESHOLD and workflow_dir.exists():
            body_bloat.append((str(s["path"]), body_tokens, str(workflow_dir)))

    skill_tokens.sort(key=lambda x: x[2], reverse=True)
    top10 = skill_tokens[:10]

    return {
        "top10_heaviest": top10,
        "agent_budgets": dict(sorted(agent_budgets.items(), key=lambda x: x[1], reverse=True)),
        "description_overages": description_overages,
        "body_bloat": body_bloat,
        "total_skill_count": len(skill_tokens),
        "total_tokens": sum(t for _, _, t in skill_tokens),
    }


# ---------------------------------------------------------------------------
# Section 5: Execution Health
# ---------------------------------------------------------------------------

def section_execution_health(skills, threshold_days: int):
    now = datetime.now(tz=timezone.utc)
    cutoff = now - timedelta(days=threshold_days)

    never_run = []
    stale = []
    active = []
    potentially_broken = []

    for s in skills:
        skill_id = s["dir_name"]
        run_data = read_run_file(skill_id)

        if run_data is None:
            # Check session JSONL as fallback
            seen_in_session = scan_session_jsonl_for_skill(skill_id)
            never_run.append((skill_id, str(s["path"]), "session_mention" if seen_in_session else "no_evidence"))
            continue

        run_ts = get_run_timestamp(run_data)

        if run_ts is None:
            never_run.append((skill_id, str(s["path"]), "run_file_exists_no_timestamp"))
            continue

        if run_ts < cutoff:
            state = "stale"
            stale.append((skill_id, str(s["path"]), run_ts.date().isoformat()))
        else:
            state = "active"
            active.append((skill_id, str(s["path"]), run_ts.date().isoformat()))

        # Check for potentially broken: last git commit after last run
        last_commit = git_last_commit_date(s["path"])
        if last_commit and run_ts and last_commit > run_ts:
            potentially_broken.append((
                skill_id,
                str(s["path"]),
                run_ts.date().isoformat(),
                last_commit.date().isoformat(),
                state,
            ))

    return {
        "threshold_days": threshold_days,
        "never_run": never_run,
        "stale": stale,
        "active": active,
        "potentially_broken": potentially_broken,
    }


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def render_report(skills, s1, s2, s3, s4, s5):
    lib_count = sum(1 for s in skills if s["root"] == "library")
    fork_count = sum(1 for s in skills if s["root"] == "fork")
    total = lib_count + fork_count
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = []
    lines.append("=" * 70)
    lines.append(f"JARVIS SKILL AUDIT — {now_str}")
    lines.append(f"{total} skills  |  {lib_count} library (skills/)  |  {fork_count} fork (.claude/skills/)")
    lines.append("=" * 70)

    # -------------------------------------------------------------------
    lines.append("\n## SECTION 1 — STRUCTURAL VALIDATION")
    lines.append("-" * 40)

    if not s1["parse_errors"] and not s1["missing_fields"] and not s1["duplicates"]:
        lines.append("Clean. No parse errors, missing fields, or duplicate names.")
    else:
        if s1["parse_errors"]:
            lines.append(f"\nPARSE ERRORS ({len(s1['parse_errors'])}):")
            for path, err in s1["parse_errors"]:
                lines.append(f"  [ERROR] {path}")
                lines.append(f"          {err}")

        if s1["missing_fields"]:
            lines.append(f"\nMISSING REQUIRED FIELDS ({len(s1['missing_fields'])}):")
            for path, fields in s1["missing_fields"]:
                lines.append(f"  [WARN]  {path}")
                lines.append(f"          Missing: {', '.join(fields)}")

        if s1["duplicates"]:
            lines.append(f"\nDUPLICATE NAMES ({len(s1['duplicates'])}):")
            for name, paths in s1["duplicates"].items():
                lines.append(f"  [WARN]  name='{name}' appears in {len(paths)} files:")
                for p in paths:
                    lines.append(f"          {p}")

    # -------------------------------------------------------------------
    lines.append("\n## SECTION 2 — ROOT COVERAGE")
    lines.append("-" * 40)

    if s2.get("manifest_missing"):
        lines.append("[CRITICAL] skills/_manifest.jsonl not found.")
    elif s2.get("manifest_read_error"):
        lines.append(f"[CRITICAL] Cannot read manifest: {s2['manifest_read_error']}")
    else:
        if s2.get("manifest_errors"):
            lines.append(f"\nMANIFEST JSON ERRORS ({len(s2['manifest_errors'])}):")
            for e in s2["manifest_errors"]:
                lines.append(f"  [ERROR] {e}")

        if not s2["not_in_manifest"] and not s2["manifest_no_dir"] and not s2["cross_root_conflicts"]:
            lines.append("Clean. All skills registered; all manifest entries have directories.")
        else:
            if s2["not_in_manifest"]:
                lines.append(f"\nSKILLS ON DISK NOT IN MANIFEST ({len(s2['not_in_manifest'])}):")
                for p in s2["not_in_manifest"]:
                    lines.append(f"  [WARN]  {p}")

            if s2["manifest_no_dir"]:
                lines.append(f"\nMANIFEST ENTRIES WITH NO DIRECTORY ({len(s2['manifest_no_dir'])}):")
                for skill_id, path in s2["manifest_no_dir"]:
                    lines.append(f"  [WARN]  id={skill_id!r}  path={path!r}")

            if s2["cross_root_conflicts"]:
                lines.append(f"\nCROSS-ROOT CONFLICTS — same name in both roots ({len(s2['cross_root_conflicts'])}):")
                for name in s2["cross_root_conflicts"]:
                    lines.append(f"  [WARN]  {name}")

    # -------------------------------------------------------------------
    lines.append("\n## SECTION 3 — SCHEMA CLASSIFICATION")
    lines.append("-" * 40)

    if not s3["ambiguous"] and not s3["fork_prefix_conflicts"]:
        lines.append("Clean. All skills clearly classified as library or fork.")
    else:
        if s3["ambiguous"]:
            lines.append(f"\nAMBIGUOUS SKILLS ({len(s3['ambiguous'])}) — missing owning_agent and context:fork:")
            for path, reason in s3["ambiguous"]:
                lines.append(f"  [WARN]  {path}")
                lines.append(f"          {reason}")

        if s3["fork_prefix_conflicts"]:
            lines.append(f"\nFORK PREFIX CONFLICTS ({len(s3['fork_prefix_conflicts'])}):")
            for path, reason in s3["fork_prefix_conflicts"]:
                lines.append(f"  [WARN]  {path}")
                lines.append(f"          {reason}")

    # -------------------------------------------------------------------
    lines.append("\n## SECTION 4 — TOKEN PRESSURE")
    lines.append("-" * 40)
    lines.append(f"Total library: {s4['total_tokens']:,} tokens across {s4['total_skill_count']} skills")
    lines.append(f"Average: {s4['total_tokens'] // max(s4['total_skill_count'], 1):,} tokens/skill")

    lines.append("\nAGENT BUDGET TOTALS (owning + trigger):")
    for agent, tokens in s4["agent_budgets"].items():
        lines.append(f"  {agent:<20} {tokens:>7,} tokens")

    lines.append("\nTOP 10 HEAVIEST SKILLS:")
    for skill_id, path, tokens in s4["top10_heaviest"]:
        lines.append(f"  {tokens:>6,}t  {skill_id}")

    if s4["description_overages"]:
        lines.append(f"\nDESCRIPTION OVER {MAX_DESCRIPTION_CHARS} CHARS ({len(s4['description_overages'])}):")
        for path, length in s4["description_overages"]:
            lines.append(f"  [WARN]  {path}  ({length} chars)")

    if s4["body_bloat"]:
        lines.append(f"\nSUSPECTED BODY BLOAT ({len(s4['body_bloat'])}) — body >{BODY_BLOAT_TOKEN_THRESHOLD}t with matching workflow:")
        for path, tokens, wf_dir in s4["body_bloat"]:
            lines.append(f"  [WARN]  {path}  ({tokens:,}t body)  workflow: {wf_dir}")
    else:
        lines.append("\nNo suspected body bloat detected.")

    # -------------------------------------------------------------------
    lines.append(f"\n## SECTION 5 — EXECUTION HEALTH (threshold: {s5['threshold_days']} days)")
    lines.append("-" * 40)

    lines.append(f"Active:            {len(s5['active'])}")
    lines.append(f"Stale:             {len(s5['stale'])}")
    lines.append(f"Never run:         {len(s5['never_run'])}")
    lines.append(f"Potentially broken: {len(s5['potentially_broken'])}")

    if s5["stale"]:
        lines.append(f"\nSTALE SKILLS (last run > {s5['threshold_days']} days ago):")
        for skill_id, path, last_run in s5["stale"]:
            lines.append(f"  {skill_id:<35} last run: {last_run}")

    if s5["never_run"]:
        lines.append(f"\nNEVER-RUN SKILLS ({len(s5['never_run'])}):")
        for skill_id, path, evidence in s5["never_run"]:
            note = "(mentioned in session logs)" if evidence == "session_mention" else ""
            lines.append(f"  {skill_id:<35} {note}")

    if s5["potentially_broken"]:
        lines.append(f"\nPOTENTIALLY BROKEN ({len(s5['potentially_broken'])}) — edited after last successful run:")
        lines.append(f"  {'Skill':<35} {'Last Run':<12} {'Last Commit':<12} State")
        lines.append(f"  {'-'*35} {'-'*12} {'-'*12} -----")
        for skill_id, path, last_run, last_commit, state in s5["potentially_broken"]:
            lines.append(f"  {skill_id:<35} {last_run:<12} {last_commit:<12} {state}")

    lines.append("\n" + "=" * 70)

    # Summary counts for Rigby parsing
    critical = len(s1["parse_errors"]) + (1 if s2.get("manifest_missing") else 0)
    warnings = (
        len(s1["missing_fields"]) + len(s1["duplicates"]) +
        len(s2.get("not_in_manifest", [])) + len(s2.get("manifest_no_dir", [])) +
        len(s2.get("cross_root_conflicts", [])) +
        len(s3["ambiguous"]) + len(s3["fork_prefix_conflicts"]) +
        len(s4["description_overages"]) + len(s4["body_bloat"])
    )
    health_flags = len(s5["stale"]) + len(s5["never_run"]) + len(s5["potentially_broken"])

    lines.append(f"SUMMARY: {critical} critical  |  {warnings} warnings  |  {health_flags} health flags")
    lines.append("=" * 70)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Audit Jarvis skill library")
    parser.add_argument("--threshold-days", type=int, default=90,
                        help="Days before a skill run is considered stale (default: 90)")
    args = parser.parse_args()

    # Verify we're running from the jarvis root
    if not MANIFEST_PATH.exists() and not LIBRARY_ROOT.exists():
        print("ERROR: Run this script from the jarvis repo root (where skills/ lives).", file=sys.stderr)
        sys.exit(1)

    skills = discover_skills()

    if not skills:
        print("ERROR: No skills found. Check that skills/ and .claude/skills/ exist.", file=sys.stderr)
        sys.exit(1)

    s1 = section_structural(skills)
    s2 = section_root_coverage(skills)
    s3 = section_schema_classification(skills)
    s4 = section_token_pressure(skills)
    s5 = section_execution_health(skills, args.threshold_days)

    report = render_report(skills, s1, s2, s3, s4, s5)
    print(report)


if __name__ == "__main__":
    main()
