export interface StockSearchResult {
  symbol: string;
  name: string;
  exchange: string;
}

export interface StockSearchResponse {
  results: StockSearchResult[];
}

export interface OHLCVPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface OverviewStats {
  current_price: number;
  price_change_1d: number;
  price_change_1d_percent: number;
  market_cap?: number;
  pe_ratio?: number;
  week_52_high?: number;
  week_52_low?: number;
  avg_volume?: number;
}

export interface StockOverviewResponse {
  symbol: string;
  name: string;
  current_price: number;
  chart_data: OHLCVPoint[];
  buy_hold_return: number;
  stats: OverviewStats;
}

export interface StrategyParameter {
  name: string;
  type: 'number' | 'boolean' | 'enum';
  default: number | boolean | string;
  min?: number;
  max?: number;
  step?: number;
  options?: string[];
  description: string;
}

export interface StrategyInfo {
  name: string;
  display_name: string;
  description: string;
  parameters: Record<string, StrategyParameter>;
}

export interface StrategiesResponse {
  strategies: StrategyInfo[];
}

export interface TradeMetadata {
  reason: string;
  action: 'LONG' | 'SHORT' | 'EXIT';
  price: number;
  quantity: number;
  sentiment_score_at_trade?: number;
}

export interface NewsSentimentSummary {
  avg_sentiment: number;
  news_count: number;
  dominant_theme: string;
  impact_assessment: string;
}

export interface BacktestMetrics {
  total_return: number;
  annualized_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  total_trades: number;
  profit_factor: number;
}

export interface BacktestResponse {
  metrics: BacktestMetrics;
  equity_curve: OHLCVPoint[];
  trades: TradeMetadata[];
  buy_hold_comparison: {
    strategy_return: number;
    buy_hold_return: number;
    outperformance: number;
  };
  news_sentiment_summary?: NewsSentimentSummary;
  ai_reasoning_text?: string;
  ai_analysis?: AIAnalysis;
}

export interface AIAnalysis {
  performance_summary: string;
  news_impact: string;
  political_factors: string;
  parameter_sensitivity: string;
  suggestions: string[];
  confidence_score: number;
}

export interface BacktestRequest {
  symbol: string;
  strategy_type: string;
  params: Record<string, any>;
  initial_capital: number;
  commission: number;
  include_news_analysis?: boolean;
}

export interface ErrorResponse {
  detail: string;
}
