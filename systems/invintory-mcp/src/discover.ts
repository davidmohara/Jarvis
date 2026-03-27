#!/usr/bin/env tsx
// ── Invintory API Discovery ───────────────────────────────────────────────────
// Launches a headed browser, intercepts all network traffic on app.invintory.com,
// and dumps captured requests + cookies to ~/.config/invintory/discovery.json.
//
// Run: npx tsx src/discover.ts
//
// What this captures:
//   - All _server RPC calls (SolidStart server functions) — URL, body, response
//   - All api.invintorywines.com calls the SSR makes (via response body)
//   - Session cookies after login
//   - Firebase token in sessionStorage
//
// Goal: determine if we can call _server endpoints directly with a session cookie
// to get live data without Playwright, or if full browser automation is required.

import { chromium } from 'playwright';
import { existsSync, mkdirSync, writeFileSync, readFileSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

const CACHE_DIR = join(homedir(), '.config', 'invintory');
const DISCOVERY_FILE = join(CACHE_DIR, 'discovery.json');
const TOKEN_FILE = join(CACHE_DIR, 'firebase-token.json');
const PROFILE_DIR = join(CACHE_DIR, 'playwright-profile');

const FIREBASE_API_KEY = 'AIzaSyDFYtBIYm-Z9HUbMTcB-4vP1FJMm7lX4LA';
const FIREBASE_SS_KEY = `firebase:authUser:${FIREBASE_API_KEY}:[DEFAULT]`;
const TOKEN_REFRESH_URL = `https://securetoken.googleapis.com/v1/token?key=${FIREBASE_API_KEY}`;
const INVINTORY_URL = 'https://app.invintory.com';

interface CapturedRequest {
  url: string;
  method: string;
  requestHeaders: Record<string, string>;
  requestBody: string | null;
  status: number;
  responseHeaders: Record<string, string>;
  responseBody: string | null;
  timestamp: string;
}

interface DiscoveryReport {
  captured_at: string;
  cookies: Array<{ name: string; value: string; domain: string; path: string; httpOnly: boolean; secure: boolean }>;
  firebase_auth_state: Record<string, unknown> | null;
  server_rpc_calls: CapturedRequest[];
  api_calls_observed: CapturedRequest[];
  other_auth_calls: CapturedRequest[];
  direct_api_test: {
    used_token: string;
    response_status: number;
    response_body: string;
  } | null;
}

async function tryGetRefreshToken(): Promise<string | null> {
  if (!existsSync(TOKEN_FILE)) return null;
  try {
    const data = JSON.parse(readFileSync(TOKEN_FILE, 'utf-8'));
    return data.refreshToken ?? null;
  } catch { return null; }
}

async function getFreshIdToken(refreshToken: string): Promise<string | null> {
  try {
    const res = await fetch(TOKEN_REFRESH_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `grant_type=refresh_token&refresh_token=${encodeURIComponent(refreshToken)}`,
    });
    if (!res.ok) return null;
    const data = await res.json() as { id_token: string; refresh_token: string };
    // Save updated refresh token
    writeFileSync(TOKEN_FILE, JSON.stringify({ refreshToken: data.refresh_token, savedAt: new Date().toISOString() }, null, 2), { mode: 0o600 });
    return data.id_token;
  } catch { return null; }
}

async function testDirectApiCall(idToken: string): Promise<NonNullable<DiscoveryReport['direct_api_test']>> {
  const profileId = 'FDi9sqylzBXcnR5Dk6vlPjanNC22';
  const url = `https://api.invintorywines.com/v3/profiles/${profileId}`;
  try {
    const res = await fetch(url, {
      headers: { 'Authorization': `Bearer ${idToken}` },
    });
    const body = await res.text();
    return {
      used_token: idToken.slice(0, 40) + '...',
      response_status: res.status,
      response_body: body.slice(0, 500),
    };
  } catch (err) {
    return {
      used_token: idToken.slice(0, 40) + '...',
      response_status: 0,
      response_body: err instanceof Error ? err.message : String(err),
    };
  }
}

