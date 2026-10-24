#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""
Stop Hook: Close Out Turn-Level Eval Record

Fires at the end of every assistant turn. If eval-turn-start.py opened a
turn-level eval record this session (monitoring.active) AND the monitored
workflow's state.yaml has reached a terminal status (complete/aborted/
blocked), finalize the record: completed timestamp, duration, final status,
structural assertions, version hash.

If state.yaml is still in-progress or awaiting-input (the workflow will
continue in a later turn — same pattern plaud-ingest uses for its speaker-ID
pause), leave the record open. The next turn's Stop event will re-check it.

If no turn-level eval was ever opened this session, this hook does nothing —
no stub, no partial record, per spec.
"""

import sys
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone

_IES_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_IES_ROOT / "systems" / "eval-harness" / "vendor"))
sys.path.insert(0, str(_IES_ROOT / "systems" / "eval-harness"))
import yaml
from hook_utils import (
    IES_ROOT, EVAL_RUNS_DIR, log_error, log_info, atomic_write_json, read_stdin,
    infer_session_id, find_open_turn_record,
)
try:
    from token_usage import usage_between
except Exception:
    usage_between = None
try:
    import fully_loaded_cost as _flc
except Exception:
    _flc = None
try:
    from step_audit import steps_all_terminal
except Exception:
    steps_all_terminal = None
try:
    from step_audit import MANIFEST_AGENTS, normalize_agent_label
except Exception:
    MANIFEST_AGENTS = (
        "master", "chief", "chase", "knox", "shep", "quinn",
        "harper", "rigby", "sterling", "galen", "ralph",
    )

    def normalize_agent_label(agent):
        if not agent:
            return None
        a = str(agent).strip().lower()
        if a in ("master", "jarvis"):
            return "master"
        return a if a in MANIFEST_AGENTS else None

TAG = "TURN-STOP"
ASSERTIONS_DIR = IES_ROOT / "systems" / "eval-harness" / "assertions"

TERMINAL_STATUSES = {"complete", "aborted", "blocked"}


def extract_frontmatter_block(content: str) -> str:
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return content
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[1:i])
    return "\n".join(lines[1:])


# --- Stage 3 Phase 1 check helpers (parity with assertion_checks.py) ---------
# These mirror assertion_checks.py's step_owner_manifest / grade_threshold /
# yaml_* helpers so this hook evaluates the new check types identically.

GRADE_ORDER = {"A": 4, "B": 3, "C": 2, "D": 1, "F": 0}


def _frontmatter_field(text: str, field: str):
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


def _manifest_ownership(ies_root) -> dict:
    path = ies_root / "agents" / "manifest.md"
    if not path.is_file():
        return {}
    owners = {}
    for line in path.read_text(errors="replace").split("\n"):
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
        if agent in MANIFEST_AGENTS:
            owners[agent] = cells[3]
    return owners


def _manifest_boot_step_ranges(owners: dict):
    ranges = []
    for agent, owns in owners.items():
        for m in re.finditer(
            r"boot steps?\s+(\d+(?:\.\d+)?)\s*(?:[-–]\s*(\d+(?:\.\d+)?))?", owns or ""
        ):
            lo = float(m.group(1))
            hi = float(m.group(2)) if m.group(2) else lo
            ranges.append((agent, lo, hi))
    return ranges


def _workflow_step_owner_map(ies_root) -> dict:
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
        owner = normalize_agent_label(_frontmatter_field(wf_md.read_text(errors="replace"), "agent"))
        steps_dir = wf / "steps"
        if not steps_dir.is_dir():
            continue
        for sf in steps_dir.glob("*.md"):
            step_owners.setdefault(sf.name, set()).add(owner or wf.name)
    return step_owners


def _yaml_walk(data, field_path):
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


def _leaf_values(node):
    """Every scalar leaf under a parsed-YAML node (a scalar is its own leaf).
    Parity with assertion_checks._leaf_values."""
    if isinstance(node, dict):
        out = []
        for v in node.values():
            out.extend(_leaf_values(v))
        return out
    if isinstance(node, list):
        out = []
        for v in node:
            out.extend(_leaf_values(v))
        return out
    return [node]


def _gate_truthy(node):
    """Gate helper (parity with assertion_checks._gate_truthy): non-empty/truthy."""
    if node is None or node is False:
        return False
    if isinstance(node, str):
        return node.strip() != ""
    if isinstance(node, (list, dict)):
        return len(node) > 0
    if isinstance(node, (int, float)):
        return node != 0
    return True


def check_yaml_field_pattern(a, data):
    """Conditional regex match on a dotted YAML field / its scalar leaves.
    Parity with assertion_checks.check_yaml_field_pattern — see that function
    for the full field reference. Returns (passed, extra)."""
    when_field = a.get("when_field")
    if when_field:
        gate_nodes = _yaml_walk(data, when_field)
        when_pattern = a.get("when_pattern")
        if when_pattern:
            gate_open = any(
                re.search(when_pattern, str(v), re.IGNORECASE)
                for n in gate_nodes for v in _leaf_values(n)
            )
        else:
            gate_open = any(_gate_truthy(n) for n in gate_nodes)
        if not gate_open:
            return True, {"gate": "closed", "reason": "gate condition not met (vacuous pass)"}

    nodes = _yaml_walk(data, a.get("field", ""))
    leaves = [v for n in nodes for v in _leaf_values(n)]
    pattern = a.get("pattern", "")
    matched = [v for v in leaves if re.search(pattern, str(v), re.IGNORECASE)]

    if a.get("negate", False):
        extra = {"leaf_count": len(leaves)}
        if matched:
            extra["matched_sample"] = [str(v) for v in matched[:3]]
        return len(matched) == 0, extra

    min_matches = a.get("min_matches", 1)
    return len(matched) >= min_matches, {"leaf_count": len(leaves), "match_count": len(matched)}


def _draft_norm(text) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def _draft_url_norm(url) -> str:
    return _draft_norm(url).rstrip("/")


def _draft_word_tokens(text):
    return re.findall(r"[a-z0-9']+", str(text or "").lower())


def _longest_common_run(a_tokens, b_tokens):
    """Length + text of the longest contiguous verbatim word run shared by two
    token lists. Parity with assertion_checks._longest_common_run."""
    if not a_tokens or not b_tokens:
        return 0, ""
    b_positions = {}
    for j, tok in enumerate(b_tokens):
        b_positions.setdefault(tok, []).append(j)
    prev = [0] * (len(b_tokens) + 1)
    best_len = 0
    best_end_a = 0
    for i in range(1, len(a_tokens) + 1):
        cur = [0] * (len(b_tokens) + 1)
        for j in b_positions.get(a_tokens[i - 1], ()):
            jj = j + 1
            run = prev[jj - 1] + 1
            cur[jj] = run
            if run > best_len:
                best_len = run
                best_end_a = i
        prev = cur
    run_text = " ".join(a_tokens[best_end_a - best_len:best_end_a]) if best_len else ""
    return best_len, run_text


def check_draft_quality(a, eval_record):
    """Harper P4 content-discovery draft-quality gate. Parity with
    assertion_checks.check_draft_quality — see that function for the full
    field reference. Returns (passed, extra)."""
    import json as _json
    dimension = a.get("dimension", "voice")
    pattern = a.get("path", "")
    matches = list(IES_ROOT.glob(pattern))
    if a.get("newest_only") and len(matches) > 1:
        matches = [max(matches, key=lambda m: m.stat().st_mtime)]

    if not matches:
        outs = eval_record.get("outputs") or {}
        declared = outs.get("posts_drafted")
        try:
            declared = int(declared)
        except (TypeError, ValueError):
            declared = None
        if declared and declared > 0:
            return False, {"dimension": dimension, "reason": "draft manifest not found",
                           "posts_drafted": declared}
        return True, {"dimension": dimension, "posts": 0, "reason": "no drafts to check"}

    try:
        data = _json.loads(matches[0].read_text(errors="replace"))
    except Exception:
        return False, {"dimension": dimension, "reason": "manifest is not valid JSON"}
    if not isinstance(data, dict):
        return False, {"dimension": dimension, "reason": "manifest is not a JSON object"}
    posts = data.get("posts")
    if posts is None:
        return False, {"dimension": dimension, "reason": "manifest has no 'posts' list"}
    if not isinstance(posts, list):
        return False, {"dimension": dimension, "reason": "'posts' is not a list"}
    if not posts:
        return True, {"dimension": dimension, "posts": 0}

    failures = []
    for idx, post in enumerate(posts):
        if not isinstance(post, dict):
            failures.append(f"post[{idx}]: not an object")
            continue
        title = post.get("title") or f"post[{idx}]"
        if dimension == "voice":
            body = post.get("body") or ""
            source = post.get("source_text") or ""
            if not str(body).strip():
                failures.append(f"'{title}': body not recorded")
                continue
            if not str(source).strip():
                failures.append(f"'{title}': source_text not recorded (voice cannot be checked)")
                continue
            if not post.get("is_voice_original"):
                failures.append(f"'{title}': is_voice_original not true")
            max_run = int(a.get("max_verbatim_run", 12))
            run_len, run_text = _longest_common_run(
                _draft_word_tokens(body), _draft_word_tokens(source))
            if run_len > max_run:
                failures.append(
                    f"'{title}': {run_len}-word verbatim run from source "
                    f"(limit {max_run}): \"{run_text[:80]}\"")
            min_q = int(a.get("min_quote_words", 4))
            for quote in re.findall(r"[\"“]([^\"”]{1,400})[\"”]", str(body)):
                if len(_draft_word_tokens(quote)) >= min_q and _draft_norm(quote) not in _draft_norm(source):
                    failures.append(
                        f"'{title}': quoted text not present verbatim in source: \"{quote[:80]}\"")
        elif dimension == "image":
            img = str(post.get("feature_image") or "").strip()
            if not img:
                failures.append(f"'{title}': feature_image not set")
            elif not re.match(r"^https?://", img):
                failures.append(f"'{title}': feature_image is not an http(s) URL: {img!r}")
            if not post.get("image_landscape"):
                failures.append(f"'{title}': image_landscape not true")
            if post.get("geo_specific"):
                city = str(post.get("post_city") or "").strip()
                query = str(post.get("image_search_query") or "")
                if not city:
                    failures.append(f"'{title}': geo_specific but post_city not recorded")
                elif city.lower() not in query.lower():
                    failures.append(
                        f"'{title}': image_search_query does not name '{city}': {query!r}")
                if not post.get("image_geo_confirmed"):
                    failures.append(f"'{title}': image_geo_confirmed not true for geo-specific post")
        elif dimension == "links":
            related = post.get("related_published_post")
            if related:
                links = post.get("internal_links") or []
                norm_links = {_draft_url_norm(x) for x in links if isinstance(x, str)}
                if not links:
                    failures.append(f"'{title}': related post exists but no internal_links recorded")
                elif _draft_url_norm(related) not in norm_links:
                    failures.append(
                        f"'{title}': internal_links does not contain related post {related!r}")
        else:
            return False, {"dimension": dimension, "reason": f"unknown dimension {dimension!r}"}

    passed = not failures
    extra = {"dimension": dimension, "posts": len(posts)}
    if failures:
        extra["failures"] = failures[:10]
        extra["failure_count"] = len(failures)
    return passed, extra


def read_state_yaml(rel_path: str) -> dict:
    path = IES_ROOT / rel_path
    if not path.exists():
        return {}
    try:
        return yaml.safe_load(extract_frontmatter_block(path.read_text())) or {}
    except Exception as e:
        log_error(f"Failed to read {path}: {e}", TAG)
        return {}


def compute_version_hash(name: str) -> str | None:
    candidate = IES_ROOT / "workflows" / name / "workflow.md"
    if candidate.exists():
        return hashlib.sha256(candidate.read_bytes()).hexdigest()
    return None


def run_assertions(name: str, eval_record: dict) -> dict:
    """Same check-type set as post-tool-use.py's run_assertions, kept
    independent rather than imported to avoid coupling this hook's control
    flow to post-tool-use.py's larger session-index responsibilities."""
    structural = eval_record.get("assessment", {}).get("structural", {})
    assertion_file = ASSERTIONS_DIR / f"{name}.json"
    if not assertion_file.exists():
        return structural

    try:
        import json
        with open(assertion_file, "r") as f:
            assertion_data = json.load(f)
    except Exception as e:
        log_error(f"Failed to load {assertion_file}: {e}", TAG)
        return structural

    results = []
    for a in assertion_data.get("assertions", []):
        # Date-scoped assertions: resolve `{run_date}` in a declared
        # `date_path_template` (parity with assertion_checks.run_assertions) so
        # the check measures THIS run's output, not a historical file the bare
        # glob happens to match. Falls back to the bare path when no date is
        # derivable from the record.
        tpl = a.get("date_path_template")
        if tpl:
            _rd = eval_record.get("run_date")
            _rd = str(_rd)[:10] if _rd else str(eval_record.get("started", ""))[:10]
            if re.match(r"^\d{4}-\d{2}-\d{2}$", _rd):
                a = dict(a)
                a["path"] = tpl.replace("{run_date}", _rd)
        check = a.get("check")
        a_id = a.get("id", "unknown")
        description = a.get("description", "")
        passed = None
        try:
            if check == "file_exists":
                passed = len(list(IES_ROOT.glob(a.get("path", "")))) > 0
            elif check == "file_min_bytes":
                matches = list(IES_ROOT.glob(a.get("path", "")))
                passed = bool(matches) and all(m.stat().st_size >= a.get("min_bytes", 0) for m in matches)
            elif check == "file_contains":
                matches = list(IES_ROOT.glob(a.get("path", "")))
                passed = any(re.search(a.get("pattern", ""), m.read_text(errors="replace"), re.IGNORECASE) for m in matches) if matches else False
            elif check == "file_not_contains":
                matches = list(IES_ROOT.glob(a.get("path", "")))
                passed = True if not matches else not any(re.search(a.get("pattern", ""), m.read_text(errors="replace"), re.IGNORECASE) for m in matches)
            elif check == "yaml_field_equals":
                yaml_path = IES_ROOT / a.get("path", "")
                if yaml_path.exists():
                    data = yaml.safe_load(extract_frontmatter_block(yaml_path.read_text())) or {}
                    passed = data.get(a.get("field")) == a.get("value")
                else:
                    passed = False
            elif check == "yaml_field_not_equals":
                # Parity with assertion_checks.check_yaml_field_not_equals:
                # dotted field path; missing path == null (fails only when the
                # forbidden value is null — the "must be recorded" intent).
                yaml_matches = list(IES_ROOT.glob(a.get("path", "")))
                if not yaml_matches:
                    passed = False
                else:
                    try:
                        ydata = yaml.safe_load(
                            extract_frontmatter_block(yaml_matches[0].read_text(errors="replace"))
                        ) or {}
                    except Exception:
                        ydata = {}
                    nodes = _yaml_walk(ydata, a.get("field", ""))
                    value = a.get("value")
                    if not nodes:
                        passed = value is not None
                    else:
                        passed = all(node != value for node in nodes)
            elif check == "json_path_exists":
                # Field-path check (parity with assertion_checks.check_json_path_exists):
                # walk a dotted path, fanning out over `[]` array segments.
                import json as _json
                json_matches = list(IES_ROOT.glob(a.get("path", "")))
                field_path = a.get("field_path", "")
                min_matches = a.get("min_matches", 1)
                if not json_matches:
                    passed = False
                else:
                    try:
                        data = _json.loads(json_matches[0].read_text(errors="replace"))
                    except Exception:
                        data = None
                    if data is None:
                        passed = False
                    else:
                        nodes = [data]
                        for seg in [s for s in field_path.split(".") if s]:
                            is_list = seg.endswith("[]")
                            key = seg[:-2] if is_list else seg
                            nxt = []
                            for node in nodes:
                                if isinstance(node, dict) and key in node:
                                    val = node[key]
                                    if is_list:
                                        if isinstance(val, list):
                                            nxt.extend(val)
                                    else:
                                        nxt.append(val)
                            nodes = nxt
                            if not nodes:
                                break
                        passed = len(nodes) >= min_matches
            elif check == "step_owner_manifest":
                # Master J2 — parity with assertion_checks.check_step_owner_manifest.
                steps = eval_record.get("steps") or []
                if not steps:
                    passed = None
                else:
                    owners_map = _manifest_ownership(IES_ROOT)
                    boot_ranges = _manifest_boot_step_ranges(owners_map)
                    step_owners = _workflow_step_owner_map(IES_ROOT)
                    violations = 0
                    for s in steps:
                        if isinstance(s, dict):
                            nm = s.get("name") or ""
                            ow = normalize_agent_label(s.get("owning_agent"))
                        elif isinstance(s, str):
                            nm, ow = s, None
                        else:
                            continue
                        if not nm:
                            continue
                        expected = set()
                        base = nm if nm.endswith(".md") else f"{nm}.md"
                        for o in step_owners.get(base, set()):
                            if o and o in MANIFEST_AGENTS:
                                expected.add(o)
                        num = re.match(r"^step-(\d+(?:\.\d+)?)", nm)
                        if num:
                            n = float(num.group(1))
                            for agent, lo, hi in boot_ranges:
                                if lo <= n <= hi:
                                    expected.add(agent)
                        if expected and ow == "master" and "master" not in expected:
                            violations += 1
                    passed = violations == 0
            elif check == "grade_threshold":
                grading = (eval_record.get("assessment", {}) or {}).get("grading", {}) or {}
                grade = grading.get("grade")
                min_grade = str(a.get("min_grade", "B")).upper()
                if not grade:
                    passed = None
                else:
                    g = GRADE_ORDER.get(str(grade).upper())
                    passed = (g is not None) and g >= GRADE_ORDER.get(min_grade, 3)
            elif check == "yaml_field_pattern":
                yp_matches = list(IES_ROOT.glob(a.get("path", "")))
                if not yp_matches:
                    passed = False
                else:
                    try:
                        yp_data = yaml.safe_load(
                            extract_frontmatter_block(yp_matches[0].read_text(errors="replace"))
                        ) or {}
                    except Exception:
                        yp_data = {}
                    passed, _extra = check_yaml_field_pattern(a, yp_data)
            elif check in ("yaml_path_exists", "yaml_list_field_present", "yaml_list_counts_gte"):
                ymatches = list(IES_ROOT.glob(a.get("path", "")))
                if not ymatches:
                    passed = False
                else:
                    try:
                        ydata = yaml.safe_load(
                            extract_frontmatter_block(ymatches[0].read_text(errors="replace"))
                        ) or {}
                    except Exception:
                        ydata = {}
                    if check == "yaml_path_exists":
                        passed = len(_yaml_walk(ydata, a.get("field_path", ""))) >= a.get("min_matches", 1)
                    elif check == "yaml_list_field_present":
                        nodes = _yaml_walk(ydata, a.get("list_field", ""))
                        items = nodes[0] if nodes and isinstance(nodes[0], list) else []
                        if not items:
                            passed = None
                        else:
                            item_field = a.get("item_field", "")
                            missing = [
                                i for i, it in enumerate(items)
                                if not (isinstance(it, dict) and str(it.get(item_field, "")).strip())
                            ]
                            passed = len(missing) == 0
                    else:  # yaml_list_counts_gte
                        def _ylist(field):
                            if not field:
                                return []
                            nn = _yaml_walk(ydata, field)
                            return nn[0] if nn and isinstance(nn[0], list) else []
                        src = _ylist(a.get("source_field", ""))
                        acct = _ylist(a.get("accounted_field", ""))
                        skip = _ylist(a.get("skipped_field", ""))
                        passed = True if not src else (len(acct) + len(skip)) >= len(src)
            elif check == "draft_quality":
                passed, _extra = check_draft_quality(a, eval_record)
            elif check == "duration_lte":
                passed = eval_record.get("duration_seconds", float("inf")) <= a.get("max_duration_seconds", float("inf"))
            else:
                continue  # unknown/timing-only checks (e.g. tool_was_called) skipped here as elsewhere
        except Exception as e:
            log_error(f"Assertion {a_id} failed: {e}", TAG)
        results.append({"assertion": a_id, "description": description, "passed": passed})

    checked = len(results)
    passed_count = sum(1 for r in results if r.get("passed") is True)
    structural["assertion_results"] = results
    structural["assertions_checked"] = checked
    structural["assertions_passed"] = passed_count
    return structural


