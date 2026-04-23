#!/usr/bin/env tsx
// ── Invintory Export via Live Chrome Tab ──────────────────────────────────────
// Triggers CSV export from the user's authenticated Chrome session.
// Cloudflare is already satisfied in the real browser — no Playwright needed.
//
// Flow:
//   1. Find Invintory tab in Chrome (must be open + logged in)
//   2. Navigate to collection page
//   3. Click the "Export CSV" button via JS
//   4. Wait for download to appear in ~/Downloads
//   5. Import CSV into local cache
//
// Run: npx tsx src/export-via-chrome.ts

import { execSync } from 'child_process';
import { writeFileSync, existsSync, readdirSync, statSync, mkdirSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';
import { importCSV, saveCache, summarize } from './cache.js';

const CACHE_DIR = join(homedir(), '.config', 'invintory');
const TOKEN_FILE = join(CACHE_DIR, 'firebase-token.json');
const DOWNLOADS_DIR = join(homedir(), 'Downloads');

if (!existsSync(CACHE_DIR)) mkdirSync(CACHE_DIR, { recursive: true, mode: 0o700 });

// ── AppleScript helpers ───────────────────────────────────────────────────────

function runAppleScript(script: string): string {
  writeFileSync('/tmp/inv-export.applescript', script);
  try {
    return execSync('osascript /tmp/inv-export.applescript', { encoding: 'utf8', timeout: 30000 }).trim();
  } finally {
    try { execSync('rm -f /tmp/inv-export.applescript'); } catch { /**/ }
  }
}

function runInChrome(js: string): string {
  const escaped = js.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, ' ');
  return runAppleScript([
    'tell application "Google Chrome"',
    '  repeat with w in windows',
    '    repeat with t in tabs of w',
    '      if URL of t contains "invintory.com" then',
    `        return execute t javascript "${escaped}"`,
    '      end if',
    '    end repeat',
    '  end repeat',
    '  return "TAB_NOT_FOUND"',
    'end tell',
  ].join('\n'));
}

function sleep(ms: number) { return new Promise(r => setTimeout(r, ms)); }

// ── Find newest CSV in Downloads ──────────────────────────────────────────────

