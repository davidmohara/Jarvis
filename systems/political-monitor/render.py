#!/usr/bin/env python3
"""
Political news monitor - dashboard renderer.

Reads an analyzed run JSON (runs/YYYY-MM-DD.json) and emits a single
self-contained dashboard.html (inline CSS/JS, no external deps). Watchtower
style: header counts, shared-topic cards with a color-banded correlation
gauge and side-by-side L/R framing, two gap panels, weekly source suggestions,
and a source roster footer (active + muted).

Stdlib only - no pip install required.
Usage:
  python3 render.py                      # latest runs/*.json -> dashboard.html
  python3 render.py runs/2026-06-20.json # specific run
"""
import json, sys, html
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"


def esc(s):
    return html.escape(str(s or ""))


def pick_run():
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        p = Path(sys.argv[1])
        return p if p.is_absolute() else ROOT / p
    runs = sorted(RUNS.glob("*.json"))
    if not runs:
        sys.exit("No run JSON found in runs/. Run the analysis step first.")
    return runs[-1]


def corr_band(c):
    """Return (css_class, hex) for a 0-100 correlation score."""
    if c >= 85:
        return "c-vhi", "#1a9850"
    if c >= 65:
        return "c-hi", "#66bd63"
    if c >= 40:
        return "c-mid", "#fdae61"
    if c >= 20:
        return "c-lo", "#f46d43"
    return "c-vlo", "#d73027"


def relevance_badge(t):
    """Return HTML for a NEW / Day-N relevance badge, or '' if no relevance data."""
    days = t.get("days_seen")
    if days is None:
        return ""
    days = int(days)
    if days <= 1:
        klass, label = "r-new", "NEW"
    elif days == 2:
        klass, label = "r-d2", "DAY 2"
    else:
        klass, label = "r-d3", f"DAY {days}+" if days > 3 else "DAY 3"
    rel = t.get("relevance")
    title = esc(t.get("relevance_label", ""))
    rel_txt = f" {int(rel)}" if rel is not None else ""
    return f'<span class="relbadge {klass}" title="{title}">{label}{rel_txt}</span>'


def source_links(srcs):
    if not srcs:
        return ""
    out = []
    for s in srcs:
        url = esc(s.get("url"))
        name = esc(s.get("source"))
        if url:
            out.append(f'<a href="{url}" target="_blank" rel="noopener">{name}</a>')
        else:
            out.append(f"<span>{name}</span>")
    return '<div class="srcs">' + " &middot; ".join(out) + "</div>"


def render_shared(t):
    c = int(t.get("correlation", 0))
    klass, hexc = corr_band(c)
    return f"""
    <div class="card shared">
      <div class="card-head">
        <h3>{esc(t.get('title'))} {relevance_badge(t)}</h3>
        <div class="gauge {klass}">
          <div class="gauge-num">{c}</div>
          <div class="gauge-cap">correlation</div>
        </div>
      </div>
      <p class="summary">{esc(t.get('summary'))}</p>
      <div class="corr-label" style="border-left-color:{hexc}">{esc(t.get('correlation_label'))}</div>
      <div class="cols">
        <div class="col left">
          <div class="col-tag">LEFT</div>
          <p>{esc(t.get('left', {}).get('framing'))}</p>
          {source_links(t.get('left', {}).get('sources'))}
        </div>
        <div class="col right">
          <div class="col-tag">RIGHT</div>
          <p>{esc(t.get('right', {}).get('framing'))}</p>
          {source_links(t.get('right', {}).get('sources'))}
        </div>
      </div>
    </div>"""


def render_gap_item(it, side):
    return f"""
      <div class="card gap {side}">
        <h4>{esc(it.get('title'))} {relevance_badge(it)}</h4>
        <p class="summary">{esc(it.get('summary'))}</p>
        {source_links(it.get('sources'))}
      </div>"""


def render_suggestion(s):
    return f"""
      <div class="sugg lean-{esc(s.get('lean'))}">
        <div class="sugg-name">{esc(s.get('name'))} <span class="lean-tag">{esc(s.get('lean'))}</span></div>
        <div class="sugg-why">{esc(s.get('rationale'))}</div>
      </div>"""


