// Tracks which tickers the user has opened, most-recent first, persisted to
// localStorage. Visits are recorded on both the overview page and the backtest
// dashboard so the list reflects anything actually looked at.
//
// Storage is best-effort: private-mode / quota-exceeded failures degrade to
// an in-memory list rather than breaking the page.

const STORAGE_KEY = 'tsb.recentStocks';
const MAX_ENTRIES = 8;

export interface RecentStock {
  symbol: string;
  name: string;
  /** Epoch ms of the most recent visit. */
  lastViewed: number;
  /** How many times the ticker has been opened. */
  viewCount: number;
}

// Module-level mirror of storage, so reads are synchronous for consumers and
// the list survives navigation within a session even if writes are debounced.
let cache: RecentStock[] | null = null;

function isBrowser() {
  return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';
}

function readStorage(): RecentStock[] {
  if (cache) return cache;

  if (!isBrowser()) {
    cache = [];
    return cache;
  }

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      cache = [];
      return cache;
    }
    const parsed = JSON.parse(raw);
    cache = Array.isArray(parsed) ? parsed.filter(isValidEntry) : [];
  } catch {
    // Corrupt or unreadable payload — start clean rather than throwing.
    cache = [];
  }

  return cache;
}

function isValidEntry(entry: unknown): entry is RecentStock {
  if (typeof entry !== 'object' || entry === null) return false;
  const e = entry as Record<string, unknown>;
  return (
    typeof e.symbol === 'string' &&
    typeof e.name === 'string' &&
    typeof e.lastViewed === 'number' &&
    typeof e.viewCount === 'number'
  );
}

function writeStorage(entries: RecentStock[]) {
  cache = entries;
  if (!isBrowser()) return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
  } catch {
    // Quota or private mode — keep the in-memory cache, skip persistence.
  }
}

export function getRecentStocks(): RecentStock[] {
  return [...readStorage()].sort((a, b) => b.lastViewed - a.lastViewed);
}

/**
 * Record a visit to `symbol`. Re-visiting bumps it to the front and
 * increments viewCount; a first visit appends it. Blank names are tolerated
 * because some callers only know the ticker.
 */
export function recordStockView(symbol: string, name?: string) {
  const clean = symbol.trim().toUpperCase();
  if (!clean) return;

  const entries = readStorage();
  const existing = entries.find(e => e.symbol === clean);
  const displayName = name?.trim() || existing?.name || clean;

  const updated: RecentStock = {
    symbol: clean,
    name: displayName,
    lastViewed: Date.now(),
    viewCount: (existing?.viewCount ?? 0) + 1,
  };

  const next = [updated, ...entries.filter(e => e.symbol !== clean)]
    .sort((a, b) => b.lastViewed - a.lastViewed)
    .slice(0, MAX_ENTRIES);

  writeStorage(next);
}

/** Remove a single ticker (used by the per-item dismiss button). */
export function removeRecentStock(symbol: string) {
  const clean = symbol.trim().toUpperCase();
  writeStorage(readStorage().filter(e => e.symbol !== clean));
}

/** Clear the whole list. */
export function clearRecentStocks() {
  writeStorage([]);
}

export const RECENT_STOCKS_KEY = STORAGE_KEY;