function findNewestInvintoryCSV(since: number): string | null {
  try {
    const files = readdirSync(DOWNLOADS_DIR)
      .filter(f => f.toLowerCase().endsWith('.csv') &&
        (f.toLowerCase().includes('invintory') || f.toLowerCase().includes('collection') || f.toLowerCase().includes('wine')))
      .map(f => ({ name: f, path: join(DOWNLOADS_DIR, f), mtime: statSync(join(DOWNLOADS_DIR, f)).mtimeMs }))
      .filter(f => f.mtime > since)
      .sort((a, b) => b.mtime - a.mtime);
    return files[0]?.path ?? null;
  } catch { return null; }
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  // 1. Check Chrome has an Invintory tab
  console.log('Checking for Invintory tab in Chrome...');
  const tabUrl = runInChrome('document.location.href');
  if (tabUrl === 'TAB_NOT_FOUND') {
    throw new Error('No Invintory tab found in Chrome. Open app.invintory.com and log in, then retry.');
  }
  console.log(`  Found: ${tabUrl}`);

  // Save refresh token while we have access
  const rt = runInChrome(
    '(function(){' +
    '  var k=Object.keys(sessionStorage).find(function(k){return k.indexOf("firebase:authUser")!==-1;});' +
    '  if(!k)return "";' +
    '  try{var a=JSON.parse(sessionStorage.getItem(k)||"{}");return a.stsTokenManager?a.stsTokenManager.refreshToken:"";}' +
    '  catch(e){return "";}' +
    '})()'
  );
  if (rt) {
    writeFileSync(TOKEN_FILE, JSON.stringify({ refreshToken: rt, savedAt: new Date().toISOString() }, null, 2), { mode: 0o600 });
  }

  // 2. Navigate to collection page if not already there
  if (!tabUrl.includes('/collection')) {
    console.log('Navigating to collection page...');
    runInChrome('window.location.href = "https://app.invintory.com/collection/bottles"');
    await sleep(4000);
  }

  // 3. Look for Export CSV button — try multiple selector strategies
  console.log('Looking for Export CSV button...');

  // First, dump what buttons exist so we can see the UI
  const buttonInfo = runInChrome(
    '(function(){' +
    '  var btns=Array.from(document.querySelectorAll("button,[role=button]"));' +
    '  return JSON.stringify(btns.map(function(b){return {text:(b.innerText||"").trim().substring(0,40),aria:b.getAttribute("aria-label"),title:b.getAttribute("title")};}).filter(function(b){return b.text||b.aria||b.title;}).slice(0,30));' +
    '})()'
  );
  const buttons: Array<{ text: string; aria: string; title: string }> = JSON.parse(buttonInfo || '[]');
  console.log('  Buttons found:', buttons.map(b => `"${b.text || b.aria || b.title}"`).join(', '));

  // Look for export-related elements
  const exportInfo = runInChrome(
    '(function(){' +
    '  var all=Array.from(document.querySelectorAll("*"));' +
    '  var matches=all.filter(function(el){' +
    '    var t=(el.innerText||el.textContent||"").trim().toLowerCase();' +
    '    var a=(el.getAttribute("aria-label")||"").toLowerCase();' +
    '    return (t==="export csv"||t==="export"||t.includes("export csv")||a.includes("export"));' +
    '  });' +
    '  return JSON.stringify(matches.slice(0,5).map(function(el){return {tag:el.tagName,text:(el.innerText||"").trim().substring(0,40),visible:el.offsetParent!==null};}));' +
    '})()'
  );
  const exportEls: Array<{ tag: string; text: string; visible: boolean }> = JSON.parse(exportInfo || '[]');
  console.log('  Export elements:', JSON.stringify(exportEls));

  if (exportEls.length === 0) {
    // The export button might be behind a menu — try the 3-dot/kebab menu or toolbar
    console.log('  No export button visible. Looking for toolbar/menu...');

    // Try clicking a settings/options button that might reveal export
    const menuClicked = runInChrome(
      '(function(){' +
      '  var candidates=Array.from(document.querySelectorAll("button,[role=button]")).filter(function(b){' +
      '    var t=(b.innerText||b.getAttribute("aria-label")||b.getAttribute("title")||"").toLowerCase();' +
      '    return t.includes("option")||t.includes("more")||t.includes("menu")||t.includes("setting")||t==="..."||t==="⋮"||t==="•••";' +
      '  });' +
      '  if(candidates.length>0){candidates[0].click();return "clicked:"+((candidates[0].innerText||candidates[0].getAttribute("aria-label")||"").substring(0,30));}' +
      '  return "none";' +
      '})()'
    );
    console.log('  Menu click result:', menuClicked);
    await sleep(1000);

    // Re-check for export
    const exportInfo2 = runInChrome(
      '(function(){' +
      '  var all=Array.from(document.querySelectorAll("*"));' +
      '  var matches=all.filter(function(el){' +
      '    var t=(el.innerText||el.textContent||"").trim().toLowerCase();' +
      '    return t.includes("export");' +
      '  });' +
      '  return JSON.stringify(matches.slice(0,8).map(function(el){return {tag:el.tagName,text:(el.innerText||"").trim().substring(0,50),visible:el.offsetParent!==null};}));' +
      '})()'
    );
    console.log('  After menu click:', exportInfo2);
  }

  // 4. Record time before triggering download
  const beforeDownload = Date.now();

  // 5. Click Export CSV — try to find and click it
  const clickResult = runInChrome(
    '(function(){' +
    '  function findAndClick(pred){' +
    '    var els=Array.from(document.querySelectorAll("*"));' +
    '    for(var i=0;i<els.length;i++){' +
    '      if(pred(els[i])){els[i].click();return "clicked:"+((els[i].innerText||els[i].getAttribute("aria-label")||"?").substring(0,30));}' +
    '    }' +
    '    return "not_found";' +
    '  }' +
    '  var r=findAndClick(function(el){' +
    '    var t=(el.innerText||"").trim().toLowerCase();' +
    '    return (t==="export csv"||t==="export as csv"||t==="download csv");' +
    '  });' +
    '  if(r!=="not_found")return r;' +
    '  r=findAndClick(function(el){' +
    '    var t=(el.innerText||"").trim().toLowerCase();' +
    '    var a=(el.getAttribute("aria-label")||"").toLowerCase();' +
    '    return t.includes("export csv")||a.includes("export csv");' +
    '  });' +
    '  return r;' +
    '})()'
  );
  console.log('Click result:', clickResult);

  if (clickResult === 'not_found') {
    throw new Error(
      'Export CSV button not found. The UI may have changed.\n' +
      'Buttons visible: ' + buttons.map(b => `"${b.text || b.aria}"`).join(', ') + '\n' +
      'Open app.invintory.com/collection/bottles and look for the Export CSV option, then run again.'
    );
  }

  // 6. Wait for CSV to appear in Downloads
  console.log('Waiting for download...');
  let csvPath: string | null = null;
  for (let i = 0; i < 30; i++) {
    await sleep(1000);
    csvPath = findNewestInvintoryCSV(beforeDownload);
    if (csvPath) break;
    process.stdout.write('.');
  }
  console.log('');

  if (!csvPath) {
    throw new Error('Download timed out — no new CSV appeared in ~/Downloads within 30 seconds.');
  }
  console.log(`  Downloaded: ${csvPath}`);

  // 7. Import into cache
  console.log('Importing into cache...');
  const wines = importCSV(csvPath);
  saveCache(wines, csvPath);
  const summary = summarize(wines);

  console.log(`\nDone:`);
  console.log(`  Labels:       ${wines.length}`);
  console.log(`  Bottles:      ${summary.total_bottles}`);
  console.log(`  Market value: $${summary.total_market_value.toLocaleString()}`);
  console.log(`  Ready:        ${summary.ready_to_drink} bottles`);
}

main().catch(err => {
  console.error('Export failed:', err.message);
  process.exit(1);
});
