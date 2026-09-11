import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
from functools import lru_cache
import random

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.loader import load_data, load_enriched_data
from data.indicator import sma, ema, rsi, macd, bollinger_bands
from strategy.basic_strategy import MACrossoverStrategy, RSIStrategy, MACDStrategy, CombinedStrategy
from backtest.engine import BacktestEngine
from ai.reasoning_engine import generate_backtest_analysis as ai_generate_analysis

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI(
    title="Trading Strategy Backtester API",
    description="API for running trading strategy backtests with news sentiment integration",
    version="1.0.0"
)

# CORS Configuration for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-Memory Cache for Stock Overviews (TTL: 5 minutes) ---
overview_cache: Dict[str, tuple] = {}  # {ticker: (data, timestamp)}
CACHE_TTL_SECONDS = 300

def is_cache_valid(ticker: str) -> bool:
    """Check if cached data is still valid."""
    if ticker not in overview_cache:
        return False
    _, timestamp = overview_cache[ticker]
    return (datetime.now() - timestamp).total_seconds() < CACHE_TTL_SECONDS


# --- Pydantic Schemas for API ---

class StockSearchResult(BaseModel):
    symbol: str
    name: str
    exchange: str

class StockSearchResponse(BaseModel):
    results: List[StockSearchResult]

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

class StrategyParameter(BaseModel):
    name: str
    type: str
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

class BacktestRequestLegacy(BaseModel):
    symbol: str = "AAPL"
    initial_capital: float = 10000
    commission: float = 0.001
    slippage: float = 0
    position_size: float = 0.5
    short_window: int = 20
    long_window: int = 50

class BacktestRequest(BaseModel):
    symbol: str
    strategy_type: str = Field(..., description="e.g., 'news_enhanced_ma', 'rsi', 'macd'")
    params: Dict[str, Any] = Field(default_factory=dict)
    initial_capital: float = 10000.0
    commission: float = 0.001
    include_news_analysis: bool = True

class TradeMetadata(BaseModel):
    date: str
    action: str
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
    equity_curve: List[Dict[str, Any]]
    trades: List[TradeMetadata]
    news_sentiment_summary: Optional[NewsSentimentSummary] = None
    ai_reasoning_text: Optional[str] = None


# --- Helper Functions ---

def search_stocks_yfinance(query: str) -> List[Dict]:
    """Search stocks using yfinance ticker lookup."""
    results = []
    query_upper = query.upper()
    
    # Try exact match first
    try:
        ticker = yf.Ticker(query_upper)
        info = ticker.info
        if info.get('symbol'):
            results.append({
                "symbol": info.get('symbol', query_upper),
                "name": info.get('shortName', info.get('longName', 'N/A')),
                "exchange": info.get('exchange', 'Unknown')
            })
    except Exception:
        pass
    
    # Common tickers for demo purposes
    common_tickers = {
        'AAPL': ('Apple Inc.', 'NASDAQ'),
        'GOOGL': ('Alphabet Inc.', 'NASDAQ'),
        'MSFT': ('Microsoft Corporation', 'NASDAQ'),
        'AMZN': ('Amazon.com Inc.', 'NASDAQ'),
        'TSLA': ('Tesla Inc.', 'NASDAQ'),
        'META': ('Meta Platforms Inc.', 'NASDAQ'),
        'NVDA': ('NVIDIA Corporation', 'NASDAQ'),
        'JPM': ('JPMorgan Chase & Co.', 'NYSE'),
        'V': ('Visa Inc.', 'NYSE'),
        'WMT': ('Walmart Inc.', 'NYSE'),
    }
    
    for symbol, (name, exchange) in common_tickers.items():
        if query_upper in symbol or query_upper in name.upper():
            if not any(r['symbol'] == symbol for r in results):
                results.append({
                    "symbol": symbol,
                    "name": name,
                    "exchange": exchange
                })
    
    return results[:10]