def finalize(eval_path: Path, eval_record: dict, state_data: dict, force_status: str | None = None, reason: str | None = None, transcript_path: str | None = None):
    now = datetime.now(timezone.utc)
    started = datetime.fromisoformat(eval_record["started"].replace("Z", "+00:00"))
    duration = round((now - started).total_seconds(), 2)

    state_status = state_data.get("status")

    # Aggregate totals from steps[] (populated by the existing post-tool-use.py
    # inline-step path) and subagents[] (populated by eval-agent-start/stop.py
    # when a subagent ran while this record was open).
    # Double-count guard: a step stamped with executed_by_agent_id was filled
    # by eval-agent-stop.py's partition backfill from that subagent's own
    # transcript, so its tokens are the SAME tokens the subagents[] rollup
    # carries. Count such steps only when the corresponding subagents[] entry
    # has no tokens (e.g. its stop hook was lost), never both.
    sub_ids_with_tokens = {
        s.get("agent_id") for s in eval_record.get("subagents", [])
        if s.get("tokens_input") is not None
    }
    def _step_counts(s):
        ex = s.get("executed_by_agent_id")
        return not (ex and ex in sub_ids_with_tokens)
    total_in = sum(s.get("tokens_input") or 0 for s in eval_record.get("steps", []) if _step_counts(s))
    total_in += sum(s.get("tokens_input") or 0 for s in eval_record.get("subagents", []))
    total_out = sum(s.get("tokens_output") or 0 for s in eval_record.get("steps", []) if _step_counts(s))
    total_out += sum(s.get("tokens_output") or 0 for s in eval_record.get("subagents", []))
    total_cost = sum(s.get("cost_usd") or 0 for s in eval_record.get("steps", []) if _step_counts(s))
    total_cost += sum(s.get("cost_usd") or 0 for s in eval_record.get("subagents", []))

    # Harness-reported subagent totals (from <task-notification> usage blocks)
    # ride alongside, never inside, the input/output sums — they are a
    # single aggregate with no input/output split.
    harness_total = sum(s.get("harness_tokens") or 0 for s in eval_record.get("subagents", []))
    if harness_total:
        eval_record["harness_tokens_total"] = harness_total

    eval_record["completed"] = now.isoformat().replace("+00:00", "Z")
    eval_record["duration_seconds"] = duration
    eval_record["total_tokens_input"] = total_in or None
    eval_record["total_tokens_output"] = total_out or None
    eval_record["total_cost_usd"] = round(total_cost, 6) if total_cost else None

    # Fully-loaded cost (2026-10-21, David's ruling): the record's cost must
    # include the PARENT session's own turns during the run window — the
    # orchestration cost, often the expensive part — as a labeled
    # parent_window component alongside the subagent components. Computed at
    # finalize because the window [started, completed] closes exactly here;
    # the transcript slice is stable afterwards. transcript_path comes from
    # the Stop payload when available; otherwise the module locates the
    # session transcript by the record's session_id.
    if _flc is not None:
        try:
            _flc.apply_to_record(eval_record, transcript_path=transcript_path)
        except Exception as e:
            log_error(f"parent-window cost computation failed: {e}", TAG)

    # Top-level model backstop (2026-10-23): the workflow record's model is
    # the orchestrating session's dominant model over the run window. If
    # eval-turn-start.py didn't capture one at open (or the run pre-dates
    # that capture), take it from the freshly computed parent_window. Never
    # overwrite an existing value — an open-time capture or a prior writer
    # wins over a re-derivation.
    if not eval_record.get("model"):
        pw_model = (eval_record.get("parent_window") or {}).get("model")
        if pw_model:
            eval_record["model"] = pw_model
            eval_record["model_source"] = "parent-window"

    tool_failures = eval_record.get("assessment", {}).get("mechanical", {}).get("tool_failures", 0)
    error_ids = eval_record.get("assessment", {}).get("mechanical", {}).get("error_ids", [])
    # mechanical.completed derivation (Stage 3 Phase 0): a run is mechanically
    # complete when state.yaml reached `complete` OR when every recorded step
    # is in a terminal status — the same step-evidence rule eval-agent-stop.py
    # uses (step_audit.steps_all_terminal). Previously this keyed on state.yaml
    # alone, so runs whose steps all finished but whose state completion was
    # never captured read as mechanical.completed=false.
    completed_ok = state_status == "complete" or bool(
        steps_all_terminal and steps_all_terminal(eval_record)
    )
    all_steps_finished = completed_ok

    if force_status:
        status = force_status
        completed_ok = False
        all_steps_finished = False
    elif error_ids:
        status = "failure"
    elif state_status in ("aborted", "blocked"):
        status = "aborted"
    elif not completed_ok:
        status = "aborted"
    elif tool_failures > 0:
        status = "partial"
    else:
        status = "success"

    eval_record["status"] = status

    # Every abort carries a reason. This path used to leave abort_reason null
    # on in-run aborts, which made aborted runs indistinguishable from
    # unverifiable no-ops in the Stage 4 success-rate baseline. Derive a
    # machine-readable code when the caller/state didn't supply one.
    if status == "aborted" and not eval_record["assessment"]["mechanical"].get("abort_reason"):
        if error_ids:
            abort_code = "error-logged"
        elif state_status in ("aborted", "blocked"):
            abort_code = f"state-{state_status}"
        else:
            abort_code = "unspecified"
        eval_record["assessment"]["mechanical"]["abort_reason"] = abort_code

    eval_record["assessment"]["mechanical"]["completed"] = completed_ok
    eval_record["assessment"]["mechanical"]["all_steps_finished"] = all_steps_finished
    eval_record["assessment"]["structural"] = run_assertions(eval_record["name"], eval_record)
    eval_record["version_hash"] = compute_version_hash(eval_record["name"])
    eval_record["monitoring"]["active"] = False
    if reason:
        eval_record["monitoring"]["close_reason"] = reason

    atomic_write_json(eval_path, eval_record)
    log_info(f"Closed turn-level eval record {eval_record['id']} for '{eval_record['name']}' — status={status}" + (f" ({reason})" if reason else ""), TAG)


