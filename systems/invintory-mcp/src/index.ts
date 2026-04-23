#!/usr/bin/env node
// ── Invintory MCP Server ────────────────────────────────────────────────────
// Serves wine collection data from a local JSON cache.
// Cache is populated by the Playwright refresh script (refresh.ts).

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { loadCache, getCacheAge, summarize, importCSV, saveCache } from './cache.js';
import { fetchLiveCollection } from './api.js';
import type { Wine } from './types.js';

// ── State ───────────────────────────────────────────────────────────────────

let wines: Wine[] = [];
let cacheLoaded = false;

function ensureCache(): Wine[] {
  if (!cacheLoaded) {
    const data = loadCache();
    if (data) {
      wines = data.wines;
      cacheLoaded = true;
    }
  }
  return wines;
}

function jsonResponse(obj: unknown): { content: Array<{ type: 'text'; text: string }> } {
  return { content: [{ type: 'text' as const, text: JSON.stringify(obj, null, 2) }] };
}

// ── Server Setup ────────────────────────────────────────────────────────────

const server = new McpServer({
  name: 'invintory',
  version: '1.0.0',
});

// ── Tool: Collection Summary ────────────────────────────────────────────────

server.tool(
  'invintory_summary',
  'Get collection overview: total bottles, market value, breakdown by type/country/storage, drink status counts',
  {},
  async () => {
    const w = ensureCache();
    if (!w.length) return jsonResponse({ error: 'No collection data. Run refresh to load data.' });

    const age = getCacheAge();
    const summary = summarize(w);
    return jsonResponse({ ...summary, cache_age_hours: age?.hours, cache_stale: age?.stale });
  }
);

// ── Tool: Search Wines ──────────────────────────────────────────────────────

server.tool(
  'invintory_search',
  'Search wines by name, producer, grape, region, or tag. Returns matching wines with full details.',
  {
    query: z.string().describe('Search term — matches against wine name, producer, grapes, region, tags'),
    type: z.enum(['red', 'white', 'rose', 'sparkling', 'fortified', 'dessert', 'unknown', 'all']).default('all').describe('Filter by wine type'),
    limit: z.number().min(1).max(100).default(20).describe('Max results to return'),
  },
  async ({ query, type, limit }) => {
    const w = ensureCache();
    const lower = query.toLowerCase();

    let results = w.filter(wine => {
      const haystack = [
        wine.name, wine.producer, wine.country, wine.region,
        wine.subregion, ...wine.grapes, ...wine.tags,
      ].join(' ').toLowerCase();
      return haystack.includes(lower);
    });

    if (type !== 'all') results = results.filter(wine => wine.type === type);

    return jsonResponse({
      query,
      matches: results.length,
      wines: results.slice(0, limit),
    });
  }
);

// ── Tool: Ready to Drink ────────────────────────────────────────────────────

server.tool(
  'invintory_ready',
  'List wines that are ready to drink or in their optimal drinking window right now',
  {
    include_expiring: z.boolean().default(true).describe('Include wines nearing end of window'),
    limit: z.number().min(1).max(100).default(25).describe('Max results'),
  },
  async ({ include_expiring, limit }) => {
    const w = ensureCache();
    const statuses = ['ready'];
    if (include_expiring) statuses.push('expiring_soon');

    const ready = w
      .filter(wine => statuses.includes(wine.drink_status))
      .sort((a, b) => (a.drink_window.end ?? 9999) - (b.drink_window.end ?? 9999));

    return jsonResponse({
      count: ready.length,
      wines: ready.slice(0, limit),
    });
  }
);

// ── Tool: Wine Recommend ────────────────────────────────────────────────────

server.tool(
  'invintory_recommend',
  'Get wine recommendations for a meal, occasion, or preference. Filters by type, grape, price range.',
  {
    occasion: z.string().describe('What the wine is for: dinner pairing, gift, casual, celebration, etc.'),
    type: z.enum(['red', 'white', 'rose', 'sparkling', 'all']).default('all').describe('Preferred wine type'),
    max_price: z.number().optional().describe('Max market price per bottle'),
    grape: z.string().optional().describe('Preferred grape variety'),
  },
  async ({ occasion, type, max_price, grape }) => {
    const w = ensureCache();

    let candidates = w.filter(wine =>
      wine.quantity > 0 &&
      (wine.drink_status === 'ready' || wine.drink_status === 'expiring_soon')
    );

    if (type !== 'all') candidates = candidates.filter(wine => wine.type === type);
    if (max_price) candidates = candidates.filter(wine => (wine.market_price ?? 0) <= max_price);
    if (grape) {
      const grpLower = grape.toLowerCase();
      candidates = candidates.filter(wine =>
        wine.grapes.some(g => g.toLowerCase().includes(grpLower))
      );
    }

    // Sort: expiring soon first, then by market value descending (best bottles first)
    candidates.sort((a, b) => {
      if (a.drink_status === 'expiring_soon' && b.drink_status !== 'expiring_soon') return -1;
      if (b.drink_status === 'expiring_soon' && a.drink_status !== 'expiring_soon') return 1;
      return (b.market_price ?? 0) - (a.market_price ?? 0);
    });

    return jsonResponse({
      occasion,
      candidates: candidates.length,
      recommendations: candidates.slice(0, 10),
    });
  }
);

