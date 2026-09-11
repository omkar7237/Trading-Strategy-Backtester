"""
Tests for news integration module.
Covers news download robustness, sentiment alignment, and edge cases.
"""

import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestNewsDownloader:
    """Tests for NewsDownloader class."""
    
    def test_news_downloader_initialization(self):
        """Test that NewsDownloader initializes correctly."""
        from data.downloader import NewsDownloader
        
        # Test without API key (should use GDELT fallback)
        downloader = NewsDownloader()
        assert downloader.news_dir == Path("data/raw/news")
        assert downloader.api_key is None
        
        # Test with API key
        downloader_with_key = NewsDownloader(api_key="test_key")
        assert downloader_with_key.api_key == "test_key"
    
    def test_news_downloader_creates_directory(self):
        """Test that news directory is created on initialization."""
        from data.downloader import NewsDownloader
        
        downloader = NewsDownloader()
        assert downloader.news_dir.exists()
        assert downloader.news_dir.is_dir()
    
    def test_parse_articles_empty_list(self):
        """Test parsing empty article list."""
        from data.downloader import NewsDownloader
        
        downloader = NewsDownloader()
        df = downloader.parse_articles([], "AAPL")
        
        assert df.empty
        assert list(df.columns) == ["date", "headline", "summary", "source", "sentiment_score"]
    
    def test_parse_articles_valid_data(self):
        """Test parsing valid article data."""
        from data.downloader import NewsDownloader
        
        downloader = NewsDownloader()
        
        articles = [
            {
                "title": "Apple Reports Record Earnings",
                "description": "Apple Inc. announced record quarterly earnings.",
                "publishedAt": "2024-01-15T10:00:00Z",
                "source": {"name": "Financial Times"}
            },
            {
                "title": "Tech Sector Outlook Positive",
                "description": "Analysts bullish on tech stocks.",
                "publishedAt": "2024-01-16T14:30:00Z",
                "source": {"name": "Bloomberg"}
            }
        ]
        
        df = downloader.parse_articles(articles, "AAPL")
        
        assert len(df) == 2
        assert "Apple" in df.iloc[0]["headline"]
        assert "Financial Times" in df.iloc[0]["source"]
        assert df.iloc[0]["sentiment_score"] == 0.0  # Placeholder
    
    def test_parse_articles_deduplication(self):
        """Test that duplicate headlines are removed."""
        from data.downloader import NewsDownloader
        
        downloader = NewsDownloader()
        
        articles = [
            {
                "title": "Duplicate Headline",
                "description": "First occurrence",
                "publishedAt": "2024-01-15T10:00:00Z",
                "source": {"name": "Source A"}
            },
            {
                "title": "Duplicate Headline",
                "description": "Second occurrence",
                "publishedAt": "2024-01-15T12:00:00Z",
                "source": {"name": "Source B"}
            }
        ]
        
        df = downloader.parse_articles(articles, "AAPL")
        
        assert len(df) == 1
    
    def test_load_cached_news_nonexistent(self):
        """Test loading news that doesn't exist."""
        from data.downloader import NewsDownloader
        
        downloader = NewsDownloader()
        result = downloader.load_cached_news("NONEXISTENT_TICKER_XYZ")
        
        assert result is None
    
    def test_fetch_news_gdelt_no_api_key(self):
        """Test GDELT fallback when no API key."""
        from data.downloader import NewsDownloader
        
        downloader = NewsDownloader()
        # Should not raise, just print info message
        articles = downloader.fetch_news_gdelt("AAPL", days=7)
        
        assert isinstance(articles, list)


class TestNewsSentimentAnalyzer:
    """Tests for NewsSentimentAnalyzer class."""
    
    def test_analyzer_initialization_ollama(self):
        """Test analyzer initializes with Ollama."""
        from data.news_processor import NewsSentimentAnalyzer
        
        analyzer = NewsSentimentAnalyzer(provider="ollama")
        assert analyzer.provider == "ollama"
        assert analyzer.model == "llama2"
    
    def test_analyzer_initialization_openai(self):
        """Test analyzer initializes with OpenAI."""
        from data.news_processor import NewsSentimentAnalyzer
        
        analyzer = NewsSentimentAnalyzer(provider="openai", api_key="test_key")
        assert analyzer.provider == "openai"
        assert analyzer.model == "gpt-3.5-turbo"
    
    def test_analyzer_custom_model(self):
        """Test analyzer with custom model."""
        from data.news_processor import NewsSentimentAnalyzer
        
        analyzer = NewsSentimentAnalyzer(provider="ollama", model="mistral")
        assert analyzer.model == "mistral"


