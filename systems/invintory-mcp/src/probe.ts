#!/usr/bin/env tsx
// ── Invintory Live API Probe ──────────────────────────────────────────────────
// Executes fetch calls from inside your live Chrome Invintory tab via AppleScript.
// Requires Chrome to be open with app.invintory.com logged in.
//
// Run: npx tsx src/probe.ts

import { execSync, execFileSync } from 'child_process';
import { writeFileSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

const CACHE_DIR = join(homedir(), '.config', 'invintory');
const PROBE_FILE = join(CACHE_DIR, 'probe.json');

const PROFILE_ID = 'FDi9sqylzBXcnR5Dk6vlPjanNC22';
const COLLECTION_ID = '63421';

// ── AppleScript executor ──────────────────────────────────────────────────────

function runInChrome(js: string): string {
  // Escape JS for AppleScript string embedding
  const escaped = js.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, ' ');
  const script = `
tell application "Google Chrome"
  repeat with w in windows
    repeat with t in tabs of w
      if URL of t contains "invintory.com" then
        set result to execute t javascript "${escaped}"
        return result
      end if
    end repeat
  end repeat
  return "TAB_NOT_FOUND"
end tell`;

  const tmp = '/tmp/invintory-probe.applescript';
  writeFileSync(tmp, script);
  try {
    return execSync(`osascript ${tmp}`, { encoding: 'utf8', timeout: 30000 }).trim();
  } finally {
    try { execSync(`rm -f ${tmp}`); } catch { /* ignore */ }
  }
}

// ── Run a fetch from inside the page and return parsed JSON ───────────────────