STATE_COMPLETION_FIELDS = ("completed-at", "session-completed", "completed_at", "session_completed")
STALE_RECORD_ABORT_AFTER_HOURS = 2


def _parse_ts(value) -> "datetime | None":
    if not value or not isinstance(value, str):
        return None
    try:
        v = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(v)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def _state_genuinely_completed_after(state_data: dict, opened_at: "datetime | None") -> bool:
    """Is there a completion timestamp on state.yaml that is at/after this
    eval record's own `started` time?

    Root cause of a real incident: shutdown-cleanup's state.yaml has sat at
    `status: complete` since 2026-08-12 (completed-at that same date) —
    nearly two weeks stale. A spurious turn-level record opened on
    2026-08-27 (from a detect_workflow false-positive, see that fix in
    eval-turn-start.py) was checking ONLY `status in TERMINAL_STATUSES` with
    no regard for *when* that status was set, so it finalized as a fake
    "success" in 26.8 seconds — the very next Stop event after it opened,
    because the file just happened to already say "complete" from two weeks
    ago. `status: complete` is necessary but not sufficient evidence that
    THIS monitoring window's workflow run actually completed; the
    completion timestamp must fall inside the window this record opened."""
    if opened_at is None:
        return True  # can't compare — don't block finalization on this alone
    for field in STATE_COMPLETION_FIELDS:
        completed = _parse_ts(state_data.get(field))
        if completed is not None:
            return completed >= opened_at
    # No completion timestamp field at all on this workflow's state.yaml
    # schema — nothing to compare against, so don't manufacture a false
    # block. This only matters for workflows that do stamp a completion
    # time, which boot and shutdown-cleanup both do.
    return True


