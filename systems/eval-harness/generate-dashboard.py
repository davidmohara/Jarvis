#!/usr/bin/env python3
"""
Generate an HTML dashboard visualizing eval harness data.

The dashboard is self-contained (no external dependencies) and can be opened in any browser.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict


def parse_args():
    parser = argparse.ArgumentParser(description="Generate eval dashboard HTML")
    parser.add_argument("--eval-dir", required=True, help="Directory containing eval records")
    parser.add_argument("--output", default="systems/eval-harness/dashboard.html", help="Output HTML path")
    parser.add_argument("--recent", type=int, default=100, help="Number of recent records to include")
    parser.add_argument("--period", type=int, default=30, help="Include records from last N days")
    parser.add_argument("--workflow", help="Filter to specific workflow")
    parser.add_argument("--skill", help="Filter to specific skill")
    parser.add_argument("--agent", help="Filter to specific agent")
    return parser.parse_args()


def load_eval_records(eval_dir, recent, period, workflow, skill, agent):
    """Load and filter eval records."""
    eval_path = Path(eval_dir)
    if not eval_path.exists():
        return []

    records = []
    cutoff = datetime.now() - timedelta(days=period)

    for f in eval_path.glob("eval-*.json"):
        try:
            with open(f, "r") as file:
                data = json.load(file)

            # Apply filters
            if workflow and data.get("name") != workflow:
                continue
            if skill and data.get("name") != skill:
                continue
            if agent and data.get("agent") != agent:
                continue

            # Apply time filter
            started = data.get("started")
            if started:
                try:
                    started_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                    if started_dt < cutoff:
                        continue
                except ValueError:
                    pass

            records.append(data)
        except Exception:
            continue

    # Sort by started timestamp and limit
    records.sort(key=lambda x: x.get("started", ""), reverse=True)
    return records[:recent]


def calculate_metrics(records):
    """Calculate metrics across eval records."""
    if not records:
        return {}

    total = len(records)
    success = sum(1 for r in records if r.get("status") == "success")
    failure = sum(1 for r in records if r.get("status") == "failure")
    aborted = sum(1 for r in records if r.get("status") == "aborted")

    # Tier 1 metrics
    completed = sum(1 for r in records if r.get("assessment", {}).get("mechanical", {}).get("completed") is True)
    tool_failures = sum(r.get("assessment", {}).get("mechanical", {}).get("tool_failures", 0) for r in records)
    error_correlated = sum(1 for r in records if r.get("assessment", {}).get("mechanical", {}).get("error_ids"))

    # Tier 2 metrics
    assertions_checked = sum(r.get("assessment", {}).get("structural", {}).get("assertions_checked", 0) for r in records)
    assertions_passed = sum(r.get("assessment", {}).get("structural", {}).get("assertions_passed", 0) for r in records)
    assertion_pass_rate = (assertions_passed / assertions_checked * 100) if assertions_checked > 0 else 0

    # Tier 3 metrics
    graded = [r for r in records if r.get("assessment", {}).get("grading", {}).get("grade")]
    grade_counts = defaultdict(int)
    for r in graded:
        grade = r.get("assessment", {}).get("grading", {}).get("grade")
        grade_counts[grade] += 1

    # Performance metrics
    durations = [r.get("duration_seconds") for r in records if r.get("duration_seconds")]
    avg_duration = sum(durations) / len(durations) if durations else 0

    return {
        "total": total,
        "success": success,
        "failure": failure,
        "aborted": aborted,
        "success_rate": (success / total * 100) if total > 0 else 0,
        "tier1": {
            "completed": completed,
            "completion_rate": (completed / total * 100) if total > 0 else 0,
            "avg_tool_failures": tool_failures / total if total > 0 else 0,
            "error_correlated": error_correlated
        },
        "tier2": {
            "assertions_checked": assertions_checked,
            "assertions_passed": assertions_passed,
            "pass_rate": assertion_pass_rate
        },
        "tier3": {
            "graded": len(graded),
            "grade_rate": (len(graded) / total * 100) if total > 0 else 0,
            "grade_distribution": dict(grade_counts)
        },
        "performance": {
            "avg_duration": avg_duration
        }
    }


def generate_html(records, metrics, output_path):
    """Generate the HTML dashboard."""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>IES Eval Harness Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ color: #333; margin-bottom: 20px; }}
        .timestamp {{ color: #666; font-size: 14px; margin-bottom: 30px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-card h3 {{ color: #333; font-size: 14px; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .metric-card .value {{ font-size: 32px; font-weight: bold; color: #2563eb; }}
        .metric-card .sub {{ font-size: 12px; color: #666; margin-top: 5px; }}
        .tier-section {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .tier-section h2 {{ color: #333; margin-bottom: 15px; font-size: 18px; border-bottom: 2px solid #e5e5e5; padding-bottom: 10px; }}
        .tier-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .tier-metric {{ text-align: center; padding: 15px; background: #f9fafb; border-radius: 6px; }}
        .tier-metric .label {{ font-size: 12px; color: #666; margin-bottom: 5px; }}
        .tier-metric .val {{ font-size: 24px; font-weight: bold; color: #333; }}
        .records-table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .records-table th {{ background: #f3f4f6; padding: 12px; text-align: left; font-size: 12px; color: #666; text-transform: uppercase; }}
        .records-table td {{ padding: 12px; border-bottom: 1px solid #e5e5e5; font-size: 14px; }}
        .records-table tr:hover {{ background: #f9fafb; }}
        .status-success {{ color: #059669; font-weight: bold; }}
        .status-failure {{ color: #dc2626; font-weight: bold; }}
        .status-aborted {{ color: #d97706; font-weight: bold; }}
        .grade {{ font-weight: bold; }}
        .grade-A {{ color: #059669; }}
        .grade-B {{ color: #2563eb; }}
        .grade-C {{ color: #d97706; }}
        .grade-D {{ color: #dc2626; }}
        .grade-F {{ color: #7c2d12; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>IES Eval Harness Dashboard</h1>
        <div class="timestamp">Generated: {datetime.now().isoformat()} | Records: {metrics.get('total', 0)}</div>

        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Success Rate</h3>
                <div class="value">{metrics.get('success_rate', 0):.1f}%</div>
                <div class="sub">{metrics.get('success', 0)} / {metrics.get('total', 0)} successful</div>
            </div>
            <div class="metric-card">
                <h3>Failure Rate</h3>
                <div class="value">{metrics.get('failure', 0)}</div>
                <div class="sub">{(metrics.get('failure', 0) / metrics.get('total', 1) * 100):.1f}% of total</div>
            </div>
            <div class="metric-card">
                <h3>Avg Duration</h3>
                <div class="value">{metrics.get('performance', {}).get('avg_duration', 0):.1f}s</div>
                <div class="sub">Across all records</div>
            </div>
            <div class="metric-card">
                <h3>Assertion Pass Rate</h3>
                <div class="value">{metrics.get('tier2', {}).get('pass_rate', 0):.1f}%</div>
                <div class="sub">{metrics.get('tier2', {}).get('assertions_passed', 0)} / {metrics.get('tier2', {}).get('assertions_checked', 0)} passed</div>
            </div>
        </div>

        <div class="tier-section">
            <h2>Tier 1: Mechanical Assessment</h2>
            <div class="tier-grid">
                <div class="tier-metric">
                    <div class="label">Completion Rate</div>
                    <div class="val">{metrics.get('tier1', {}).get('completion_rate', 0):.1f}%</div>
                </div>
                <div class="tier-metric">
                    <div class="label">Avg Tool Failures</div>
                    <div class="val">{metrics.get('tier1', {}).get('avg_tool_failures', 0):.2f}</div>
                </div>
                <div class="tier-metric">
                    <div class="label">Error Correlated</div>
                    <div class="val">{metrics.get('tier1', {}).get('error_correlated', 0)}</div>
                </div>
            </div>
        </div>

        <div class="tier-section">
            <h2>Tier 2: Structural Assessment</h2>
            <div class="tier-grid">
                <div class="tier-metric">
                    <div class="label">Assertions Checked</div>
                    <div class="val">{metrics.get('tier2', {}).get('assertions_checked', 0)}</div>
                </div>
                <div class="tier-metric">
                    <div class="label">Assertions Passed</div>
                    <div class="val">{metrics.get('tier2', {}).get('assertions_passed', 0)}</div>
                </div>
                <div class="tier-metric">
                    <div class="label">Pass Rate</div>
                    <div class="val">{metrics.get('tier2', {}).get('pass_rate', 0):.1f}%</div>
                </div>
            </div>
        </div>

        <div class="tier-section">
            <h2>Tier 3: Grading</h2>
            <div class="tier-grid">
                <div class="tier-metric">
                    <div class="label">Graded Records</div>
                    <div class="val">{metrics.get('tier3', {}).get('graded', 0)}</div>
                </div>
"""

    # Add grade distribution
    grade_dist = metrics.get('tier3', {}).get('grade_distribution', {})
    for grade in ['A', 'B', 'C', 'D', 'F']:
        count = grade_dist.get(grade, 0)
        html += f"""
                <div class="tier-metric">
                    <div class="label">Grade {grade}</div>
                    <div class="val grade-{grade}">{count}</div>
                </div>
"""

    html += """
            </div>
        </div>

        <div class="tier-section">
            <h2>Recent Eval Records</h2>
            <table class="records-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Status</th>
                        <th>Duration</th>
                        <th>Grade</th>
                        <th>Started</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Add records table
    for record in records:
        status_class = f"status-{record.get('status', 'unknown')}"
        grade = record.get('assessment', {}).get('grading', {}).get('grade')
        grade_html = f'<span class="grade grade-{grade}">{grade}</span>' if grade else '-'
        duration = record.get('duration_seconds')
        duration_html = f"{duration:.1f}s" if duration else '-'
        started = record.get('started', '')[:19] if record.get('started') else '-'

        html += f"""
                    <tr>
                        <td><code>{record.get('id', 'unknown')}</code></td>
                        <td>{record.get('name', 'unknown')}</td>
                        <td>{record.get('type', 'unknown')}</td>
                        <td class="{status_class}">{record.get('status', 'unknown')}</td>
                        <td>{duration_html}</td>
                        <td>{grade_html}</td>
                        <td>{started}</td>
                    </tr>
"""

    html += """
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(html)
    print(f"Dashboard generated: {output_path}")


def main():
    args = parse_args()
    records = load_eval_records(args.eval_dir, args.recent, args.period, args.workflow, args.skill, args.agent)
    metrics = calculate_metrics(records)
    generate_html(records, metrics, args.output)


if __name__ == "__main__":
    main()
