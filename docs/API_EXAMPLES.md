# Trading Strategy Backtester API - HTTP Examples

## Base URL
```
http://localhost:8000
```

## Interactive Documentation
Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 1. Stock Search Endpoint

### Search by Ticker
```bash
curl -X GET "http://localhost:8000/api/stocks/search?q=AAPL"
```

**HTTPie:**
```bash
http GET :8000/api/stocks/search q==AAPL
```

**Expected Response:**
```json
{
  "results": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "exchange": "NASDAQ"
    }
  ]
}
```

### Search by Company Name
```bash
curl -X GET "http://localhost:8000/api/stocks/search?q=Microsoft"
```

---

## 2. Stock Overview Endpoint

### Get Stock Overview with 1Y Chart Data
```bash
curl -X GET "http://localhost:8000/api/stocks/AAPL/overview"
```

**HTTPie:**
```bash
http GET :8000/api/stocks/AAPL/overview
```

**Expected Response:**
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "current_price": 178.52,
  "buy_hold_return_1y": 12.45,
  "stats": {
    "current_price": 178.52,
    "day_change_percent": 1.23,
    "year_high": 199.62,
    "year_low": 143.90,
    "market_cap": 2800000000000,
    "pe_ratio": 28.5
  },
  "chart_data": [
    {
      "date": "2023-11-01",
      "open": 171.00,
      "high": 173.00,
      "low": 170.50,
      "close": 172.50,
      "volume": 50000000
    }
    // ... more data points
  ]
}
```

---

## 3. Strategies Endpoint

### List Available Strategies
```bash
curl -X GET "http://localhost:8000/api/strategies"
```

**HTTPie:**
```bash
http GET :8000/api/strategies
```

**Expected Response:**
```json
{
  "strategies": [
    {
      "id": "simple_ma",
      "name": "Simple Moving Average Crossover",
      "description": "Buy when short MA crosses above long MA, sell on reverse.",
      "parameters": [
        {
          "name": "short_window",
          "type": "int",
          "default": 20,
          "min_val": 5,
          "max_val": 50,
          "step": 1
        },
        {
          "name": "long_window",
          "type": "int",
          "default": 50,
          "min_val": 20,
          "max_val": 200,
          "step": 1
        }
      ]
    },
    {
      "id": "news_enhanced_ma",
      "name": "News-Enhanced MA Crossover",
      "description": "MA crossover strategy weighted by news sentiment analysis.",
      "parameters": [
        {
          "name": "short_window",
          "type": "int",
          "default": 20,
          "min_val": 5,
          "max_val": 50,
          "step": 1
        },
        {
          "name": "long_window",
          "type": "int",
          "default": 50,
          "min_val": 20,
          "max_val": 200,
          "step": 1
        },
        {
          "name": "news_weight",
          "type": "float",
          "default": 0.4,
          "min_val": 0.0,
          "max_val": 1.0,
          "step": 0.1
        }
      ]
    },
    {
      "id": "rsi",
      "name": "RSI Mean Reversion",
      "description": "Buy when RSI is oversold, sell when overbought.",
      "parameters": [
        {
          "name": "rsi_period",
          "type": "int",
          "default": 14,
          "min_val": 7,
          "max_val": 28,
          "step": 1
        },
        {
          "name": "oversold_threshold",
          "type": "float",
          "default": 30.0,
          "min_val": 20.0,
          "max_val": 40.0,
          "step": 1.0
        },
        {
          "name": "overbought_threshold",
          "type": "float",
          "default": 70.0,
          "min_val": 60.0,
          "max_val": 80.0,
          "step": 1.0
        }
      ]
    },
    {
      "id": "macd",
      "name": "MACD Momentum",
      "description": "Trade based on MACD line crossing signal line.",
      "parameters": [
        {
          "name": "fast_period",
          "type": "int",
          "default": 12,
          "min_val": 5,
          "max_val": 20,
          "step": 1
        },
        {
          "name": "slow_period",
          "type": "int",
          "default": 26,
          "min_val": 15,
          "max_val": 50,
          "step": 1
        },
        {
          "name": "signal_period",
          "type": "int",
          "default": 9,
          "min_val": 5,
          "max_val": 15,
          "step": 1
        }
      ]
    }
  ]
}
```

---

## 4. Backtest Endpoint

### Simple MA Strategy Backtest
```bash
curl -X POST "http://localhost:8000/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "strategy_type": "simple_ma",
    "params": {"short_window": 20, "long_window": 50},
    "initial_capital": 10000,
    "commission": 0.001,
    "include_news_analysis": false
  }'
