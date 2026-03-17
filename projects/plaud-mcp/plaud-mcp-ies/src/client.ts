// ── Plaud API client ─────────────────────────────────────────────────────────
// Wraps the Plaud web API with typed methods.
// Handles region auto-detection (US/EU redirect).

import { PlaudAuth } from './auth.js';
import { BASE_URLS } from './types.js';
import type { PlaudRecording, PlaudRecordingDetail, PlaudUserInfo } from './types.js';

export class PlaudClient {
  private auth: PlaudAuth;
  private region: string;

  constructor(auth: PlaudAuth, region: string = 'us') {
    this.auth = auth;
    this.region = region;
  }

  private get baseUrl(): string {
    return BASE_URLS[this.region] ?? BASE_URLS['us'];
  }

  private async request(path: string, options?: RequestInit): Promise<any> {
    const token = await this.auth.getToken();
    const url = `${this.baseUrl}${path}`;
    const res = await fetch(url, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!res.ok) {
      throw new Error(`Plaud API error: ${res.status} ${res.statusText}`);
    }

    const data = await res.json();

    // Handle region mismatch — Plaud returns -302 with correct domain
    if (data?.status === -302 && data?.data?.domains?.api) {
      const domain: string = data.data.domains.api;
      this.region = domain.includes('euc1') ? 'eu' : 'us';
      return this.request(path, options);
    }

    return data;
  }

  // ── Core tools (equivalent to plaud-toolkit) ──────────────────────────────

  async listRecordings(): Promise<PlaudRecording[]> {
    const data = await this.request('/file/simple/web');
    const list: PlaudRecording[] = data.data_file_list ?? data.data ?? [];
    return list.filter(r => !r.is_trash);
  }

  async getRecording(id: string): Promise<PlaudRecordingDetail> {
    const data = await this.request(`/file/detail/${id}`);
    const raw = data.data ?? data;

    // Extract longest transcript from pre_download_content_list
    let transcript = '';
    let summary = '';
    const preDownload: any[] = raw.pre_download_content_list ?? [];
    for (const item of preDownload) {
      const content = item.data_content ?? '';
      const contentType = item.content_type ?? '';

      // Plaud stores multiple content types — transcript, summary, mind map, etc.
      // The longest text-type content is typically the transcript.
      // Items with content_type containing "summary" are summaries.
      if (contentType.includes('summary') || contentType.includes('mind_map')) {
        if (content.length > summary.length) summary = content;
      } else {
        if (content.length > transcript.length) transcript = content;
      }
    }

    return {
      ...raw,
      id: raw.file_id ?? id,
      filename: raw.file_name ?? raw.filename ?? id,
      transcript,
      summary: summary || undefined,
    } as PlaudRecordingDetail;
  }

  async getUserInfo(): Promise<PlaudUserInfo> {
    const data = await this.request('/user/me');
    const user = data.data_user ?? data.data ?? data;
    return {
      id: user.id,
      nickname: user.nickname,
      email: user.email,
      country: user.country,
      membership_type: data.data_state?.membership_type ?? 'unknown',
    };
  }

  async getMp3Url(id: string): Promise<string | null> {
    try {
      const data = await this.request(`/file/temp-url/${id}?is_opus=false`);
      return data?.url ?? data?.data?.url ?? data?.data ?? data?.temp_url ?? null;
    } catch {
      return null;
    }
  }

  async getTags(): Promise<Array<{ id: string; name: string }>> {
    try {
      const data = await this.request('/filetag/');
      return data.data ?? [];
    } catch {
      return [];
    }
  }

  // ── IES extensions ────────────────────────────────────────────────────────

  /**
   * List recordings from the last N days.
   * Filters client-side since the API doesn't support date ranges.
   */
  async listRecent(days: number = 7): Promise<PlaudRecording[]> {
    const cutoff = Date.now() - (days * 24 * 60 * 60 * 1000);
    const all = await this.listRecordings();
    return all
      .filter(r => r.start_time > cutoff)
      .sort((a, b) => b.start_time - a.start_time);
  }

  /**
   * Search recordings by keyword (client-side).
   * Searches title and keywords. For transcript search, use searchTranscripts().
   */
  async searchRecordings(query: string, limit: number = 20): Promise<PlaudRecording[]> {
    const q = query.toLowerCase();
    const all = await this.listRecordings();
    return all
      .filter(r =>
        r.filename.toLowerCase().includes(q) ||
        r.fullname?.toLowerCase().includes(q) ||
        r.keywords?.some(k => k.toLowerCase().includes(q))
      )
      .slice(0, limit);
  }

  /**
   * Deep search — searches inside transcript text.
   * More expensive: fetches detail for each recording.
   * Use sparingly; prefer searchRecordings() for title/keyword matches.
   */
  async searchTranscripts(
    query: string,
    limit: number = 10,
    candidateLimit: number = 50
  ): Promise<Array<{ recording: PlaudRecording; snippet: string }>> {
    const q = query.toLowerCase();
    const all = await this.listRecordings();
    const candidates = all.filter(r => r.is_trans).slice(0, candidateLimit);

    const results: Array<{ recording: PlaudRecording; snippet: string }> = [];
    for (const rec of candidates) {
      if (results.length >= limit) break;
      try {
        const detail = await this.getRecording(rec.id);
        const idx = detail.transcript.toLowerCase().indexOf(q);
        if (idx !== -1) {
          // Extract snippet: 100 chars before and after match
          const start = Math.max(0, idx - 100);
          const end = Math.min(detail.transcript.length, idx + query.length + 100);
          const snippet = (start > 0 ? '...' : '') +
            detail.transcript.slice(start, end) +
            (end < detail.transcript.length ? '...' : '');
          results.push({ recording: rec, snippet });
        }
      } catch {
        // Skip recordings that fail to load
      }
    }
    return results;
  }
}