// ── Tool: Storage View ──────────────────────────────────────────────────────

server.tool(
  'invintory_storage',
  'View contents of a specific cellar or fridge',
  {
    name: z.string().optional().describe('Storage name (Classic, Cellar, Study, Kitchen). Omit to list all.'),
  },
  async ({ name }) => {
    const w = ensureCache();

    if (!name) {
      const storages: Record<string, { bottles: number; labels: number }> = {};
      for (const wine of w) {
        const s = wine.storage || 'Unassigned';
        if (!storages[s]) storages[s] = { bottles: 0, labels: 0 };
        storages[s].bottles += wine.quantity;
        storages[s].labels += 1;
      }
      return jsonResponse({ storages });
    }

    const lower = name.toLowerCase();
    const contents = w.filter(wine => wine.storage.toLowerCase().includes(lower));
    return jsonResponse({
      storage: name,
      labels: contents.length,
      bottles: contents.reduce((s, wine) => s + wine.quantity, 0),
      wines: contents,
    });
  }
);

// ── Tool: Value Report ──────────────────────────────────────────────────────

server.tool(
  'invintory_value',
  'Portfolio value analysis: total value, top bottles by market price, best ROI, undervalued gems',
  {
    top_n: z.number().min(1).max(50).default(10).describe('How many top wines to show per category'),
  },
  async ({ top_n }) => {
    const w = ensureCache();
    const withMarket = w.filter(wine => wine.market_price && wine.market_price > 0);

    const byMarketValue = [...withMarket]
      .sort((a, b) => (b.market_price! * b.quantity) - (a.market_price! * a.quantity))
      .slice(0, top_n);

    const withBoth = withMarket.filter(wine => wine.purchase_price && wine.purchase_price > 0);
    const byROI = [...withBoth]
      .map(wine => ({
        ...wine,
        roi: ((wine.market_price! - wine.purchase_price!) / wine.purchase_price!) * 100,
      }))
      .sort((a, b) => b.roi - a.roi)
      .slice(0, top_n);

    const totalMarket = withMarket.reduce((s, wine) => s + (wine.market_price ?? 0) * wine.quantity, 0);
    const totalPurchase = withBoth.reduce((s, wine) => s + (wine.purchase_price ?? 0) * wine.quantity, 0);

    return jsonResponse({
      total_market_value: Math.round(totalMarket * 100) / 100,
      total_purchase_value: Math.round(totalPurchase * 100) / 100,
      total_gain_loss: Math.round((totalMarket - totalPurchase) * 100) / 100,
      most_valuable: byMarketValue.map(wine => ({
        name: wine.name, vintage: wine.vintage, quantity: wine.quantity,
        market_price: wine.market_price, total_value: Math.round(wine.market_price! * wine.quantity * 100) / 100,
      })),
      best_roi: byROI.map(wine => ({
        name: wine.name, vintage: wine.vintage,
        purchase_price: wine.purchase_price, market_price: wine.market_price,
        roi_percent: Math.round(wine.roi * 10) / 10,
      })),
    });
  }
);

// ── Tool: Cache Status ──────────────────────────────────────────────────────

server.tool(
  'invintory_cache_status',
  'Check when collection data was last refreshed and whether it is stale. Use invintory_refresh to pull latest data from the live API.',
  {},
  async () => {
    const age = getCacheAge();
    const data = loadCache();
    if (!age || !data) {
      return jsonResponse({
        status: 'no_cache',
        message: 'No collection data cached. Call invintory_refresh to pull live data from the Invintory API.',
      });
    }
    return jsonResponse({
      status: age.stale ? 'stale' : 'fresh',
      cache_age_hours: age.hours,
      wine_count: data.meta.wine_count,
      exported_at: data.meta.exported_at,
      source_file: data.meta.source_file,
      hint: age.stale ? 'Cache is stale — call invintory_refresh to update from the live API.' : undefined,
    });
  }
);

