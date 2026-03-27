// ── CSV → JSON cache manager ────────────────────────────────────────────────
// Parses Invintory CSV export into typed Wine[] and persists as JSON.

import { readFileSync, writeFileSync, existsSync, mkdirSync, statSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';
import type { Wine, WineType, DrinkStatus, CacheMetadata, CollectionSummary } from './types.js';

const CACHE_DIR = join(homedir(), '.config', 'invintory');
const CACHE_FILE = join(CACHE_DIR, 'collection.json');
const META_FILE = join(CACHE_DIR, 'cache-meta.json');

// ── CSV Parsing ─────────────────────────────────────────────────────────────

function parseCSVLine(line: string): string[] {
  const fields: string[] = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (inQuotes) {
      if (ch === '"' && line[i + 1] === '"') {
        current += '"';
        i++;
      } else if (ch === '"') {
        inQuotes = false;
      } else {
        current += ch;
      }
    } else {
      if (ch === '"') {
        inQuotes = true;
      } else if (ch === ',') {
        fields.push(current.trim());
        current = '';
      } else {
        current += ch;
      }
    }
  }
  fields.push(current.trim());
  return fields;
}

function normalizeType(raw: string): WineType {
  const lower = raw.toLowerCase().trim();
  if (lower === 'red') return 'red';
  if (lower === 'white') return 'white';
  if (lower === 'rose' || lower === 'rosé') return 'rose';
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

function parseDrinkWindow(raw: string): { start: number | null; end: number | null } {
  if (!raw) return { start: null, end: null };
  const match = raw.match(/(\d{4})\s*[-–]\s*(\d{4})/);
  if (match) return { start: parseInt(match[1]), end: parseInt(match[2]) };
  const single = raw.match(/(\d{4})/);
  if (single) return { start: parseInt(single[1]), end: null };
  return { start: null, end: null };
}

// ── Column Mapping ──────────────────────────────────────────────────────────
// Maps CSV header names to our Wine fields. Case-insensitive, handles variations.

function buildColumnMap(headers: string[]): Record<string, number> {
  const map: Record<string, number> = {};
  const lower = headers.map(h => h.toLowerCase().trim());

  const find = (patterns: string[]): number => {
    for (const p of patterns) {
      const idx = lower.findIndex(h => h.includes(p));
      if (idx >= 0) return idx;
    }
    return -1;
  };

  map.storage = find(['cellar or fridge', 'cellar', 'storage']);
  map.name = find(['wine name', 'name']);
  map.vintage = find(['vintage']);
  map.type = find(['wine type', 'type']);
  map.grapes = find(['grape', 'varietal']);
  map.producer = find(['producer', 'winery']);
  map.country = find(['country']);
  map.region = find(['region']);
  map.subregion = find(['subregion', 'sub-region', 'appellation']);
  map.size = find(['size', 'bottle size']);
  map.quantity = find(['quantity', 'qty']);
  map.market = find(['market price', 'market value']);
  map.purchase = find(['purchase price', 'average purchase', 'cost']);
  map.window = find(['drink window', 'drinking window', 'window']);
  map.tags = find(['tag']);

  return map;
}

// ── Core Functions ──────────────────────────────────────────────────────────

export function importCSV(csvPath: string): Wine[] {
  const raw = readFileSync(csvPath, 'utf-8').replace(/^\uFEFF/, ''); // strip BOM
  const lines = raw.split('\n').filter(l => l.trim());
  if (lines.length < 2) throw new Error('CSV has no data rows');

  const headers = parseCSVLine(lines[0]);
  const col = buildColumnMap(headers);
  const hasQuantityCol = col.quantity >= 0;

  // First pass: parse all rows
  const rows: Wine[] = [];
  for (let i = 1; i < lines.length; i++) {
    const fields = parseCSVLine(lines[i]);
    if (fields.length < 3) continue;

    const get = (key: string): string => {
      const idx = col[key];
      return idx >= 0 && idx < fields.length ? fields[idx] : '';
    };

    const vintageRaw = get('vintage');
    const vintage = vintageRaw ? parseInt(vintageRaw) || null : null;
    const marketRaw = get('market');
    const purchaseRaw = get('purchase');
    const window = parseDrinkWindow(get('window'));
    const grapesRaw = get('grapes');
    const tagsRaw = get('tags');

    rows.push({
      name: get('name'),
      vintage,
      type: normalizeType(get('type')),
      grapes: grapesRaw ? grapesRaw.split(',').map(g => g.trim()).filter(Boolean) : [],
      producer: get('producer'),
      country: get('country'),
      region: get('region'),
      subregion: get('subregion'),
      size: get('size') || '750ml',
      quantity: hasQuantityCol ? (parseInt(get('quantity')) || 1) : 1,
      market_price: marketRaw ? parseFloat(marketRaw) || null : null,
      purchase_price: purchaseRaw ? parseFloat(purchaseRaw) || null : null,
      drink_window: window,
      drink_status: computeDrinkStatus(window.start, window.end),
      storage: get('storage'),
      tags: tagsRaw ? tagsRaw.split(',').map(t => t.trim()).filter(Boolean) : [],
    });
  }

  // If no quantity column, each row = 1 bottle; group by label to aggregate
  if (!hasQuantityCol) {
    const labelMap = new Map<string, Wine>();
    for (const row of rows) {
      const key = `${row.name}|${row.vintage}|${row.producer}|${row.type}`;
      const existing = labelMap.get(key);
      if (existing) {
        existing.quantity += 1;
      } else {
        labelMap.set(key, { ...row });
      }
    }
    return Array.from(labelMap.values());
  }

  return rows;
}

export function saveCache(wines: Wine[], sourceFile: string): void {
  if (!existsSync(CACHE_DIR)) mkdirSync(CACHE_DIR, { recursive: true });

  writeFileSync(CACHE_FILE, JSON.stringify(wines, null, 2));

  const meta: CacheMetadata = {
    exported_at: new Date().toISOString(),
    loaded_at: new Date().toISOString(),
    wine_count: wines.length,
    source_file: sourceFile,
  };
  writeFileSync(META_FILE, JSON.stringify(meta, null, 2));
}

export function loadCache(): { wines: Wine[]; meta: CacheMetadata } | null {
  if (!existsSync(CACHE_FILE) || !existsSync(META_FILE)) return null;

  const wines: Wine[] = JSON.parse(readFileSync(CACHE_FILE, 'utf-8'));
  const meta: CacheMetadata = JSON.parse(readFileSync(META_FILE, 'utf-8'));
  meta.loaded_at = new Date().toISOString();
  return { wines, meta };
}

export function getCacheAge(): { hours: number; stale: boolean } | null {
  if (!existsSync(META_FILE)) return null;
  const meta: CacheMetadata = JSON.parse(readFileSync(META_FILE, 'utf-8'));
  const exported = new Date(meta.exported_at).getTime();
  const hours = (Date.now() - exported) / (1000 * 60 * 60);
  return { hours: Math.round(hours * 10) / 10, stale: hours > 24 };
}

// ── Collection Summary ──────────────────────────────────────────────────────

export function summarize(wines: Wine[]): CollectionSummary {
  const totalBottles = wines.reduce((s, w) => s + w.quantity, 0);
  const totalMarket = wines.reduce((s, w) => s + (w.market_price ?? 0) * w.quantity, 0);
  const totalPurchase = wines.reduce((s, w) => s + (w.purchase_price ?? 0) * w.quantity, 0);

  const byType: Record<string, number> = {};
  const byCountry: Record<string, number> = {};
  const byStorage: Record<string, number> = {};
  let ready = 0, pastWindow = 0, hold = 0;

  for (const w of wines) {
    byType[w.type] = (byType[w.type] || 0) + w.quantity;
    if (w.country) byCountry[w.country] = (byCountry[w.country] || 0) + w.quantity;
    if (w.storage) byStorage[w.storage] = (byStorage[w.storage] || 0) + w.quantity;
    if (w.drink_status === 'ready' || w.drink_status === 'expiring_soon') ready += w.quantity;
    if (w.drink_status === 'past_window') pastWindow += w.quantity;
    if (w.drink_status === 'hold') hold += w.quantity;
  }

  return {
    total_bottles: totalBottles,
    total_labels: wines.length,
    total_market_value: Math.round(totalMarket * 100) / 100,
    total_purchase_value: Math.round(totalPurchase * 100) / 100,
    by_type: byType,
    by_country: byCountry,
    by_storage: byStorage,
    ready_to_drink: ready,
    past_window: pastWindow,
    hold,
  };
}

export { CACHE_DIR, CACHE_FILE };
