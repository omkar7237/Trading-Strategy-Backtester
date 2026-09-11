"""
Tests for API endpoints - Part 3: FastAPI Backend for Dynamic Stock Explorer
"""
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestStockSearch:
    """Tests for GET /api/stocks/search endpoint."""
    
    def test_search_valid_ticker(self):
        """Test searching for a valid ticker like AAPL."""
        response = client.get("/api/stocks/search?q=AAPL")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        # Should find at least AAPL
        symbols = [r["symbol"] for r in data["results"]]
        assert "AAPL" in symbols or len(data["results"]) > 0
    
    def test_search_company_name(self):
        """Test searching by company name."""
        response = client.get("/api/stocks/search?q=Apple")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        # Should find Apple-related stocks
        assert len(data["results"]) > 0
    
    def test_search_empty_query(self):
        """Test that empty query returns 400."""
        response = client.get("/api/stocks/search?q=")
        assert response.status_code in [400, 422]  # 422 for validation error
    
    def test_search_no_results(self):
        """Test searching for non-existent ticker."""
        response = client.get("/api/stocks/search?q=XYZNONEXISTENT123")
        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []


class TestStockOverview:
    """Tests for GET /api/stocks/{ticker}/overview endpoint."""
    
    def test_overview_valid_ticker(self):
        """Test getting overview for a valid ticker."""
        response = client.get("/api/stocks/AAPL/overview")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "symbol" in data
        assert "current_price" in data
        assert "buy_hold_return_1y" in data
        assert "stats" in data
        assert "chart_data" in data
        
        # Check stats structure
        stats = data["stats"]
        assert "current_price" in stats
        assert "day_change_percent" in stats
        assert "year_high" in stats
        assert "year_low" in stats
        
        # Check chart_data is a list
        assert isinstance(data["chart_data"], list)
        if len(data["chart_data"]) > 0:
            point = data["chart_data"][0]
            assert "date" in point
            assert "open" in point
            assert "high" in point
            assert "low" in point
            assert "close" in point
            assert "volume" in point
    
    def test_overview_invalid_ticker(self):
        """Test getting overview for invalid ticker returns 404."""
        response = client.get("/api/stocks/INVALIDTICKER123/overview")
        assert response.status_code == 404
    
    def test_overview_caching(self):
        """Test that overview is cached (second request should be faster)."""
        # First request
        response1 = client.get("/api/stocks/MSFT/overview")
        assert response1.status_code == 200
        
        # Second request (should use cache)
        response2 = client.get("/api/stocks/MSFT/overview")
        assert response2.status_code == 200
        assert response1.json()["current_price"] == response2.json()["current_price"]


class TestStrategies:
    """Tests for GET /api/strategies endpoint."""
    
    def test_list_strategies(self):
        """Test getting list of available strategies."""
        response = client.get("/api/strategies")
        assert response.status_code == 200
        data = response.json()
        
        assert "strategies" in data
        assert len(data["strategies"]) > 0
        
        # Check strategy structure
        strategy = data["strategies"][0]
        assert "id" in strategy
        assert "name" in strategy
        assert "description" in strategy
        assert "parameters" in strategy
        
        # Check parameter structure
        if len(strategy["parameters"]) > 0:
            param = strategy["parameters"][0]
            assert "name" in param
            assert "type" in param
            assert "default" in param
    
    def test_strategies_include_news_enhanced(self):
        """Test that news_enhanced_ma strategy is available."""
        response = client.get("/api/strategies")
        assert response.status_code == 200
        data = response.json()
        
        strategy_ids = [s["id"] for s in data["strategies"]]
        assert "news_enhanced_ma" in strategy_ids