async function pageF(url: string, opts: Record<string, unknown> = {}): Promise<{ status: number; body: string; error?: string }> {
  const optsJson = JSON.stringify(opts).replace(/"/g, '\\"');
  const js = `
(async () => {
  try {
    const res = await fetch("${url}", ${optsJson});
    const body = await res.text();
    return JSON.stringify({ status: res.status, body: body.substring(0, 4000), headers: Object.fromEntries(res.headers.entries()) });
  } catch(e) {
    return JSON.stringify({ status: 0, body: '', error: String(e) });
  }
})()`;

  const raw = runInChrome(js);
  try {
    return JSON.parse(raw) as { status: number; body: string; error?: string };
  } catch {
    return { status: 0, body: raw, error: 'Could not parse response' };
  }
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  console.log('Checking for Invintory tab in Chrome...');
  const tabCheck = runInChrome('document.location.href');
  if (tabCheck === 'TAB_NOT_FOUND') {
    console.error('No Invintory tab found in Chrome. Open app.invintory.com and log in first.');
    process.exit(1);
  }
  console.log(`  Found tab: ${tabCheck}`);

  // Extract Firebase token and get current user info
  console.log('\nExtracting auth state from page...');
  const authRaw = runInChrome(`
    (() => {
      const key = Object.keys(sessionStorage).find(k => k.includes('firebase:authUser'));
      if (!key) return JSON.stringify({ error: 'no firebase auth in sessionStorage' });
      const auth = JSON.parse(sessionStorage.getItem(key));
      return JSON.stringify({
        uid: auth.uid,
        email: auth.email,
        token_preview: auth.stsTokenManager?.accessToken?.substring(0, 40) + '...',
        token_expires: new Date(auth.stsTokenManager?.expirationTime).toISOString(),
        provider: auth.providerData?.[0]?.providerId
      });
    })()`);

  let authInfo: Record<string, string> = {};
  try { authInfo = JSON.parse(authRaw); } catch { authInfo = { raw: authRaw }; }
  console.log('  Auth:', JSON.stringify(authInfo, null, 2).split('\n').join('\n  '));

  const results: Record<string, unknown> = { tab_url: tabCheck, auth: authInfo, tests: [] };
  const tests = results.tests as Array<{ name: string; url: string; status: number; body: string; error?: string }>;

  // ── Test 1: Profile endpoint ────────────────────────────────────────────────
  console.log('\n[1] Testing profile endpoint...');
  const profileUrl = `https://api.invintorywines.com/v3/profiles/${PROFILE_ID}`;
  const t1 = await pageF(profileUrl, { credentials: 'include' });
  console.log(`    HTTP ${t1.status}${t1.error ? ' — ' + t1.error : ''}`);
  if (t1.status === 200) console.log(`    Body preview: ${t1.body.slice(0, 120)}`);
  tests.push({ name: 'profile (credentials:include)', url: profileUrl, ...t1 });

  // ── Test 2: Profile with Firebase Bearer token ──────────────────────────────
  console.log('\n[2] Testing profile with Bearer token...');
  const tokenJs = `
    (() => {
      const key = Object.keys(sessionStorage).find(k => k.includes('firebase:authUser'));
      if (!key) return '';
      const auth = JSON.parse(sessionStorage.getItem(key));
      return auth.stsTokenManager?.accessToken ?? '';
    })()`;
  const idToken = runInChrome(tokenJs);

  const t2 = await pageF(profileUrl, {
    credentials: 'include',
    headers: { 'Authorization': `Bearer ${idToken}` },
  });
  console.log(`    HTTP ${t2.status}${t2.error ? ' — ' + t2.error : ''}`);
  if (t2.status === 200) console.log(`    Body preview: ${t2.body.slice(0, 120)}`);
  tests.push({ name: 'profile (Bearer + credentials:include)', url: profileUrl, ...t2 });

  // ── Test 3: Collection details ──────────────────────────────────────────────
  console.log('\n[3] Testing collection details...');
  const collUrl = `https://api.invintorywines.com/v3/collections/${COLLECTION_ID}/details`;
  const t3 = await pageF(collUrl, {
    credentials: 'include',
    headers: { 'Authorization': `Bearer ${idToken}` },
  });
  console.log(`    HTTP ${t3.status}${t3.error ? ' — ' + t3.error : ''}`);
  if (t3.status === 200) console.log(`    Body preview: ${t3.body.slice(0, 120)}`);
  tests.push({ name: 'collection details', url: collUrl, ...t3 });

  // ── Test 4: Bottles list ────────────────────────────────────────────────────
  console.log('\n[4] Testing bottles list...');
  const bottlesUrl = `https://api.invintorywines.com/v3/collections/${COLLECTION_ID}/bottles?page=1&limit=5`;
  const t4 = await pageF(bottlesUrl, {
    credentials: 'include',
    headers: { 'Authorization': `Bearer ${idToken}` },
  });
  console.log(`    HTTP ${t4.status}${t4.error ? ' — ' + t4.error : ''}`);
  if (t4.status === 200) console.log(`    Body preview: ${t4.body.slice(0, 200)}`);
  tests.push({ name: 'bottles list', url: bottlesUrl, ...t4 });

  // ── Test 5: Labels list ─────────────────────────────────────────────────────
  console.log('\n[5] Testing labels list...');
  const labelsUrl = `https://api.invintorywines.com/v3/collections/${COLLECTION_ID}/labels?page=1&limit=5`;
  const t5 = await pageF(labelsUrl, {
    credentials: 'include',
    headers: { 'Authorization': `Bearer ${idToken}` },
  });
  console.log(`    HTTP ${t5.status}${t5.error ? ' — ' + t5.error : ''}`);
  if (t5.status === 200) console.log(`    Body preview: ${t5.body.slice(0, 200)}`);
  tests.push({ name: 'labels list', url: labelsUrl, ...t5 });

  // ── Test 6: Check CORS headers on preflight ─────────────────────────────────
  console.log('\n[6] Checking CORS headers via OPTIONS preflight...');
  const corsJs = `
    (async () => {
      try {
        const res = await fetch("${profileUrl}", { method: 'OPTIONS', credentials: 'include' });
        return JSON.stringify({
          status: res.status,
          allow_origin: res.headers.get('access-control-allow-origin'),
          allow_headers: res.headers.get('access-control-allow-headers'),
          allow_methods: res.headers.get('access-control-allow-methods'),
        });
      } catch(e) { return JSON.stringify({ error: String(e) }); }
    })()`;
  const corsRaw = runInChrome(corsJs);
  let corsInfo: Record<string, string> = {};
  try { corsInfo = JSON.parse(corsRaw); } catch { corsInfo = { raw: corsRaw }; }
  console.log('    CORS:', JSON.stringify(corsInfo));
  (results as Record<string, unknown>).cors_preflight = corsInfo;

  // ── Save results ─────────────────────────────────────────────────────────────
  writeFileSync(PROBE_FILE, JSON.stringify(results, null, 2));
  console.log(`\n✓ Probe results saved to: ${PROBE_FILE}`);

  // ── Summary ──────────────────────────────────────────────────────────────────
  console.log('\n── Results ──────────────────────────────────────────────────');
  for (const t of tests) {
    const icon = t.status === 200 ? '✓' : t.status === 0 ? '✗' : '~';
    console.log(`${icon} [${t.status}] ${t.name}`);
    if (t.status === 200) {
      console.log(`      → LIVE ACCESS WORKS`);
    } else if (t.error) {
      console.log(`      → ${t.error.slice(0, 100)}`);
    }
  }

  const anySuccess = tests.some(t => t.status === 200);
  console.log(anySuccess
    ? '\n🟢 Live API access confirmed from browser context. Live MCP is viable.'
    : '\n🔴 All endpoints blocked. Live access requires server-side proxy or CSV path.'
  );
}

main().catch(err => {
  console.error('Probe failed:', err.message);
  process.exit(1);
});