// ── Tool: Import CSV ────────────────────────────────────────────────────────

server.tool(
  'invintory_import',
  'Import a CSV file exported from Invintory into the local cache. Use when refreshing data.',
  {
    csv_path: z.string().describe('Absolute path to the Invintory CSV export file'),
  },
  async ({ csv_path }) => {
    try {
      const imported = importCSV(csv_path);
      saveCache(imported, csv_path);
      wines = imported;
      cacheLoaded = true;
      return jsonResponse({
        status: 'imported',
        wine_count: imported.length,
        total_bottles: imported.reduce((s, w) => s + w.quantity, 0),
        summary: summarize(imported),
      });
    } catch (err) {
      return jsonResponse({
        status: 'error',
        message: err instanceof Error ? err.message : String(err),
      });
    }
  }
);

// ── Tool: Live Refresh ──────────────────────────────────────────────────────

server.tool(
  'invintory_refresh',
  'Pull the latest collection data from Invintory and update the local cache. Runs the refresh script via osascript on the Mac (bypasses Cloudflare bot protection).',
  {},
  async () => {
    const { execSync } = await import('child_process');
    const SCRIPT_DIR = `${process.env.HOME}/Library/CloudStorage/OneDrive-Improving/IES/systems/invintory-mcp`;

    try {
      // Run the refresh script on the Mac side via osascript — this uses the Mac's
      // Node/npx and Playwright persistent profile which has Cloudflare cookies cached.
      const script = `osascript -e 'do shell script "cd ${SCRIPT_DIR} && npx tsx src/refresh.ts 2>&1"'`;
      const output = execSync(script, { encoding: 'utf-8', timeout: 120000 });

      // Reload cache from disk (refresh script wrote it)
      cacheLoaded = false;
      const data = loadCache();
      if (data) {
        wines = data.wines;
        cacheLoaded = true;
        const summary = summarize(wines);
        return jsonResponse({
          status: 'refreshed',
          wine_count: data.meta.wine_count,
          total_bottles: summary.total_bottles,
          total_market_value: summary.total_market_value,
          ready_to_drink: summary.ready_to_drink,
          refreshed_at: data.meta.exported_at,
          script_output: output.trim().slice(-500), // last 500 chars of output
        });
      } else {
        return jsonResponse({
          status: 'error',
          message: 'Refresh script ran but cache file not found afterward.',
          script_output: output.trim().slice(-500),
        });
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      return jsonResponse({
        status: 'error',
        message: msg.slice(0, 1000),
        hint: 'If this fails, run manually: cd ~/Library/CloudStorage/OneDrive-Improving/IES/systems/invintory-mcp && npx tsx src/refresh.ts',
      });
    }
  }
);

// ── Tool: Grape/Varietal Breakdown ──────────────────────────────────────────

server.tool(
  'invintory_grapes',
  'See what grape varieties are in the collection and how many bottles of each',
  {},
  async () => {
    const w = ensureCache();
    const grapes: Record<string, { labels: number; bottles: number }> = {};

    for (const wine of w) {
      for (const grape of wine.grapes) {
        if (!grapes[grape]) grapes[grape] = { labels: 0, bottles: 0 };
        grapes[grape].labels += 1;
        grapes[grape].bottles += wine.quantity;
      }
    }

    const sorted = Object.entries(grapes)
      .sort(([, a], [, b]) => b.bottles - a.bottles)
      .map(([name, counts]) => ({ grape: name, ...counts }));

    return jsonResponse({ total_varieties: sorted.length, grapes: sorted });
  }
);

// ── Tool: Tags ──────────────────────────────────────────────────────────────

server.tool(
  'invintory_tags',
  'List all tags and the wines associated with each tag',
  {
    tag: z.string().optional().describe('Show wines for a specific tag. Omit to list all tags.'),
  },
  async ({ tag }) => {
    const w = ensureCache();

    if (!tag) {
      const tags: Record<string, number> = {};
      for (const wine of w) {
        for (const t of wine.tags) {
          tags[t] = (tags[t] || 0) + 1;
        }
      }
      return jsonResponse({ tags });
    }

    const lower = tag.toLowerCase();
    const tagged = w.filter(wine => wine.tags.some(t => t.toLowerCase() === lower));
    return jsonResponse({
      tag,
      count: tagged.length,
      wines: tagged,
    });
  }
);

// ── Start Server ────────────────────────────────────────────────────────────

async function main() {
  // Try to load cache on startup
  ensureCache();

  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(err => {
  console.error('Failed to start Invintory MCP server:', err);
  process.exit(1);
});
