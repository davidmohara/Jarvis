#!/usr/bin/env python3
"""Run trigger evaluation for a skill description.

Tests whether a skill's description causes Claude to trigger (read the skill)
for a set of queries. Outputs results as JSON.
"""

import argparse
import json
import os
import select
import subprocess
import sys
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from scripts.utils import parse_skill_md


def find_project_root() -> Path:
    """Find the project root by walking up from cwd looking for .claude/.

    Mimics how Claude Code discovers its project root, so the command file
    we create ends up where claude -p will look for it.
    """
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return current


def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    project_root: str,
    model: str | None = None,
) -> dict:
    """Run a single query; return {"triggered": bool, "usage": {...}, ...}.

    Creates a command file in .claude/commands/ so it appears in Claude's
    available_skills list, then runs `claude -p` with the raw query.
    Uses --include-partial-messages to detect triggering early from
    stream events (content_block_start) rather than waiting for the
    full assistant message, which only arrives after tool execution.

    Token usage is captured from message_delta stream events, which carry
    each request's final usage and arrive BEFORE tool execution begins, so
    the capture survives the early-trigger return. The result event (end of
    session) carries authoritative totals plus cost; when the stream reaches
    it those overwrite the accumulated values and "complete" is True.
    """
    unique_id = uuid.uuid4().hex[:8]
    clean_name = f"{skill_name}-skill-{unique_id}"
    project_commands_dir = Path(project_root) / ".claude" / "commands"
    command_file = project_commands_dir / f"{clean_name}.md"

    try:
        project_commands_dir.mkdir(parents=True, exist_ok=True)
        # Use YAML block scalar to avoid breaking on quotes in description
        indented_desc = "\n  ".join(skill_description.split("\n"))
        command_content = (
            f"---\n"
            f"description: |\n"
            f"  {indented_desc}\n"
            f"---\n\n"
            f"# {skill_name}\n\n"
            f"This skill handles: {skill_description}\n"
        )
        command_file.write_text(command_content)

        cmd = [
            "claude",
            "-p", query,
            "--output-format", "stream-json",
            "--verbose",
            "--include-partial-messages",
        ]
        if model:
            cmd.extend(["--model", model])

        # Remove CLAUDECODE env var to allow nesting claude -p inside a
        # Claude Code session. The guard is for interactive terminal conflicts;
        # programmatic subprocess usage is safe.
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=project_root,
            env=env,
        )

        triggered = False
        decided = False  # trigger decision made; waiting for usage before exiting
        tool_ahead = False  # a tool_use block was seen: execution will follow
        saw_result = False
        cost_usd = None  # total_cost_usd from the result event, when reached
        model_usage = None  # per-model breakdown from the result event
        cost_basis = None  # CLI's own flag on how costUSD was computed
        judge_model = None
        requests_seen = 0
        usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_input_tokens": 0,
            "cache_creation_input_tokens": 0,
        }
        start_time = time.time()
        buffer = ""
        # Track state for stream event detection
        pending_tool_name = None
        accumulated_json = ""

        def record() -> dict:
            rec = {
                "triggered": triggered,
                "usage": dict(usage),
                "model": judge_model,
                "requests_seen": requests_seen,
                # True only when the end-of-session result event supplied
                # authoritative totals; otherwise usage is partial (sum of
                # message_delta events seen before the early exit).
                "usage_complete": saw_result,
                "elapsed": round(time.time() - start_time, 3),
            }
            if cost_usd is not None:
                rec["cost_usd"] = cost_usd
            if model_usage is not None:
                rec["model_usage"] = model_usage
            if cost_basis is not None:
                rec["cost_basis"] = cost_basis
            return rec

        def add_usage(u: dict) -> None:
            if not u:
                return
            for key in usage:
                usage[key] += int(u.get(key) or 0)

        try:
            while time.time() - start_time < timeout:
                if process.poll() is not None:
                    remaining = process.stdout.read()
                    if remaining:
                        buffer += remaining.decode("utf-8", errors="replace")
                    break

                ready, _, _ = select.select([process.stdout], [], [], 1.0)
                if not ready:
                    continue

                chunk = os.read(process.stdout.fileno(), 8192)
                if not chunk:
                    break
                buffer += chunk.decode("utf-8", errors="replace")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Early detection via stream events
                    if event.get("type") == "stream_event":
                        se = event.get("event", {})
                        se_type = se.get("type", "")

                        if se_type == "message_start":
                            msg = se.get("message", {})
                            if not judge_model:
                                judge_model = msg.get("model")

                        elif se_type == "content_block_start":
                            cb = se.get("content_block", {})
                            if cb.get("type") == "tool_use":
                                tool_ahead = True  # tool execution will follow
                                tool_name = cb.get("name", "")
                                if tool_name in ("Skill", "Read"):
                                    pending_tool_name = tool_name
                                    accumulated_json = ""
                                else:
                                    decided = True  # other tool used: not triggered

                        elif se_type == "content_block_delta" and pending_tool_name:
                            delta = se.get("delta", {})
                            if delta.get("type") == "input_json_delta":
                                accumulated_json += delta.get("partial_json", "")
                                if clean_name in accumulated_json:
                                    triggered = True
                                    decided = True

                        elif se_type == "message_delta":
                            # Final usage for the request that just ended.
                            # Arrives before tool execution, so it survives
                            # the early-trigger exit once we hold on for it.
                            add_usage(se.get("usage"))
                            requests_seen += 1
                            if decided and tool_ahead:
                                # Tool execution would follow; exit early
                                # with message_delta usage (partial).
                                return record()

                        elif se_type in ("content_block_stop", "message_stop"):
                            if pending_tool_name:
                                triggered = clean_name in accumulated_json
                                decided = True
                            if se_type == "message_stop" and not pending_tool_name:
                                decided = True

                    # Fallback: full assistant message
                    elif event.get("type") == "assistant":
                        # NOTE: this event arrives BEFORE message_delta in
                        # the stream; never return here without usage — the
                        # message_delta/result events right behind it carry it.
                        message = event.get("message", {})
                        for content_item in message.get("content", []):
                            if content_item.get("type") != "tool_use":
                                continue
                            tool_name = content_item.get("name", "")
                            tool_input = content_item.get("input", {})
                            if tool_name == "Skill" and clean_name in tool_input.get("skill", ""):
                                triggered = True
                            elif tool_name == "Read" and clean_name in tool_input.get("file_path", ""):
                                triggered = True
                        decided = True
                        if message.get("usage"):
                            add_usage(message["usage"])
                            requests_seen += 1

                    elif event.get("type") == "result":
                        # End of session: authoritative totals plus cost.
                        saw_result = True
                        if event.get("usage"):
                            usage.update({
                                key: int(event["usage"].get(key) or 0)
                                for key in usage
                            })
                        if event.get("total_cost_usd") is not None:
                            cost_usd = event["total_cost_usd"]
                        # Per-model breakdown (costUSD is a CLI-computed
                        # estimate; cost_basis records how it was derived,
                        # currently "unknown" under this routing).
                        mu = event.get("modelUsage")
                        if isinstance(mu, dict) and mu:
                            model_usage = {
                                m: {
                                    "cost_usd": stats.get("costUSD"),
                                    "input_tokens": stats.get("inputTokens"),
                                    "output_tokens": stats.get("outputTokens"),
                                    "cache_read_input_tokens": stats.get("cacheReadInputTokens"),
                                    "cache_creation_input_tokens": stats.get("cacheCreationInputTokens"),
                                    "provider": stats.get("provider"),
                                    "cost_basis": stats.get("costBasis"),
                                }
                                for m, stats in mu.items()
                                if isinstance(stats, dict)
                            }
                            bases = {v.get("cost_basis") for v in model_usage.values() if v.get("cost_basis")}
                            cost_basis = sorted(bases)[0] if len(bases) == 1 else (sorted(bases) if bases else None)
                        return record()
        finally:
            # Clean up process on any exit path (return, exception, timeout)
            if process.poll() is None:
                process.kill()
                process.wait()

        return record()
    finally:
        if command_file.exists():
            command_file.unlink()


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    project_root: Path,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
) -> dict:
    """Run the full eval set and return results."""
    results = []

    # Token usage aggregated across every judge run (records, or None when a
    # caller-supplied bool result or a failed run carries no usage).
    usage_totals = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_input_tokens": 0,
        "cache_creation_input_tokens": 0,
    }
    usage_runs_measured = 0
    usage_runs_total = 0
    usage_runs_complete = 0
    cost_usd_total = 0.0
    cost_runs = 0  # runs that reached the result event and reported cost
    cost_bases: set = set()
    per_model: dict[str, int] = {}
    per_model_usage: dict[str, dict] = {}  # costUSD/token totals summed per model
    per_run_records: list[dict] = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_info = {}
        for item in eval_set:
            for run_idx in range(runs_per_query):
                future = executor.submit(
                    run_single_query,
                    item["query"],
                    skill_name,
                    description,
                    timeout,
                    str(project_root),
                    model,
                )
                future_to_info[future] = (item, run_idx)

        query_triggers: dict[str, list[bool]] = {}
        query_items: dict[str, dict] = {}
        for future in as_completed(future_to_info):
            item, _ = future_to_info[future]
            query = item["query"]
            query_items[query] = item
            if query not in query_triggers:
                query_triggers[query] = []
            try:
                run_result = future.result()
            except Exception as e:
                print(f"Warning: query failed: {e}", file=sys.stderr)
                query_triggers[query].append(False)
                usage_runs_total += 1
                continue

            usage_runs_total += 1
            if isinstance(run_result, dict):
                query_triggers[query].append(run_result.get("triggered", False))
                per_run_records.append({
                    "query": query,
                    "triggered": run_result.get("triggered", False),
                    "usage": run_result.get("usage"),
                    "model": run_result.get("model"),
                    "usage_complete": run_result.get("usage_complete", False),
                    "elapsed": run_result.get("elapsed"),
                    **({"cost_usd": run_result["cost_usd"]}
                       if run_result.get("cost_usd") is not None else {}),
                    **({"model_usage": run_result["model_usage"]}
                       if run_result.get("model_usage") is not None else {}),
                    **({"cost_basis": run_result["cost_basis"]}
                       if run_result.get("cost_basis") is not None else {}),
                })
                u = run_result.get("usage")
                if u:
                    usage_runs_measured += 1
                    for key in usage_totals:
                        usage_totals[key] += int(u.get(key) or 0)
                if run_result.get("usage_complete"):
                    usage_runs_complete += 1
                m = run_result.get("model")
                if m:
                    per_model[m] = per_model.get(m, 0) + 1
                ru = run_result.get("cost_usd")
                if ru is not None:
                    cost_usd_total += float(ru)
                    cost_runs += 1
                if run_result.get("cost_basis"):
                    cost_bases.add(
                        run_result["cost_basis"]
                        if isinstance(run_result["cost_basis"], str)
                        else tuple(run_result["cost_basis"])
                    )
                # Sum per-model cost/token totals from result-event breakdowns.
                for m2, stats in (run_result.get("model_usage") or {}).items():
                    agg = per_model_usage.setdefault(m2, {
                        "cost_usd": 0.0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "cache_read_input_tokens": 0,
                        "cache_creation_input_tokens": 0,
                    })
                    agg["cost_usd"] += float(stats.get("cost_usd") or 0)
                    for k in ("input_tokens", "output_tokens",
                              "cache_read_input_tokens", "cache_creation_input_tokens"):
                        agg[k] += int(stats.get(k) or 0)
            else:
                # Backward compatibility: bare bool from an older caller.
                query_triggers[query].append(bool(run_result))

    for query, triggers in query_triggers.items():
        item = query_items[query]
        trigger_rate = sum(triggers) / len(triggers)
        should_trigger = item["should_trigger"]
        if should_trigger:
            did_pass = trigger_rate >= trigger_threshold
        else:
            did_pass = trigger_rate < trigger_threshold
        results.append({
            "query": query,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": did_pass,
        })

    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    return {
        "skill_name": skill_name,
        "description": description,
        "results": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        },
        "usage": {
            "runs": usage_runs_total,
            "runs_measured": usage_runs_measured,
            # Runs whose usage came from the end-of-session result event
            # (authoritative). Others are partial: summed from message_delta
            # events observed before the early-trigger exit.
            "runs_complete": usage_runs_complete,
            **usage_totals,
            "per_model": per_model,
            # Dollar cost summed from result-event total_cost_usd; only runs
            # that reached the result event contribute (cost_runs of runs).
            # costUSD is a CLI-computed estimate (cost_basis, currently
            # "unknown" under this routing); token counts are authoritative.
            "cost_usd": round(cost_usd_total, 6),
            "cost_runs": cost_runs,
            "cost_basis": (sorted(cost_bases)[0] if len(cost_bases) == 1
                           else (sorted(map(str, cost_bases)) if cost_bases else None)),
            "per_model_usage": per_model_usage,
        },
        "run_details": per_run_records,
    }


def main():
    parser = argparse.ArgumentParser(description="Run trigger evaluation for a skill description")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=10, help="Number of parallel workers")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per query in seconds")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--model", default=None, help="Model to use for claude -p (default: user's configured model)")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text())
    skill_path = Path(args.skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, original_description, content = parse_skill_md(skill_path)
    description = args.description or original_description
    project_root = find_project_root()

    if args.verbose:
        print(f"Evaluating: {description}", file=sys.stderr)

    output = run_eval(
        eval_set=eval_set,
        skill_name=name,
        description=description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        project_root=project_root,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
    )

    if args.verbose:
        summary = output["summary"]
        print(f"Results: {summary['passed']}/{summary['total']} passed", file=sys.stderr)
        for r in output["results"]:
            status = "PASS" if r["pass"] else "FAIL"
            rate_str = f"{r['triggers']}/{r['runs']}"
            print(f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
