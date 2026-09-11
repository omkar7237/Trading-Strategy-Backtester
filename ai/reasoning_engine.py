"""
AI Reasoning Engine for Trading Strategy Analysis.

This module synthesizes backtest metrics, trade data, and news sentiment
to generate comprehensive AI-powered analysis reports.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import hashlib

# Try to import optional LLM dependencies
try:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_openai import ChatOpenAI
    from langchain_ollama import ChatOllama
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


@dataclass
class AIAnalysisResult:
    """Structured output from AI reasoning engine."""
    
    # Performance Analysis
    performance_summary: str
    outperformance_reasons: List[str]
    underperformance_reasons: List[str]
    
    # News & Sentiment Analysis
    key_news_events: List[Dict[str, Any]]
    sentiment_impact_analysis: str
    political_factors: List[str]
    
    # Strategy Insights
    parameter_sensitivity: Dict[str, Any]
    strategy_strengths: List[str]
    strategy_weaknesses: List[str]
    
    # Actionable Recommendations
    suggestions: List[str]
    risk_warnings: List[str]
    
    # Metadata
    confidence_score: float  # 0.0 to 1.0
    model_used: str
    generated_at: str
    cache_key: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_markdown(self) -> str:
        """Convert analysis to Markdown format for display."""
        md = []
        md.append("# 🤖 AI Trading Strategy Analysis\n")
        md.append(f"*Generated: {self.generated_at} | Confidence: {self.confidence_score:.0%}*\n")
        
        md.append("\n## 📊 Performance Summary\n")
        md.append(self.performance_summary)
        
        if self.outperformance_reasons:
            md.append("\n### ✅ Why We Outperformed Buy & Hold\n")
            for reason in self.outperformance_reasons:
                md.append(f"- {reason}")
        
        if self.underperformance_reasons:
            md.append("\n### ⚠️ Areas of Underperformance\n")
            for reason in self.underperformance_reasons:
                md.append(f"- {reason}")
        
        md.append("\n## 📰 Key News Events Impact\n")
        if self.key_news_events:
            for event in self.key_news_events:
                headline = event.get('headline', 'Unknown')
                date = event.get('date', 'N/A')
                impact = event.get('sentiment_impact', 'N/A')
                md.append(f"- **{date}**: {headline} (Impact: {impact})")
        else:
            md.append("No significant news events identified.")
        
        md.append("\n### 📈 Sentiment Impact Analysis\n")
        md.append(self.sentiment_impact_analysis)
        
        if self.political_factors:
            md.append("\n### 🏛️ Political & Regulatory Factors\n")
            for factor in self.political_factors:
                md.append(f"- {factor}")
        
        md.append("\n## 🎯 Strategy Insights\n")
        
        md.append("\n### Parameter Sensitivity\n")
        for param, sensitivity in self.parameter_sensitivity.items():
            md.append(f"- **{param}**: {sensitivity}")
        
        md.append("\n### Strengths\n")
        for strength in self.strategy_strengths:
            md.append(f"✅ {strength}")
        
        md.append("\n### Weaknesses\n")
        for weakness in self.strategy_weaknesses:
            md.append(f"⚠️ {weakness}")
        
        md.append("\n## 💡 Actionable Recommendations\n")
        for suggestion in self.suggestions:
            md.append(f"👉 {suggestion}")
        
        if self.risk_warnings:
            md.append("\n### ⚠️ Risk Warnings\n")
            for warning in self.risk_warnings:
                md.append(f"❗ {warning}")
        
        md.append(f"\n---\n*Model: {self.model_used}*")
        
        return "\n".join(md)


class ReasoningEngine:
    """
    AI Reasoning Engine that synthesizes trading data into insights.
    
    Supports multiple LLM backends (OpenAI, Ollama) with fallback to 
    rule-based analysis when LLM is unavailable.
    """
    
    SYSTEM_PROMPT = """You are an expert quantitative analyst and financial advisor. 
Your task is to analyze backtest results and provide actionable insights.

Analyze the following trading strategy performance data and generate a comprehensive report covering:
1. Why the strategy outperformed or underperformed vs Buy & Hold
2. Key news events and their impact on trades
3. Political/regulatory factors that may have influenced results
4. Parameter sensitivity observations
5. Concrete, actionable suggestions for improvement

