import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, Trash2, X, TrendingUp, TrendingDown, Eye } from 'lucide-react';
import { getRecentStocks, removeRecentStock, clearRecentStocks } from '../lib/recentStocks';
import type { RecentStock } from '../lib/recentStocks';
import type { StockOverviewResponse } from '../types';
import { getStockOverview } from '../api';

/**
 * "Recently viewed" panel for the home page. Each row shows the cached name
 * from localStorage immediately, then upgrades to live price/change once the
 * overview fetch resolves — so the list paints instantly without waiting on
 * the network.
 */
export const RecentStocksPanel: React.FC = () => {
  const navigate = useNavigate();
  const [recent, setRecent] = useState<RecentStock[]>([]);
  // Live stats keyed by symbol; absent until each fetch resolves.
  const [liveStats, setLiveStats] = useState<
    Record<string, { price: number; dayChangePercent: number }>
  >({});

  const loadRecents = useCallback(() => {
    setRecent(getRecentStocks());
  }, []);

  useEffect(() => {
    loadRecents();
    // Re-read when the window regains focus so views made in another tab
    // (or via back-navigation) are reflected.
    window.addEventListener('focus', loadRecents);
    return () => window.removeEventListener('focus', loadRecents);
  }, [loadRecents]);

  // Fetch live stats for each ticker; failures just leave the row showing
  // its stored name, so one bad ticker can't blank the whole panel.
  useEffect(() => {
    let cancelled = false;

    recent.forEach(async (entry) => {
      if (liveStats[entry.symbol]) return;
      try {
        const data: StockOverviewResponse = await getStockOverview(entry.symbol);
        if (cancelled) return;
        setLiveStats(prev => {
          if (prev[entry.symbol]) return prev;
          return {
            ...prev,
            [entry.symbol]: {
              price: data.current_price,
              dayChangePercent: data.stats.day_change_percent,
            },
          };
        });
      } catch {
        // Leave this row without live stats.
      }
    });

    return () => { cancelled = true; };
  }, [recent]);

  const handleDismiss = (e: React.MouseEvent, symbol: string) => {
    // Stop the click from also navigating via the row's own handler.
    e.stopPropagation();
    e.preventDefault();
    removeRecentStock(symbol);
    setRecent(getRecentStocks());
  };

  const handleClearAll = () => {
    clearRecentStocks();
    setRecent([]);
    setLiveStats({});
  };

  if (recent.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
        <Clock className="h-10 w-10 text-gray-300 mx-auto mb-3" />
        <h3 className="text-lg font-semibold text-gray-900 mb-1">No recent stocks</h3>
        <p className="text-gray-600 text-sm">
          Search for a ticker above — anything you open shows up here for quick access.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-primary-500" />
          <h3 className="text-lg font-semibold text-gray-900">Recently Viewed</h3>
          <span className="text-sm text-gray-500">({recent.length})</span>
        </div>
        <button
          onClick={handleClearAll}
          className="flex items-center gap-1 text-sm text-gray-500 hover:text-danger transition-colors"
        >
          <Trash2 className="h-4 w-4" />
          Clear all
        </button>
      </div>

      <div className="divide-y divide-gray-100">
        {recent.map((entry) => {
          const stats = liveStats[entry.symbol];
          const isPositive = stats ? stats.dayChangePercent >= 0 : true;

          return (
            <div
              key={entry.symbol}
              role="button"
              tabIndex={0}
              onClick={() => navigate(`/stock/${entry.symbol}`)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  navigate(`/stock/${entry.symbol}`);
                }
              }}
              className="flex items-center justify-between px-6 py-4 hover:bg-gray-50 cursor-pointer transition-colors group"
            >
              <div className="flex items-center gap-4 min-w-0">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-gray-900">{entry.symbol}</span>
                    <span className="text-sm text-gray-500 truncate">{entry.name}</span>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-gray-400 mt-0.5">
                    <Eye className="h-3 w-3" />
                    Viewed {entry.viewCount} {entry.viewCount === 1 ? 'time' : 'times'}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4 shrink-0">
                {stats ? (
                  <div className="text-right">
                    <p className="font-medium text-gray-900">
                      ${stats.price.toLocaleString('en-US', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      })}
                    </p>
                    <p className={`text-sm flex items-center justify-end gap-1 ${
                      isPositive ? 'text-success' : 'text-danger'
                    }`}>
                      {isPositive ? (
                        <TrendingUp className="h-3.5 w-3.5" />
                      ) : (
                        <TrendingDown className="h-3.5 w-3.5" />
                      )}
                      {isPositive ? '+' : ''}{stats.dayChangePercent.toFixed(2)}%
                    </p>
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">Loading…</p>
                )}

                <button
                  onClick={(e) => handleDismiss(e, entry.symbol)}
                  title={`Remove ${entry.symbol} from recent stocks`}
                  aria-label={`Remove ${entry.symbol} from recent stocks`}
                  className="p-1 text-gray-300 hover:text-danger opacity-0 group-hover:opacity-100 focus:opacity-100 transition-all"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};