```

**HTTPie:**
```bash
http POST :8000/api/backtest \
  symbol=AAPL \
  strategy_type=simple_ma \
  params:='{"short_window": 20, "long_window": 50}' \
  initial_capital=10000 \
  commission=0.001 \
  include_news_analysis:=false
```

### News-Enhanced MA Strategy Backtest
```bash
curl -X POST "http://localhost:8000/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "strategy_type": "news_enhanced_ma",
    "params": {"short_window": 20, "long_window": 50, "news_weight": 0.4},
    "initial_capital": 10000,
    "commission": 0.001,
    "include_news_analysis": true
  }'
```

**HTTPie:**
```bash
http POST :8000/api/backtest \
  symbol=AAPL \
  strategy_type=news_enhanced_ma \
  params:='{"short_window": 20, "long_window": 50, "news_weight": 0.4}' \
  initial_capital=10000 \
  commission=0.001 \
  include_news_analysis:=true
```

**Expected Response:**
```json
{
  "symbol": "AAPL",
  "strategy_type": "news_enhanced_ma",
  "total_return": 1250.50,
  "total_return_percent": 12.51,
  "sharpe_ratio": 1.45,
  "max_drawdown": 0.0823,
  "trade_count": 8,
  "equity_curve": [
    {"date": "2023-11-01", "value": 10000.00},
    {"date": "2023-11-02", "value": 10150.25}
    // ... more data points
  ],
  "trades": [
    {
      "date": "2023-11-15",
      "action": "BUY",
      "price": 175.25,
      "quantity": 54,
      "reason": "News-Enhanced Ma Crossover strategy: Short MA (20) crossed above Long MA (50). Sentiment boost: 0.120",
      "sentiment_score_at_trade": 0.312
    },
    {
      "date": "2023-12-01",
      "action": "SELL",
      "price": 182.50,
      "quantity": 54,
      "reason": "News-Enhanced Ma Crossover strategy: Short MA (20) crossed below Long MA (50). Trade P&L: 4.14%. Sentiment: 0.312",
      "sentiment_score_at_trade": 0.312
    }
  ],
  "news_sentiment_summary": {
    "avg_sentiment": 0.312,
    "news_count": 28,
    "dominant_theme": "Positive earnings and market expansion",
    "impact_assessment": "Bullish sentiment supported long positions"
  },
  "ai_reasoning_text": "The News-Enhanced Ma Crossover strategy executed 8 trades over the backtest period. Average news sentiment was 0.312, which amplified trading signals. The strategy achieved a total return of 12.51% with a maximum drawdown of 8.23%. Key drivers: positive earnings and market expansion. Bullish sentiment supported long positions."
}
```

### RSI Strategy Backtest
```bash
curl -X POST "http://localhost:8000/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "GOOGL",
    "strategy_type": "rsi",
    "params": {"rsi_period": 14, "oversold_threshold": 30.0, "overbought_threshold": 70.0},
    "initial_capital": 10000,
    "commission": 0.001,
    "include_news_analysis": false
  }'
```

### MACD Strategy Backtest
```bash
curl -X POST "http://localhost:8000/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "MSFT",
    "strategy_type": "macd",
    "params": {"fast_period": 12, "slow_period": 26, "signal_period": 9},
    "initial_capital": 10000,
    "commission": 0.001,
    "include_news_analysis": false
  }'
```

---

## 5. Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

---

## Error Handling

### Invalid Strategy Type
```bash
curl -X POST "http://localhost:8000/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "strategy_type": "invalid_strategy",
    "params": {},
    "initial_capital": 10000,
    "commission": 0.001,
    "include_news_analysis": false
  }'
```

**Response (400 Bad Request):**
```json
{
  "detail": "Invalid strategy type. Choose from: simple_ma, news_enhanced_ma, rsi, macd"
}
```

### Invalid Ticker
```bash
curl -X GET "http://localhost:8000/api/stocks/INVALID123/overview"
```

**Response (404 Not Found):**
```json
{
  "detail": "Failed to fetch data for INVALID123: No data found"
}
```

---

## Running the Server

```bash
cd /workspace
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Or with Python:
```bash
python -m api.main
```

---

## Testing

Run all API tests:
```bash
pytest tests/test_api_endpoints.py -v
```

Run specific test class:
```bash
pytest tests/test_api_endpoints.py::TestBacktest -v
```
