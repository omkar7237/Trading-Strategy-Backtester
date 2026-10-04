import React, { useState, useCallback, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import { Play, RefreshCw, TrendingUp, AlertCircle } from 'lucide-react';
import { getStrategies, runBacktest } from '../api';
import type { StrategyInfo, BacktestRequest } from '../types';
import { AppHeader, PriceChart, MetricsCard } from '../components';
import { AIAnalysisPanel } from '../components/AIAnalysisPanel';
import { recordStockView } from '../lib/recentStocks';

export const BacktestDashboard: React.FC = () => {
  const [searchParams] = useSearchParams();
  
  const initialSymbol = searchParams.get('symbol') || 'AAPL';
  
  const [selectedStrategy, setSelectedStrategy] = useState<string>('');
  const [params, setParams] = useState<Record<string, any>>({});
  const [initialCapital] = useState(10000);
  const [commission] = useState(0.001);
  const [includeNewsAnalysis, setIncludeNewsAnalysis] = useState(true);

  const { data: strategiesData } = useQuery({
    queryKey: ['strategies'],
    queryFn: getStrategies,
    staleTime: 10 * 60 * 1000,
  });

  const strategies = strategiesData?.strategies || [];
    const selectedStrategyInfo = strategies.find(s => s.id === selectedStrategy);

    // Running a backtest means the user is working with this ticker, so count
    // it as a view too. No name is known here — the overview page supplies the
    // real one later, and recordStockView keeps whichever it has.
    useEffect(() => {
      if (initialSymbol) {
        recordStockView(initialSymbol);
      }
    }, [initialSymbol]);

  const handleStrategyChange = useCallback((strategyId: string) => {
      setSelectedStrategy(strategyId);
      // Seed the form with the strategy's declared defaults. `parameters` is a
      // list, so index it by name to build the initial values map.
      const strategy = strategies.find(s => s.id === strategyId);
      if (strategy) {
        const defaultParams: Record<string, any> = {};
        strategy.parameters.forEach((param) => {
          defaultParams[param.name] = param.default;
        });
        setParams(defaultParams);
      }
    }, [strategies]);

  const handleParamChange = useCallback((paramName: string, value: any) => {
    setParams(prev => ({ ...prev, [paramName]: value }));
  }, []);

  const backtestMutation = useMutation({
    mutationFn: async (request: BacktestRequest) => {
      return await runBacktest(request);
    },
  });

  const handleRunBacktest = useCallback(() => {
    if (!selectedStrategy) return;
    
    const request: BacktestRequest = {
      symbol: initialSymbol,
      strategy_type: selectedStrategy,
      params,
      initial_capital: initialCapital,
      commission,
      include_news_analysis: includeNewsAnalysis,
    };
    
    backtestMutation.mutate(request);
  }, [selectedStrategy, params, initialSymbol, initialCapital, commission, includeNewsAnalysis, backtestMutation]);

  const result = backtestMutation.data;

  return (
    <div className="min-h-screen bg-gray-50">
          <AppHeader />

          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Panel - Controls */}
          <div className="lg:col-span-1 space-y-6">
            {/* Strategy Selector */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Strategy Configuration</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Strategy
                  </label>
                  <select
                    value={selectedStrategy}
                    onChange={(e) => handleStrategyChange(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">Select a strategy...</option>
                    {strategies.map((strategy: StrategyInfo) => (
                                          <option key={strategy.id} value={strategy.id}>
                                            {strategy.name}
                                          </option>
                                        ))}
                  </select>
                </div>

                {/* Dynamic Parameters */}
                                {selectedStrategy && (
                                  <div className="space-y-4 pt-4 border-t border-gray-200">
                                    <h3 className="text-sm font-medium text-gray-700">Parameters</h3>
                                    {selectedStrategyInfo?.parameters.map((paramDef) => {
                                      const value = params[paramDef.name];

                                      return (
                                        <div key={paramDef.name}>
                                          <label className="block text-sm text-gray-600 mb-1">
                                            {paramDef.description || paramDef.name}
                                          </label>

                                          {(paramDef.type === 'int' || paramDef.type === 'float') && (
                                            <div className="flex items-center gap-2">
                                              <input
                                                type="range"
                                                min={paramDef.min_val}
                                                max={paramDef.max_val}
                                                step={paramDef.step || 1}
                                                value={value}
                                                onChange={(e) => handleParamChange(paramDef.name, parseFloat(e.target.value))}
                                                className="flex-1"
                                              />
                                              <span className="w-16 text-right text-sm font-medium">{value}</span>
                                            </div>
                                          )}

                                          {paramDef.type === 'bool' && (
                                            <button
                                              onClick={() => handleParamChange(paramDef.name, !value)}
                                              className={`px-3 py-1 rounded-full text-sm font-medium ${
                                                value ? 'bg-success text-white' : 'bg-gray-200 text-gray-700'
                                              }`}
                                            >
                                              {value ? 'Enabled' : 'Disabled'}
                                            </button>
                                          )}

                                          {paramDef.type === 'enum' && paramDef.options && (
                                            <select
                                              value={value}
                                              onChange={(e) => handleParamChange(paramDef.name, e.target.value)}
                                              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                                            >
                                              {paramDef.options.map((opt: string) => (
                                                <option key={opt} value={opt}>{opt}</option>
                                              ))}
                                            </select>
                                          )}
                                        </div>
                                      );
                                    })}
                                  </div>
                                )}

                <div className="pt-4 border-t border-gray-200">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={includeNewsAnalysis}
                      onChange={(e) => setIncludeNewsAnalysis(e.target.checked)}
                      className="rounded border-gray-300 text-primary-500 focus:ring-primary-500"
                    />
                    <span className="text-sm text-gray-700">Include AI News Analysis</span>
                  </label>
                </div>

                <button
                  onClick={handleRunBacktest}
                  disabled={!selectedStrategy || backtestMutation.isPending}
                  className="w-full py-3 bg-primary-500 text-white font-semibold rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {backtestMutation.isPending ? (
                    <>
                      <RefreshCw className="h-5 w-5 animate-spin" />
                      Running...
                    </>
                  ) : (
                    <>
                      <Play className="h-5 w-5" />
                      Run Backtest
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Right Panel - Results */}
          <div className="lg:col-span-2 space-y-6">
            {result && (
                          <>
                            {/* Performance Metrics */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                              <MetricsCard
                                title="Total Return"
                                value={`${result.total_return_percent.toFixed(2)}%`}
                                change={result.total_return_percent}
                              />
                              <MetricsCard
                                title="Net Profit"
                                value={`$${result.total_return.toFixed(2)}`}
                              />
                              <MetricsCard
                                title="Sharpe Ratio"
                                value={result.sharpe_ratio.toFixed(2)}
                              />
                              <MetricsCard
                                title="Max Drawdown"
                                value={`${(result.max_drawdown * 100).toFixed(2)}%`}
                              />
                            </div>

                {/* Equity Curve */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Equity Curve</h3>
                  <PriceChart data={result.equity_curve} height={300} />
                </div>

                {/* Trade Summary */}
                                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                                    Trade Summary ({result.trade_count} trades)
                                  </h3>
                                  <div className="overflow-x-auto">
                                    <table className="w-full">
                                      <thead>
                                        <tr className="border-b border-gray-200">
                                          <th className="text-left py-3 px-4 font-medium text-gray-700">Date</th>
                                          <th className="text-left py-3 px-4 font-medium text-gray-700">Action</th>
                                          <th className="text-right py-3 px-4 font-medium text-gray-700">Price</th>
                                          <th className="text-right py-3 px-4 font-medium text-gray-700">Quantity</th>
                                          <th className="text-left py-3 px-4 font-medium text-gray-700">Reason</th>
                                        </tr>
                                      </thead>
                                      <tbody>
                                        {result.trades.length === 0 && (
                                          <tr>
                                            <td colSpan={5} className="py-3 px-4 text-gray-500">
                                              No trades were generated for these parameters.
                                            </td>
                                          </tr>
                                        )}
                                        {result.trades.map((trade, index) => (
                                          <tr key={index} className="border-b border-gray-100">
                                            <td className="py-3 px-4 text-gray-600">{trade.date}</td>
                                            <td className={`py-3 px-4 font-medium ${trade.action === 'BUY' ? 'text-success' : 'text-danger'}`}>
                                              {trade.action}
                                            </td>
                                            <td className="py-3 px-4 text-right">${trade.price.toFixed(2)}</td>
                                            <td className="py-3 px-4 text-right">{trade.quantity}</td>
                                            <td className="py-3 px-4 text-gray-600">{trade.reason}</td>
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  </div>
                                </div>

                                {/* News Sentiment */}
                                {result.news_sentiment_summary && (
                                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4">News Sentiment</h3>
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                      <div>
                                        <p className="text-sm text-gray-500">Average Sentiment</p>
                                        <p className={`text-2xl font-bold ${
                                          result.news_sentiment_summary.avg_sentiment >= 0 ? 'text-success' : 'text-danger'
                                        }`}>
                                          {result.news_sentiment_summary.avg_sentiment.toFixed(3)}
                                        </p>
                                      </div>
                                      <div>
                                        <p className="text-sm text-gray-500">Articles Analyzed</p>
                                        <p className="text-2xl font-bold text-gray-900">
                                          {result.news_sentiment_summary.news_count}
                                        </p>
                                      </div>
                                      <div>
                                        <p className="text-sm text-gray-500">Impact Assessment</p>
                                        <p className="text-gray-700 mt-2">{result.news_sentiment_summary.impact_assessment}</p>
                                      </div>
                                    </div>
                                  </div>
                                )}

                                {/* AI Reasoning */}
                                {result.ai_reasoning_text && (
                                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Reasoning</h3>
                                    <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                                      {result.ai_reasoning_text}
                                    </p>
                                  </div>
                                )}

                {/* AI Analysis */}
                {result.ai_analysis && (
                  <AIAnalysisPanel analysis={result.ai_analysis} />
                )}
              </>
            )}

            {!result && !backtestMutation.isPending && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
                <TrendingUp className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No Backtest Results Yet</h3>
                <p className="text-gray-600 mb-4">
                  Select a strategy and configure parameters to run your first backtest.
                </p>
              </div>
            )}

            {backtestMutation.isError && (
              <div className="bg-danger/10 border border-danger rounded-xl p-6">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-6 w-6 text-danger flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold text-danger mb-1">Backtest Failed</h3>
                    <p className="text-gray-700">
                      {backtestMutation.error instanceof Error 
                        ? backtestMutation.error.message 
                        : 'An unexpected error occurred'}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};
