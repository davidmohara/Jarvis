// ── Config management ────────────────────────────────────────────────────────
// Reads credentials from ~/.plaud/config.json (compatible with plaud-toolkit)
// or from environment variables PLAUD_EMAIL, PLAUD_PASSWORD, PLAUD_REGION.

import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import type { PlaudConfig, PlaudCredentials, PlaudTokenData } from './types.js';

const DEFAULT_DIR = path.join(os.homedir(), '.plaud');
const CONFIG_FILE = 'config.json';

export class ConfigManager {
  private dir: string;

  constructor(dir?: string) {
    this.dir = dir ?? DEFAULT_DIR;
  }

  private filePath(): string {
    return path.join(this.dir, CONFIG_FILE);
  }

  load(): PlaudConfig {
    try {
      const raw = fs.readFileSync(this.filePath(), 'utf-8');
      return JSON.parse(raw) as PlaudConfig;
    } catch {
      return {};
    }
  }

  save(data: Partial<PlaudConfig>): void {
    fs.mkdirSync(this.dir, { recursive: true, mode: 0o700 });
    const existing = this.load();
    const merged = { ...existing, ...data };
    fs.writeFileSync(this.filePath(), JSON.stringify(merged, null, 2), { mode: 0o600 });
  }

  saveToken(token: PlaudTokenData): void {
    this.save({ token });
  }

  getToken(): PlaudTokenData | undefined {
    return this.load().token;
  }

  /**
   * Resolve credentials from env vars first, then config file.
   * Env vars: PLAUD_EMAIL, PLAUD_PASSWORD, PLAUD_REGION
   */
  getCredentials(): PlaudCredentials | undefined {
    // Environment variables take precedence (useful for Cowork/CI)
    const email = process.env.PLAUD_EMAIL;
    const password = process.env.PLAUD_PASSWORD;
    const region = (process.env.PLAUD_REGION ?? 'us') as 'us' | 'eu';

    if (email && password) {
      return { email, password, region };
    }

    // Fall back to config file (plaud-toolkit compatible)
    return this.load().credentials;
  }
}
