// Types mirror the FastAPI schemas in api/main.py exactly.
// Field names are snake_case on the wire (no camelCase mapping layer).

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

// Mirrors OverviewStats: there is no avg_volume, and the 52-week bounds are
// named year_high / year_low (not week_52_*).
export interface OverviewStats {
  current_price: number;
  day_change_percent: number;
  year_high: number;
  year_low: number;
  market_cap?: number;
  pe_ratio?: number;
}

export interface StockOverviewResponse {
  symbol: string;
  name: string;
  current_price: number;
  buy_hold_return_1y: number;
  stats: OverviewStats;
  chart_data: OHLCVPoint[];
}

// Mirrors StrategyParameter: the API sends type strings like "int"/"float"
// (not "number") and constraints named min_val/max_val (not min/max).
export interface StrategyParameter {
  name: string;
  type: 'int' | 'float' | 'bool' | 'enum' | string;
  default: any;
  min_val?: number;
  max_val?: number;
  step?: number;
  options?: string[];
  description?: string;
}

// Mirrors StrategyInfo: the identifier that /api/backtest expects is `id`,
// the human label is `name`, and `parameters` is a LIST (not a keyed record).
export interface StrategyInfo {
  id: string;
  name: string;
  description: string;
  parameters: StrategyParameter[];
}

export interface StrategiesResponse {
  strategies: StrategyInfo[];
}

export interface TradeMetadata {
  date: string;
  action: string;
  price: number;
  quantity: number;
  reason: string;
  sentiment_score_at_trade?: number | null;
}

export interface NewsSentimentSummary {
  avg_sentiment: number;
  news_count: number;
  dominant_theme: string;
  impact_assessment: string;
}

// Mirrors BacktestResponse: metrics are FLAT top-level fields (not nested
// under a `metrics` object), and `equity_curve` is {date, value} pairs — not
// OHLCV — so it gets its own type. total_return is a currency amount while
// total_return_percent is the scaled percentage.
export interface BacktestResponse {
  symbol: string;
  strategy_type: string;
  total_return: number;
  total_return_percent: number;
  sharpe_ratio: number;
  max_drawdown: number;
  trade_count: number;
  equity_curve: EquityPoint[];
  trades: TradeMetadata[];
  news_sentiment_summary?: NewsSentimentSummary | null;
  ai_reasoning_text?: string | null;
  ai_analysis?: AIAnalysis | null;
}

export interface EquityPoint {
  date: string;
  value: number;
}

export interface NewsEventDetail {
  headline: string;
  date: string;
  sentiment_impact: string;
}

// Mirrors AIAnalysisDetail in api/main.py, which mirrors
// ai.reasoning_engine.AIAnalysisResult.to_dict().
export interface AIAnalysis {
  performance_summary: string;
  outperformance_reasons: string[];
  underperformance_reasons: string[];
  key_news_events: NewsEventDetail[];
  sentiment_impact_analysis: string;
  political_factors: string[];
  parameter_sensitivity: Record<string, any>;
  strategy_strengths: string[];
  strategy_weaknesses: string[];
  suggestions: string[];
  risk_warnings: string[];
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
