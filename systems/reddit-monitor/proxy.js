#!/usr/bin/env node
// Reddit Monitor proxy + app server
// Serves the Reddit Monitor UI at http://localhost:7429/
// Proxies Reddit data via Arctic Shift at http://localhost:7429/api/*
// Run: node /Users/davidohara/develop/jarvis/systems/reddit-monitor/proxy.js
// Then open: http://localhost:7429 in any browser

const http = require('http');
const https = require('https');
const path = require('path');

const PORT = 7429;
const API_BASE = 'arctic-shift.photon-reddit.com';

// ── HTML app ─────────────────────────────────────────────────────────────────
const APP_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Reddit Monitor — Kare Devices</title>
<style>
  :root {
    --bg:#f8f9fa;--surface:#fff;--border:#e2e8f0;--text:#1a202c;--muted:#718096;
    --light:#a0aec0;--primary:#4a90d9;--high:#e53e3e;--high-bg:#fff5f5;
    --high-border:#fed7d7;--med:#dd6b20;--med-bg:#fffaf0;--med-border:#feebc8;
    --low:#718096;--low-bg:#f7fafc;--low-border:#e2e8f0;
    --resp-bg:#f0fff4;--resp-border:#c6f6d5;--resp-text:#276749;
    --r:8px;--shadow:0 1px 3px rgba(0,0,0,.08);
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);font-size:14px;line-height:1.5;padding:16px}
  h1{font-size:18px;font-weight:700}
  h2{font-size:15px;font-weight:600;margin-bottom:12px}
  h3{font-size:13px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
  .header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:8px}
  .header-left{display:flex;align-items:center;gap:10px}
  .badge{background:#e9d8fd;color:#553c9a;font-size:11px;font-weight:600;padding:2px 8px;border-radius:12px}
  .btn{padding:6px 12px;border-radius:var(--r);border:1px solid var(--border);background:var(--surface);color:var(--text);font-size:13px;cursor:pointer;font-weight:500;transition:background .15s}
  .btn:hover{background:#edf2f7}
  .btn-primary{background:var(--primary);color:#fff;border-color:var(--primary)}
  .btn-primary:hover{background:#3a7bc8}
  .btn-sm{padding:3px 8px;font-size:12px}
  .stats{display:flex;gap:12px;background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:10px 16px;margin-bottom:16px;flex-wrap:wrap;align-items:center}
  .stat{display:flex;flex-direction:column;align-items:center;min-width:60px}
  .stat-v{font-size:22px;font-weight:700;line-height:1}
  .stat-l{font-size:11px;color:var(--muted);margin-top:2px}
  .divider{width:1px;height:36px;background:var(--border)}
  .stats-r{margin-left:auto;font-size:12px;color:var(--muted);display:flex;flex-direction:column;align-items:flex-end;gap:2px}
  .panel{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);margin-bottom:16px;overflow:hidden}
  .panel-body{padding:16px;display:none}
  .panel-body.open{display:block}
  .grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
  @media(max-width:700px){.grid3{grid-template-columns:1fr}}
  .field label{display:block;font-size:12px;font-weight:600;color:var(--muted);margin-bottom:6px;text-transform:uppercase;letter-spacing:.04em}
  .tags{display:flex;flex-wrap:wrap;gap:4px;min-height:28px;margin-bottom:6px}
  .tag{display:flex;align-items:center;gap:4px;background:#edf2f7;border-radius:4px;padding:2px 6px;font-size:12px}
  .tag-x{cursor:pointer;color:var(--muted);font-size:14px;line-height:1}
  .tag-x:hover{color:var(--high)}
  .tag-row{display:flex;gap:6px}
  .tag-in{flex:1;padding:4px 8px;border:1px solid var(--border);border-radius:4px;font-size:13px}
  .lb-row{display:flex;align-items:center;gap:8px;margin-top:12px}
  .lb-row label{font-size:12px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
  select{padding:4px 8px;border:1px solid var(--border);border-radius:4px;font-size:13px;background:#fff}
  .section{margin-bottom:20px}
  .sec-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
  .list{display:flex;flex-direction:column;gap:8px}
  .card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r);padding:12px 14px;display:flex;align-items:flex-start;gap:12px;box-shadow:var(--shadow)}
  .card:hover{border-color:#cbd5e0}
  .card.resp{background:var(--resp-bg);border-color:var(--resp-border);opacity:.85}
  .dot{flex-shrink:0;width:8px;height:8px;border-radius:50%;margin-top:6px}
  .dot-high{background:var(--high)}.dot-med{background:var(--med)}.dot-low{background:var(--low)}
  .cbody{flex:1;min-width:0}
  .meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:4px}
  .sub-badge{background:#ebf4ff;color:#2b6cb0;font-size:11px;font-weight:600;padding:1px 6px;border-radius:4px}
  .pri{font-size:11px;font-weight:600;padding:1px 6px;border-radius:4px}
  .pri.high{background:var(--high-bg);color:var(--high);border:1px solid var(--high-border)}
  .pri.med{background:var(--med-bg);color:var(--med);border:1px solid var(--med-border)}
  .pri.low{background:var(--low-bg);color:var(--low);border:1px solid var(--low-border)}
  .resp-badge{font-size:11px;font-weight:600;padding:1px 6px;border-radius:4px;background:var(--resp-bg);color:var(--resp-text);border:1px solid var(--resp-border)}
  .age,.cmts{font-size:12px;color:var(--muted)}
  .title{font-size:14px;font-weight:500;color:var(--text);text-decoration:none;display:block;margin-bottom:4px}
  .title:hover{color:var(--primary);text-decoration:underline}
  .kws{display:flex;flex-wrap:wrap;gap:4px;margin-top:4px}
  .kw{font-size:11px;background:#fefcbf;color:#744210;border-radius:3px;padding:0 4px}
  .actions{flex-shrink:0;display:flex;flex-direction:column;gap:4px;align-items:flex-end}
  .score{font-size:11px;color:var(--light);margin-top:2px}
  .resp-toggle{display:flex;align-items:center;gap:8px;cursor:pointer;user-select:none;color:var(--muted);font-size:13px}
  .resp-toggle:hover{color:var(--text)}
  .resp-ct{background:#e2e8f0;border-radius:10px;padding:1px 7px;font-size:12px}
  .loading{text-align:center;padding:40px;color:var(--muted)}
  .spinner{display:inline-block;width:24px;height:24px;border:3px solid #e2e8f0;border-top-color:var(--primary);border-radius:50%;animation:spin .8s linear infinite;margin-bottom:12px}
  @keyframes spin{to{transform:rotate(360deg)}}
  .err{background:var(--high-bg);border:1px solid var(--high-border);color:var(--high);border-radius:var(--r);padding:10px 14px;font-size:13px;margin-bottom:8px}
  .empty{color:var(--muted);font-size:13px;padding:20px 0;text-align:center}
  .chev{transition:transform .2s;display:inline-block}
  .chev.open{transform:rotate(180deg)}
  .draft-box{margin-top:10px;border-top:1px solid var(--border);padding-top:10px}
  .draft-label{font-size:11px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;margin-bottom:6px;display:flex;align-items:center;gap:6px}
  .draft-text{font-size:13px;color:#2d3748;background:#f7fafc;border:1px solid var(--border);border-radius:6px;padding:10px 12px;line-height:1.6;white-space:pre-wrap;word-break:break-word}
  .draft-actions{display:flex;gap:6px;margin-top:6px}
  .btn-copy{padding:3px 10px;font-size:12px;border-radius:4px;border:1px solid var(--border);background:#fff;cursor:pointer;color:var(--muted)}
  .btn-copy:hover{background:#edf2f7;color:var(--text)}
  .btn-copy.copied{background:#f0fff4;color:var(--resp-text);border-color:var(--resp-border)}
  .btn-skip{padding:3px 8px;font-size:12px;border-radius:var(--r);border:1px solid var(--border);background:#fff;cursor:pointer;color:var(--muted);font-weight:500}
  .btn-skip:hover{background:#edf2f7;color:var(--text)}
</style>
</head>
<body>

<div class="header">
  <div class="header-left"><h1>Reddit Monitor</h1><span class="badge">✍️ Harper</span></div>
  <div style="display:flex;gap:8px">
    <button class="btn btn-sm" onclick="toggleSettings()">⚙ Settings</button>
    <button class="btn btn-primary btn-sm" onclick="loadAll()">↻ Reload</button>
  </div>
</div>

<div class="stats">
  <div class="stat"><span class="stat-v" id="sFetched">—</span><span class="stat-l">Fetched</span></div>
  <div class="divider"></div>
  <div class="stat"><span class="stat-v" id="sMatched">—</span><span class="stat-l">Matched</span></div>
  <div class="divider"></div>
  <div class="stat"><span class="stat-v" id="sSubs">—</span><span class="stat-l">Subreddits</span></div>
  <div class="divider"></div>
  <div class="stat"><span class="stat-v" id="sResp">—</span><span class="stat-l">Responded</span></div>
  <div class="stats-r">
    <span id="refreshed">Not yet loaded</span>
    <span id="status" style="font-size:11px"></span>
  </div>
</div>

<div class="panel">
  <div class="panel-body" id="settBody">
    <div class="grid3">
      <div class="field"><label>Monitored Subreddits</label><div class="tags" id="subTags"></div>
        <div class="tag-row"><input class="tag-in" id="subIn" placeholder="Add subreddit…" onkeydown="if(event.key==='Enter')addTag('subreddits','subIn')"><button class="btn btn-sm" onclick="addTag('subreddits','subIn')">Add</button></div>
      </div>
      <div class="field"><label>Keywords</label><div class="tags" id="kwTags"></div>
        <div class="tag-row"><input class="tag-in" id="kwIn" placeholder="Add keyword…" onkeydown="if(event.key==='Enter')addTag('keywords','kwIn')"><button class="btn btn-sm" onclick="addTag('keywords','kwIn')">Add</button></div>
      </div>
      <div class="field"><label>My Reddit Accounts</label><div class="tags" id="userTags"></div>
        <div class="tag-row"><input class="tag-in" id="userIn" placeholder="Add username…" onkeydown="if(event.key==='Enter')addTag('usernames','userIn')"><button class="btn btn-sm" onclick="addTag('usernames','userIn')">Add</button></div>
      </div>
    </div>
    <div class="lb-row">
      <label>Lookback</label>
      <select id="lbSel" onchange="saveLb()">
        <option value="7">7 days</option><option value="10" selected>10 days</option>
        <option value="14">14 days</option><option value="30">30 days</option>
      </select>
      <label style="margin-left:16px">Auto-skip older than</label>
      <select id="asSel" onchange="saveAs()">
        <option value="3">3 days</option><option value="5">5 days</option>
        <option value="7">7 days</option><option value="8" selected>8 days</option>
        <option value="10">10 days</option><option value="14">14 days</option>
        <option value="0">Off</option>
      </select>
      <button class="btn btn-sm btn-primary" onclick="loadAll()" style="margin-left:8px">Apply & Reload</button>
    </div>
  </div>
</div>

<div id="errBox"></div>

<div class="section">
  <div class="sec-hdr"><h2>🔥 Active Queue</h2><span id="actCt" style="font-size:13px;color:var(--muted)"></span></div>
  <div id="actList" class="list"><div class="loading"><div class="spinner"></div><br>Loading posts…</div></div>
</div>

<div class="section">
  <div class="sec-hdr">
    <div class="resp-toggle" onclick="toggleResp()">
      <span>✓ Responded</span><span class="resp-ct" id="respCt">0</span><span class="chev" id="respChev">▼</span>
    </div>
  </div>
  <div id="respList" class="list" style="display:none"></div>
</div>

<script>
const DEFAULTS={subreddits:['feedingtube','Gastroparesis','nursing','ChronicIllness','spinalcordinjury','neurogenicbladder','Parenting','NICU','CaregiverSupport','POTS','EhlersDanlos','MultipleSclerosis'],keywords:['catheter','tube securement','skin irritation','Grip-Lok','adhesive','dislodge','tape','GJ tube','NG tube','PEG tube','feeding tube','stoma','tubie','MCAS','skin breakdown'],usernames:[],lookback_days:10,auto_skip_days:8};
const SK={subreddits:'reddit_monitor_subreddits',keywords:'reddit_monitor_keywords',usernames:'reddit_monitor_usernames'};
const ls={g:(k,d)=>{try{const v=localStorage.getItem(k);return v!==null?JSON.parse(v):d}catch{return d}},s:(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v))}catch{}}};
const cfg=()=>({subreddits:ls.g('reddit_monitor_subreddits',DEFAULTS.subreddits),keywords:ls.g('reddit_monitor_keywords',DEFAULTS.keywords),usernames:ls.g('reddit_monitor_usernames',DEFAULTS.usernames),lookback_days:ls.g('reddit_monitor_lookback_days',DEFAULTS.lookback_days),auto_skip_days:ls.g('reddit_monitor_auto_skip_days',DEFAULTS.auto_skip_days)});

let posts=[],responded=new Set(ls.g('reddit_monitor_responded',[])),autoResp=new Set(ls.g('reddit_monitor_auto_responded',[])),skipped=new Set(ls.g('reddit_monitor_skipped',[])),settOpen=false,respOpen=false,loading=false;

function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}
function ago(u){const d=Math.floor(Date.now()/1000)-u;if(d<60)return'just now';if(d<3600)return Math.floor(d/60)+'m ago';if(d<86400)return Math.floor(d/3600)+'h ago';return Math.floor(d/86400)+'d ago'}
function sleep(ms){return new Promise(r=>setTimeout(r,ms))}

function toggleSettings(){settOpen=!settOpen;document.getElementById('settBody').classList.toggle('open',settOpen)}
function toggleResp(){respOpen=!respOpen;const el=document.getElementById('respList');el.style.display=respOpen?'flex':'none';if(respOpen){el.style.flexDirection='column';el.style.gap='8px'}document.getElementById('respChev').classList.toggle('open',respOpen)}
function saveLb(){ls.s('reddit_monitor_lookback_days',parseInt(document.getElementById('lbSel').value))}
function saveAs(){ls.s('reddit_monitor_auto_skip_days',parseInt(document.getElementById('asSel').value))}

function renderTags(){
  const c=cfg();
  ['subreddits','keywords','usernames'].forEach((k,i)=>{
    const id=['subTags','kwTags','userTags'][i];
    document.getElementById(id).innerHTML=c[k].map((v,j)=>\`<span class="tag">\${esc(v)}<span class="tag-x" onclick="removeTag('\${k}','\${SK[k]}',\${j})">×</span></span>\`).join('');
  });
  document.getElementById('lbSel').value=String(c.lookback_days);
  document.getElementById('asSel').value=String(c.auto_skip_days);
}

function addTag(key,inputId){
  const el=document.getElementById(inputId),v=el.value.trim().replace(/^[ru]\\//,'');
  if(!v)return;const c=cfg(),arr=c[key];
  if(!arr.includes(v)){arr.push(v);ls.s(SK[key],arr)}
  el.value='';renderTags();
}
function removeTag(key,sk,idx){const c=cfg();c[key].splice(idx,1);ls.s(sk,c[key]);renderTags()}

function score(p,keywords,now,days){
  const txt=((p.title||'')+' '+(p.selftext||'')).toLowerCase();
  const matched=keywords.filter(k=>txt.includes(k.toLowerCase()));
  if(!matched.length)return{score:0,matched:[]};
  const age=Math.max(0,1-(now-p.created_utc)/(days*86400));
  const cmts=Math.min(1,(p.num_comments||0)/50);
  const kw=Math.min(1,matched.length/3);
  return{score:Math.round(kw*50+cmts*30+age*20),matched};
}
const plv=s=>s>=55?'high':s>=30?'med':'low';
const ptx=s=>s>=55?'HIGH':s>=30?'MED':'LOW';
const isResp=id=>responded.has(id)||autoResp.has(id);
const isSkipped=id=>skipped.has(id);

// Draft reply templates keyed by matched keyword themes
function draftReply(p){
  const txt=((p.title||'')+' '+(p.selftext||'')).toLowerCase();
  const title=p.title||'';

  // Sensitive skin / tape reactions
  if(/sensitive skin|skin.?(reaction|breakdown|irritat)|allev[iy]n|tegaderm|rash under|tape rash/.test(txt))
    return \`Skin reactions under tube tape are so common and so frustrating — especially on little ones where the skin is already delicate. A few things that have helped others in this community:\\n\\n- Skin barrier wipes or spray (Cavilon, 3M) before applying any adhesive can make a big difference for reactive skin\\n- Some families have had better luck with silicone-based securement rather than traditional adhesive — gentler on removal too\\n- If there's been breakdown already, giving the skin a full rest cycle before reapplying in the same spot helps\\n\\nHas the care team weighed in on what's causing the reaction — the adhesive itself or the tape edges?\`;

  // Tape coming loose / dislodging
  if(/dislodg|fall.?off|coming off|keep.?fall|pull.?out|accidental|tape.?hold|won.?t stay|not stay/.test(txt))
    return \`Tube dislodgement is one of the most stressful parts of tube life, especially with active kids or patients. A few things worth trying if you haven't already:\\n\\n- Chevron or H-taping techniques (there are good YouTube demos) distribute tension better than a single piece\\n- Looping the tube and securing the loop separately from the insertion site takes tension off the site itself\\n- Some people find anchoring to clothing rather than skin helps during active periods\\n\\nWhat's the current setup — is it pulling at the insertion site or coming loose at the tape edges?\`;

  // Skin breakdown / wound under tube
  if(/skin.?breakdown|wound|granuloma|leaking around|stomal|stoma.?(irritat|bleed|sore)/.test(txt))
    return \`Stomal irritation and skin breakdown around tubes is really common and really hard to manage — especially when you have to keep the tube in place while trying to heal the skin underneath.\\n\\nA few things that have helped others:\\n- Keeping the site dry is huge; some people use a thin foam dressing cut to fit around the tube\\n- Zinc oxide or barrier paste (not directly on the stoma, but around it) can protect raw skin\\n- If there's granulation tissue, the care team may want to look at silver nitrate treatment\\n\\nIs the breakdown mostly from movement/friction or from leakage around the site?\`;

  // Feeding tube general / new to tubes
  if(/new to|just got|first time|overwhelm|scared|anxious|don.?t know|where do i start|advice/.test(txt))
    return \`Welcome to a community that gets it — the early days with a feeding tube can feel completely overwhelming, and that's completely normal.\\n\\nA few things that tend to help new tube families:\\n- Connect with a tube-savvy dietitian if you haven't already; they're often more hands-on than the prescribing team\\n- Keep a simple log for the first few weeks (feeds, flushes, anything unusual) — it pays off at appointments\\n- This subreddit is genuinely one of the best resources out there; don't hesitate to ask specific questions\\n\\nWhat type of tube is it, and how long have you been home with it?\`;

  // NG tube specific
  if(/ng tube|nasogastric|nasal.?tube|nose tube|inserting|reinserting|re.?insert/.test(txt))
    return \`NG tubes are a whole skill set — reinsertion especially gets easier but never really feels routine. A few things that help:\\n\\n- Chilling the tube briefly in ice water stiffens it slightly and makes passing easier\\n- Having everything set up and verified before starting reduces the stress of the moment\\n- Lubrication and having the person swallow sips of water as you advance makes a big difference\\n\\nIf reinsertion is becoming frequent, it might be worth a conversation with the team about whether a longer-term tube option makes sense. What's prompting the question?\`;

  // GJ / PEG / button tube
  if(/gj tube|peg tube|button|mic-key|g.?tube|gastrostomy|jejun/.test(txt))
    return \`G and GJ tube questions are very site-specific — so much depends on the individual setup. That said, a few things come up a lot in this community:\\n\\n- Button tubes typically need replacement every 3–6 months; knowing the balloon water volume is important for home troubleshooting\\n- GJ tubes are trickier because displacement means the J port ends up in the stomach — worth knowing the signs (increased residuals, reflux returning)\\n- For leakage around the site, granulation tissue or a worn-out balloon are the two most common culprits\\n\\nWhat's the specific issue you're running into?\`;

  // Catheter / urinary
  if(/catheter|foley|urinary|bladder/.test(txt))
    return \`Catheter management questions are so often undersupported — a lot of people figure this out on their own through communities like this one.\\n\\nA few common pain points that come up:\\n- Securement is underemphasized in most discharge training; proper anchoring reduces urethral trauma significantly\\n- Skin irritation at the leg strap or tape site is really common and usually fixable with different securement methods\\n- If there's recurrent UTI, the insertion technique and care routine are worth reviewing with the team\\n\\nWhat's the specific challenge you're dealing with?\`;

  // Generic fallback for any matched post
  return \`This comes up a lot in communities like this one, and there's usually more support available than people realize at first.\\n\\nWithout knowing the full picture — what's the main challenge right now? Happy to share what's worked for others in similar situations or point you toward resources that tend to actually help.\`;
}

function copyDraft(id){
  const el=document.getElementById('draft-text-'+id);
  if(!el)return;
  navigator.clipboard.writeText(el.textContent).then(()=>{
    const btn=document.getElementById('draft-copy-'+id);
    if(btn){btn.textContent='✓ Copied';btn.classList.add('copied');setTimeout(()=>{btn.textContent='Copy';btn.classList.remove('copied')},2000)}
  });
}

function card(p,resp,inResp){
  const pl=plv(p.score),url='https://www.reddit.com'+p.permalink;
  const isHigh=pl==='high'&&!resp;
  const draft=isHigh?draftReply(p):'';
  return \`<div class="card\${resp?' resp':''}" id="card-\${p.id}">
    <div class="dot dot-\${pl}"></div>
    <div class="cbody">
      <div class="meta">
        <span class="sub-badge">r/\${esc(p.subreddit)}</span>
        \${resp?\`<span class="resp-badge">\${autoResp.has(p.id)?'🤖 Auto-detected':'✓ You responded'}</span>\`:\`<span class="pri \${pl}">\${ptx(p.score)}</span>\`}
        <span class="age">\${ago(p.created_utc)}</span>
        <span class="cmts">💬 \${p.num_comments||0}</span>
      </div>
      <a class="title" href="\${esc(url)}" target="_blank" rel="noopener">\${esc(p.title)}</a>
      <div class="kws">\${p.matched.map(k=>\`<span class="kw">\${esc(k)}</span>\`).join('')}</div>
      \${isHigh?\`<div class="draft-box">
        <div class="draft-label">✏️ Suggested reply</div>
        <div class="draft-text" id="draft-text-\${p.id}">\${esc(draft)}</div>
        <div class="draft-actions">
          <button class="btn-copy" id="draft-copy-\${p.id}" onclick="copyDraft('\${p.id}')">Copy</button>
        </div>
      </div>\`:''}
    </div>
    <div class="actions">
      \${inResp?\`<button class="btn btn-sm" onclick="unmark('\${p.id}')">↩ Move back</button>\`:\`<button class="btn btn-sm btn-primary" onclick="mark('\${p.id}')">✓ Responded</button><button class="btn btn-sm btn-skip" onclick="skip('\${p.id}')">Skip</button>\`}
      <a class="btn btn-sm" href="\${esc(url)}" target="_blank" rel="noopener">Open ↗</a>
    </div>
  </div>\`;
}

function renderAll(){
  const bandOrder=s=>s>=55?0:s>=30?1:2;
  const byBandThenRecency=(a,b)=>bandOrder(a.score)-bandOrder(b.score)||b.created_utc-a.created_utc;
  const active=posts.filter(p=>!isResp(p.id)&&!isSkipped(p.id)).sort(byBandThenRecency);
  const resp=posts.filter(p=>isResp(p.id)).sort(byBandThenRecency);
  document.getElementById('actCt').textContent=active.length+' post'+(active.length!==1?'s':'');
  document.getElementById('actList').innerHTML=active.length?active.map(p=>card(p,false,false)).join(''):'<div class="empty">No active posts — all caught up! ✓</div>';
  document.getElementById('respCt').textContent=resp.length;
  document.getElementById('respList').innerHTML=resp.length?resp.map(p=>card(p,true,true)).join(''):'<div class="empty">No responded posts yet.</div>';
  document.getElementById('sMatched').textContent=posts.length;
  document.getElementById('sResp').textContent=resp.length;
}

function mark(id){responded.add(id);ls.s('reddit_monitor_responded',[...responded]);renderAll()}
function unmark(id){responded.delete(id);autoResp.delete(id);ls.s('reddit_monitor_responded',[...responded]);ls.s('reddit_monitor_auto_responded',[...autoResp]);renderAll()}
function skip(id){skipped.add(id);ls.s('reddit_monitor_skipped',[...skipped]);renderAll()}

async function loadAll(){
  if(loading)return;loading=true;
  const c=cfg(),now=Math.floor(Date.now()/1000);
  const after=new Date(Date.now()-c.lookback_days*86400*1000).toISOString().split('T')[0];
  document.getElementById('errBox').innerHTML='';
  document.getElementById('actList').innerHTML='<div class="loading"><div class="spinner"></div><br>Fetching posts…</div>';
  document.getElementById('sFetched').textContent='…';
  document.getElementById('sMatched').textContent='…';
  document.getElementById('sSubs').textContent=c.subreddits.length;
  document.getElementById('sResp').textContent='…';
  renderTags();

  const errors=[],fetched=[];
  for(let i=0;i<c.subreddits.length;i++){
    const sub=c.subreddits[i];
    document.getElementById('status').textContent=\`Fetching r/\${sub}… (\${i+1}/\${c.subreddits.length})\`;
    try{
      const r=await fetch(\`/api/posts?subreddit=\${encodeURIComponent(sub)}&limit=100&after=\${after}\`);
      if(!r.ok)throw new Error('HTTP '+r.status);
      const d=await r.json();
      if(d.error)throw new Error(d.error);
      fetched.push(...(d.data||[]));
    }catch(e){errors.push('r/'+sub+': '+e.message)}
    if(i<c.subreddits.length-1)await sleep(200);
  }

  document.getElementById('sFetched').textContent=fetched.length;
  posts=fetched.map(p=>{const{score:s,matched}=score(p,c.keywords,now,c.lookback_days);return{...p,score:s,matched}}).filter(p=>p.matched.length>0);

  // Auto-skip posts older than threshold
  if(c.auto_skip_days>0){
    const threshold=c.auto_skip_days*86400;
    let changed=false;
    posts.forEach(p=>{if(!isResp(p.id)&&!skipped.has(p.id)&&(now-p.created_utc)>threshold){skipped.add(p.id);changed=true}});
    if(changed)ls.s('reddit_monitor_skipped',[...skipped]);
  }

  if(errors.length)document.getElementById('errBox').innerHTML=errors.map(e=>\`<div class="err">⚠ \${esc(e)}</div>\`).join('');

  if(c.usernames.length){
    document.getElementById('status').textContent='Checking comment history…';
    const idSet=new Set(posts.map(p=>p.id));const newAuto=new Set();
    for(const u of c.usernames){
      try{
        const r=await fetch(\`/api/comments?author=\${encodeURIComponent(u)}&limit=100&after=\${after}\`);
        const d=await r.json();
        (d.data||[]).forEach(c=>{const id=(c.link_id||'').replace('t3_','');if(id&&idSet.has(id))newAuto.add(id)});
      }catch{}
      await sleep(200);
    }
    autoResp=newAuto;ls.s('reddit_monitor_auto_responded',[...autoResp]);
  }

  document.getElementById('status').textContent='';
  document.getElementById('refreshed').textContent='Last refreshed: '+new Date().toLocaleTimeString();
  document.getElementById('sSubs').textContent=c.subreddits.length-errors.length;
  renderAll();loading=false;
}

renderTags();loadAll();
</script>
</body>
</html>`;

// ── HTTP server ───────────────────────────────────────────────────────────────
function proxyRequest(targetPath, res) {
  const options = {
    hostname: API_BASE,
    path: targetPath,
    method: 'GET',
    headers: {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
      'Accept': 'application/json',
    }
  };
  const req = https.request(options, proxyRes => {
    res.writeHead(proxyRes.statusCode, {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    });
    proxyRes.pipe(res);
  });
  req.on('error', e => { res.writeHead(502); res.end(JSON.stringify({error: e.message})); });
  req.end();
}

// ── Idle shutdown ─────────────────────────────────────────────────────────────
const IDLE_MS = 30 * 60 * 1000; // 30 minutes
let idleTimer;
function resetIdle() {
  clearTimeout(idleTimer);
  idleTimer = setTimeout(() => {
    console.log('\n💤 No activity for 30 minutes — shutting down.');
    server.close(() => process.exit(0));
  }, IDLE_MS);
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);

  if (req.method === 'OPTIONS') {
    res.writeHead(204, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET'});
    res.end(); return;
  }

  // Graceful shutdown endpoint (called by artifact close/unload)
  if (url.pathname === '/shutdown') {
    res.writeHead(200, {'Content-Type': 'text/plain', 'Access-Control-Allow-Origin': '*'});
    res.end('shutting down');
    console.log('\n🛑 Shutdown requested via /shutdown');
    server.close(() => process.exit(0));
    return;
  }

  // Reset idle timer on every real request
  resetIdle();

  // Serve the app
  if (url.pathname === '/' || url.pathname === '/index.html') {
    res.writeHead(200, {'Content-Type': 'text/html'});
    res.end(APP_HTML); return;
  }

  // Proxy posts
  if (url.pathname === '/api/posts') {
    const sub   = url.searchParams.get('subreddit') || '';
    const limit = url.searchParams.get('limit') || '100';
    const after = url.searchParams.get('after') || '';
    if (!sub || !/^[a-zA-Z0-9_]+$/.test(sub)) { res.writeHead(400); res.end('bad subreddit'); return; }
    proxyRequest(`/api/posts/search?subreddit=${encodeURIComponent(sub)}&limit=${limit}&after=${after}`, res);
    return;
  }

  // Proxy comments
  if (url.pathname === '/api/comments') {
    const author = url.searchParams.get('author') || '';
    const limit  = url.searchParams.get('limit') || '100';
    const after  = url.searchParams.get('after') || '';
    if (!author || !/^[a-zA-Z0-9_-]+$/.test(author)) { res.writeHead(400); res.end('bad author'); return; }
    proxyRequest(`/api/comments/search?author=${encodeURIComponent(author)}&limit=${limit}&after=${after}`, res);
    return;
  }

  res.writeHead(404); res.end('not found');
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`\n✅ Reddit Monitor running at http://localhost:${PORT}`);
  console.log(`   Auto-shuts down after 30 min of inactivity.\n`);
  resetIdle(); // start the idle clock
});
