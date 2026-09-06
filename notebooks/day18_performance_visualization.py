import sys
from pathlib import Path

import pandas as pd
import numpy as np
import plotly.graph_objects as go

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

def prepare_data(data):

    data = data.copy()

    data["SMA_20"] = sma(data, 20)
    data["SMA_50"] = sma(data, 50)

    data["EMA_20"] = ema(data, 20)

    data["RSI_14"] = rsi(data)

    data["MACD"], data["MACD_Signal"], data["MACD_Hist"] = (
        macd(data)
    )

    data["BB_Upper"], data["BB_Middle"], data["BB_Lower"] = (
        bollinger_bands(data)
    )

    data["Signal"] = generate_signals(data)

    return data

def run_backtest(data):

    engine = BacktestEngine(
        initial_capital=10000,
        commission=0.001,
        slippage=0,
        position_size=0.5
    )

    portfolio_values = []

    for i in range(len(data) - 1):

        current_date = data.index[i]
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

        portfolio_value = engine.portfolio_value(
            next_open
        )

        portfolio_values.append({
            "Date": next_date,
            "Portfolio": portfolio_value
        })

    portfolio = pd.DataFrame(
        portfolio_values
    )

    portfolio.set_index(
        "Date",
        inplace=True
    )

    return engine, portfolio

def calculate_buy_and_hold(data):

    initial_capital = 10000

    first_price = data["Open"].iloc[0]

    shares = initial_capital // first_price

    cash = initial_capital - (
        shares * first_price
    )

    portfolio = (
        shares * data["Close"]
    ) + cash

    return portfolio

def calculate_drawdown(portfolio):

    running_max = portfolio.cummax()

    drawdown = (
        portfolio - running_max
    ) / running_max

    return drawdown * 100

data = load_data("AAPL")

data = prepare_data(data)

engine, portfolio = run_backtest(data)

buy_hold = calculate_buy_and_hold(data)

portfolio["Buy_Hold"] = buy_hold.reindex(
    portfolio.index
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=portfolio.index,
        y=portfolio["Portfolio"],
        mode="lines",
        name="Strategy"
    )
)

fig.add_trace(
    go.Scatter(
        x=portfolio.index,
        y=portfolio["Buy_Hold"],
        mode="lines",
        name="Buy & Hold"
    )
)

fig.update_layout(
    title="Strategy vs Buy & Hold",
    xaxis_title="Date",
    yaxis_title="Portfolio Value ($)"
)

fig.show()

portfolio["Drawdown"] = calculate_drawdown(
    portfolio["Portfolio"]
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=portfolio.index,
        y=portfolio["Drawdown"],
        mode="lines",
        name="Strategy Drawdown"
    )
)

fig.update_layout(
    title="Strategy Drawdown",
    xaxis_title="Date",
    yaxis_title="Drawdown (%)"
)

fig.show()

strategy_final = portfolio["Portfolio"].iloc[-1]

buy_hold_final = portfolio["Buy_Hold"].iloc[-1]

strategy_return = (
    (strategy_final - 10000)
    / 10000
) * 100

buy_hold_return = (
    (buy_hold_final - 10000)
    / 10000
) * 100

maximum_drawdown = portfolio["Drawdown"].min()

print("\n" + "=" * 60)
print("PERFORMANCE COMPARISON")
print("=" * 60)

print(
    f"Strategy Final Value: ${strategy_final:,.2f}"
)

print(
    f"Strategy Return:      {strategy_return:.2f}%"
)

print(
    f"Buy & Hold Value:     ${buy_hold_final:,.2f}"
)

print(
    f"Buy & Hold Return:    {buy_hold_return:.2f}%"
)

print(
    f"Maximum Drawdown:     {maximum_drawdown:.2f}%"
)

print("=" * 60)


engine, portfolio = run_backtest(data)

print("\nTRADES")
print(engine.get_trades())

buy_hold = calculate_buy_and_hold(data)