def try_finalize(eval_path: Path, transcript_path: str | None = None) -> bool:
    """Read one turn-level record, finalize it if its monitored state.yaml
    is terminal AND that terminal status was actually reached during this
    record's own open window (see _state_genuinely_completed_after).
    Returns True if it finalized (success or stale-abort), False if it's
    genuinely still in-progress and should stay open.

    transcript_path (the Stop payload's main-session transcript) is threaded
    through to finalize() for the parent-window cost component; the orphan
    sweep calls this without one and the module falls back to locating the
    transcript by the record's own session_id."""
    import json
    try:
        with open(eval_path, "r") as f:
            eval_record = json.load(f)
    except Exception as e:
        log_error(f"Failed to read {eval_path}: {e}", TAG)
        return False

    state_yaml_path = eval_record.get("monitoring", {}).get("state_yaml_path")
    if not state_yaml_path:
        return False

    state_data = read_state_yaml(state_yaml_path)
    opened_at = _parse_ts(eval_record.get("started"))

    if state_data.get("status") not in TERMINAL_STATUSES:
        log_info(f"'{eval_record['name']}' state.yaml still {state_data.get('status')!r} — leaving eval record open", TAG)
        return False

    if not _state_genuinely_completed_after(state_data, opened_at):
        # state.yaml says terminal, but from before this record even opened —
        # stale evidence, not proof this record's own run finished. Leave it
        # open unless it's been sitting long enough that it's clearly never
        # going to get real evidence (e.g. a false-trigger record that will
        # never see genuine new activity) — then close it as aborted, never
        # as a fabricated "success".
        age_hours = (datetime.now(timezone.utc) - opened_at).total_seconds() / 3600 if opened_at else 0
        if age_hours >= STALE_RECORD_ABORT_AFTER_HOURS:
            if not eval_record.get("steps") and not eval_record.get("subagents"):
                # Never accrued a single step or subagent — the workflow this
                # record guessed at (typically eval-turn-start.py's
                # 'boot-first-prompt-of-session' heuristic) never actually
                # ran this session. There is no real run here to record as
                # aborted, success, or failure — the record itself shouldn't
                # exist. Delete rather than finalize. Root cause: David
                # caught a live instance of this (a phantom 'boot' record
                # with zero activity, wrongly reported as a failed boot run)
                # and rejected even archiving it — see err-20260829T161711-3IPMKR.
                try:
                    eval_path.unlink()
                    log_info(f"Deleted phantom eval record {eval_record.get('id')} for '{eval_record['name']}' — "
                             f"no steps/subagents ever recorded, state.yaml completion predates open by {age_hours:.1f}h", TAG)
                except Exception as e:
                    log_error(f"Failed to delete phantom eval record {eval_path}: {e}", TAG)
                return True
            finalize(eval_path, eval_record, state_data, force_status="aborted",
                     reason=f"state.yaml's own completion timestamp predates this record's open time by {age_hours:.1f}h — likely a spurious open, not a real run",
                     transcript_path=transcript_path)
            return True
        log_info(f"'{eval_record['name']}' state.yaml is terminal but its completion timestamp predates this record's open — treating as stale, leaving open (age={age_hours:.1f}h)", TAG)
        return False

    finalize(eval_path, eval_record, state_data, transcript_path=transcript_path)
    return True


