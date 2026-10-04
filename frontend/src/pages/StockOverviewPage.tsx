import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { TrendingUp, DollarSign, BarChart3, Activity } from 'lucide-react';
import { getStockOverview } from '../api';
import { AppHeader, PriceChart, MetricsCard } from '../components';
import { recordStockView } from '../lib/recentStocks';

export const StockOverviewPage: React.FC = () => {
  const { ticker } = useParams<{ ticker: string }>();
  const navigate = useNavigate();

  const { data, isLoading, error } = useQuery({
    queryKey: ['stockOverview', ticker],
    queryFn: () => getStockOverview(ticker!),
    enabled: !!ticker,
    staleTime: 5 * 60 * 1000,
  });

  // Record the visit once real data is in, so the recents list gets the
  // company name from the API rather than echoing back the bare ticker.
  useEffect(() => {
    if (data?.symbol && data?.name) {
      recordStockView(data.symbol, data.name);
    }
  }, [data?.symbol, data?.name]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading stock data...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Data</h2>
          <p className="text-gray-600 mb-4">
            {error instanceof Error ? error.message : 'Failed to load stock overview'}
          </p>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  const handleRunBacktest = () => {
    navigate(`/backtest?symbol=${data.symbol}`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
          <AppHeader />

          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stock Title */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-2">
            <h2 className="text-3xl font-bold text-gray-900">{data.symbol}</h2>
            <span className="text-lg text-gray-600">{data.name}</span>
          </div>
          <div className="flex items-center gap-4">
                      <span className="text-4xl font-bold text-gray-900">${data.current_price.toFixed(2)}</span>
                      <span className={`text-lg font-medium ${data.stats.day_change_percent >= 0 ? 'text-success' : 'text-danger'}`}>
                        {data.stats.day_change_percent >= 0 ? '+' : ''}{data.stats.day_change_percent.toFixed(2)}%
                      </span>
                    </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricsCard
                      title="Buy & Hold Return (1Y)"
                      value={`${data.buy_hold_return_1y.toFixed(2)}%`}
                      change={data.buy_hold_return_1y}
                      icon={<TrendingUp className="h-5 w-5" />}
                    />
                    <MetricsCard
                      title="Current Price"
                      value={`$${data.current_price.toFixed(2)}`}
                      icon={<DollarSign className="h-5 w-5" />}
                    />
                    <MetricsCard
                      title="P/E Ratio"
                      value={data.stats.pe_ratio?.toFixed(2) || 'N/A'}
                      icon={<BarChart3 className="h-5 w-5" />}
                    />
                    <MetricsCard
                      title="52-Week Range"
                      value={`$${data.stats.year_low.toFixed(2)} - $${data.stats.year_high.toFixed(2)}`}
                      icon={<Activity className="h-5 w-5" />}
                    />
        </div>

        {/* Price Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">1 Year Price Chart</h3>
          <PriceChart data={data.chart_data} height={400} />
        </div>

        {/* Run Backtest CTA */}
        <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl p-8 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-bold mb-2">Ready to Test Your Strategy?</h3>
              <p className="text-primary-100">
                Run a backtest on {data.symbol} with customizable parameters and AI-powered analysis.
              </p>
            </div>
            <button
              onClick={handleRunBacktest}
              className="px-6 py-3 bg-white text-primary-600 font-semibold rounded-lg hover:bg-primary-50 transition-colors"
            >
              Run Backtest
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};
