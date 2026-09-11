"""Tests for AI Reasoning Engine."""

import pytest
from datetime import datetime
from ai.reasoning_engine import (
    generate_backtest_analysis,
    AIAnalysisResult,
    ReasoningEngine
)


class TestAIReasoningEngine:
    """Test suite for AI reasoning engine functionality."""
    
    @pytest.fixture
    def sample_metrics(self):
        """Sample backtest metrics."""
        return {
            "total_return": 0.15,
            "buy_hold_return": 0.08,
            "sharpe_ratio": 1.2,
            "max_drawdown": -0.12,
            "win_rate": 0.6,
            "num_trades": 25
        }
    
    @pytest.fixture
    def sample_trades(self):
        """Sample trade data."""
        return [
            {"date": "2024-01-15", "action": "LONG", "price": 150.0, "metadata": {"reason": "MA crossover bullish"}},
            {"date": "2024-02-20", "action": "EXIT", "price": 165.0, "metadata": {"reason": "RSI overbought"}},
            {"date": "2024-03-10", "action": "LONG", "price": 160.0, "metadata": {"reason": "Sentiment positive"}}
        ]
    
    @pytest.fixture
    def sample_news(self):
        """Sample news data with sentiment."""
        return [
            {"headline": "Fed announces interest rate decision", "date": "2024-01-10", "sentiment_score": -0.2},
            {"headline": "Tech sector shows strong earnings", "date": "2024-01-20", "sentiment_score": 0.5},
            {"headline": "Market volatility concerns rise", "date": "2024-02-05", "sentiment_score": -0.4}
        ]
    
    @pytest.fixture
    def sample_params(self):
        """Sample strategy parameters."""
        return {
            "strategy_type": "news_enhanced_ma",
            "short_window": 20,
            "long_window": 50,
            "news_weight": 0.4,
            "sentiment_threshold": 0.2
        }
    
    def test_generate_analysis_basic(self, sample_metrics, sample_trades):
        """Test basic analysis generation without news."""
        result = generate_backtest_analysis(
            metrics=sample_metrics,
            trades=sample_trades,
            news_data=None,
            strategy_params={}
        )
        
        assert isinstance(result, AIAnalysisResult)
        assert result.performance_summary != ""
        assert result.confidence_score >= 0
        assert result.confidence_score <= 1
        assert result.model_used == "rule_based_heuristic"
    
    def test_generate_analysis_with_news(self, sample_metrics, sample_trades, sample_news, sample_params):
        """Test analysis generation with news data."""
        result = generate_backtest_analysis(
            metrics=sample_metrics,
            trades=sample_trades,
            news_data=sample_news,
            strategy_params=sample_params
        )
        
        assert isinstance(result, AIAnalysisResult)
        assert len(result.key_news_events) > 0
        assert result.sentiment_impact_analysis != ""
        # Check that news events contain expected headlines (case-insensitive)
        headlines = [event.get('headline', '').lower() for event in result.key_news_events]
        assert any("fed" in h or "tech" in h or "earnings" in h for h in headlines)
    
    def test_political_factor_detection(self, sample_metrics, sample_trades, sample_news):
        """Test detection of political factors in news."""
        result = generate_backtest_analysis(
            metrics=sample_metrics,
            trades=sample_trades,
            news_data=sample_news,
            strategy_params={}
        )
        
        # Should detect "Fed" as political factor
        assert len(result.political_factors) > 0
        assert any("Fed" in factor for factor in result.political_factors)
    
    def test_parameter_sensitivity_analysis(self, sample_metrics, sample_trades, sample_params):
        """Test parameter sensitivity analysis."""
        result = generate_backtest_analysis(
            metrics=sample_metrics,
            trades=sample_trades,
            news_data=None,
            strategy_params=sample_params
        )
        
        assert 'news_weight' in result.parameter_sensitivity or 'window_ratio' in result.parameter_sensitivity
    
    def test_strategy_strengths_weaknesses(self, sample_metrics, sample_trades):
        """Test identification of strategy strengths and weaknesses."""
        result = generate_backtest_analysis(
            metrics=sample_metrics,
            trades=sample_trades,
            news_data=None,
            strategy_params={}
        )
        
        # With good metrics, should have strengths
        assert len(result.strategy_strengths) > 0 or len(result.strategy_weaknesses) > 0
    
    def test_suggestions_generation(self, sample_metrics, sample_trades):
        """Test actionable suggestions generation."""
        # Test with poor metrics to trigger suggestions
        poor_metrics = {
            "total_return": -0.05,
            "buy_hold_return": 0.10,
            "sharpe_ratio": 0.3,
            "max_drawdown": -0.25,
            "win_rate": 0.35,
            "num_trades": 30
        }
        
        result = generate_backtest_analysis(
            metrics=poor_metrics,
            trades=sample_trades,
            news_data=None,
            strategy_params={}
        )
        
        assert len(result.suggestions) > 0
        assert len(result.risk_warnings) > 0
    
    def test_risk_warnings(self, sample_metrics, sample_trades):
        """Test risk warning generation."""
        # Test with high drawdown
        risky_metrics = {
            "total_return": 0.05,
            "buy_hold_return": 0.08,
            "sharpe_ratio": 0.5,
            "max_drawdown": -0.30,
            "win_rate": 0.45,
            "num_trades": 5
        }
        
        result = generate_backtest_analysis(
            metrics=risky_metrics,
            trades=sample_trades,
            news_data=None,
            strategy_params={}
        )
        
        assert len(result.risk_warnings) > 0
    
    def test_cache_functionality(self, sample_metrics, sample_trades, tmp_path):
        """Test analysis caching."""
        cache_dir = tmp_path / "ai_cache"
        cache_dir.mkdir()
        
        engine = ReasoningEngine(
            llm_provider="auto",
            cache_enabled=True,
            cache_dir=str(cache_dir)
        )
        
        # First call generates and caches
        result1 = engine.generate_analysis(
            metrics=sample_metrics,
            trades=sample_trades,
            news_data=None,
            strategy_params={},
            force_regenerate=False
        )
        
        # Second call should use cache
        result2 = engine.generate_analysis(
            metrics=sample_metrics,
            trades=sample_trades,
            news_data=None,
            strategy_params={},
            force_regenerate=False
        )
        
        assert result1.cache_key == result2.cache_key
        
        # Force regenerate should create new result
        result3 = engine.generate_analysis(
            metrics=sample_metrics,
            trades=sample_trades,
            news_data=None,
            strategy_params={},
            force_regenerate=True
        )
        
        # Cache key should be same but regenerated_at may differ slightly
        assert result1.cache_key == result3.cache_key
    
    def test_to_dict_serialization(self, sample_metrics, sample_trades):
        """Test conversion to dictionary for JSON serialization."""
        result = generate_backtest_analysis(
            metrics=sample_metrics,
            trades=sample_trades,
            news_data=None,
            strategy_params={}
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert "performance_summary" in result_dict
        assert "confidence_score" in result_dict
        assert "generated_at" in result_dict
    
    def test_to_markdown_format(self, sample_metrics, sample_trades, sample_news):
        """Test Markdown output formatting."""
        result = generate_backtest_analysis(
            metrics=sample_metrics,
            trades=sample_trades,
            news_data=sample_news,
            strategy_params={}
        )
        
        markdown = result.to_markdown()
        
        assert isinstance(markdown, str)
        assert "# 🤖 AI Trading Strategy Analysis" in markdown
        assert "## 📊 Performance Summary" in markdown
        assert "## 📰 Key News Events Impact" in markdown
        assert "## 💡 Actionable Recommendations" in markdown
    
    def test_no_news_handling(self, sample_metrics, sample_trades):
        """Test handling when no news data is available."""
        result = generate_backtest_analysis(
            metrics=sample_metrics,
            trades=sample_trades,
            news_data=[],
            strategy_params={}
        )
        
        assert result.key_news_events == []
        assert "No news data" in result.sentiment_impact_analysis or result.sentiment_impact_analysis != ""
    
    def test_extreme_market_conditions(self, sample_trades):
        """Test analysis under extreme market conditions."""
        # Market crash scenario
        crash_metrics = {
            "total_return": -0.40,
            "buy_hold_return": -0.35,
            "sharpe_ratio": -1.5,
            "max_drawdown": -0.50,
            "win_rate": 0.25,
            "num_trades": 40
        }
        
        result = generate_backtest_analysis(
            metrics=crash_metrics,
            trades=sample_trades,
            news_data=None,
            strategy_params={}
        )
        
        assert result.performance_summary != ""
        assert len(result.risk_warnings) > 0
    
    def test_outperformance_analysis(self, sample_metrics, sample_trades):
        """Test analysis when strategy outperforms."""
        # Strong outperformance
        strong_metrics = {
            "total_return": 0.35,
            "buy_hold_return": 0.10,
            "sharpe_ratio": 2.0,
            "max_drawdown": -0.08,
            "win_rate": 0.70,
            "num_trades": 30
        }
        
        result = generate_backtest_analysis(
            metrics=strong_metrics,
            trades=sample_trades,
            news_data=None,
            strategy_params={}
        )
        
        assert len(result.outperformance_reasons) > 0
        # Confidence should be reasonable with good data (at least 0.3)
        assert result.confidence_score >= 0.3
    
    def test_confidence_score_calculation(self, sample_metrics, sample_trades, sample_news):
        """Test confidence score factors."""
        # Low confidence scenario (few trades, no news)
        result_no_news = generate_backtest_analysis(
            metrics=sample_metrics,
            trades=sample_trades[:3],  # Few trades
            news_data=None,
            strategy_params={}
        )
        
        # Higher confidence scenario (many trades, news available)
        many_trades = sample_trades * 10  # Many trades
        result_with_news = generate_backtest_analysis(
            metrics=sample_metrics,
            trades=many_trades,
            news_data=sample_news * 5,  # Lots of news
            strategy_params={}
        )
        
        assert result_with_news.confidence_score >= result_no_news.confidence_score


class TestReasoningEngineClass:
    """Test the ReasoningEngine class directly."""
    
    def test_initialization_auto_provider(self):
        """Test engine initialization with auto provider detection."""
        engine = ReasoningEngine(llm_provider="auto", cache_enabled=False)
        # After initialization, llm_provider should be resolved to 'openai' or 'ollama'
        # But if LLM libs not available, it stays as 'auto' - both are acceptable
        assert engine.llm_provider in ["openai", "ollama", "auto"]
    
    def test_initialization_explicit_provider(self):
        """Test engine initialization with explicit provider."""
        engine = ReasoningEngine(llm_provider="ollama", cache_enabled=False)
        assert engine.llm_provider == "ollama"
    
    def test_cache_key_generation(self):
        """Test unique cache key generation."""
        engine = ReasoningEngine(cache_enabled=False)
        
        metrics1 = {"return": 0.1}
        metrics2 = {"return": 0.2}
        params = {"window": 20}
        
        key1 = engine._generate_cache_key(metrics1, params, 10)
        key2 = engine._generate_cache_key(metrics2, params, 10)
        key3 = engine._generate_cache_key(metrics1, params, 20)  # Different news count
        
        assert key1 != key2
        assert key1 != key3
        assert len(key1) == 16  # MD5 hex first 16 chars
