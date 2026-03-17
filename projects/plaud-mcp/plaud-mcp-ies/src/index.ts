#!/usr/bin/env npx tsx
// ── IES Plaud MCP Server ─────────────────────────────────────────────────────
//
// Extended MCP server for the Improving Executive System (IES).
// Inherits all plaud-toolkit tools + adds: search, recent, summary, token health.
//
// Auth: ~/.plaud/config.json (plaud-toolkit compatible)
//       or env vars: PLAUD_EMAIL, PLAUD_PASSWORD, PLAUD_REGION
//
// Register in ~/.claude/mcp.json:
//   "plaud": {
//     "command": "node",
//     "args": ["/path/to/plaud-mcp-ies/dist/index.js"]
//   }

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { ConfigManager } from './config.js';
import { PlaudAuth } from './auth.js';
import { PlaudClient } from './client.js';

async function main() {
  const config = new ConfigManager();
  const maybeCreds = config.getCredentials();

  if (!maybeCreds) {
    console.error(
      'No Plaud credentials found.\n' +
      'Set PLAUD_EMAIL + PLAUD_PASSWORD env vars,\n' +
      'or run `plaud login` (plaud-toolkit CLI) to store in ~/.plaud/config.json.'
    );
    process.exit(1);
  }

  const creds = maybeCreds;
  const auth = new PlaudAuth(config);
  const client = new PlaudClient(auth, creds.region);

  const server = new McpServer({
    name: 'plaud-mcp-ies',
    version: '1.0.0',
  });

  // ── Helper ──────────────────────────────────────────────────────────────

  function formatRecording(r: any) {
    return {
      id: r.id,
      title: r.filename,
      date: new Date(r.start_time).toISOString().slice(0, 16),
      duration_minutes: Math.round(r.duration / 60000),
      has_transcript: r.is_trans,
      has_summary: r.is_summary,
      keywords: r.keywords ?? [],
    };
  }

  function jsonResponse(data: any) {
    return { content: [{ type: 'text' as const, text: JSON.stringify(data, null, 2) }] };
  }

  const recordingIdParam = { recording_id: z.string().describe('The Plaud recording ID') };

  // ── Core tools (plaud-toolkit equivalent) ───────────────────────────────

  server.tool(
    'plaud_list_recordings',
    'List all Plaud recordings with ID, date, duration, title, and transcript/summary availability.',
    async () => {
      const recs = await client.listRecordings();
      return jsonResponse(recs.map(formatRecording));
    }
  );

  server.tool(
    'plaud_get_transcript',
    'Get the full transcript text of a Plaud recording. Returns speaker-diarized text when available.',
    recordingIdParam,
    async (params) => {
      const detail = await client.getRecording(params.recording_id);
      return jsonResponse({
        id: detail.id,
        title: detail.filename,
        date: new Date(detail.start_time).toISOString().slice(0, 16),
        duration_minutes: Math.round(detail.duration / 60000),
        transcript: detail.transcript || 'No transcript available.',
      });
    }
  );

  server.tool(
    'plaud_get_summary',
    'Get the AI-generated summary of a Plaud recording (action items, key points, decisions).',
    recordingIdParam,
    async (params) => {
      const detail = await client.getRecording(params.recording_id);
      return jsonResponse({
        id: detail.id,
        title: detail.filename,
        summary: detail.summary || 'No summary available. Transcript may need to be summarized manually.',
      });
    }
  );

  server.tool(
    'plaud_get_recording_detail',
    'Get full metadata and content for a Plaud recording — including transcript, summary, duration, speakers, and keywords.',
    recordingIdParam,
    async (params) => {
      const detail = await client.getRecording(params.recording_id);
      return jsonResponse({
        id: detail.id,
        title: detail.filename,
        date: new Date(detail.start_time).toISOString().slice(0, 16),
        duration_minutes: Math.round(detail.duration / 60000),
        has_transcript: detail.is_trans,
        has_summary: detail.is_summary,
        keywords: detail.keywords ?? [],
        transcript: detail.transcript || null,
        summary: detail.summary || null,
      });
    }
  );

  server.tool(
    'plaud_get_mp3_url',
    'Get a temporary download URL for the MP3 audio of a recording.',
    recordingIdParam,
    async (params) => {
      const url = await client.getMp3Url(params.recording_id);
      return jsonResponse({
        url: url || null,
        message: url ? 'Temporary URL — valid for a limited time.' : 'No MP3 available.',
      });
    }
  );

  server.tool(
    'plaud_user_info',
    'Get current Plaud user account information (name, email, membership).',
    async () => {
      const user = await client.getUserInfo();
      return jsonResponse(user);
    }
  );

  // ── IES extension tools ─────────────────────────────────────────────────

  server.tool(
    'plaud_get_recent',
    'Get recordings from the last N days. Defaults to 7 days. Used for morning briefings and daily reviews.',
    {
      days: z.number().optional().default(7).describe('Number of days to look back (default: 7)'),
    },
    async (params) => {
      const recs = await client.listRecent(params.days);
      return jsonResponse({
        days: params.days,
        count: recs.length,
        recordings: recs.map(formatRecording),
      });
    }
  );

  server.tool(
    'plaud_search',
    'Search recordings by keyword. Searches titles and keywords. For searching inside transcript text, set search_transcripts=true (slower — fetches each recording).',
    {
      query: z.string().describe('Search term'),
      limit: z.number().optional().default(10).describe('Max results (default: 10)'),
      search_transcripts: z.boolean().optional().default(false).describe('Also search inside transcript text (slower)'),
    },
    async (params) => {
      if (params.search_transcripts) {
        const results = await client.searchTranscripts(params.query, params.limit);
        return jsonResponse({
          query: params.query,
          count: results.length,
          results: results.map(r => ({
            ...formatRecording(r.recording),
            snippet: r.snippet,
          })),
        });
      }

      const recs = await client.searchRecordings(params.query, params.limit);
      return jsonResponse({
        query: params.query,
        count: recs.length,
        recordings: recs.map(formatRecording),
      });
    }
  );

  server.tool(
    'plaud_get_tags',
    'List all recording tags/folders in the Plaud account.',
    async () => {
      const tags = await client.getTags();
      return jsonResponse(tags);
    }
  );

  server.tool(
    'plaud_token_health',
    'Check the health of the Plaud auth token — expiry date and days remaining. Used for proactive monitoring in morning briefings.',
    async () => {
      const expiry = auth.getTokenExpiry();
      if (!expiry) {
        return jsonResponse({ status: 'no_token', message: 'No token stored. Re-authentication required.' });
      }
      const status = expiry.daysRemaining > 30 ? 'healthy' :
                     expiry.daysRemaining > 7 ? 'expiring_soon' : 'critical';
      return jsonResponse({
        status,
        expires_at: new Date(expiry.expiresAt).toISOString(),
        days_remaining: expiry.daysRemaining,
        message: status === 'healthy'
          ? `Token valid for ${expiry.daysRemaining} more days.`
          : `Token expires in ${expiry.daysRemaining} days — re-authenticate soon.`,
      });
    }
  );

  // ── Start server ────────────────────────────────────────────────────────

  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch(err => {
  console.error('Failed to start Plaud MCP server:', err);
  process.exit(1);
});
