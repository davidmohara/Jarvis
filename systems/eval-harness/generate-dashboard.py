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
    from datetime import timezone
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=period)

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
    """Generate the HTML dashboard with data baked in — no runtime fetches."""
    import json as _json
    records_json = _json.dumps(records, indent=2)

    # Extract unique values for filters
    agents = sorted(set(r.get('agent') for r in records if r.get('agent')))
    workflows = sorted(set(r.get('name') for r in records if r.get('name')))
    statuses = sorted(set(r.get('status') for r in records if r.get('status')))

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>IES Eval Harness Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.0/dist/chart.umd.js" integrity="sha384-iU8HYtnGQ8Cy4zl7gbNMOhsDTTKX02BTXptVP/vqAWIaTfM7isw76iyZCsjL2eVi" crossorigin="anonymous"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ color: #333; margin-bottom: 20px; }}
        .timestamp {{ color: #666; font-size: 14px; margin-bottom: 30px; }}
        .filters {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 30px; display: flex; gap: 15px; flex-wrap: wrap; align-items: center; }}
        .filters select {{ padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; background: white; }}
        .filters label {{ font-size: 14px; color: #374151; font-weight: 500; }}
        .filters button {{ padding: 8px 16px; background: #2563eb; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; }}
        .filters button:hover {{ background: #1d4ed8; }}
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
        .reliability-strip {{ display: inline-flex; gap: 2px; vertical-align: middle; }}
        .trial-dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; }}
        .trial-success {{ background: #059669; }}
        .trial-failure {{ background: #dc2626; }}
        .reliability-score {{ font-size: 11px; color: #555; margin-left: 4px; vertical-align: middle; }}
        .reliability-fail {{ color: #dc2626; font-weight: bold; }}
        .reliability-pass {{ color: #059669; font-weight: bold; }}
        .records-table tbody tr {{ cursor: pointer; }}
        .records-table tbody tr:hover {{ background: #f9fafb; }}
        .status-success {{ color: #059669; font-weight: bold; }}
        .status-failure {{ color: #dc2626; font-weight: bold; }}
        .status-aborted {{ color: #d97706; font-weight: bold; }}
        .grade {{ font-weight: bold; }}
        .grade-A {{ color: #059669; }}
        .grade-B {{ color: #2563eb; }}
        .grade-C {{ color: #d97706; }}
        .grade-D {{ color: #dc2626; }}
        .grade-F {{ color: #7c2d12; }}
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; }}
        .modal-content {{ background: white; margin: 5% auto; padding: 30px; border-radius: 8px; max-width: 800px; max-height: 80vh; overflow-y: auto; }}
        .modal-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
        .modal-close {{ background: none; border: none; font-size: 24px; cursor: pointer; }}
        .modal-section {{ margin-bottom: 20px; }}
        .modal-section h3 {{ color: #333; margin-bottom: 10px; font-size: 16px; }}
        .modal-section pre {{ background: #f3f4f6; padding: 15px; border-radius: 6px; overflow-x: auto; font-size: 12px; }}
        .regression-alert {{ background: #fef2f2; border: 1px solid #fecaca; padding: 15px; border-radius: 8px; margin-bottom: 20px; display: none; }}
        .regression-alert h3 {{ color: #dc2626; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>IES Eval Harness Dashboard</h1>
        <div class="timestamp">Generated: {datetime.now().isoformat()} | Records: {metrics.get('total', 0)}</div>

        <div class="filters">
            <label>Agent:
                <select id="agentFilter" onchange="filterRecords()">
                    <option value="">All Agents</option>
                    {"".join(f'<option value="{a}">{a}</option>' for a in agents)}
                </select>
            </label>
            <label>Workflow:
                <select id="workflowFilter" onchange="filterRecords()">
                    <option value="">All Workflows</option>
                    {"".join(f'<option value="{w}">{w}</option>' for w in workflows)}
                </select>
            </label>
            <label>Status:
                <select id="statusFilter" onchange="filterRecords()">
                    <option value="">All Statuses</option>
                    {"".join(f'<option value="{s}">{s}</option>' for s in statuses)}
                </select>
            </label>
            <button onclick="resetFilters()">Reset Filters</button>
        </div>

        <div class="regression-alert" id="regressionAlert">
            <h3>⚠️ Regression Detected</h3>
            <p id="regressionMessage"></p>
        </div>

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
                        <th>Reliability</th>
                        <th>Started</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Add records table with data attributes for filtering
    for record in records:
        status_class = f"status-{record.get('status', 'unknown')}"
        grade = record.get('assessment', {}).get('grading', {}).get('grade')
        grade_html = f'<span class="grade grade-{grade}">{grade}</span>' if grade else '-'
        duration = record.get('duration_seconds')
        duration_html = f"{duration:.1f}s" if duration else '-'
        started = record.get('started', '')[:19] if record.get('started') else '-'

        # Reliability column
        reliability = record.get('assessment', {}).get('reliability')
        if reliability:
            per_trial = reliability.get('per_trial', [])
            dots = ''.join(
                f'<span class="trial-dot trial-{"success" if t == "success" else "failure"}" title="{t}"></span>'
                for t in per_trial
            )
            pass_hat_k = reliability.get('pass_hat_k', 0)
            gate_result = reliability.get('gate_result', '')
            gate_class = 'reliability-pass' if gate_result == 'pass' else 'reliability-fail'
            gate_label = f'<span class="{gate_class}">{"✓" if gate_result == "pass" else "✗"}</span>' if gate_result else ''
            reliability_html = (
                f'<span class="reliability-strip">{dots}</span>'
                f'<span class="reliability-score">{pass_hat_k:.0%} {gate_label}</span>'
            )
        else:
            reliability_html = '-'

        html += f"""
                    <tr data-agent="{record.get('agent', '')}" data-workflow="{record.get('name', '')}" data-status="{record.get('status', '')}" onclick="showRecordDetails({records.index(record)})">
                        <td><code>{record.get('id', 'unknown')}</code></td>
                        <td>{record.get('name', 'unknown')}</td>
                        <td>{record.get('type', 'unknown')}</td>
                        <td class="{status_class}">{record.get('status', 'unknown')}</td>
                        <td>{duration_html}</td>
                        <td>{grade_html}</td>
                        <td>{reliability_html}</td>
                        <td>{started}</td>
                    </tr>
"""

    html += """
                </tbody>
            </table>
        </div>

        <!-- Modal for record details -->
        <div class="modal" id="recordModal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2 id="modalTitle">Eval Record Details</h2>
                    <button class="modal-close" onclick="closeModal()">&times;</button>
                </div>
                <div id="modalBody"></div>
            </div>
        </div>
    </div>

    <script>
        const records = """ + records_json + """;

        function filterRecords() {
            const agentFilter = document.getElementById('agentFilter').value;
            const workflowFilter = document.getElementById('workflowFilter').value;
            const statusFilter = document.getElementById('statusFilter').value;

            const rows = document.querySelectorAll('.records-table tbody tr');
            rows.forEach(row => {
                const agent = row.dataset.agent;
                const workflow = row.dataset.workflow;
                const status = row.dataset.status;

                const agentMatch = !agentFilter || agent === agentFilter;
                const workflowMatch = !workflowFilter || workflow === workflowFilter;
                const statusMatch = !statusFilter || status === statusFilter;

                row.style.display = (agentMatch && workflowMatch && statusMatch) ? '' : 'none';
            });
        }

        function resetFilters() {
            document.getElementById('agentFilter').value = '';
            document.getElementById('workflowFilter').value = '';
            document.getElementById('statusFilter').value = '';
            filterRecords();
        }

        function showRecordDetails(index) {
            const record = records[index];
            const modal = document.getElementById('recordModal');
            const title = document.getElementById('modalTitle');
            const body = document.getElementById('modalBody');

            title.textContent = `Eval Record: ${record.id}`;
            body.innerHTML = `
                <div class="modal-section">
                    <h3>Basic Info</h3>
                    <pre>${JSON.stringify({
                        id: record.id,
                        name: record.name,
                        type: record.type,
                        agent: record.agent,
                        status: record.status,
                        started: record.started,
                        duration_seconds: record.duration_seconds
                    }, null, 2)}</pre>
                </div>
                <div class="modal-section">
                    <h3>Tier 1: Mechanical</h3>
                    <pre>${JSON.stringify(record.assessment?.mechanical || {}, null, 2)}</pre>
                </div>
                <div class="modal-section">
                    <h3>Tier 2: Structural</h3>
                    <pre>${JSON.stringify(record.assessment?.structural || {}, null, 2)}</pre>
                </div>
                <div class="modal-section">
                    <h3>Tier 3: Grading</h3>
                    <pre>${JSON.stringify(record.assessment?.grading || {}, null, 2)}</pre>
                </div>
                ${record.assessment?.reliability ? `
                <div class="modal-section">
                    <h3>Multi-Trial Reliability</h3>
                    <pre>${JSON.stringify(record.assessment.reliability, null, 2)}</pre>
                </div>` : ''}
            `;

            modal.style.display = 'block';
        }

        function closeModal() {
            document.getElementById('recordModal').style.display = 'none';
        }

        // Close modal on outside click
        window.onclick = function(event) {
            const modal = document.getElementById('recordModal');
            if (event.target == modal) {
                closeModal();
            }
        }
    </script>
</body>
</html>
"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(html)
    print(f"Dashboard generated: {output_path}")


def update_artifact_records(eval_dir, artifact_path="systems/eval-harness/dashboard-artifact.html", exclude_ids=None):
    """Rebuild the RECORDS array in dashboard-artifact.html from current eval run files.

    Previously this function only updated a KNOWN_IDS list, which was never read by the
    render logic — leaving the artifact with stale hardcoded data.  Now it loads every
    closed record, serialises the full array, and regex-replaces the ALL_RECORDS (or
    legacy RECORDS) constant so the artifact always reflects the live corpus.
    """
    import re, json
    from datetime import datetime, timezone

    exclude_ids = set(exclude_ids or [])
    artifact = Path(artifact_path)
    if not artifact.exists():
        return

    runs = sorted(Path(eval_dir).glob("eval-*.json"))
    records = []
    for run_path in runs:
        try:
            with open(run_path) as fh:
                rec = json.load(fh)
        except Exception:
            continue
        if rec.get("status") == "in-progress":
            continue
        if rec.get("id") in exclude_ids:
            continue
        records.append(rec)

    records.sort(key=lambda r: r.get("started", ""), reverse=True)
    records_json = json.dumps(records, separators=(",", ":"))

    text = artifact.read_text()
    # Replace ALL_RECORDS = [...] or legacy RECORDS = [...]
    # Use a lambda replacement to avoid re.sub interpreting backslashes in the JSON
    replacement = f'const ALL_RECORDS = {records_json};'
    updated = re.sub(
        r'const (ALL_RECORDS|RECORDS) = \[.*?\];',
        lambda _: replacement,
        text,
        flags=re.DOTALL,
        count=1,
    )
    # Update the snapshot timestamp and record count in the subtitle line
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    updated = re.sub(
        r'Snapshot: [^&]+',
        f'Snapshot: {now_str}Z',
        updated,
    )
    updated = re.sub(
        r'<span id="rec-count">\d+</span>',
        f'<span id="rec-count">{len(records)}</span>',
        updated,
    )
    artifact.write_text(updated)
    print(f"dashboard-artifact.html RECORDS updated: {len(records)} records")


def main():
    args = parse_args()
    records = load_eval_records(args.eval_dir, args.recent, args.period, args.workflow, args.skill, args.agent)
    metrics = calculate_metrics(records)
    generate_html(records, metrics, args.output)
    update_artifact_records(args.eval_dir)


if __name__ == "__main__":
    main()
