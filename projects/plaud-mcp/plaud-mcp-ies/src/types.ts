// ── Plaud API types ──────────────────────────────────────────────────────────
// Derived from plaud-toolkit @plaud/core and reverse-engineered API responses.

export const BASE_URLS: Record<string, string> = {
  us: 'https://api.plaud.ai',
  eu: 'https://api-euc1.plaud.ai',
};

export interface PlaudCredentials {
  email: string;
  password: string;
  region: 'us' | 'eu';
}

export interface PlaudTokenData {
  accessToken: string;
  tokenType: string;
  issuedAt: number;   // epoch ms
  expiresAt: number;  // epoch ms (decoded from JWT)
}

export interface PlaudConfig {
  credentials?: PlaudCredentials;
  token?: PlaudTokenData;
}

export interface PlaudRecording {
  id: string;
  filename: string;
  fullname: string;
  filesize: number;
  duration: number;      // milliseconds
  start_time: number;    // epoch ms
  end_time: number;      // epoch ms
  is_trash: boolean;
  is_trans: boolean;
  is_summary: boolean;
  keywords: string[];
  serial_number: string;
}

export interface PlaudRecordingDetail extends PlaudRecording {
  transcript: string;
  summary?: string;
}

export interface PlaudUserInfo {
  id: string;
  nickname: string;
  email: string;
  country: string;
  membership_type: string;
}

// ── IES extension types ──────────────────────────────────────────────────────

export interface RoutingRule {
  match: string;           // regex pattern applied to title + transcript
  destination: string;     // Obsidian vault path or Google Drive folder
  tag?: string;            // optional tag to apply
}

export interface RoutingConfig {
  rules: RoutingRule[];
  default: string;         // fallback destination
}

export interface RecordingListItem {
  id: string;
  title: string;
  date: string;            // ISO date string
  duration_minutes: number;
  has_transcript: boolean;
  has_summary: boolean;
  keywords: string[];
}

export interface TranscriptResult {
  id: string;
  title: string;
  date: string;
  duration_minutes: number;
  transcript: string;
  summary?: string;
}
