#!/usr/bin/env tsx
// ── Invintory CSV Refresh ─────────────────────────────────────────────────────
// Fully automated. No manual steps after initial setup.
//
// Auth strategy:
//   1. Extract Firebase refresh token from Chrome (AppleScript, one-time per session)
//      OR use cached refresh token from disk
//   2. Exchange refresh token → fresh ID token via Firebase REST API
//   3. Inject auth into Playwright's sessionStorage
//   4. Headless Chrome navigates to Invintory, exports CSV
//   5. CSV imported into local JSON cache

import { chromium } from 'playwright';
import { existsSync, mkdirSync, writeFileSync, readFileSync, unlinkSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';
import { execSync } from 'child_process';
import { importCSV, saveCache, summarize } from './cache.js';

const CACHE_DIR = join(homedir(), '.config', 'invintory');
const CSV_PATH = join(CACHE_DIR, 'collection.csv');
const TOKEN_FILE = join(CACHE_DIR, 'firebase-token.json');

const FIREBASE_API_KEY = 'AIzaSyDFYtBIYm-Z9HUbMTcB-4vP1FJMm7lX4LA';
const FIREBASE_SS_KEY = `firebase:authUser:${FIREBASE_API_KEY}:[DEFAULT]`;
const TOKEN_REFRESH_URL = `https://securetoken.googleapis.com/v1/token?key=${FIREBASE_API_KEY}`;

const INVINTORY_URL = 'https://app.invintory.com';

// ── Token management ──────────────────────────────────────────────────────────

interface CachedToken {
  refreshToken: string;
  savedAt: string;
}

interface FirebaseAuthState {
  uid: string;
  email: string;
  emailVerified: boolean;
  displayName?: string;
  isAnonymous: boolean;
  providerData: unknown[];
  stsTokenManager: {
    refreshToken: string;
    accessToken: string;
    expirationTime: number;
  };
  createdAt: string;
  lastLoginAt: string;
  apiKey: string;
  appName: string;
}

function loadCachedToken(): string | null {
  if (!existsSync(TOKEN_FILE)) return null;
  try {
    const data: CachedToken = JSON.parse(readFileSync(TOKEN_FILE, 'utf-8'));
    return data.refreshToken || null;
  } catch {
    return null;
  }
}

function saveCachedToken(refreshToken: string): void {
  const data: CachedToken = { refreshToken, savedAt: new Date().toISOString() };
  writeFileSync(TOKEN_FILE, JSON.stringify(data, null, 2), { mode: 0o600 });
}

function extractFromChrome(): string {
  // Write AppleScript to temp file — avoids shell escaping issues with the Firebase key
  // Searches all Chrome tabs for an Invintory tab (not just the active one)
  const tmpScript = '/tmp/invintory-extract.applescript';
  writeFileSync(tmpScript, `tell application "Google Chrome"\n  repeat with w in windows\n    repeat with t in tabs of w\n      if URL of t contains "invintory.com" then\n        return execute t javascript "JSON.stringify(sessionStorage.getItem('${FIREBASE_SS_KEY}'))"\n      end if\n    end repeat\n  end repeat\n  return "NOT_FOUND"\nend tell\n`);

  let raw: string;
  try {
    raw = execSync(`osascript ${tmpScript}`, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
  } finally {
    try { unlinkSync(tmpScript); } catch { /* ignore */ }
  }

  // AppleScript returns "missing value" for null; JSON.stringify returns the string "null"
  if (!raw || raw === 'missing value' || raw === 'null' || raw === 'NOT_FOUND') {
    throw new Error(
      'Invintory session not found in Chrome. ' +
      'Open app.invintory.com in Chrome and ensure you are logged in.'
    );
  }

  // Result is JSON.stringify of the sessionStorage value (which is itself a JSON string)
  // Parse once to get inner JSON string, then parse again to get auth object
  let inner: string;
  try {
    inner = JSON.parse(raw);
  } catch {
    inner = raw;
  }

  let authState: FirebaseAuthState;
  try {
    authState = JSON.parse(inner);
  } catch {
    throw new Error('Could not parse Firebase auth state from Chrome sessionStorage.');
  }

  const refreshToken = authState?.stsTokenManager?.refreshToken;
  if (!refreshToken) throw new Error('Firebase auth state has no refresh token.');

  return refreshToken;
}

async function getFreshIdToken(refreshToken: string): Promise<{ idToken: string; newRefreshToken: string; authState: string }> {
  const res = await fetch(TOKEN_REFRESH_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `grant_type=refresh_token&refresh_token=${encodeURIComponent(refreshToken)}`,
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Firebase token refresh failed (${res.status}): ${body}`);
  }

  const data = await res.json() as {
    access_token: string;
    refresh_token: string;
    id_token: string;
    expires_in: string;
    user_id: string;
    token_type: string;
  };

  // Build the sessionStorage value that Invintory's Firebase SDK expects
  const expirationTime = Date.now() + parseInt(data.expires_in) * 1000;
  const authState: FirebaseAuthState = {
    uid: data.user_id,
    email: '',          // populated by Firebase SDK from token
    emailVerified: true,
    isAnonymous: false,
    providerData: [],
    stsTokenManager: {
      refreshToken: data.refresh_token,
      accessToken: data.id_token,
      expirationTime,
    },
    createdAt: Date.now().toString(),
    lastLoginAt: Date.now().toString(),
    apiKey: FIREBASE_API_KEY,
    appName: '[DEFAULT]',
  };

  return {
    idToken: data.id_token,
    newRefreshToken: data.refresh_token,
    authState: JSON.stringify(authState),
  };
}

// ── Export navigation ─────────────────────────────────────────────────────────

async function findAndClickExport(page: import('playwright').Page): Promise<void> {
  const attempts = [
    async () => {
      await page.goto(`${INVINTORY_URL}/settings`, { waitUntil: 'load', timeout: 20000 });
      for (const locator of [
        page.getByRole('button', { name: /export/i }),
        page.getByRole('link', { name: /export/i }),
        page.getByText(/export/i),
      ]) {
        if (await locator.first().isVisible({ timeout: 2000 }).catch(() => false)) {
          await locator.first().click();
          return true;
        }
      }
      return false;
    },
    async () => {
      await page.goto(INVINTORY_URL, { waitUntil: 'load', timeout: 20000 });
      const menuTriggers = [
        page.getByRole('button', { name: /menu/i }),
        page.locator('[aria-label*="menu" i]').first(),
        page.locator('button[aria-haspopup="true"]').first(),
      ];
      for (const trigger of menuTriggers) {
        if (await trigger.isVisible({ timeout: 1000 }).catch(() => false)) {
          await trigger.click();
          await page.waitForTimeout(400);
          const item = page.getByRole('menuitem', { name: /export/i }).first();
          if (await item.isVisible({ timeout: 2000 }).catch(() => false)) {
            await item.click();
            return true;
          }
        }
      }
      return false;
    },
    async () => {
      const el = page.getByText(/export/i).first();
      if (await el.isVisible({ timeout: 3000 }).catch(() => false)) {
        await el.click();
        return true;
      }
      return false;
    },
  ];

  for (const attempt of attempts) {
    if (await attempt()) return;
  }

  throw new Error('Could not find Export button in Invintory. The UI may have changed.');
}

async function downloadCSV(page: import('playwright').Page): Promise<string> {
  await page.waitForTimeout(800);

  const csvBtn = page.getByRole('button', { name: /csv/i })
    .or(page.getByText(/export.*csv/i))
    .or(page.getByText(/csv/i))
    .first();

  if (await csvBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 30000 }),
      csvBtn.click(),
    ]);
    await download.saveAs(CSV_PATH);
    console.log(`  Saved: ${CSV_PATH}`);
    return CSV_PATH;
  }

  throw new Error('Export dialog opened but CSV option not found. Invintory UI may have changed.');
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  const csvFlagIdx = process.argv.indexOf('--csv');
  if (csvFlagIdx !== -1 && process.argv[csvFlagIdx + 1]) {
    importAndReport(process.argv[csvFlagIdx + 1]);
    return;
  }

  if (!existsSync(CACHE_DIR)) mkdirSync(CACHE_DIR, { recursive: true, mode: 0o700 });

  // Step 1: Get refresh token (cached or from Chrome)
  let refreshToken = loadCachedToken();
  if (refreshToken) {
    console.log('Using cached refresh token...');
  } else {
    console.log('No cached token — extracting from Chrome...');
    refreshToken = extractFromChrome();
    saveCachedToken(refreshToken);
    console.log('  Token cached to disk.');
  }

  // Step 2: Exchange for fresh ID token
  console.log('Refreshing Firebase ID token...');
  let idToken: string;
  let authStateJson: string;
  let newRefreshToken: string;

  try {
    ({ idToken, authState: authStateJson, newRefreshToken } = await getFreshIdToken(refreshToken));
    // Always save latest refresh token (Firebase may rotate it)
    saveCachedToken(newRefreshToken);
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    if (msg.includes('TOKEN_EXPIRED') || msg.includes('INVALID_REFRESH_TOKEN')) {
      console.log('  Cached token expired. Re-extracting from Chrome...');
      refreshToken = extractFromChrome();
      saveCachedToken(refreshToken);
      ({ idToken, authState: authStateJson, newRefreshToken } = await getFreshIdToken(refreshToken));
      saveCachedToken(newRefreshToken);
    } else {
      throw err;
    }
  }

  console.log('  ID token obtained.');

  // Step 3: Launch Playwright with persistent profile (preserves auth cookies across runs)
  const PROFILE_DIR = join(CACHE_DIR, 'playwright-profile');
  console.log('Launching browser...');

  const context = await chromium.launchPersistentContext(PROFILE_DIR, {
    headless: true,
    channel: 'chrome',
    acceptDownloads: true,
    downloadsPath: CACHE_DIR,
  });

  // Inject Firebase auth into sessionStorage before any page scripts run
  await context.addInitScript(({ key, value }: { key: string; value: string }) => {
    sessionStorage.setItem(key, value);
  }, { key: FIREBASE_SS_KEY, value: authStateJson });

  const page = await context.newPage();

  try {
    await page.goto(`${INVINTORY_URL}/collection/bottles?page=1&limit=50`, {
      waitUntil: 'load',
      timeout: 30000,
    });
    await page.waitForTimeout(4000);

    if (page.url().includes('/login')) {
      throw new Error(
        'Still on login page after injecting auth. ' +
        'Open app.invintory.com in Chrome, log in, then retry.'
      );
    }

    console.log('Authenticated. Triggering CSV export...');

    const [download] = await Promise.all([
      page.waitForEvent('download', { timeout: 30000 }),
      page.getByRole('button', { name: /export csv/i }).click(),
    ]);

    await download.saveAs(CSV_PATH);
    console.log(`  Saved: ${CSV_PATH}`);
    importAndReport(CSV_PATH);

  } finally {
    await context.close();
  }
}

function importAndReport(csvFile: string) {
  console.log('Importing into cache...');
  const wines = importCSV(csvFile);
  saveCache(wines, csvFile);
  const summary = summarize(wines);
  console.log(`\nCache refreshed:`);
  console.log(`  Labels:       ${wines.length}`);
  console.log(`  Bottles:      ${summary.total_bottles}`);
  console.log(`  Market value: $${summary.total_market_value.toLocaleString()}`);
  console.log(`  Ready:        ${summary.ready_to_drink} bottles`);
}

main().catch(err => {
  console.error('Refresh failed:', err.message);
  process.exit(1);
});
