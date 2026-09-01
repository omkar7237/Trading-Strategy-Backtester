import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)

from data.loader import load_data
from data.indicator import (
    sma,
    ema,
    rsi,
    macd,
    bollinger_bands
)

from strategy.basic_strategy import generate_signals

data = load_data("AAPL")

data["SMA_20"] = sma(data, 20)

data["SMA_50"] = sma(data, 50)

data["EMA_20"] = ema(data, 20)

data["RSI_14"] = rsi(data)

data["MACD"], \
data["MACD_Signal"], \
data["MACD_Hist"] = macd(data)

data["BB_Upper"], \
data["BB_Middle"], \
data["BB_Lower"] = bollinger_bands(data)

data["Signal"] = generate_signals(data)

print(
    data[
        [
            "Close",
            "SMA_20",
            "SMA_50",
            "RSI_14",
            "MACD",
            "MACD_Signal",
            "Signal"
        ]
    ].tail(30)
)

print("\nSignal counts:")

print(
    data["Signal"].value_counts()
)

buy_count = (
    data["Signal"] == 1
).sum()

sell_count = (
    data["Signal"] == -1
).sum()

hold_count = (
    data["Signal"] == 0
).sum()

print("BUY :", buy_count)
print("SELL:", sell_count)
print("HOLD:", hold_count)

import plotly.graph_objects as go

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=data.index,
        y=data["Close"],
        mode="lines",
        name="AAPL"
    )
)

buy_signals = data[
    data["Signal"] == 1
]

sell_signals = data[
    data["Signal"] == -1
]

fig.add_trace(
    go.Scatter(
        x=buy_signals.index,
        y=buy_signals["Close"],
        mode="markers",
        name="BUY",
        marker=dict(
            symbol="triangle-up",
            size=10
        )
    )
)

fig.add_trace(
    go.Scatter(
        x=sell_signals.index,
        y=sell_signals["Close"],
        mode="markers",
        name="SELL",
        marker=dict(
            symbol="triangle-down",
            size=10
        )
    )
)

fig.update_layout(
    title="AAPL Strategy Signals",
    xaxis_title="Date",
    yaxis_title="Price"
)

fig.show()

from backtest.engine import BacktestEngine

engine = BacktestEngine(
    initial_capital=10000,
    commission=0.001,
    slippage=0.001
)

portfolio_values = []

for i in range(len(data) - 1):

    next_date = data.index[i + 1]

    signal = data["Signal"].iloc[i]

    next_open = data["Open"].iloc[i + 1]

    if signal == 1:

        engine.buy(
            next_date,
            next_open
        )

    elif signal == -1:

        engine.sell(
            next_date,
            next_open
        )

    value = engine.portfolio_value(
        next_open
    )

    portfolio_values.append({
        "Date": next_date,
        "Portfolio": value
    })