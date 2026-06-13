// ── Invintory Live API Client ────────────────────────────────────────────────
// Fetches collection data directly from the Invintory REST API.
// Uses the cached Firebase refresh token to obtain a fresh ID token,
// then calls GET /v3/collections/{id}/labels with pagination.
//
// Auth flow:
//   cached refresh token → POST securetoken.googleapis.com/v1/token → ID token
//   GET api.invintorywines.com/v3/collections/63421/labels?limit=200&page=N
//   → Wine[] (transformed from API shape)

import { existsSync, readFileSync, writeFileSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';
import * as https from 'https';
import type { Wine, WineType, DrinkStatus } from './types.js';

// ── fetch polyfill using node:https ──────────────────────────────────────────
// Native fetch may not be available in all Node versions / MCP runtime contexts.

interface FetchResponse {
  ok: boolean;
  status: number;
  text: () => Promise<string>;
  json: () => Promise<unknown>;
}

function httpsRequest(url: string, options: https.RequestOptions, body?: string): Promise<FetchResponse> {
  return new Promise((resolve, reject) => {
    const req = https.request(url, options, (res) => {
      const chunks: Buffer[] = [];
      res.on('data', (chunk: Buffer) => chunks.push(chunk));
      res.on('end', () => {
        const raw = Buffer.concat(chunks).toString('utf-8');
        const status = res.statusCode ?? 0;
        resolve({
          ok: status >= 200 && status < 300,
          status,
          text: async () => raw,
          json: async () => JSON.parse(raw),
        });
      });
      res.on('error', reject);
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

async function fetchPost(url: string, body: string, contentType: string): Promise<FetchResponse> {
  const parsed = new URL(url);
  return httpsRequest(url, {
    hostname: parsed.hostname,
    path: parsed.pathname + parsed.search,
    method: 'POST',
    headers: {
      'Content-Type': contentType,
      'Content-Length': Buffer.byteLength(body),
    },
  }, body);
}

async function fetchGet(url: string, headers: Record<string, string>): Promise<FetchResponse> {
  const parsed = new URL(url);
  return httpsRequest(url, {
    hostname: parsed.hostname,
    path: parsed.pathname + parsed.search,
    method: 'GET',
    headers,
  });
}

const CACHE_DIR = join(homedir(), '.config', 'invintory');
const TOKEN_FILE = join(CACHE_DIR, 'firebase-token.json');

const FIREBASE_API_KEY = 'AIzaSyDFYtBIYm-Z9HUbMTcB-4vP1FJMm7lX4LA';
const TOKEN_REFRESH_URL = `https://securetoken.googleapis.com/v1/token?key=${FIREBASE_API_KEY}`;

const API_BASE = 'https://api.invintorywines.com/v3';
const COLLECTION_ID = '63421';
const PAGE_LIMIT = 200;

// ── Token management ──────────────────────────────────────────────────────────

interface CachedToken {
  refreshToken: string;
  savedAt: string;
}

interface FirebaseTokenResponse {
  access_token: string;
  refresh_token: string;
  id_token: string;
  expires_in: string;
  user_id: string;
  token_type: string;
}

function loadRefreshToken(): string | null {
  if (!existsSync(TOKEN_FILE)) return null;
  try {
    const data: CachedToken = JSON.parse(readFileSync(TOKEN_FILE, 'utf-8'));
    return data.refreshToken || null;
  } catch {
    return null;
  }
}

function saveRefreshToken(refreshToken: string): void {
  const data: CachedToken = { refreshToken, savedAt: new Date().toISOString() };
  writeFileSync(TOKEN_FILE, JSON.stringify(data, null, 2), { mode: 0o600 });
}

async function getIdToken(refreshToken: string): Promise<{ idToken: string; newRefreshToken: string }> {
  const body = `grant_type=refresh_token&refresh_token=${encodeURIComponent(refreshToken)}`;
  const res = await fetchPost(TOKEN_REFRESH_URL, body, 'application/x-www-form-urlencoded');

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Firebase token refresh failed (${res.status}): ${body}`);
  }

  const data = await res.json() as FirebaseTokenResponse;
  return { idToken: data.id_token, newRefreshToken: data.refresh_token };
}

// ── API response types ────────────────────────────────────────────────────────

interface ApiLabel {
  id?: string | number;
  name?: string;
  wine_name?: string;
  vintage?: number | string | null;
  wine_type?: string;
  type?: string;
  grapes?: string[] | string;
  grape_varieties?: string[] | string;
  producer?: string;
  winery?: string;
  country?: string;
  region?: string;
  sub_region?: string;
  subregion?: string;
  bottle_size?: string;
  size?: string;
  quantity?: number;
  bottles?: number;
  market_price?: number | string | null;
  market_value?: number | string | null;
  purchase_price?: number | string | null;
  average_purchase_price?: number | string | null;
  drink_window_start?: number | string | null;
  drink_window_end?: number | string | null;
  drink_from?: number | string | null;
  drink_until?: number | string | null;
  cellar?: string;
  storage?: string;
  location?: string;
  tags?: string[] | string;
}

interface ApiResponse {
  data?: ApiLabel[];
  labels?: ApiLabel[];
  items?: ApiLabel[];
  results?: ApiLabel[];
  total?: number;
  total_count?: number;
  page?: number;
  pages?: number;
  has_more?: boolean;
}

// ── Data transformation ───────────────────────────────────────────────────────

function normalizeType(raw: string | undefined): WineType {
  if (!raw) return 'unknown';
  const lower = raw.toLowerCase().trim();
  if (lower === 'red') return 'red';
  if (lower === 'white') return 'white';
  if (lower === 'rose' || lower === 'rosé' || lower === 'rosé') return 'rose';
  if (lower === 'sparkling') return 'sparkling';
  if (lower === 'fortified') return 'fortified';
  if (lower === 'dessert') return 'dessert';
  return 'unknown';
}

function computeDrinkStatus(start: number | null, end: number | null): DrinkStatus {
  if (!start && !end) return 'unknown';
  const year = new Date().getFullYear();
  if (end && year > end) return 'past_window';
  if (end && year >= end - 1) return 'expiring_soon';
  if (start && year >= start) return 'ready';
  return 'hold';
}

function toNum(val: number | string | null | undefined): number | null {
  if (val === null || val === undefined || val === '') return null;
  const n = typeof val === 'number' ? val : parseFloat(String(val));
  return isNaN(n) ? null : n;
}

function toInt(val: number | string | null | undefined): number | null {
  const n = toNum(val);
  return n === null ? null : Math.round(n);
}

function toStrArray(val: string[] | string | undefined): string[] {
  if (!val) return [];
  if (Array.isArray(val)) return val.filter(Boolean);
  return val.split(',').map(s => s.trim()).filter(Boolean);
}

function transformLabel(label: ApiLabel): Wine {
  const name = label.name ?? label.wine_name ?? '';
  const vintage = toInt(label.vintage);
  const type = normalizeType(label.wine_type ?? label.type);
  const grapes = toStrArray(label.grapes ?? label.grape_varieties);
  const producer = label.producer ?? label.winery ?? '';
  const country = label.country ?? '';
  const region = label.region ?? '';
  const subregion = label.sub_region ?? label.subregion ?? '';
  const size = label.bottle_size ?? label.size ?? '750ml';
  const quantity = toInt(label.quantity ?? label.bottles) ?? 1;
  const market_price = toNum(label.market_price ?? label.market_value);
  const purchase_price = toNum(label.purchase_price ?? label.average_purchase_price);
  const storage = label.cellar ?? label.storage ?? label.location ?? '';
  const tags = toStrArray(label.tags);

  // Drink window — try explicit start/end fields first, then range-style
  const drinkStart = toInt(label.drink_window_start ?? label.drink_from);
  const drinkEnd = toInt(label.drink_window_end ?? label.drink_until);

  return {
    name,
    vintage,
    type,
    grapes,
    producer,
    country,
    region,
    subregion,
    size,
    quantity,
    market_price,
    purchase_price,
    drink_window: { start: drinkStart, end: drinkEnd },
    drink_status: computeDrinkStatus(drinkStart, drinkEnd),
    storage,
    tags,
  };
}

// ── API pagination ────────────────────────────────────────────────────────────

function extractLabels(body: ApiResponse): ApiLabel[] {
  return body.data ?? body.labels ?? body.items ?? body.results ?? [];
}

function hasMorePages(body: ApiResponse, page: number, fetched: number): boolean {
  if (body.has_more === true) return true;
  if (body.pages && page < body.pages) return true;
  const total = body.total ?? body.total_count;
  if (total && fetched < total) return true;
  return false;
}

// ── Main export ───────────────────────────────────────────────────────────────

export interface LiveFetchResult {
  wines: Wine[];
  idToken: string;
}

/**
 * Fetch the full collection from the Invintory live API.
 * Requires a cached Firebase refresh token at ~/.config/invintory/firebase-token.json.
 * Paginates through all labels and returns a Wine[].
 */
export async function fetchLiveCollection(): Promise<LiveFetchResult> {
  // 1. Load cached refresh token
  const refreshToken = loadRefreshToken();
  if (!refreshToken) {
    throw new Error(
      'No Firebase refresh token cached. Open app.invintory.com in Chrome while logged in, ' +
      'then run the refresh script once to cache credentials.'
    );
  }

  // 2. Exchange for fresh ID token
  let idToken: string;
  let newRefreshToken: string;

  try {
    ({ idToken, newRefreshToken } = await getIdToken(refreshToken));
    saveRefreshToken(newRefreshToken);
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    if (msg.includes('TOKEN_EXPIRED') || msg.includes('INVALID_REFRESH_TOKEN') || msg.includes('400')) {
      throw new Error(
        'Firebase refresh token has expired. Open app.invintory.com in Chrome, log in, ' +
        'then run the refresh script to re-cache credentials.'
      );
    }
    throw err;
  }

  // 3. Paginate through all labels
  const allLabels: ApiLabel[] = [];
  let page = 1;
  let totalFetched = 0;

  while (true) {
    const url = `${API_BASE}/collections/${COLLECTION_ID}/labels?limit=${PAGE_LIMIT}&page=${page}`;

    const res = await fetchGet(url, {
      'Authorization': `Bearer ${idToken}`,
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    });

    if (!res.ok) {
      const body = await res.text();
      if (res.status === 401) {
        throw new Error(`Invintory API unauthorized (401). Token may be invalid: ${body}`);
      }
      if (res.status === 404) {
        // Try alternate endpoint patterns
        throw new Error(
          `Invintory API returned 404 for ${url}. ` +
          'Collection ID or endpoint may have changed. Check API docs.'
        );
      }
      throw new Error(`Invintory API error (${res.status}): ${body}`);
    }

    const body = await res.json() as ApiResponse;
    const labels = extractLabels(body);

    if (labels.length === 0) break;

    allLabels.push(...labels);
    totalFetched += labels.length;

    if (!hasMorePages(body, page, totalFetched)) break;

    page++;

    // Safety cap at 50 pages (10,000 labels)
    if (page > 50) break;
  }

  if (allLabels.length === 0) {
    throw new Error('Invintory API returned no labels. Collection may be empty or endpoint format changed.');
  }

  const wines = allLabels.map(transformLabel);
  return { wines, idToken };
}
