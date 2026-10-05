#!/usr/bin/env python3
"""Live scoreboard dashboard for the Amazing Race monitor.

A small localhost server that reads the state files on every request —
every sweep's writes show up live; nothing is pre-rendered. David keeps
the tab open for the whole event.

Usage:
  dashboard_server.py [--port 7430]        # run in foreground
  dashboard_server.py --stop              # stop a running daemon (via pid file)
  dashboard_server.py --status            # is it running?

Endpoints:
  /           — dashboard page (auto-refreshes every 5s)
  /api/state  — scoring.compute_state() JSON
  /media/...  — posted media + extracted video frames
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import scoring
import apply_ruling

IES_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DATA_DIR = os.path.join(IES_ROOT, "data", "amazing-race")
PID_PATH = os.path.join(DATA_DIR, "dashboard.pid")

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Amazing Race — Live Scoreboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root { color-scheme: light dark; }
  body { font-family: -apple-system, "Segoe UI", system-ui, sans-serif; margin: 0; background: #111; color: #eee; }
  .wrap { max-width: 1100px; margin: 0 auto; padding: 16px; }
  h1 { font-size: 1.3rem; margin: 0; }
  .sub { color: #999; font-size: 0.8rem; margin-bottom: 12px; }
  table { border-collapse: collapse; width: 100%; margin-bottom: 24px; font-size: 0.9rem; }
  th, td { border-bottom: 1px solid #333; padding: 6px 8px; text-align: left; }
  th { color: #999; font-weight: 600; }
  td.points { text-align: right; font-variant-numeric: tabular-nums; }
  tr.pending td { color: #e6b450; }
  .flag { border-left: 3px solid #e6484f; padding: 6px 10px; margin: 6px 0; background: #1c1c1c; border-radius: 4px; font-size: 0.85rem; }
  .flag.bonus { border-left-color: #46a758; }
  .flag.ruled { border-left-color: #666; opacity: 0.7; }
  .flag a { color: #6db3f2; }
  .dim { color: #999; font-size: 0.8rem; }
  .qid { font-family: ui-monospace, monospace; }
  h2 { font-size: 1rem; margin: 24px 0 8px; }
  button { background: #2d2d2d; color: #eee; border: 1px solid #555; border-radius: 5px; padding: 4px 12px; font-size: 0.8rem; cursor: pointer; margin-right: 6px; }
  button:hover { border-color: #6db3f2; }
  button.approve { border-color: #46a758; color: #7ee08f; }
  button.reject { border-color: #e6484f; color: #ff8a8e; }
  button.ruled { border-color: #333; color: #555; cursor: default; }
  .ruledtag { color: #7ee08f; font-size: 0.75rem; margin-left: 8px; }
  img { max-width: 180px; border-radius: 4px; margin: 2px; }
  #refresh { color: #666; font-size: 0.75rem; }
</style>
</head>
<body>
<div class="wrap">
  <h1>Amazing Race — Live Scoreboard</h1>
  <div class="sub" id="meta"></div>
  <div id="content">Loading…</div>
  <div id="refresh"></div>
</div>
<script>
let lastTs = null;
let lastState = null;
async function rule(fid, ruling) {
  try {
    const r = await (await fetch('/api/rule', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({flag_id: fid, ruling})})).json();
    if (!r.ok) alert(r.error || 'ruling failed');
    tick();
  } catch (e) { alert('ruling failed: ' + e); }
}
async function ignorePost(pid) {
  try {
    const r = await (await fetch('/api/ignore', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({post_id: pid})})).json();
    if (!r.ok) alert(r.error || 'ignore failed');
    tick();
  } catch (e) { alert('ignore failed: ' + e); }
}
async function classify(pid) {
  const team = document.getElementById('t_' + pid).value;
  const quest = document.getElementById('q_' + pid).value;
  if (!team || !quest) { alert('Enter both team and quest numbers'); return; }
  try {
    const r = await (await fetch('/api/classify', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({post_id: pid, team, quest})})).json();
    if (!r.ok) alert(r.error || 'classify failed');
    tick();
  } catch (e) { alert('classify failed: ' + e); }
}
async function tick() {
  try {
    const s = await (await fetch('/api/state')).json();
    let h = '<table><tr><th>Team</th><th>Total</th><th>Quests (points)</th><th>Flags</th></tr>';
    for (const [team, st] of Object.entries(s.standings)) {
      const q = Object.entries(st.quests).map(([q,v]) => `Q${q}: ${v.points}`).join(' · ') || '—';
      h += `<tr class="${st.pending_flags ? 'pending' : ''}"><td>Team ${team}</td><td class="points"><b>${st.total}</b></td><td>${q}</td><td>${st.pending_flags || ''}</td></tr>`;
    }
    h += '</table>';
    const fmtF = (f, buttons) => {
      const q = f.quest == null ? (f.assumed_quest ? 'Q' + f.assumed_quest + ' (assumed)' : 'Q?') : 'Q' + f.quest;
      const t = f.team == null ? (f.assumed_team ? 'Team ' + f.assumed_team + ' (roster)' : 'Team ?') : 'Team ' + f.team;
      let c = `<div class="flag"><b>${t} · ${q}</b> · <span class="qid">${f.flag_id || ''}</span> · ${f.verdict || ''}`;
      if (f.link) c += ` · <a href="${f.link}" target="_blank">Open in Teams</a>`;
      c += '<br>';
      if (f.thumb) c += `<img src="/${f.thumb.replace(/^\\/*/, '')}">`;
      if (f.author || f.text) c += `<br><span class="dim">${(f.author || '')}${f.text ? ': ' + f.text : ''}</span>`;
      if (f.reasons && f.reasons.length) c += `<br> ${(f.reasons.join('; '))}`;
      if (buttons && f.flag_id) {
        if (f.ruled_at) {
          c += `<span class="ruledtag">ruled: ${f.ruling}${f.ruled_points != null ? ' → ' + f.ruled_points + ' pts' : ''}</span>`;
        } else {
          c += `<br><button class="approve" onclick="rule('${f.flag_id}','ok')">Approve (${f.approve_points != null ? f.approve_points : '?'} pts)</button>` +
               `<button class="reject" onclick="rule('${f.flag_id}','reject')">Reject</button>`;
        }
      }
      c += '</div>';
      return c;
    };
    if (s.pending_rulings && s.pending_rulings.length) {
      h += '<h2>Flags awaiting ruling — click to score</h2>';
      for (const f of s.pending_rulings) h += fmtF(f, true);
    }
    if (s.bonus_candidates && s.bonus_candidates.length) {
      h += '<h2>Bonus candidates (for Dawn)</h2>';
      for (const f of s.bonus_candidates) h += fmtF(f, false).replace('class="flag"', 'class="flag bonus"');
    }
    if (s.unidentified && s.unidentified.length) {
      h += '<h2>Unidentified posts — enter team + quest to classify and score</h2>';
      for (const u of s.unidentified) {
        let c = fmtF({...u, verdict: 'unidentified'}, false);
        c = c.slice(0, c.length - 6) +
          `<br><input id="t_${u.post_id}" type="number" placeholder="Team #" min="1" style="width:70px;background:#222;color:#eee;border:1px solid #555;border-radius:4px;padding:3px 6px">` +
          `<input id="q_${u.post_id}" type="number" placeholder="Quest #" min="1" max="16" style="width:70px;background:#222;color:#eee;border:1px solid #555;border-radius:4px;padding:3px 6px;margin-left:6px">` +
          `<button class="approve" onclick="classify('${u.post_id}')">Classify & score full points</button>` +
          `<button class="reject" onclick="ignorePost('${u.post_id}')">Ignore</button></div>`;
        h += c;
      }
    }
    const j = JSON.stringify(s);
    const typing = document.activeElement && document.activeElement.tagName === 'INPUT';
    if (j !== lastState && !typing) {
      document.getElementById('content').innerHTML = h;
      lastState = j;
    }
    document.getElementById('meta').textContent =
      `${s.counts.posts} posts · ${s.counts.flags} flags · ${s.counts.pending_rulings} pending rulings · ${s.counts.bonus_candidates} bonus candidates`;
    lastTs = new Date().toLocaleTimeString();
    document.getElementById('refresh').textContent = 'Auto-refreshing every 5s · last update ' + lastTs;
  } catch (e) {
    document.getElementById('refresh').textContent = 'refresh error: ' + e;
  }
}
tick();
setInterval(tick, 5000);
</script>
</body>
</html>
"""


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=os.path.join(IES_ROOT, "data", "amazing-race"), **kw)

    def log_message(self, *a):
        pass  # quiet daemon

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            body = PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/state":
            try:
                body = json.dumps(scoring.compute_state()).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                body = json.dumps({"error": str(e)}).encode()
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        elif self.path == "/healthz":
            self.send_response(200)
            self.end_headers()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/ignore":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length).decode("utf-8"))
                result = apply_ruling.ignore_post(body.get("post_id"))
                code = 200 if result.get("ok") else 400
            except Exception as e:
                result, code = {"ok": False, "error": str(e)}, 400
        elif self.path == "/api/classify":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length).decode("utf-8"))
                result = apply_ruling.classify(body.get("post_id"), body.get("team"),
                                               body.get("quest"))
                code = 200 if result.get("ok") else 400
            except Exception as e:
                result, code = {"ok": False, "error": str(e)}, 400
        elif self.path == "/api/rule":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length).decode("utf-8"))
                result = apply_ruling.apply(body.get("flag_id"), body.get("ruling", ""),
                                            body.get("points"))
                code = 200 if result.get("ok") else 400
            except Exception as e:
                result, code = {"ok": False, "error": str(e)}, 400
        else:
            self.send_error(404)
            return
        payload = json.dumps(result).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def is_running():
    if not os.path.exists(PID_PATH):
        return False
    try:
        pid = int(open(PID_PATH).read().strip())
        os.kill(pid, 0)
        return True
    except (ValueError, ProcessLookupError, PermissionError):
        os.remove(PID_PATH)
        return False


def cmd_stop():
    if not is_running():
        print(json.dumps({"ok": True, "running": False}))
        return
    pid = int(open(PID_PATH).read().strip())
    os.kill(pid, signal.SIGTERM)
    for _ in range(20):
        if not is_running():
            break
        time.sleep(0.2)
    print(json.dumps({"ok": True, "running": False, "stopped": True}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=7430)
    ap.add_argument("--stop", action="store_true")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args()
    if args.stop:
        cmd_stop()
        return
    if args.status:
        print(json.dumps({"ok": True, "running": is_running(),
                          "pid": int(open(PID_PATH).read()) if is_running() else None,
                          "url": "http://localhost:%d" % args.port}))
        return
    if is_running():
        print(json.dumps({"ok": True, "already_running": True, "url": "http://localhost:%d" % args.port}))
        return
    os.makedirs(DATA_DIR, exist_ok=True)
    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    with open(PID_PATH, "w") as f:
        f.write(str(os.getpid()))
    print(json.dumps({"ok": True, "url": "http://localhost:%d" % args.port}), flush=True)
    try:
        httpd.serve_forever()
    finally:
        if os.path.exists(PID_PATH):
            os.remove(PID_PATH)


if __name__ == "__main__":
    main()