def validate_run(d, run_path):
    """Hard schema check — aborts render with a clear error if any required field is missing or wrong type.
    This runs on every invocation. It is not optional and cannot be skipped.
    Required shape documented here is the single source of truth for what the run JSON must contain."""
    errors = []

    # Top-level required fields
    for field in ("date", "generated", "window_hours", "counts", "sources_used",
                  "sources_muted", "shared_topics", "gap_left", "gap_right"):
        if field not in d:
            errors.append(f"Missing top-level field: '{field}'")

    # counts sub-schema
    counts = d.get("counts", {})
    for key in ("total_items", "shared_topics", "gap_left", "gap_right"):
        if key not in counts:
            errors.append(f"counts missing required key: '{key}' (got keys: {list(counts.keys())})")
        elif not isinstance(counts[key], int):
            errors.append(f"counts.{key} must be int, got {type(counts[key]).__name__}")
    by_lean = counts.get("by_lean", None)
    if by_lean is None:
        errors.append("counts missing required key: 'by_lean' (must be object with left/right/center int values)")
    else:
        for lean in ("left", "right", "center"):
            if lean not in by_lean:
                errors.append(f"counts.by_lean missing key: '{lean}'")
            elif not isinstance(by_lean[lean], int):
                errors.append(f"counts.by_lean.{lean} must be int, got {type(by_lean[lean]).__name__}")

    # shared_topics items
    for i, t in enumerate(d.get("shared_topics", [])):
        for key in ("topic_key", "title", "summary", "left", "right", "correlation", "correlation_label",
                    "relevance", "relevance_label", "days_seen"):
            if key not in t:
                errors.append(f"shared_topics[{i}] ('{t.get('title', '?')}') missing field: '{key}'")
        for side in ("left", "right"):
            side_obj = t.get(side, {})
            for key in ("framing", "sources"):
                if key not in side_obj:
                    errors.append(f"shared_topics[{i}].{side} missing field: '{key}'")

    # gap items
    for section in ("gap_left", "gap_right"):
        for i, t in enumerate(d.get(section, [])):
            for key in ("topic_key", "title", "summary", "sources", "relevance", "relevance_label", "days_seen"):
                if key not in t:
                    errors.append(f"{section}[{i}] ('{t.get('title', '?')}') missing field: '{key}'")

    if errors:
        print(f"\n❌ SCHEMA VALIDATION FAILED for {run_path.name} — render aborted.\n")
        for e in errors:
            print(f"  • {e}")
        print(f"\nFix the run JSON before re-running render.py.\n")
        sys.exit(1)

    print(f"✓ Schema validation passed ({len(d.get('shared_topics',[]))} shared, "
          f"{len(d.get('gap_left',[]))} gap_left, {len(d.get('gap_right',[]))} gap_right, "
          f"items={counts.get('total_items')}, "
          f"left={counts.get('by_lean',{}).get('left')}, right={counts.get('by_lean',{}).get('right')}, "
          f"center={counts.get('by_lean',{}).get('center')})")


def main():
    run_path = pick_run()
    d = json.loads(run_path.read_text())
    validate_run(d, run_path)
    counts = d.get("counts", {})
    by_lean = counts.get("by_lean", {})

    gen = d.get("generated", "")
    try:
        gen_disp = datetime.fromisoformat(gen.replace("Z", "+00:00")).strftime("%b %d, %Y %H:%M UTC")
    except Exception:
        gen_disp = gen

    def by_correlation(items):
        """Shared topics: highest correlation (most aligned) at top."""
        return sorted(items, key=lambda t: t.get("correlation", 0), reverse=True)

    def by_relevance(items):
        """Gap topics: newest / freshest at top."""
        return sorted(items, key=lambda t: t.get("relevance", 100), reverse=True)

    shared_html = "\n".join(render_shared(t) for t in by_correlation(d.get("shared_topics", []))) or \
        '<p class="empty">No topics covered by both left and right in this window.</p>'
    gap_l = "\n".join(render_gap_item(i, "left") for i in by_relevance(d.get("gap_left", []))) or \
        '<p class="empty">No left-only topics in this window.</p>'
    gap_r = "\n".join(render_gap_item(i, "right") for i in by_relevance(d.get("gap_right", []))) or \
        '<p class="empty">No right-only topics in this window.</p>'

    suggestions = d.get("suggestions", [])
    if suggestions:
        sugg_block = f"""
    <section>
      <h2>Suggested Sources <span class="sub">weekly &middot; reply to Jarvis "add X" or "skip X"</span></h2>
      <div class="sugg-grid">
        {''.join(render_suggestion(s) for s in suggestions)}
      </div>
    </section>"""
    else:
        sugg_block = ""

    muted = d.get("sources_muted", [])
    muted_note = ""
    if muted:
        names = ", ".join(esc(m.get("name")) for m in muted)
        muted_note = f'<div class="muted-note">Muted (not machine-readable to our crawler): {names}</div>'

    muted_rows = "".join(
        f'<li class="lean-{esc(m.get("lean"))} muted">{esc(m.get("name"))} '
        f'<span class="lean-tag">{esc(m.get("lean"))}</span> '
        f'<span class="why">{esc(m.get("reason"))}</span></li>'
        for m in muted
    )
    used_rows = "".join(
        f'<li class="src-used"><code>{esc(s)}</code></li>' for s in d.get("sources_used", [])
    )

    htmlout = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Political Monitor &mdash; {esc(gen_disp)}</title>