Be specific, data-driven, and avoid generic statements. Reference actual metrics and dates where possible.
Format your response as valid JSON matching this schema:
{
    "performance_summary": "string",
    "outperformance_reasons": ["string"],
    "underperformance_reasons": ["string"],
    "key_news_events": [{"headline": "string", "date": "string", "sentiment_impact": "string"}],
    "sentiment_impact_analysis": "string",
    "political_factors": ["string"],
    "parameter_sensitivity": {"param_name": "observation"},
    "strategy_strengths": ["string"],
    "strategy_weaknesses": ["string"],
    "suggestions": ["string"],
    "risk_warnings": ["string"],
    "confidence_score": 0.0-1.0
}"""

    def __init__(
        self,
        llm_provider: str = "auto",
        openai_api_key: Optional[str] = None,
        ollama_model: str = "llama3.1",
        cache_enabled: bool = True,
        cache_dir: str = ".cache/ai_analysis"
    ):
        """
        Initialize the reasoning engine.
        
        Args:
            llm_provider: "openai", "ollama", or "auto" (tries OpenAI first)
            openai_api_key: API key for OpenAI (or set OPENAI_API_KEY env var)
            ollama_model: Model name for Ollama
            cache_enabled: Whether to cache analysis results
            cache_dir: Directory for caching
        """
        self.llm_provider = llm_provider
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.ollama_model = ollama_model
        self.cache_enabled = cache_enabled
        self.cache_dir = cache_dir
        
        # Create cache directory
        if cache_enabled:
            os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize LLM client
        self._llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM client based on provider settings."""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        # Auto-detect: prefer OpenAI if key available
        if self.llm_provider == "auto":
            if self.openai_api_key:
                self.llm_provider = "openai"
            else:
                self.llm_provider = "ollama"
        
        try:
            if self.llm_provider == "openai" and self.openai_api_key:
                return ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=self.openai_api_key,
                    temperature=0.3
                )
            elif self.llm_provider == "ollama":
                return ChatOllama(
                    model=self.ollama_model,
                    temperature=0.3
                )
        except Exception as e:
            print(f"Warning: Failed to initialize LLM: {e}")
            return None
        
        return None
    
    def _generate_cache_key(self, metrics: Dict, params: Dict, news_count: int) -> str:
        """Generate a unique cache key based on input parameters."""
        content = f"{json.dumps(metrics, sort_keys=True)}|{json.dumps(params, sort_keys=True)}|{news_count}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _get_cached_analysis(self, cache_key: str) -> Optional[AIAnalysisResult]:
        """Retrieve cached analysis if available."""
        if not self.cache_enabled:
            return None
        
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                return AIAnalysisResult(**data)
            except Exception:
                return None
        return None
    
    def _cache_analysis(self, cache_key: str, result: AIAnalysisResult):
        """Cache the analysis result."""
        if not self.cache_enabled:
            return
        
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        try:
            with open(cache_file, 'w') as f:
                json.dump(result.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to cache analysis: {e}")
    
    def _generate_rule_based_analysis(
        self,
        metrics: Dict,
        trades: List[Dict],
        news_data: Optional[List[Dict]],
        params: Dict
    ) -> AIAnalysisResult:
        """
        Generate analysis using rule-based heuristics (fallback when LLM unavailable).
        
        This provides reasonable analysis even without an LLM by applying
        quantitative rules and pattern recognition.
        """
        cache_key = self._generate_cache_key(metrics, params, len(news_data or []))
        generated_at = datetime.utcnow().isoformat()
        
        # Extract key metrics
        total_return = metrics.get('total_return', 0)
        bh_return = metrics.get('buy_hold_return', 0)
        sharpe = metrics.get('sharpe_ratio', 0)
        max_dd = metrics.get('max_drawdown', 0)
        win_rate = metrics.get('win_rate', 0)
        
        # Determine outperformance
        excess_return = total_return - bh_return
        outperformed = excess_return > 0
        
        # Generate performance summary
        if outperformed:
            performance_summary = (
                f"The strategy achieved a {total_return:.1%} return, outperforming Buy & Hold "
                f"({bh_return:.1%}) by {excess_return:.1%}. "
                f"With a Sharpe ratio of {sharpe:.2f} and maximum drawdown of {max_dd:.1%}, "
                f"the risk-adjusted returns {'were' if sharpe > 1 else 'could be'} attractive."
            )
        else:
            performance_summary = (
                f"The strategy returned {total_return:.1%}, underperforming Buy & Hold "
                f"({bh_return:.1%}) by {abs(excess_return):.1%}. "
                f"The Sharpe ratio of {sharpe:.2f} suggests {'poor' if sharpe < 0.5 else 'moderate'} "
                f"risk-adjusted performance."
            )
        
        # Analyze outperformance/underperformance reasons
        outperformance_reasons = []
        underperformance_reasons = []
        
        if outperformed:
            if excess_return > 0.1:
                outperformance_reasons.append(
                    f"Generated {excess_return:.1%} alpha over the benchmark period"
                )
            if win_rate > 0.55:
                outperformance_reasons.append(
                    f"High win rate ({win_rate:.0%}) indicates effective signal generation"
                )
            if max_dd < -0.15:
                outperformance_reasons.append(
                    "Superior risk management limited drawdowns during market stress"
                )
        else:
            if excess_return < -0.1:
                underperformance_reasons.append(
                    f"Underperformed benchmark by {abs(excess_return):.1%}"
                )
            if win_rate < 0.45:
                underperformance_reasons.append(
                    f"Low win rate ({win_rate:.0%}) suggests signal quality issues"
                )
            if max_dd < -0.25:
                underperformance_reasons.append(
                    "Excessive drawdown eroded capital during adverse periods"
                )
        
        # Analyze news impact
        key_news_events = []
        sentiment_impact = "No news data available for analysis."
        political_factors = []
        
        if news_data:
            avg_sentiment = sum(n.get('sentiment_score', 0) for n in news_data) / len(news_data)
            positive_news = [n for n in news_data if n.get('sentiment_score', 0) > 0.3]
            negative_news = [n for n in news_data if n.get('sentiment_score', 0) < -0.3]
            
            if positive_news:
                key_news_events.extend([
                    {"headline": n['headline'], "date": n['date'], "sentiment_impact": "Positive"}
                    for n in positive_news[:3]
                ])
            if negative_news:
                key_news_events.extend([
                    {"headline": n['headline'], "date": n['date'], "sentiment_impact": "Negative"}
                    for n in negative_news[:3]
                ])
            
            if avg_sentiment > 0.2:
                sentiment_impact = (
                    f"Overall positive sentiment (avg: {avg_sentiment:.2f}) likely supported "
                    f"bullish positions. {len(positive_news)} significantly positive articles "
                    f"may have contributed to successful long entries."
                )
            elif avg_sentiment < -0.2:
                sentiment_impact = (
                    f"Negative sentiment environment (avg: {avg_sentiment:.2f}) created headwinds. "
                    f"Strategy {'successfully navigated' if outperformed else 'struggled with'} "
                    f"the bearish news flow."
                )
            else:
                sentiment_impact = (
                    f"Neutral sentiment (avg: {avg_sentiment:.2f}) suggests news had minimal "
                    f"directional impact. Technical signals likely drove most trades."
                )
            
            # Detect potential political factors from headlines
            political_keywords = ['fed', 'interest rate', 'inflation', 'election', 'policy', 
                                 'regulation', 'sec', 'tariff', 'trade war', 'congress']
            for news in news_data:
                headline_lower = news.get('headline', '').lower()
                if any(kw in headline_lower for kw in political_keywords):
                    political_factors.append(news['headline'])
        
        # Parameter sensitivity analysis
        param_sensitivity = {}
        strategy_type = params.get('strategy_type', 'unknown')
        
        if 'short_window' in params and 'long_window' in params:
            short_w = params['short_window']
            long_w = params['long_window']
            ratio = long_w / max(short_w, 1)
            
            if ratio < 2:
                param_sensitivity['window_ratio'] = "Tight window ratio may cause whipsaw signals"
            elif ratio > 5:
                param_sensitivity['window_ratio'] = "Wide window ratio provides smoother but lagging signals"
            else:
                param_sensitivity['window_ratio'] = "Balanced window ratio for trend detection"
        
        if 'news_weight' in params:
            nw = params['news_weight']
            if nw > 0.7:
                param_sensitivity['news_weight'] = "Heavy reliance on sentiment; vulnerable to news noise"
            elif nw < 0.3:
                param_sensitivity['news_weight'] = "Minimal news integration; primarily technical approach"
            else:
                param_sensitivity['news_weight'] = "Balanced technical-sentiment weighting"
        
        # Strategy strengths/weaknesses
        strengths = []
        weaknesses = []
        
        if sharpe > 1.0:
            strengths.append("Strong risk-adjusted returns (Sharpe > 1.0)")
        if win_rate > 0.55:
            strengths.append("Consistent winning trades")
        if len(trades) > 10 and win_rate > 0.5:
            strengths.append("Scalable signal frequency with maintained accuracy")
        
        if max_dd < -0.2:
            weaknesses.append("Significant drawdown exposure")
        if len(trades) < 5:
            weaknesses.append("Limited trade sample size reduces statistical significance")
        if abs(total_return) < 0.05:
            weaknesses.append("Marginal absolute returns may not justify active management")
        
        # Generate suggestions
        suggestions = []
        if not outperformed:
            suggestions.append("Consider adjusting entry/exit thresholds to reduce false signals")
        if max_dd < -0.15:
            suggestions.append("Implement stop-loss mechanisms to limit downside risk")
        if news_data and 'news_weight' not in params:
            suggestions.append("Integrate sentiment analysis to enhance signal timing")
        if len(trades) > 20 and win_rate < 0.5:
            suggestions.append("Reduce trade frequency by filtering for higher-confidence setups")
        
        # Risk warnings
        risk_warnings = []
        if max_dd < -0.25:
            risk_warnings.append("Historical drawdown exceeds typical risk tolerance (25%)")
        if len(trades) < 10:
            risk_warnings.append("Limited trade history; results may not be statistically significant")
        if abs(total_return - bh_return) < 0.02:
            risk_warnings.append("Minimal alpha generation; consider passive alternative")
        
        # Calculate confidence score
        confidence_factors = []
        if len(trades) >= 20:
            confidence_factors.append(0.3)
        elif len(trades) >= 10:
            confidence_factors.append(0.2)
        else:
            confidence_factors.append(0.1)
        
        if news_data and len(news_data) > 10:
            confidence_factors.append(0.2)
        elif news_data:
            confidence_factors.append(0.1)
        
        if abs(sharpe) > 1:
            confidence_factors.append(0.3)
        elif abs(sharpe) > 0.5:
            confidence_factors.append(0.2)
        
        confidence_score = min(sum(confidence_factors), 0.95)
        
        return AIAnalysisResult(
            performance_summary=performance_summary,
            outperformance_reasons=outperformance_reasons,
            underperformance_reasons=underperformance_reasons,
            key_news_events=key_news_events,
            sentiment_impact_analysis=sentiment_impact,
            political_factors=political_factors,
            parameter_sensitivity=param_sensitivity,
            strategy_strengths=strengths,
            strategy_weaknesses=weaknesses,
            suggestions=suggestions,
            risk_warnings=risk_warnings,
            confidence_score=confidence_score,
            model_used="rule_based_heuristic",
            generated_at=generated_at,
            cache_key=cache_key
        )
    
    def _generate_llm_analysis(
        self,
        metrics: Dict,
        trades: List[Dict],
        news_data: Optional[List[Dict]],
        params: Dict
    ) -> AIAnalysisResult:
        """Generate analysis using LLM."""
        cache_key = self._generate_cache_key(metrics, params, len(news_data or []))
        
        # Prepare context for LLM
        context = {
            "metrics": metrics,
            "num_trades": len(trades),
            "trade_sample": trades[:5] if trades else [],  # First 5 trades as examples
            "news_summary": {
                "count": len(news_data) if news_data else 0,
                "avg_sentiment": sum(n.get('sentiment_score', 0) for n in news_data) / len(news_data) if news_data else 0,
                "recent_headlines": [n['headline'] for n in (news_data or [])[:5]]
            },
            "parameters": params
        }
        
        user_prompt = f"""Analyze this trading strategy performance:

METRICS:
{json.dumps(metrics, indent=2)}

TRADES (sample):
{json.dumps(context['trade_sample'], indent=2)}

NEWS CONTEXT:
{json.dumps(context['news_summary'], indent=2)}

PARAMETERS:
{json.dumps(params, indent=2)}

Provide your analysis in the exact JSON format specified in the system prompt."""

        try:
            if not self._llm:
                raise ValueError("LLM not initialized")
            
            messages = [
                SystemMessage(content=self.SYSTEM_PROMPT),
                HumanMessage(content=user_prompt)
            ]
            
            response = self._llm.invoke(messages)
            response_content = response.content
            
            # Parse JSON response
            # Handle potential markdown code blocks
            if "```json" in response_content:
                response_content = response_content.split("```json")[1].split("```")[0]
            elif "```" in response_content:
                response_content = response_content.split("```")[1].split("```")[0]
            
            analysis_data = json.loads(response_content.strip())
            
            # Build result object
            generated_at = datetime.utcnow().isoformat()
            
            return AIAnalysisResult(
                performance_summary=analysis_data.get('performance_summary', ''),
                outperformance_reasons=analysis_data.get('outperformance_reasons', []),
                underperformance_reasons=analysis_data.get('underperformance_reasons', []),
                key_news_events=analysis_data.get('key_news_events', []),
                sentiment_impact_analysis=analysis_data.get('sentiment_impact_analysis', ''),
                political_factors=analysis_data.get('political_factors', []),
                parameter_sensitivity=analysis_data.get('parameter_sensitivity', {}),
                strategy_strengths=analysis_data.get('strategy_strengths', []),
                strategy_weaknesses=analysis_data.get('strategy_weaknesses', []),
                suggestions=analysis_data.get('suggestions', []),
                risk_warnings=analysis_data.get('risk_warnings', []),
                confidence_score=float(analysis_data.get('confidence_score', 0.5)),
                model_used=f"{self.llm_provider}:{getattr(self._llm, 'model_name', getattr(self._llm, 'model', 'unknown'))}",
                generated_at=generated_at,
                cache_key=cache_key
            )
            
        except Exception as e:
            print(f"LLM analysis failed: {e}. Falling back to rule-based analysis.")
            return self._generate_rule_based_analysis(metrics, trades, news_data, params)
    
    def generate_analysis(
        self,
        metrics: Dict[str, Any],
        trades: List[Dict[str, Any]],
        news_data: Optional[List[Dict[str, Any]]] = None,
        strategy_params: Optional[Dict[str, Any]] = None,
        force_regenerate: bool = False
    ) -> AIAnalysisResult:
        """
        Generate comprehensive AI analysis of backtest results.
        
        Args:
            metrics: Dictionary of performance metrics
            trades: List of trade dictionaries with metadata
            news_data: Optional list of news articles with sentiment scores
            strategy_params: Strategy parameters used in backtest
            force_regenerate: If True, bypass cache and regenerate
            
        Returns:
            AIAnalysisResult with structured analysis
        """
        strategy_params = strategy_params or {}
        
        # Check cache first
        cache_key = self._generate_cache_key(metrics, strategy_params, len(news_data or []))
        if not force_regenerate:
            cached = self._get_cached_analysis(cache_key)
            if cached:
                return cached
        
        # Generate analysis
        if self._llm and LANGCHAIN_AVAILABLE:
            result = self._generate_llm_analysis(metrics, trades, news_data, strategy_params)
        else:
            result = self._generate_rule_based_analysis(metrics, trades, news_data, strategy_params)
        
        # Cache result
        self._cache_analysis(cache_key, result)
        
        return result


def generate_backtest_analysis(
    metrics: Dict[str, Any],
    trades: List[Dict[str, Any]],
    news_data: Optional[List[Dict[str, Any]]] = None,
    strategy_params: Optional[Dict[str, Any]] = None,
    llm_provider: str = "auto",
    cache_enabled: bool = True
) -> AIAnalysisResult:
    """
    Convenience function to generate backtest analysis.
    
    Args:
        metrics: Performance metrics dictionary
        trades: List of trade records
        news_data: Optional news with sentiment data
        strategy_params: Strategy configuration
        llm_provider: "openai", "ollama", or "auto"
        cache_enabled: Whether to use caching
        
    Returns:
        AIAnalysisResult with comprehensive analysis
    """
    engine = ReasoningEngine(
        llm_provider=llm_provider,
        cache_enabled=cache_enabled
    )
    
    return engine.generate_analysis(
        metrics=metrics,
        trades=trades,
        news_data=news_data,
        strategy_params=strategy_params
    )
