import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies."""
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
        """Generate trading signals based on input data and parameters."""
        pass
    
    @abstractmethod
    def get_param_schema(self) -> List[Dict[str, Any]]:
        """Return parameter schema for frontend form generation."""
        pass


class MACrossoverStrategy(BaseStrategy):
    """Moving Average Crossover Strategy."""
    
    def generate_signals(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
        short_window = params.get('short_window', 20)
        long_window = params.get('long_window', 50)
        
        signals = pd.Series(0, index=data.index, name="Signal")
        
        sma_short = data[f'SMA_{short_window}'] if f'SMA_{short_window}' in data.columns else data['Close'].rolling(window=short_window).mean()
        sma_long = data[f'SMA_{long_window}'] if f'SMA_{long_window}' in data.columns else data['Close'].rolling(window=long_window).mean()
        
        # Buy when short MA crosses above long MA
        buy_condition = (sma_short > sma_long) & (sma_short.shift(1) <= sma_long.shift(1))
        # Sell when short MA crosses below long MA
        sell_condition = (sma_short < sma_long) & (sma_short.shift(1) >= sma_long.shift(1))
        
        signals[buy_condition] = 1
        signals[sell_condition] = -1
        
        return signals
    
    def get_param_schema(self) -> List[Dict[str, Any]]:
        return [
            {"name": "short_window", "type": "int", "default": 20, "min_val": 5, "max_val": 50, "step": 1},
            {"name": "long_window", "type": "int", "default": 50, "min_val": 20, "max_val": 200, "step": 1}
        ]


class RSIStrategy(BaseStrategy):
    """RSI Mean Reversion Strategy."""
    
    def generate_signals(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
        rsi_period = params.get('rsi_period', 14)
        oversold = params.get('oversold_threshold', 30)
        overbought = params.get('overbought_threshold', 70)
        
        signals = pd.Series(0, index=data.index, name="Signal")
        
        rsi_col = f'RSI_{rsi_period}'
        if rsi_col not in data.columns:
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=rsi_period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = data[rsi_col]
        
        # Buy when RSI is oversold
        buy_condition = rsi < oversold
        # Sell when RSI is overbought
        sell_condition = rsi > overbought
        
        signals[buy_condition] = 1
        signals[sell_condition] = -1
        
        return signals
    
    def get_param_schema(self) -> List[Dict[str, Any]]:
        return [
            {"name": "rsi_period", "type": "int", "default": 14, "min_val": 7, "max_val": 28, "step": 1},
            {"name": "oversold_threshold", "type": "float", "default": 30.0, "min_val": 20.0, "max_val": 40.0, "step": 1},
            {"name": "overbought_threshold", "type": "float", "default": 70.0, "min_val": 60.0, "max_val": 80.0, "step": 1}
        ]


class MACDStrategy(BaseStrategy):
    """MACD Momentum Strategy."""
    
    def generate_signals(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
        fast_period = params.get('fast_period', 12)
        slow_period = params.get('slow_period', 26)
        signal_period = params.get('signal_period', 9)
        
        signals = pd.Series(0, index=data.index, name="Signal")
        
        # Calculate MACD if not present
        if 'MACD' not in data.columns:
            exp1 = data['Close'].ewm(span=fast_period, adjust=False).mean()
            exp2 = data['Close'].ewm(span=slow_period, adjust=False).mean()
            macd = exp1 - exp2
            signal_line = macd.ewm(span=signal_period, adjust=False).mean()
        else:
            macd = data['MACD']
            signal_line = data['MACD_Signal']
        
        # Buy when MACD crosses above signal line
        buy_condition = (macd > signal_line) & (macd.shift(1) <= signal_line.shift(1))
        # Sell when MACD crosses below signal line
        sell_condition = (macd < signal_line) & (macd.shift(1) >= signal_line.shift(1))
        
        signals[buy_condition] = 1
        signals[sell_condition] = -1
        
        return signals
    
    def get_param_schema(self) -> List[Dict[str, Any]]:
        return [
            {"name": "fast_period", "type": "int", "default": 12, "min_val": 5, "max_val": 20, "step": 1},
            {"name": "slow_period", "type": "int", "default": 26, "min_val": 15, "max_val": 50, "step": 1},
            {"name": "signal_period", "type": "int", "default": 9, "min_val": 5, "max_val": 15, "step": 1}
        ]


class CombinedStrategy(BaseStrategy):
    """Combined MA Crossover + RSI Strategy."""
    
    def generate_signals(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
        ma_params = {k: v for k, v in params.items() if 'window' in k}
        rsi_params = {k: v for k, v in params.items() if 'rsi' in k or 'threshold' in k}
        
        ma_strategy = MACrossoverStrategy()
        rsi_strategy = RSIStrategy()
        
        ma_signals = ma_strategy.generate_signals(data, ma_params or {'short_window': 20, 'long_window': 50})
        rsi_signals = rsi_strategy.generate_signals(data, rsi_params or {'rsi_period': 14, 'oversold_threshold': 30, 'overbought_threshold': 70})
        
        signals = pd.Series(0, index=data.index, name="Signal")
        
        # Both strategies must agree for a signal
        buy_condition = (ma_signals == 1) & (rsi_signals == 1)
        sell_condition = (ma_signals == -1) | (rsi_signals == -1)
        
        signals[buy_condition] = 1
        signals[sell_condition] = -1
        
        return signals
    
    def get_param_schema(self) -> List[Dict[str, Any]]:
        return [
            {"name": "short_window", "type": "int", "default": 20, "min_val": 5, "max_val": 50, "step": 1},
            {"name": "long_window", "type": "int", "default": 50, "min_val": 20, "max_val": 200, "step": 1},
            {"name": "rsi_period", "type": "int", "default": 14, "min_val": 7, "max_val": 28, "step": 1},
            {"name": "oversold_threshold", "type": "float", "default": 30.0, "min_val": 20.0, "max_val": 40.0, "step": 1},
            {"name": "overbought_threshold", "type": "float", "default": 70.0, "min_val": 60.0, "max_val": 80.0, "step": 1}
        ]