import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.loader import load_data
from data.indicator import (
    sma,
    ema,
    rsi,
    macd,
    bollinger_bands
)

from strategy.basic_strategy import generate_signals
from backtest.engine import BacktestEngine

symbols = [
    "AAPL",
    "GOOGL",
    "MSFT"
]

weights = {
    "AAPL": 0.4,
    "GOOGL": 0.3,
    "MSFT": 0.3
}

def prepare_data(symbol):

    data = load_data(symbol)

    data["SMA_20"] = sma(data, 20)
    data["SMA_50"] = sma(data, 50)
    data["EMA_20"] = ema(data, 20)

    data["RSI_14"] = rsi(data)

    data["MACD"], data["MACD_Signal"], data["MACD_Hist"] = macd(data)

    data["BB_Upper"], data["BB_Middle"], data["BB_Lower"] = (
        bollinger_bands(data)
    )

    data["Signal"] = generate_signals(data)

    return data

datasets = {}

for symbol in symbols:

    datasets[symbol] = prepare_data(symbol)

datasets["AAPL"]
datasets["GOOGL"]
datasets["MSFT"]

returns = {}

for symbol in symbols:

    data = datasets[symbol]

    returns[symbol] = data["Close"].pct_change()

returns_df = pd.DataFrame(returns)

print(returns_df.tail())

portfolio_returns = pd.Series(0.0, index=returns_df.index)

for symbol in symbols:

    portfolio_returns += (
        returns_df[symbol] * weights[symbol]
    )

initial_capital = 10000

portfolio_value = (
    initial_capital *
    (1 + portfolio_returns).cumprod()
)

print(portfolio_value.tail())

final_value = portfolio_value.iloc[-1]

total_return = (
    (final_value - initial_capital)
    / initial_capital
) * 100

print(
    f"Final Portfolio: ${final_value:.2f}"
)

print(
    f"Total Return: {total_return:.2f}%"
)

import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=portfolio_value.index,
        y=portfolio_value,
        mode="lines",
        name="Portfolio"
    )
)

fig.update_layout(
    title="Portfolio Equity Curve",
    xaxis_title="Date",
    yaxis_title="Portfolio Value"
)

fig.show()