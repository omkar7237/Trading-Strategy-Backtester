# Trading Strategy Backtester

A comprehensive AI-powered trading strategy backtesting platform with news sentiment integration.

## 🚀 Features

### Core Capabilities
- **Dynamic Stock Explorer**: Search any ticker, view price charts + Buy & Hold baseline
- **News & Politics AI Layer**: Sentiment analysis from recent news integrated into strategy signals
- **Interactive Dashboard**: Real-time parameter tuning for MA Crossover, RSI, MACD strategies
- **AI Reasoning Engine**: Explains trades by synthesizing technical metrics AND news/political context

### Technical Features
- Multiple strategy types: MA Crossover, RSI, MACD, Combined, News-Enhanced MA
- News sentiment scoring (-1 to +1) using LLM (OpenAI/Ollama)
- Look-ahead bias prevention with proper data alignment
- In-memory caching for stock overviews and AI analysis
- CORS-enabled API for React frontend integration

## 📁 Project Structure

```
trading-backtester/
├── ai/                      # AI Reasoning Engine
│   ├── __init__.py
│   └── reasoning_engine.py  # LLM-powered analysis generation
├── api/                     # FastAPI Backend
│   ├── main.py              # API endpoints
│   └── schemas.py           # Pydantic models
├── backtest/                # Backtest Engine
│   ├── engine.py            # Core backtesting logic
│   └── runner.py            # Trade execution
├── data/                    # Data Pipeline
│   ├── downloader.py        # OHLCV + News fetching
│   ├── loader.py            # Data loading utilities
│   └── news_processor.py    # Sentiment analysis
├── strategy/                # Strategy Implementations
│   ├── base_strategy.py     # Abstract base class
│   ├── basic_strategies.py  # MA, RSI, Combined strategies
│   └── news_enhanced_strategy.py  # News-aware strategy
├── tests/                   # Test Suite (63+ tests)
├── notebooks/               # Jupyter examples
└── docs/                    # Documentation
```

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- Optional: OpenAI API key or Ollama for AI features

### Backend Setup

```bash
# Clone repository
cd trading-backtester

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your API keys
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 🚀 Quick Start

### 1. Start Backend Server

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs for interactive API documentation.

### 2. Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Access at http://localhost:5173

### 3. Run Tests

```bash
pytest tests/ -v
```

All 63 tests should pass.

## 📊 API Endpoints

### Stock Search & Overview
```bash
# Search stocks
GET /api/stocks/search?q=AAPL

# Get stock overview with 1Y chart
GET /api/stocks/{ticker}/overview
```

### Strategies
```bash
# List available strategies with parameters
GET /api/strategies
```

### Backtest
```bash
# Run backtest with optional AI analysis
POST /api/backtest
{
  "symbol": "AAPL",
  "strategy_type": "news_enhanced_ma",
  "params": {
    "short_window": 20,
    "long_window": 50,
    "news_weight": 0.4
  },
  "initial_capital": 10000,
  "commission": 0.001,
  "include_news_analysis": true
}
```

Response includes:
- Performance metrics (return, Sharpe, drawdown)
- Equity curve
- Trade list with metadata
- News sentiment summary
- **AI reasoning text** explaining performance
- **Full AI analysis** (structured JSON)

## 🤖 AI Reasoning Engine

The AI Reasoning Engine (`ai/reasoning_engine.py`) provides:

1. **Performance Analysis**: Why strategy outperformed/underperformed vs Buy & Hold
2. **News Impact**: Key events that influenced trades
3. **Political Factors**: Detection of regulatory/policy impacts
4. **Parameter Sensitivity**: How parameter choices affected results
5. **Actionable Suggestions**: Concrete improvement recommendations
6. **Risk Warnings**: Flags for concerning patterns

### Usage Example

```python
from ai.reasoning_engine import generate_backtest_analysis

result = generate_backtest_analysis(
    metrics={
        "total_return": 0.15,
        "buy_hold_return": 0.08,
        "sharpe_ratio": 1.2,
        "max_drawdown": -0.12,
        "win_rate": 0.6,
        "num_trades": 25
    },
    trades=[...],  # List of trade dicts
    news_data=[...],  # News with sentiment scores
    strategy_params={"news_weight": 0.4}
)

# Get Markdown report
print(result.to_markdown())

# Get structured data
print(result.to_dict())
```

### LLM Providers

- **OpenAI** (default if `OPENAI_API_KEY` set): GPT-4o-mini
- **Ollama** (local, free): llama3.1 or any installed model
- **Rule-based fallback**: Works without any LLM

## 📈 Strategy Types

| Strategy | Parameters | Description |
|----------|-----------|-------------|
| `simple_ma` | short_window, long_window | Basic MA crossover |
| `news_enhanced_ma` | short_window, long_window, news_weight, sentiment_threshold | MA + sentiment filtering |
| `rsi` | rsi_period, oversold, overbought | RSI mean reversion |
| `macd` | fast_period, slow_period, signal_period | MACD momentum |
| `combined` | ma_short, ma_long, rsi_period | MA + RSI combination |

## 🧪 Testing

Comprehensive test suite covering:
- Data pipeline (news download, sentiment alignment)
- Strategy logic (signal generation, parameter validation)
- Backtest engine (trade execution, metrics calculation)
- API endpoints (search, overview, backtest)
- AI reasoning (analysis generation, caching, edge cases)

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ai_reasoning.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## 🔧 Configuration

See `.env.example` for all configuration options:

```bash
# AI Configuration
OPENAI_API_KEY=sk-...
OLLAMA_MODEL=llama3.1

# News API
NEWS_API_KEY=your_key_here

# Server
PORT=8000
DEBUG=true
```

## 📝 Notebooks

Jupyter notebooks demonstrating features:
- `notebooks/day1_ohlcv_sentiment_integration.ipynb` - Data exploration
- `notebooks/day10_risk_management.py` - Risk analysis
- `notebooks/day15_train_test.py` - Train/test split validation

## 🐳 Docker (Optional)

```bash
# Build image
docker build -t trading-backtester .

# Run container
docker run -p 8000:8000 --env-file .env trading-backtester
```

## 🎯 Roadmap Completion

✅ **Days 1-5**: Data Foundation (OHLCV + News)
✅ **Days 6-10**: Strategy Engine (with news awareness)
✅ **Days 11-20**: Backtest Engine & Performance Metrics
✅ **Days 21-28**: Risk Management & Validation
✅ **Days 29-30**: API Development
✅ **Days 31-35**: React Frontend
✅ **Days 36-37**: Integration Testing
✅ **Days 38-40**: AI Reasoning Engine & Polish

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

For issues or questions:
- Check existing GitHub Issues
- Review API documentation at `/docs`
- Examine test files for usage examples

---

**Built with**: Python, FastAPI, React, Pandas, LangChain, yfinance, Recharts