async function main() {
  if (!existsSync(CACHE_DIR)) mkdirSync(CACHE_DIR, { recursive: true, mode: 0o700 });

  const report: DiscoveryReport = {
    captured_at: new Date().toISOString(),
    cookies: [],
    firebase_auth_state: null,
    server_rpc_calls: [],
    api_calls_observed: [],
    other_auth_calls: [],
    direct_api_test: null,
  };

  // Try to get a fresh ID token from cached refresh token
  let idToken: string | null = null;
  const refreshToken = await tryGetRefreshToken();
  if (refreshToken) {
    console.log('Refreshing Firebase ID token from cache...');
    idToken = await getFreshIdToken(refreshToken);
    if (idToken) console.log('  ID token ready.');
    else console.log('  Refresh failed — will extract from browser session.');
  }

  console.log('\nLaunching browser (headed — sign in if prompted)...');
  console.log('Navigate around your collection to trigger API calls, then close the browser.\n');

  const context = await chromium.launchPersistentContext(PROFILE_DIR, {
    headless: false,
    channel: 'chrome',
    acceptDownloads: true,
  });

  // Inject Firebase auth if we have a token
  if (idToken) {
    const expirationTime = Date.now() + 3600 * 1000;
    const authState = JSON.stringify({
      uid: 'FDi9sqylzBXcnR5Dk6vlPjanNC22',
      email: '',
      emailVerified: true,
      isAnonymous: false,
      providerData: [],
      stsTokenManager: { refreshToken, accessToken: idToken, expirationTime },
      createdAt: Date.now().toString(),
      lastLoginAt: Date.now().toString(),
      apiKey: FIREBASE_API_KEY,
      appName: '[DEFAULT]',
    });
    await context.addInitScript(({ key, value }: { key: string; value: string }) => {
      sessionStorage.setItem(key, value);
    }, { key: FIREBASE_SS_KEY, value: authState });
  }

  const page = await context.newPage();

  // ── Intercept network traffic ──────────────────────────────────────────────

  page.on('response', async (response) => {
    const url = response.url();
    const method = response.request().method();
    const status = response.status();

    const isServerRpc = url.includes('/_server') || url.includes('/_rpc');
    const isInvintoryApi = url.includes('api.invintorywines.com');
    const isAuthCall = url.includes('googleapis.com') || url.includes('identitytoolkit') || url.includes('securetoken');

    if (!isServerRpc && !isInvintoryApi && !isAuthCall) return;

    let responseBody: string | null = null;
    try {
      const buffer = await response.body();
      const text = buffer.toString('utf-8');
      // Only keep up to 8KB per response
      responseBody = text.length > 8192 ? text.slice(0, 8192) + '\n... [truncated]' : text;
    } catch { /* body may not be readable */ }

    let requestBody: string | null = null;
    try {
      requestBody = response.request().postData() ?? null;
    } catch { /* ignore */ }

    const captured: CapturedRequest = {
      url,
      method,
      requestHeaders: response.request().headers(),
      requestBody,
      status,
      responseHeaders: response.headers(),
      responseBody,
      timestamp: new Date().toISOString(),
    };

    if (isServerRpc) {
      console.log(`  [_server] ${method} ${url.replace(INVINTORY_URL, '')} → ${status}`);
      report.server_rpc_calls.push(captured);
    } else if (isInvintoryApi) {
      console.log(`  [api]     ${method} ${url} → ${status}`);
      report.api_calls_observed.push(captured);
    } else if (isAuthCall) {
      console.log(`  [auth]    ${method} ${url.split('?')[0]} → ${status}`);
      report.other_auth_calls.push(captured);
    }
  });

  // Navigate to collection
  await page.goto(`${INVINTORY_URL}/collection/bottles?page=1&limit=50`, {
    waitUntil: 'load',
    timeout: 30000,
  });

  // Check if we landed on login
  if (page.url().includes('/login')) {
    console.log('\n⚠ Login page detected. Please sign in with Apple — the browser is open.');
    console.log('Waiting up to 2 minutes for authentication...\n');
    await page.waitForURL((url) => !url.toString().includes('/login'), { timeout: 120000 });
    console.log('  Authenticated. Navigating to collection...');
    await page.goto(`${INVINTORY_URL}/collection/bottles?page=1&limit=50`, {
      waitUntil: 'load',
      timeout: 30000,
    });
  }

  // Wait for page to settle and API calls to fire
  console.log('\nCollection loaded. Waiting 5 seconds for all API calls to complete...');
  await page.waitForTimeout(5000);

  // Try client-side navigation (click links) to trigger _server RPC calls
  console.log('Trying client-side navigation to trigger _server calls...');
  try {
    const labelsLink = page.getByRole('link', { name: /labels/i }).first()
      .or(page.locator('a[href*="/labels"]').first())
      .or(page.locator('nav a').nth(1));
    if (await labelsLink.isVisible({ timeout: 3000 }).catch(() => false)) {
      await labelsLink.click();
      await page.waitForTimeout(3000);
      console.log('  Clicked labels link (client-side nav)');
    } else {
      // Fall back to goto
      await page.goto(`${INVINTORY_URL}/collection/labels`, { waitUntil: 'load', timeout: 20000 });
      await page.waitForTimeout(3000);
    }
  } catch {
    await page.goto(`${INVINTORY_URL}/collection/labels`, { waitUntil: 'load', timeout: 20000 });
    await page.waitForTimeout(3000);
  }

  // Also broaden the net — capture ALL requests on second pass
  console.log('Capturing all requests (broad net)...');
  const allRequests: Array<{ url: string; method: string; status: number; body: string }> = [];
  page.on('response', async (response) => {
    const url = response.url();
    if (!url.includes('invintory') && !url.includes('googleapis') && !url.includes('pusher')) return;
    if (url.includes('font') || url.includes('.png') || url.includes('.svg')) return;
    let body = '';
    try { body = (await response.body()).toString('utf-8').slice(0, 2000); } catch { /* ignore */ }
    allRequests.push({ url, method: response.request().method(), status: response.status(), body });
  });

  // Try fetch from inside the browser using the page's auth context
  console.log('Testing fetch from inside browser context...');
  const inBrowserResults = await page.evaluate(async (profileId: string) => {
    const results: Array<{ url: string; status: number; body: string; error?: string }> = [];
    const endpoints = [
      `https://api.invintorywines.com/v3/profiles/${profileId}`,
      `https://api.invintorywines.com/v3/collections/63421/details`,
    ];
    // Get Firebase token from sessionStorage
    const authKey = Object.keys(sessionStorage).find(k => k.includes('firebase:authUser'));
    let token = '';
    if (authKey) {
      try {
        const auth = JSON.parse(sessionStorage.getItem(authKey) ?? '{}');
        token = auth?.stsTokenManager?.accessToken ?? '';
      } catch { /* ignore */ }
    }
    for (const url of endpoints) {
      try {
        const res = await fetch(url, {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {},
          credentials: 'include',
        });
        const body = await res.text();
        results.push({ url, status: res.status, body: body.slice(0, 500) });
      } catch (err) {
        results.push({ url, status: 0, body: '', error: String(err) });
      }
    }
    return results;
  }, 'FDi9sqylzBXcnR5Dk6vlPjanNC22');

  console.log('\nIn-browser fetch results:');
  for (const r of inBrowserResults) {
    console.log(`  ${r.url.replace('https://api.invintorywines.com', '')} → HTTP ${r.status}${r.error ? ' ERROR: ' + r.error : ''}`);
  }

  // Store in report
  (report as unknown as Record<string, unknown>).in_browser_fetch = inBrowserResults;
  (report as unknown as Record<string, unknown>).all_requests_broad = allRequests;

  await page.waitForTimeout(2000);

  // Extract Firebase auth state from sessionStorage
  try {
    const authStateRaw = await page.evaluate((key: string) => sessionStorage.getItem(key), FIREBASE_SS_KEY);
    if (authStateRaw) {
      report.firebase_auth_state = JSON.parse(authStateRaw) as Record<string, unknown>;
      // Extract refresh token for future use
      const mgr = (report.firebase_auth_state?.stsTokenManager as Record<string, unknown>);
      if (mgr?.refreshToken && typeof mgr.refreshToken === 'string') {
        writeFileSync(TOKEN_FILE, JSON.stringify({
          refreshToken: mgr.refreshToken,
          savedAt: new Date().toISOString(),
        }, null, 2), { mode: 0o600 });
        console.log('\n  Firebase refresh token extracted and cached.');
        // Use the access token for direct API test
        if (mgr.accessToken && typeof mgr.accessToken === 'string') {
          idToken = mgr.accessToken;
        }
      }
    }
  } catch { /* ignore */ }

  // Extract all cookies
  const cookies = await context.cookies();
  report.cookies = cookies.map(c => ({
    name: c.name,
    value: c.value,
    domain: c.domain,
    path: c.path,
    httpOnly: c.httpOnly,
    secure: c.secure,
  }));
  console.log(`\n  Captured ${report.cookies.length} cookies`);
  console.log(`  Captured ${report.server_rpc_calls.length} _server RPC calls`);
  console.log(`  Captured ${report.api_calls_observed.length} direct API calls`);

  await context.close();

  // Test direct API call with captured token
  if (idToken) {
    console.log('\nTesting direct API call with Firebase token...');
    const apiResult = await testDirectApiCall(idToken);
    report.direct_api_test = apiResult;
    console.log(`  Direct API test: HTTP ${apiResult.response_status}`);
  }

  // Save report
  writeFileSync(DISCOVERY_FILE, JSON.stringify(report, null, 2));
  console.log(`\n✓ Discovery report saved to: ${DISCOVERY_FILE}`);

  // Print summary
  console.log('\n── Summary ──────────────────────────────────────────────────');
  console.log(`Cookies:          ${report.cookies.length} (${report.cookies.filter(c => c.httpOnly).length} httpOnly)`);
  console.log(`_server calls:    ${report.server_rpc_calls.length}`);
  console.log(`Direct API calls: ${report.api_calls_observed.length}`);
  const apiTest = report.direct_api_test;
  if (apiTest) {
    console.log(`Direct API test:  HTTP ${apiTest.response_status} — ${
      apiTest.response_status === 200 ? '✓ WORKS — live client is viable!' :
      apiTest.response_status === 401 ? '✗ Unauthorized (Cloudflare blocking)' :
      apiTest.response_status === 403 ? '✗ Forbidden' :
      apiTest.response_status === 0 ? '✗ Network error (CORS/blocked)' :
      `✗ HTTP ${apiTest.response_status}`
    }`);
  }
  if (report.server_rpc_calls.length > 0) {
    console.log('\n_server endpoints captured:');
    const seen = new Set<string>();
    for (const call of report.server_rpc_calls) {
      const key = `${call.method} ${call.url.replace(INVINTORY_URL, '')}`;
      if (!seen.has(key)) { console.log(`  ${key}`); seen.add(key); }
    }
  }
  console.log('\nFull details in discovery.json for analysis.');
}

main().catch(err => {
  console.error('Discovery failed:', err.message);
  process.exit(1);
});