def get_stock_overview_data(ticker: str) -> Dict[str, Any]:
    """Fetch comprehensive stock overview data."""
    try:
        tk = yf.Ticker(ticker)
        info = tk.info
        
        # Get 1 year of historical data
        hist = tk.history(period="1y")
        
        if hist.empty:
            raise ValueError(f"No data found for ticker {ticker}")
        
        current_price = hist['Close'].iloc[-1]
        year_ago_price = hist['Close'].iloc[0] if len(hist) > 1 else current_price
        buy_hold_return = ((current_price - year_ago_price) / year_ago_price) * 100
        
        # Build chart data
        chart_data = []
        for date, row in hist.iterrows():
            chart_data.append(OHLCVPoint(
                date=date.strftime('%Y-%m-%d'),
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=int(row['Volume'])
            ))
        
        # Calculate stats
        year_high = float(hist['High'].max())
        year_low = float(hist['Low'].min())
        day_change = ((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2] * 100) if len(hist) > 1 else 0.0
        
        stats = OverviewStats(
            current_price=float(current_price),
            day_change_percent=round(day_change, 2),
            year_high=year_high,
            year_low=year_low,
            market_cap=info.get('marketCap'),
            pe_ratio=info.get('trailingPE')
        )
        
        return {
            "symbol": info.get('symbol', ticker.upper()),
            "name": info.get('shortName', info.get('longName', 'N/A')),
            "current_price": float(current_price),
            "buy_hold_return_1y": round(buy_hold_return, 2),
            "stats": stats,
            "chart_data": chart_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch data for {ticker}: {str(e)}")


def get_available_strategies() -> List[StrategyInfo]:
    """Return list of available strategies with their parameters."""
    return [
        StrategyInfo(
            id="simple_ma",
            name="Simple Moving Average Crossover",
            description="Buy when short MA crosses above long MA, sell on reverse.",
            parameters=[
                StrategyParameter(name="short_window", type="int", default=20, min_val=5, max_val=50, step=1),
                StrategyParameter(name="long_window", type="int", default=50, min_val=20, max_val=200, step=1),
            ]
        ),
        StrategyInfo(
            id="news_enhanced_ma",
            name="News-Enhanced MA Crossover",
            description="MA crossover strategy weighted by news sentiment analysis.",
            parameters=[
                StrategyParameter(name="short_window", type="int", default=20, min_val=5, max_val=50, step=1),
                StrategyParameter(name="long_window", type="int", default=50, min_val=20, max_val=200, step=1),
                StrategyParameter(name="news_weight", type="float", default=0.4, min_val=0.0, max_val=1.0, step=0.1),
            ]
        ),
        StrategyInfo(
            id="rsi",
            name="RSI Mean Reversion",
            description="Buy when RSI is oversold, sell when overbought.",
            parameters=[
                StrategyParameter(name="rsi_period", type="int", default=14, min_val=7, max_val=28, step=1),
                StrategyParameter(name="oversold_threshold", type="float", default=30.0, min_val=20.0, max_val=40.0, step=1.0),
                StrategyParameter(name="overbought_threshold", type="float", default=70.0, min_val=60.0, max_val=80.0, step=1.0),
            ]
        ),
        StrategyInfo(
            id="macd",
            name="MACD Momentum",
            description="Trade based on MACD line crossing signal line.",
            parameters=[
                StrategyParameter(name="fast_period", type="int", default=12, min_val=5, max_val=20, step=1),
                StrategyParameter(name="slow_period", type="int", default=26, min_val=15, max_val=50, step=1),
                StrategyParameter(name="signal_period", type="int", default=9, min_val=5, max_val=15, step=1),
            ]
        ),
    ]


def run_backtest_logic(
    symbol: str, 
    strategy_type: str, 
    params: Dict[str, Any], 
    initial_capital: float, 
    commission: float,
    include_news: bool
) -> Dict[str, Any]:
    """
    Enhanced backtest logic supporting news-enhanced strategies.
    """
    try:
        tk = yf.Ticker(symbol)
        hist = tk.history(period="1y")
        
        if hist.empty:
            raise ValueError(f"No data found for {symbol}")
        
        # Simulate trades based on strategy type
        trades = []
        equity_curve = []
        
        cash = initial_capital
        shares = 0
        entry_price = 0
        
        # Get parameters
        short_window = params.get('short_window', 20)
        long_window = params.get('long_window', 50)
        news_weight = params.get('news_weight', 0.4) if strategy_type == 'news_enhanced_ma' else 0.0
        
        # Calculate moving averages
        hist['SMA_SHORT'] = hist['Close'].rolling(window=short_window).mean()
        hist['SMA_LONG'] = hist['Close'].rolling(window=long_window).mean()
        
        # Generate sentiment for demo (would come from news_processor in production)
        base_sentiment = random.uniform(-0.3, 0.5)
        
        prev_short_above_long = False
        trade_reason_base = f"{strategy_type.replace('_', ' ').title()} strategy: "
        
        for i in range(long_window, len(hist)):
            date = hist.index[i]
            price = float(hist['Close'].iloc[i])
            short_ma = float(hist['SMA_SHORT'].iloc[i])
            long_ma = float(hist['SMA_LONG'].iloc[i])
            
            short_above_long = short_ma > long_ma
            
            # Sentiment adjustment for news-enhanced strategy
            if include_news and strategy_type == 'news_enhanced_ma':
                sentiment_boost = base_sentiment * news_weight
                adjusted_signal = (short_ma - long_ma) / long_ma + sentiment_boost
                should_buy = adjusted_signal > 0.01
                should_sell = adjusted_signal < -0.01
            else:
                should_buy = short_above_long and not prev_short_above_long
                should_sell = not short_above_long and prev_short_above_long
            
            # Execute trades
            if should_buy and cash > price * 10:
                shares_to_buy = int(cash * 0.95 / price)
                if shares_to_buy > 0:
                    cost = shares_to_buy * price * (1 + commission)
                    if cost <= cash:
                        cash -= cost
                        shares += shares_to_buy
                        entry_price = price
                        
                        sentiment_at_trade = round(base_sentiment, 3) if include_news else None
                        reason = f"{trade_reason_base}Short MA ({short_window}) crossed above Long MA ({long_window})"
                        if include_news and strategy_type == 'news_enhanced_ma':
                            reason += f". Sentiment boost: {sentiment_boost:.3f}"
                        
                        trades.append(TradeMetadata(
                            date=date.strftime('%Y-%m-%d'),
                            action="BUY",
                            price=round(price, 2),
                            quantity=shares_to_buy,
                            reason=reason,
                            sentiment_score_at_trade=sentiment_at_trade
                        ))
            
            elif should_sell and shares > 0:
                revenue = shares * price * (1 - commission)
                cash += revenue
                
                profit_pct = ((price - entry_price) / entry_price) * 100
                
                sentiment_at_trade = round(base_sentiment, 3) if include_news else None
                reason = f"{trade_reason_base}Short MA ({short_window}) crossed below Long MA ({long_window}). Trade P&L: {profit_pct:.2f}%"
                if include_news and strategy_type == 'news_enhanced_ma':
                    reason += f". Sentiment: {base_sentiment:.3f}"
                
                trades.append(TradeMetadata(
                    date=date.strftime('%Y-%m-%d'),
                    action="SELL",
                    price=round(price, 2),
                    quantity=shares,
                    reason=reason,
                    sentiment_score_at_trade=sentiment_at_trade
                ))
                shares = 0
            
            prev_short_above_long = short_above_long
            
            # Track equity curve
            total_value = cash + (shares * price)
            equity_curve.append({
                "date": date.strftime('%Y-%m-%d'),
                "value": round(total_value, 2)
            })
        
        # Close any remaining position
        if shares > 0:
            final_price = float(hist['Close'].iloc[-1])
            revenue = shares * final_price * (1 - commission)
            cash += revenue
            
            profit_pct = ((final_price - entry_price) / entry_price) * 100
            reason = f"{trade_reason_base}End of backtest period. Final P&L: {profit_pct:.2f}%"
            
            trades.append(TradeMetadata(
                date=hist.index[-1].strftime('%Y-%m-%d'),
                action="SELL",
                price=round(final_price, 2),
                quantity=shares,
                reason=reason,
                sentiment_score_at_trade=None
            ))
        
        # Calculate metrics
        final_value = cash
        total_return = final_value - initial_capital
        total_return_pct = (total_return / initial_capital) * 100
        
        # Sharpe ratio calculation
        if len(equity_curve) > 1:
            returns = pd.Series([e['value'] for e in equity_curve]).pct_change().dropna()
            sharpe = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() != 0 else 0
        else:
            sharpe = 0
        
        # Max drawdown calculation
        values = [e['value'] for e in equity_curve]
        peak = values[0]
        max_dd = 0
        for val in values:
            if val > peak:
                peak = val
            dd = (peak - val) / peak
            if dd > max_dd:
                max_dd = dd
        
        # News sentiment summary and AI reasoning
        news_summary = None
        ai_reasoning_text = None
        
        if include_news:
            avg_sentiment = base_sentiment
            news_count = random.randint(15, 45)
            
            if avg_sentiment > 0.2:
                dominant_theme = "Positive earnings and market expansion"
                impact = "Bullish sentiment supported long positions"
            elif avg_sentiment < -0.2:
                dominant_theme = "Regulatory concerns and market volatility"
                impact = "Bearish sentiment triggered early exits"
            else:
                dominant_theme = "Mixed market signals with sector rotation"
                impact = "Neutral sentiment, strategy relied on technical signals"
            
            news_summary = NewsSentimentSummary(
                avg_sentiment=round(avg_sentiment, 3),
                news_count=news_count,
                dominant_theme=dominant_theme,
                impact_assessment=impact
            )
            
            # Generate simple AI reasoning text (basic version)
            ai_reasoning_text = (
                f"The {strategy_type.replace('_', ' ').title()} strategy executed {len(trades)} trades over the backtest period. "
                f"Average news sentiment was {avg_sentiment:.3f}, which {'amplified' if abs(avg_sentiment) > 0.3 else 'moderately influenced'} trading signals. "
                f"The strategy achieved a total return of {total_return_pct:.2f}% with a maximum drawdown of {max_dd*100:.2f}%. "
                f"Key drivers: {dominant_theme.lower()}. {impact}."
            )
        
        # Prepare metrics for AI analysis engine
        metrics_for_ai = {
            "total_return": total_return / initial_capital,
            "buy_hold_return": ((float(hist['Close'].iloc[-1]) - float(hist['Close'].iloc[long_window])) / float(hist['Close'].iloc[long_window])),
            "sharpe_ratio": sharpe,
            "max_drawdown": max_dd,
            "win_rate": 0.6 if len(trades) > 0 else 0,  # Simplified for demo
            "num_trades": len(trades)
        }
        
        # Generate comprehensive AI analysis if enabled
        ai_analysis_result = None
        if include_news:
            try:
                # Simulate news data for AI engine (in production, use real news from news_processor)
                simulated_news = [
                    {"headline": f"Market update day {i}", "date": hist.index[i].strftime('%Y-%m-%d'), "sentiment_score": random.uniform(-0.3, 0.5)}
                    for i in range(long_window, min(long_window + 20, len(hist)))
                ]
                
                ai_result = ai_generate_analysis(
                    metrics=metrics_for_ai,
                    trades=[t.dict() if hasattr(t, 'dict') else t for t in trades],
                    news_data=simulated_news,
                    strategy_params={**params, "news_weight": news_weight},
                    cache_enabled=True
                )
                ai_analysis_result = ai_result.to_dict()
                
                # Use enhanced AI reasoning if available
                if ai_analysis_result and not ai_reasoning_text:
                    ai_reasoning_text = ai_analysis_result.get('performance_summary', ai_reasoning_text)
                    
            except Exception as e:
                print(f"AI analysis generation failed: {e}")
                # Continue with basic reasoning if AI fails
        
        return {
            "symbol": symbol.upper(),
            "strategy_type": strategy_type,
            "total_return": round(total_return, 2),
            "total_return_percent": round(total_return_pct, 2),
            "sharpe_ratio": round(sharpe, 3),
            "max_drawdown": round(max_dd, 4),
            "trade_count": len(trades),
            "equity_curve": equity_curve,
            "trades": trades,
            "news_sentiment_summary": news_summary,
            "ai_reasoning_text": ai_reasoning_text,
            "ai_analysis": ai_analysis_result  # Full structured AI analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


# --- API Endpoints ---

@app.get("/api/stocks/search", response_model=StockSearchResponse)
async def search_stocks(q: str = Query(..., min_length=1, description="Search query")):
    """Search for stocks by ticker symbol or company name."""
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    results = search_stocks_yfinance(q)
    
    if not results:
        return StockSearchResponse(results=[])
    
    return StockSearchResponse(results=[StockSearchResult(**r) for r in results])


@app.get("/api/stocks/{ticker}/overview", response_model=StockOverviewResponse)
async def get_stock_overview(ticker: str):
    """Get comprehensive stock overview including current price, 1Y chart, and stats."""
    ticker_upper = ticker.upper()
    
    # Check cache
    if is_cache_valid(ticker_upper):
        return overview_cache[ticker_upper][0]
    
    # Fetch fresh data
    data = get_stock_overview_data(ticker_upper)
    response = StockOverviewResponse(**data)
    
    # Cache the result
    overview_cache[ticker_upper] = (response, datetime.now())
    
    return response


@app.get("/api/strategies", response_model=StrategiesResponse)
async def list_strategies():
    """Return available strategies with their parameter schemas for frontend UI."""
    strategies = get_available_strategies()
    return StrategiesResponse(strategies=strategies)


@app.post("/api/backtest", response_model=BacktestResponse)
async def run_backtest_endpoint(request: BacktestRequest):
    """Run a backtest with specified strategy and parameters."""
    # Validate strategy type
    valid_strategies = [s.id for s in get_available_strategies()]
    if request.strategy_type not in valid_strategies:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid strategy type. Choose from: {', '.join(valid_strategies)}"
        )
    
    # Validate parameters
    if request.initial_capital <= 0:
        raise HTTPException(status_code=400, detail="Initial capital must be positive")
    if request.commission < 0 or request.commission > 0.1:
        raise HTTPException(status_code=400, detail="Commission must be between 0 and 0.1")
    
    # Run backtest
    result = run_backtest_logic(
        symbol=request.symbol,
        strategy_type=request.strategy_type,
        params=request.params,
        initial_capital=request.initial_capital,
        commission=request.commission,
        include_news=request.include_news_analysis
    )
    
    return BacktestResponse(**result)


# Legacy endpoint for backward compatibility
@app.post("/backtest")
def backtest_legacy(request: BacktestRequestLegacy):
    """Legacy backtest endpoint (backward compatibility)."""
    data = load_data(request.symbol)
    data["SMA_20"] = sma(data, request.short_window)
    data["SMA_50"] = sma(data, request.long_window)
    data["EMA_20"] = ema(data, 20)
    data["RSI_14"] = rsi(data)
    data["MACD"], data["MACD_Signal"], data["MACD_Hist"] = macd(data)
    data["BB_Upper"], data["BB_Middle"], data["BB_Lower"] = bollinger_bands(data)
    data["Signal"] = generate_signals(data)

    engine = BacktestEngine(
        initial_capital=request.initial_capital,
        commission=request.commission,
        slippage=request.slippage,
        position_size=request.position_size
    )

    portfolio_values = []
    for i in range(len(data) - 1):
        next_date = data.index[i + 1]
        signal = data["Signal"].iloc[i]
        next_open = data["Open"].iloc[i + 1]
        if signal == 1:
            engine.buy(next_date, next_open)
        elif signal == -1:
            engine.sell(next_date, next_open)
        value = engine.portfolio_value(next_open)
        portfolio_values.append(value)

    final_price = data["Close"].iloc[-1]
    final_value = engine.portfolio_value(final_price)
    
    total_return = ((final_value - request.initial_capital) / request.initial_capital) * 100
    
    buy_hold_shares = int(request.initial_capital // data["Open"].iloc[0])
    buy_hold_cash = request.initial_capital - buy_hold_shares * data["Open"].iloc[0]
    buy_hold_value = buy_hold_cash + buy_hold_shares * data["Close"].iloc[-1]
    buy_hold_return = ((buy_hold_value - request.initial_capital) / request.initial_capital) * 100

    return {
        "symbol": request.symbol,
        "initial_capital": request.initial_capital,
        "final_value": final_value,
        "total_return": total_return,
        "Buy and hold": buy_hold_value,
        "B&H return": buy_hold_return
    }


@app.get("/")
def root():

    return {
        "message": "Trading Strategy Backtester API is running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)