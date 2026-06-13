#!/usr/bin/env tsx
// ── Find the Export CSV button ────────────────────────────────────────────────
// Navigates to the collection page and dumps all button text/attributes
// so we can find the correct selector for the CSV export.
// Run: npx tsx src/probe.ts

import { chromium } from 'playwright';
import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

const CACHE_DIR = join(homedir(), '.config', 'invintory');
const TOKEN_FILE = join(CACHE_DIR, 'firebase-token.json');
const FIREBASE_API_KEY = 'AIzaSyDFYtBIYm-Z9HUbMTcB-4vP1FJMm7lX4LA';
const FIREBASE_SS_KEY = `firebase:authUser:${FIREBASE_API_KEY}:[DEFAULT]`;
const TOKEN_REFRESH_URL = `https://securetoken.googleapis.com/v1/token?key=${FIREBASE_API_KEY}`;
const PROFILE_DIR = join(CACHE_DIR, 'playwright-profile');

async function main() {
  const cached = JSON.parse(readFileSync(TOKEN_FILE, 'utf-8'));
  const res = await fetch(TOKEN_REFRESH_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `grant_type=refresh_token&refresh_token=${encodeURIComponent(cached.refreshToken)}`,
  });
  const data = await res.json() as any;
  const idToken: string = data.id_token;
  writeFileSync(TOKEN_FILE, JSON.stringify({ refreshToken: data.refresh_token, savedAt: new Date().toISOString() }, null, 2), { mode: 0o600 });

  const expirationTime = Date.now() + parseInt(data.expires_in) * 1000;
  const authState = JSON.stringify({
    uid: data.user_id, email: '', emailVerified: true, isAnonymous: false, providerData: [],
    stsTokenManager: { refreshToken: data.refresh_token, accessToken: idToken, expirationTime },
    createdAt: Date.now().toString(), lastLoginAt: Date.now().toString(),
    apiKey: FIREBASE_API_KEY, appName: '[DEFAULT]',
  });

  const context = await chromium.launchPersistentContext(PROFILE_DIR, {
    headless: false, channel: 'chrome', acceptDownloads: true,
  });
  await context.addInitScript((o: any) => {
    sessionStorage.setItem(o.key, o.value);
  }, { key: FIREBASE_SS_KEY, value: authState });

  const page = await context.newPage();
  console.log('Loading collection page...');
  await page.goto('https://app.invintory.com/collection/bottles', { waitUntil: 'load', timeout: 30000 });
  await page.waitForTimeout(5000);

  // Take screenshot to see what's on screen
  await page.screenshot({ path: join(CACHE_DIR, 'screenshot.png'), fullPage: false });
  console.log('Screenshot saved to:', join(CACHE_DIR, 'screenshot.png'));

  // Dump all buttons
  const buttons = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('button, [role="button"], a')).map((el: any) => ({
      tag: el.tagName,
      text: el.innerText?.trim().substring(0, 60),
      ariaLabel: el.getAttribute('aria-label'),
      title: el.getAttribute('title'),
      className: el.className?.substring(0, 80),
      id: el.id,
    })).filter(b => b.text || b.ariaLabel || b.title);
  });
  console.log('\nAll buttons/links:');
  buttons.forEach(b => console.log(`  [${b.tag}] text="${b.text}" aria="${b.ariaLabel}" title="${b.title}" id="${b.id}"`));

  // Look specifically for export-related elements
  const exportEls = await page.evaluate(() => {
    const all = Array.from(document.querySelectorAll('*'));
    return all
      .filter((el: any) => {
        const t = (el.innerText || el.textContent || '').toLowerCase();
        const a = (el.getAttribute('aria-label') || '').toLowerCase();
        return t.includes('export') || t.includes('csv') || a.includes('export') || a.includes('csv');
      })
      .map((el: any) => ({
        tag: el.tagName,
        text: (el.innerText || el.textContent || '').trim().substring(0, 60),
        ariaLabel: el.getAttribute('aria-label'),
        className: el.className?.substring(0, 60),
        visible: el.offsetParent !== null,
      }))
      .slice(0, 20);
  });
  console.log('\nExport-related elements:');
  exportEls.forEach(e => console.log(`  [${e.tag}] "${e.text}" aria="${e.ariaLabel}" visible=${e.visible}`));

  await context.close();
}

main().catch(err => { console.error('Failed:', err.message); process.exit(1); });