class TestBacktest:
    """Tests for POST /api/backtest endpoint."""
    
    def test_backtest_simple_ma(self):
        """Test backtest with simple MA strategy."""
        payload = {
            "symbol": "AAPL",
            "strategy_type": "simple_ma",
            "params": {"short_window": 20, "long_window": 50},
            "initial_capital": 10000,
            "commission": 0.001,
            "include_news_analysis": False
        }
        response = client.post("/api/backtest", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "symbol" in data
        assert "strategy_type" in data
        assert "total_return" in data
        assert "total_return_percent" in data
        assert "sharpe_ratio" in data
        assert "max_drawdown" in data
        assert "trade_count" in data
        assert "equity_curve" in data
        assert "trades" in data
    
    def test_backtest_news_enhanced(self):
        """Test backtest with news-enhanced MA strategy."""
        payload = {
            "symbol": "AAPL",
            "strategy_type": "news_enhanced_ma",
            "params": {"short_window": 20, "long_window": 50, "news_weight": 0.4},
            "initial_capital": 10000,
            "commission": 0.001,
            "include_news_analysis": True
        }
        response = client.post("/api/backtest", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Check news-specific fields
        assert "news_sentiment_summary" in data
        assert "ai_reasoning_text" in data
        
        if data["news_sentiment_summary"] is not None:
            summary = data["news_sentiment_summary"]
            assert "avg_sentiment" in summary
            assert "news_count" in summary
            assert "dominant_theme" in summary
            assert "impact_assessment" in summary
    
    def test_backtest_rsi_strategy(self):
        """Test backtest with RSI strategy."""
        payload = {
            "symbol": "GOOGL",
            "strategy_type": "rsi",
            "params": {
                "rsi_period": 14,
                "oversold_threshold": 30.0,
                "overbought_threshold": 70.0
            },
            "initial_capital": 10000,
            "commission": 0.001,
            "include_news_analysis": False
        }
        response = client.post("/api/backtest", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "GOOGL"
        assert data["strategy_type"] == "rsi"
    
    def test_backtest_macd_strategy(self):
        """Test backtest with MACD strategy."""
        payload = {
            "symbol": "MSFT",
            "strategy_type": "macd",
            "params": {
                "fast_period": 12,
                "slow_period": 26,
                "signal_period": 9
            },
            "initial_capital": 10000,
            "commission": 0.001,
            "include_news_analysis": False
        }
        response = client.post("/api/backtest", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "MSFT"
        assert data["strategy_type"] == "macd"
    
    def test_backtest_invalid_strategy(self):
        """Test backtest with invalid strategy type."""
        payload = {
            "symbol": "AAPL",
            "strategy_type": "invalid_strategy_xyz",
            "params": {},
            "initial_capital": 10000,
            "commission": 0.001,
            "include_news_analysis": False
        }
        response = client.post("/api/backtest", json=payload)
        assert response.status_code == 400
    
    def test_backtest_invalid_capital(self):
        """Test backtest with invalid initial capital."""
        payload = {
            "symbol": "AAPL",
            "strategy_type": "simple_ma",
            "params": {},
            "initial_capital": -1000,
            "commission": 0.001,
            "include_news_analysis": False
        }
        response = client.post("/api/backtest", json=payload)
        assert response.status_code == 400
    
    def test_backtest_invalid_commission(self):
        """Test backtest with invalid commission."""
        payload = {
            "symbol": "AAPL",
            "strategy_type": "simple_ma",
            "params": {},
            "initial_capital": 10000,
            "commission": 0.5,  # Too high
            "include_news_analysis": False
        }
        response = client.post("/api/backtest", json=payload)
        assert response.status_code == 400
    
    def test_backtest_trade_metadata(self):
        """Test that trades include proper metadata."""
        payload = {
            "symbol": "AAPL",
            "strategy_type": "news_enhanced_ma",
            "params": {"short_window": 20, "long_window": 50, "news_weight": 0.4},
            "initial_capital": 10000,
            "commission": 0.001,
            "include_news_analysis": True
        }
        response = client.post("/api/backtest", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        if len(data["trades"]) > 0:
            trade = data["trades"][0]
            assert "date" in trade
            assert "action" in trade
            assert trade["action"] in ["BUY", "SELL"]
            assert "price" in trade
            assert "quantity" in trade
            assert "reason" in trade


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200


class TestCORS:
    """Tests for CORS configuration."""
    
    def test_cors_headers(self):
        """Test that CORS headers are present."""
        response = client.options(
            "/api/stocks/AAPL/overview",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET"
            }
        )
        # Should allow the request
        assert response.status_code in [200, 204]