<style>
  :root {{
    --bg:#0e1116; --panel:#161b22; --panel2:#1c232d; --line:#2b333d;
    --ink:#e6edf3; --dim:#9aa7b4; --left:#4f8ef7; --right:#f7574f; --center:#9aa7b4;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
    font:15px/1.55 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif; }}
  a {{ color:#79b8ff; text-decoration:none; }} a:hover {{ text-decoration:underline; }}
  .wrap {{ max-width:1080px; margin:0 auto; padding:28px 20px 60px; }}
  header.top {{ border-bottom:1px solid var(--line); padding-bottom:16px; margin-bottom:8px; }}
  header.top h1 {{ margin:0 0 4px; font-size:26px; letter-spacing:.3px; }}
  .meta {{ color:var(--dim); font-size:13px; }}
  .counts {{ display:flex; flex-wrap:wrap; gap:10px; margin:16px 0 6px; }}
  .stat {{ background:var(--panel); border:1px solid var(--line); border-radius:8px;
    padding:8px 14px; min-width:96px; }}
  .stat .n {{ font-size:22px; font-weight:700; }}
  .stat .l {{ font-size:11px; color:var(--dim); text-transform:uppercase; letter-spacing:.6px; }}
  .stat.left .n {{ color:var(--left); }} .stat.right .n {{ color:var(--right); }}
  .muted-note {{ color:var(--dim); font-size:12px; margin-top:8px; font-style:italic; }}
  section {{ margin-top:34px; }}
  section > h2 {{ font-size:18px; border-left:4px solid #58a6ff; padding-left:10px; margin:0 0 16px; }}
  section > h2 .sub {{ font-weight:400; font-size:12px; color:var(--dim); margin-left:8px; }}
  .card {{ background:var(--panel); border:1px solid var(--line); border-radius:12px;
    padding:18px 20px; margin-bottom:18px; }}
  .card.shared .card-head {{ display:flex; justify-content:space-between; align-items:flex-start; gap:16px; }}
  .card.shared h3 {{ margin:0; font-size:18px; }}
  .summary {{ color:#cdd9e5; margin:10px 0; }}
  .gauge {{ text-align:center; border-radius:10px; padding:8px 14px; min-width:84px; color:#0b0e12; }}
  .gauge-num {{ font-size:30px; font-weight:800; line-height:1; }}
  .gauge-cap {{ font-size:10px; text-transform:uppercase; letter-spacing:.7px; opacity:.85; }}
  .c-vhi {{ background:#1a9850; }} .c-hi {{ background:#66bd63; }} .c-mid {{ background:#fdae61; }}
  .c-lo {{ background:#f46d43; color:#fff; }} .c-vlo {{ background:#d73027; color:#fff; }}
  .relbadge {{ display:inline-block; font-size:10px; font-weight:700; letter-spacing:.5px;
    border-radius:5px; padding:2px 7px; vertical-align:middle; margin-left:6px; color:#0b0e12; }}
  .relbadge.r-new {{ background:#1a9850; color:#fff; }}
  .relbadge.r-d2 {{ background:#fdae61; }}
  .relbadge.r-d3 {{ background:#d73027; color:#fff; }}
  .corr-label {{ background:var(--panel2); border-left:4px solid #888; padding:8px 12px;
    border-radius:0 6px 6px 0; font-size:14px; margin:6px 0 16px; color:#dbe4ec; }}
  .cols {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
  .col {{ background:var(--panel2); border-radius:8px; padding:12px 14px; border-top:3px solid var(--line); }}
  .col.left {{ border-top-color:var(--left); }} .col.right {{ border-top-color:var(--right); }}
  .col-tag {{ font-size:11px; font-weight:700; letter-spacing:1px; color:var(--dim); margin-bottom:6px; }}
  .col.left .col-tag {{ color:var(--left); }} .col.right .col-tag {{ color:var(--right); }}
  .col p {{ margin:0 0 8px; font-size:14px; }}
  .srcs {{ font-size:12px; color:var(--dim); }}
  .gap-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; align-items:start; }}
  .gap-grid > div {{ min-width:0; }}
  .gap-grid h3 {{ font-size:14px; margin:0 0 12px; text-transform:uppercase; letter-spacing:.6px; }}
  .gap-grid .gcol.left h3 {{ color:var(--left); }} .gap-grid .gcol.right h3 {{ color:var(--right); }}
  .card.gap {{ padding:12px 14px; }} .card.gap h4 {{ margin:0 0 6px; font-size:15px; }}
  .card.gap.left {{ border-left:3px solid var(--left); }}
  .card.gap.right {{ border-left:3px solid var(--right); }}
  .empty {{ color:var(--dim); font-style:italic; }}
  .sugg-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:14px; }}
  .sugg {{ background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:14px; }}
  .sugg-name {{ font-weight:700; margin-bottom:4px; }}
  .sugg-why {{ font-size:13px; color:var(--dim); }}
  .lean-tag {{ font-size:10px; text-transform:uppercase; letter-spacing:.6px; border:1px solid var(--line);
    border-radius:4px; padding:1px 6px; color:var(--dim); margin-left:4px; }}
  .roster ul {{ list-style:none; padding:0; display:flex; flex-wrap:wrap; gap:8px; }}
  .roster li {{ background:var(--panel); border:1px solid var(--line); border-radius:6px; padding:5px 10px; font-size:13px; }}
  .roster li.muted {{ opacity:.7; }}
  .roster li.lean-left {{ border-left:3px solid var(--left); }}
  .roster li.lean-right {{ border-left:3px solid var(--right); }}
  .roster li.lean-center {{ border-left:3px solid var(--center); }}
  .roster .why {{ color:var(--dim); font-size:11px; }}
  code {{ background:var(--panel2); padding:1px 6px; border-radius:4px; }}
  footer {{ margin-top:40px; color:var(--dim); font-size:12px; border-top:1px solid var(--line); padding-top:14px; }}
  @media (max-width:680px) {{ .cols, .gap-grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <h1>Political Monitor</h1>
    <div class="meta">Generated {esc(gen_disp)} &middot; window {esc(d.get('window_hours'))}h &middot;
      neutral / descriptive &middot; correlation = left-vs-right framing distance</div>
    <div class="counts">
      <div class="stat"><div class="n">{counts.get('total_items', 0)}</div><div class="l">Items</div></div>
      <div class="stat left"><div class="n">{by_lean.get('left', 0)}</div><div class="l">Left</div></div>
      <div class="stat right"><div class="n">{by_lean.get('right', 0)}</div><div class="l">Right</div></div>
      <div class="stat"><div class="n">{by_lean.get('center', 0)}</div><div class="l">Center</div></div>
      <div class="stat"><div class="n">{counts.get('shared_topics', 0)}</div><div class="l">Shared</div></div>
      <div class="stat"><div class="n">{counts.get('gap_left', 0)}</div><div class="l">Left-only</div></div>
      <div class="stat"><div class="n">{counts.get('gap_right', 0)}</div><div class="l">Right-only</div></div>
    </div>
    {muted_note}
  </header>

  <section>
    <h2>Shared Topics <span class="sub">covered by both sides &middot; side-by-side framing</span></h2>
    {shared_html}
  </section>

  <section>
    <h2>Gap Topics <span class="sub">covered by only one side</span></h2>
    <div class="gap-grid">
      <div class="gcol left"><h3>Only the Left is covering</h3>{gap_l}</div>
      <div class="gcol right"><h3>Only the Right is covering</h3>{gap_r}</div>
    </div>
  </section>
{sugg_block}
  <section class="roster">
    <h2>Source Roster</h2>
    <ul>{used_rows}{muted_rows}</ul>
  </section>

  <footer>
    Public news only &middot; no Protected/Confidential data. Analysis is descriptive and does not
    adjudicate which side is correct. Fetched via WebSearch (allowed_domains). Blocked outlets are
    shown muted, not scraped.
  </footer>
</div>
</body>
</html>"""

    out = ROOT / "dashboard.html"
    out.write_text(htmlout)
    print(f"Wrote {out} from {run_path.name}")


if __name__ == "__main__":
    main()
