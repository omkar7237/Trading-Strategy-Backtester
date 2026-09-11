from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Search ---
class StockSearchResult(BaseModel):
    symbol: str
    name: str
    exchange: str

class StockSearchResponse(BaseModel):
    results: List[StockSearchResult]

# --- Overview ---
class OHLCVPoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class OverviewStats(BaseModel):
    current_price: float
    day_change_percent: float
    year_high: float
    year_low: float
    market_cap: Optional[int] = None
    pe_ratio: Optional[float] = None

class StockOverviewResponse(BaseModel):
    symbol: str
    name: str
    current_price: float
    buy_hold_return_1y: float
    stats: OverviewStats
    chart_data: List[OHLCVPoint]

# --- Strategies ---
class StrategyParameter(BaseModel):
    name: str
    type: str  # "int", "float", "bool"
    default: Any
    min_val: Optional[Any] = None
    max_val: Optional[Any] = None
    step: Optional[float] = None

class StrategyInfo(BaseModel):
    id: str
    name: str
    description: str
    parameters: List[StrategyParameter]

class StrategiesResponse(BaseModel):
    strategies: List[StrategyInfo]

# --- Backtest ---
class BacktestRequest(BaseModel):
    symbol: str
    strategy_type: str = Field(..., description="e.g., 'news_enhanced_ma', 'rsi', 'macd'")
    params: Dict[str, Any] = Field(default_factory=dict)
    initial_capital: float = 10000.0
    commission: float = 0.001
    include_news_analysis: bool = True

class TradeMetadata(BaseModel):
    date: str
    action: str  # "BUY", "SELL"
    price: float
    quantity: int
    reason: str
    sentiment_score_at_trade: Optional[float] = None

class NewsSentimentSummary(BaseModel):
    avg_sentiment: float
    news_count: int
    dominant_theme: str
    impact_assessment: str

class BacktestResponse(BaseModel):
    symbol: str
    strategy_type: str
    total_return: float
    total_return_percent: float
    sharpe_ratio: float
    max_drawdown: float
    trade_count: int
    equity_curve: List[Dict[str, Any]]  # [{date, value}, ...]
    trades: List[TradeMetadata]
    news_sentiment_summary: Optional[NewsSentimentSummary] = None
    ai_reasoning_text: Optional[str] = None

# --- Error ---
class ErrorResponse(BaseModel):
    detail: str
    error_code: str