class TestSentimentAlignment:
    """Tests for sentiment alignment with OHLCV dates."""
    
    def test_merge_sentiment_with_ohlcv(self):
        """Test merging sentiment with OHLCV data."""
        from data.news_processor import merge_sentiment_with_ohlcv
        
        # Create sample OHLCV data
        dates = pd.date_range("2024-01-01", periods=10, freq="D")
        ohlcv = pd.DataFrame({
            "Open": range(100, 110),
            "Close": range(105, 115),
            "Volume": range(1000, 1010)
        }, index=dates)
        
        # Create sample news data
        news_dates = ["2024-01-02", "2024-01-05", "2024-01-08"]
        news = pd.DataFrame({
            "date": pd.to_datetime(news_dates),
            "headline": ["News 1", "News 2", "News 3"],
            "sentiment_score": [0.5, -0.3, 0.8]
        })
        
        # Merge with forward fill
        result = merge_sentiment_with_ohlcv(ohlcv, news, fill_method="ffill")
        
        assert "sentiment_score" in result.columns
        assert len(result) == 10
        
        # Check forward fill behavior
        # Day 1: no news -> 0.0
        # Day 2: news 0.5 -> 0.5
        # Day 3-4: ffill -> 0.5
        # Day 5: news -0.3 -> -0.3
        assert result.iloc[0]["sentiment_score"] == 0.0
        assert result.iloc[1]["sentiment_score"] == 0.5
        assert result.iloc[2]["sentiment_score"] == 0.5  # ffill
        assert result.iloc[4]["sentiment_score"] == -0.3
    
    def test_merge_sentiment_mean_fill(self):
        """Test merging with mean fill method."""
        from data.news_processor import merge_sentiment_with_ohlcv
        
        dates = pd.date_range("2024-01-01", periods=5, freq="D")
        ohlcv = pd.DataFrame({"Open": range(5)}, index=dates)
        
        news = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-03"]),
            "headline": ["News"],
            "sentiment_score": [0.6]
        })
        
        result = merge_sentiment_with_ohlcv(ohlcv, news, fill_method="mean")
        
        # All values should be 0.6 (the mean)
        assert all(result["sentiment_score"] == 0.6)
    
    def test_merge_sentiment_zero_fill(self):
        """Test merging with zero fill method."""
        from data.news_processor import merge_sentiment_with_ohlcv
        
        dates = pd.date_range("2024-01-01", periods=5, freq="D")
        ohlcv = pd.DataFrame({"Open": range(5)}, index=dates)
        
        news = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-03"]),
            "headline": ["News"],
            "sentiment_score": [0.6]
        })
        
        result = merge_sentiment_with_ohlcv(ohlcv, news, fill_method="zero")
        
        # Days without news should be 0
        assert result.iloc[0]["sentiment_score"] == 0.0
        assert result.iloc[2]["sentiment_score"] == 0.6  # Has news
    
    def test_merge_empty_news(self):
        """Test merging when news DataFrame is empty."""
        from data.news_processor import merge_sentiment_with_ohlcv
        
        dates = pd.date_range("2024-01-01", periods=5, freq="D")
        ohlcv = pd.DataFrame({"Open": range(5)}, index=dates)
        
        news = pd.DataFrame(columns=["date", "headline", "sentiment_score"])
        
        result = merge_sentiment_with_ohlcv(ohlcv, news)
        
        assert "sentiment_score" in result.columns
        assert all(result["sentiment_score"] == 0.0)
    
    def test_merge_empty_ohlcv(self):
        """Test merging when OHLCV DataFrame is empty."""
        from data.news_processor import merge_sentiment_with_ohlcv
        
        ohlcv = pd.DataFrame()
        news = pd.DataFrame({
            "date": pd.to_datetime(["2024-01-01"]),
            "headline": ["News"],
            "sentiment_score": [0.5]
        })
        
        result = merge_sentiment_with_ohlcv(ohlcv, news)
        
        assert result.empty


class TestLoadEnrichedData:
    """Tests for load_enriched_data function."""
    
    def test_load_enriched_data_no_news(self):
        """Test loading enriched data when no news exists."""
        from data.loader import load_enriched_data
        
        # Use a ticker that has OHLCV but no news
        df = load_enriched_data("AAPL")
        
        assert len(df) > 0
        assert "sentiment_score" in df.columns
        # Since no news exists, all sentiments should be 0
        assert all(df["sentiment_score"] == 0.0)
    
    def test_load_enriched_data_columns(self):
        """Test that enriched data has correct columns."""
        from data.loader import load_enriched_data
        
        df = load_enriched_data("AAPL")
        
        expected_cols = ["Open", "High", "Low", "Close", "Volume", "sentiment_score"]
        for col in expected_cols:
            assert col in df.columns


class TestNoNewsCoverage:
    """Tests for tickers with no news coverage."""
    
    def test_ticker_with_no_news(self):
        """Test handling of tickers with absolutely no news."""
        from data.downloader import NewsDownloader
        
        downloader = NewsDownloader()
        
        # Simulate no news scenario
        df = downloader.parse_articles([], "FAKETICKER")
        
        assert df.empty
        assert list(df.columns) == ["date", "headline", "summary", "source", "sentiment_score"]
    
    def test_sentiment_analysis_on_empty_news(self):
        """Test sentiment analysis returns empty DataFrame for no news."""
        from data.news_processor import analyze_news_sentiment
        from datetime import datetime
        
        # This will try to load cached news which doesn't exist
        # and then try to download (which will use GDELT fallback)
        result = analyze_news_sentiment(
            ticker="NONEXISTENT_XYZ",
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now(),
            use_cached=True
        )
        
        # Should return empty DataFrame or handle gracefully
        assert isinstance(result, pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