def sweep_orphaned_records(exclude: Path | None):
    """Self-heal pass: close out any OTHER open turn-level record whose
    monitored workflow has already reached a terminal state, regardless of
    session_id. Exists because session_id can legitimately (not just via
    the read-race fixed in hook_utils._read_session_index) resolve to two
    different values within one logical run — boot's own Session Index
    step appends a new memory/sessions/index.json entry partway through
    step-01, so a record opened before that append and a Stop event
    checked after it can disagree on session_id even with no bug involved.
    already_open_for_workflow() in eval-turn-start.py now dedupes by
    workflow name (not session_id) to stop this at open-time; this sweep is
    the belt-and-suspenders for anything that slips through anyway —
    without it, an orphan sits at status: in-progress forever, since no
    future Stop event's session_id would ever match it either.

    Second pass (2026-09-18): cowork-hook stubs. The turn-level branch above
    only matches records carrying monitoring.active (set by
    eval-turn-start.py). Cowork-hook stubs have no monitoring block at all,
    so an in-progress one previously sat open until the session-exit script
    swept it — and if grading ran first, it got graded as if it were a real
    run (eval-20260918T230528-J4EJWW was graded F mid-flight this way).
    A cowork-hook stub that is in-progress with zero steps AND zero
    subagents after 2h has no completion path left — delete it rather than
    finalize it, same precedent as the phantom-turn-record deletion above
    and close-open-evals.py (err-20260829T161711-3IPMKR: phantom records
    are deleted, not archived or marked)."""
    if not EVAL_RUNS_DIR.exists():
        return
    import json
    now = datetime.now(timezone.utc)
    for f in EVAL_RUNS_DIR.glob("eval-*.json"):
        if exclude is not None and f == exclude:
            continue
        try:
            with open(f, "r") as file:
                data = json.load(file)
        except Exception:
            continue
        if (
            data.get("type") == "workflow"
            and data.get("status") == "in-progress"
            and data.get("monitoring", {}).get("active")
        ):
            if try_finalize(f):
                log_info(f"Swept orphaned turn-level record {f.name} for '{data.get('name')}'", TAG)
            continue
        if (
            "cowork-hook" in data.get("tags", [])
            and data.get("status") == "in-progress"
            and not data.get("steps")
            and not data.get("subagents")
        ):
            started = _parse_ts(data.get("started"))
            age_hours = (now - started).total_seconds() / 3600 if started else float("inf")
            if age_hours >= STALE_RECORD_ABORT_AFTER_HOURS:
                try:
                    f.unlink()
                    log_info(
                        f"Deleted orphaned cowork-hook stub {f.name} for '{data.get('name')}' — "
                        f"in-progress with no steps/subagents after {age_hours:.1f}h, no completion path", TAG)
                except Exception as e:
                    log_error(f"Failed to delete orphaned cowork-hook stub {f}: {e}", TAG)


def main():
    payload = read_stdin()
    session_id = infer_session_id(payload)

    eval_path = find_open_turn_record(session_id)
    if eval_path:
        try_finalize(eval_path, transcript_path=payload.get("transcript_path"))

    sweep_orphaned_records(exclude=eval_path)

    # Phase F2 (2026-10-10): finalize pending skill runs captured by the
    # PostToolUse(Skill) hook (eval-skill-invoke.py). Hook-based capture
    # replaces the retired in-file SKILL COMPLETE sections.
    try:
        import skill_capture
        skill_capture.finalize(session_id)
        skill_capture.sweep_stale()
    except Exception as e:
        log_error(f"skill-capture finalize failed: {e}", TAG)

    if not eval_path:
        return  # no eval was opened under this Stop's session_id — no-op
                # for THIS session, per spec. The sweep above still ran, so
                # any other workflow's now-terminal orphan still gets closed.


if __name__ == "__main__":
    main()
