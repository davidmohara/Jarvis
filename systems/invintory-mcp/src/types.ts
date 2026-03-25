// ── Invintory data types ────────────────────────────────────────────────────
// Derived from CSV export columns + enriched fields.

export interface Wine {
  name: string;
  vintage: number | null;
  type: WineType;
  grapes: string[];
  producer: string;
  country: string;
  region: string;
  subregion: string;
  size: string;
  quantity: number;
  market_price: number | null;
  purchase_price: number | null;
  drink_window: {
    start: number | null;
    end: number | null;
  };
  drink_status: DrinkStatus;
  storage: string;
  tags: string[];
}

export type WineType = 'red' | 'white' | 'rose' | 'sparkling' | 'fortified' | 'dessert' | 'unknown';

export type DrinkStatus = 'hold' | 'ready' | 'expiring_soon' | 'past_window' | 'unknown';

export interface CollectionSummary {
  total_bottles: number;
  total_labels: number;
  total_market_value: number;
  total_purchase_value: number;
  by_type: Record<string, number>;
  by_country: Record<string, number>;
  by_storage: Record<string, number>;
  ready_to_drink: number;
  past_window: number;
  hold: number;
}

export interface CacheMetadata {
  exported_at: string;
  loaded_at: string;
  wine_count: number;
  source_file: string;
}
