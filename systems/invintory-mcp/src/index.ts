#!/usr/bin/env node
// ── Invintory MCP Server ────────────────────────────────────────────────────
// Serves wine collection data from a local JSON cache.
// Cache is populated by the Playwright refresh script (refresh.ts).

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { execSync } from 'child_process';
import { writeFileSync, unlinkSync } from 'fs';
import { tmpdir } from 'os';
import { join } from 'path';
import { loadCache, getCacheAge, summarize, importCSV, saveCache, loadDeliveries, saveDeliveries, addDelivery } from './cache.js';
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
  'Check when collection data was last refreshed and whether it is stale',
  {},
  async () => {
    const age = getCacheAge();
    const data = loadCache();
    if (!age || !data) {
      return jsonResponse({
        status: 'no_cache',
        message: 'No collection data cached. Run the refresh script to import data.',
      });
    }
    return jsonResponse({
      status: age.stale ? 'stale' : 'fresh',
      cache_age_hours: age.hours,
      wine_count: data.meta.wine_count,
      exported_at: data.meta.exported_at,
      source_file: data.meta.source_file,
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

// ── Tool: Add Delivery ───────────────────────────────────────────────────────

server.tool(
  'invintory_add_delivery',
  'Record a pending wine delivery — an order placed that hasn\'t arrived yet',
  {
    wine_name: z.string().describe('Name of the wine ordered'),
    producer: z.string().optional().describe('Producer or winery'),
    vintage: z.number().optional().describe('Vintage year'),
    quantity: z.number().min(1).describe('Number of bottles ordered'),
    source: z.string().describe('Retailer or source (e.g. "Last Bottle", "Wine.com", "Winc")'),
    order_date: z.string().describe('Date the order was placed (YYYY-MM-DD)'),
    expected_date: z.string().optional().describe('Expected delivery date (YYYY-MM-DD)'),
    price_per_bottle: z.number().optional().describe('Price paid per bottle'),
    status: z.enum(['pending', 'shipped', 'arrived', 'cancelled']).default('pending').describe('Delivery status'),
    destination: z.string().optional().default('Classic').describe('Destination cellar when it arrives (Classic, Cellar, Study, Kitchen)'),
    notes: z.string().optional().describe('Any notes about the order'),
  },
  async (input) => {
    const delivery = addDelivery(input);
    return jsonResponse({ status: 'recorded', delivery });
  }
);

// ── Tool: List Deliveries ────────────────────────────────────────────────────

server.tool(
  'invintory_list_deliveries',
  'List wine deliveries. Filter by status to see what\'s incoming, shipped, or arrived.',
  {
    status: z.enum(['pending', 'shipped', 'arrived', 'cancelled', 'all']).default('all').describe('Filter by delivery status. Default shows all.'),
  },
  async ({ status }) => {
    const all = loadDeliveries();
    const filtered = status === 'all' ? all : all.filter(d => d.status === status);
    const counts = {
      pending: all.filter(d => d.status === 'pending').length,
      shipped: all.filter(d => d.status === 'shipped').length,
      arrived: all.filter(d => d.status === 'arrived').length,
      cancelled: all.filter(d => d.status === 'cancelled').length,
    };
    return jsonResponse({ total: filtered.length, counts, deliveries: filtered });
  }
);

// ── Tool: Update Delivery ────────────────────────────────────────────────────

server.tool(
  'invintory_update_delivery',
  'Update the status or details of a delivery (e.g. mark as shipped or arrived)',
  {
    id: z.string().describe('Delivery ID from invintory_list_deliveries'),
    status: z.enum(['pending', 'shipped', 'arrived', 'cancelled']).optional().describe('New status'),
    expected_date: z.string().optional().describe('Updated expected delivery date (YYYY-MM-DD)'),
    notes: z.string().optional().describe('Updated notes'),
  },
  async ({ id, status, expected_date, notes }) => {
    const deliveries = loadDeliveries();
    const idx = deliveries.findIndex(d => d.id === id);
    if (idx === -1) return jsonResponse({ error: `No delivery found with id: ${id}` });
    if (status) deliveries[idx].status = status;
    if (expected_date !== undefined) deliveries[idx].expected_date = expected_date;
    if (notes !== undefined) deliveries[idx].notes = notes;
    saveDeliveries(deliveries);
    return jsonResponse({ status: 'updated', delivery: deliveries[idx] });
  }
);

// ── Chrome AppleScript helper ────────────────────────────────────────────────

function runInInvintoryTab(js: string): string {
  const asFile = join(tmpdir(), `invintory-as-${Date.now()}.applescript`);
  const jsJson = JSON.stringify(js);
  writeFileSync(asFile, `tell application "Google Chrome"
  repeat with w in windows
    repeat with t in tabs of w
      if URL of t contains "invintory.com" then
        set result to execute t javascript ${jsJson}
        return result
      end if
    end repeat
  end repeat
  return "TAB_NOT_FOUND"
end tell`);
  try {
    return execSync(`osascript ${asFile}`, { encoding: 'utf8', timeout: 45000 }).trim();
  } finally {
    try { unlinkSync(asFile); } catch { /* ignore */ }
  }
}

// ── Tool: Push Delivery to Invintory ─────────────────────────────────────────

server.tool(
  'invintory_push_delivery',
  'Push a locally-recorded delivery into Invintory native via Chrome automation. Opens the New Delivery form and pre-fills all metadata. Requires Chrome open with an Invintory tab.',
  {
    id: z.string().describe('Delivery ID from invintory_list_deliveries'),
    wine_search_terms: z.array(z.string()).optional().describe('Override wine search terms. Defaults to the wine_name on the delivery. Use exact catalog names for best matching.'),
  },
  async ({ id, wine_search_terms }) => {
    const deliveries = loadDeliveries();
    const delivery = deliveries.find(d => d.id === id);
    if (!delivery) return jsonResponse({ error: `No delivery found with id: ${id}` });

    const source = delivery.source;
    const purchaseDate = delivery.order_date;
    const deliveryDate = delivery.expected_date ?? delivery.order_date;
    const destination = delivery.destination ?? 'Classic';
    const notes = delivery.notes ?? '';
    const wines = wine_search_terms ?? [delivery.wine_name];

    // Step 1: Ensure we're on the deliveries page
    const navJs = `(function() {
  if (!location.href.includes('/collection/deliveries')) {
    location.href = 'https://app.invintory.com/collection/deliveries';
    return 'navigated';
  }
  return 'already_there';
})()`;
    const navResult = runInInvintoryTab(navJs);
    if (navResult === 'navigated') {
      // Wait for page load
      execSync('sleep 3');
    }

    // Step 2: Click New and fill the form
    const fillJs = `(async function() {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const log = [];

  // Click New button
  const newBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim() === 'New');
  if (!newBtn) return JSON.stringify({ status: 'error', message: 'New button not found' });
  newBtn.click();
  await sleep(800);

  const modal = document.querySelector('[role="dialog"]');
  if (!modal) return JSON.stringify({ status: 'error', message: 'Modal did not open' });
  log.push('modal_opened');

  // Helper: set native input value (works with React/SolidJS synthetic events)
  function setVal(el, val) {
    const proto = el.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
    setter.call(el, val);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  }

  // Fill source combobox
  const sourceInput = document.getElementById('combobox-cl-5-input');
  if (sourceInput) {
    sourceInput.focus();
    setVal(sourceInput, ${JSON.stringify(source)});
    await sleep(1200);
    // Find and click the matching dropdown option
    const optionEls = Array.from(document.querySelectorAll('[role="option"], [data-value], li[class*="item"]'));
    const match = optionEls.find(o => o.textContent.toLowerCase().includes(${JSON.stringify(source.toLowerCase())}));
    if (match) { match.click(); log.push('source_selected'); }
    else { log.push('source_not_found_in_dropdown'); }
    await sleep(300);
  }

  // Fill purchase date
  const purchaseDateInput = document.querySelector('input[name="purchase_date"]');
  if (purchaseDateInput) {
    setVal(purchaseDateInput, ${JSON.stringify(purchaseDate)});
    log.push('purchase_date_set');
  }

  // Fill delivery date
  const deliveryDateInput = document.querySelector('input[name="delivery_date"]');
  if (deliveryDateInput) {
    setVal(deliveryDateInput, ${JSON.stringify(deliveryDate)});
    log.push('delivery_date_set');
  }

  // Set destination cellar — find the visible select (select-cl-7 or similar)
  const destSelects = Array.from(document.querySelectorAll('select')).filter(s => s.name && s.name.includes('select-cl'));
  if (destSelects.length > 0) {
    const destSel = destSelects[destSelects.length - 1];
    const destOpt = Array.from(destSel.options).find(o => o.text.toLowerCase().includes(${JSON.stringify(destination.toLowerCase())}));
    if (destOpt) {
      destSel.value = destOpt.value;
      destSel.dispatchEvent(new Event('change', { bubbles: true }));
      log.push('destination_set');
    } else {
      log.push('destination_option_not_found');
    }
  }

  // Fill notes
  const notesEl = document.querySelector('textarea[name="notes"]');
  if (notesEl && ${JSON.stringify(notes)}) {
    setVal(notesEl, ${JSON.stringify(notes)});
    log.push('notes_set');
  }

  // Search and add each wine
  const wineNames = ${JSON.stringify(wines)};
  const wineResults = [];
  for (const wineName of wineNames) {
    const searchBar = document.getElementById('searchBar');
    if (!searchBar) { wineResults.push({ wine: wineName, result: 'search_bar_not_found' }); continue; }
    searchBar.focus();
    setVal(searchBar, wineName);
    await sleep(1500);
    // Find search result items
    const resultItems = Array.from(document.querySelectorAll('[class*="result"], [class*="wine"], li[class*="item"], [data-wine-id]'))
      .filter(el => el.textContent && el.textContent.length > 5 && !el.textContent.includes('Search wine'));
    const firstResult = resultItems[0];
    if (firstResult) {
      firstResult.click();
      wineResults.push({ wine: wineName, result: 'added', matched: firstResult.textContent.trim().substring(0, 60) });
      await sleep(600);
    } else {
      wineResults.push({ wine: wineName, result: 'no_results_found' });
    }
  }
  log.push('wines_processed');

  return JSON.stringify({ status: 'filled', log, wine_results: wineResults, next: 'Review form in Chrome and click Create' });
})()`;

    try {
      const raw = runInInvintoryTab(fillJs);
      let result: unknown;
      try { result = JSON.parse(raw); } catch { result = { raw }; }
      return jsonResponse({ delivery_id: id, delivery_name: delivery.wine_name, automation: result });
    } catch (err) {
      return jsonResponse({ error: err instanceof Error ? err.message : String(err) });
    }
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
