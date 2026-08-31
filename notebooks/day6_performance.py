import sys
from pathlib import Path

import pandas as pd
import numpy as np
import plotly.graph_objects as go

PROJECT_ROOT = Path(__file__).resolve().parent.parent 

sys.path.insert(0,str(PROJECT_ROOT))

from data.loader import load_data

from data.indicator import sma,ema,rsi,macd,bollinger_bands

from strategy.basic_strategy import generate_signals

from backtest.engine import BacktestEngine

from performance.metrics import (
    total_return,
    cagr,
    sharpe_ratio,
    calculate_trade_statistics,
    maximum_drawdown
)

data = load_data("AAPL")

data["SMA_20"] = sma(data,20)

data["SMA_50"] = sma(data,50)

data["EMA_20"] = ema(data,50)

data["RSI_14"] = rsi(data)

data["MACD"], data["MACD_Signal"], data["MACD_Hist"] = macd(data)

data["BB_Upper"], data["BB_Middle"], data["BB_Lower"] = bollinger_bands(data)

data["Signal"] = generate_signals(data)

engine = BacktestEngine(initial_capital=10000)

portfolio_values = []

for i in range(len(data) - 1):

    next_date = data.index[i+1]

    signal = data["Signal"].iloc[i]

    next_open = data["Open"].iloc[i+1]

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

    value = engine.portfolio_value(next_open)

    portfolio_values.append({
        "Date":next_date,
        "Portfolio":value
    })

    portfolio = pd.DataFrame(
    portfolio_values
)

portfolio.set_index(
    "Date",
    inplace=True
)

portfolio["Portfolio"]

final_price = data["Close"].iloc[-1]

final_value = engine.portfolio_value(
    final_price
)

initial_capital = engine.initial_capital

days = (
    data.index[-1] - data.index[0]
).days

years = days / 365.25

strategy_return = total_return(
    initial_capital,
    final_value
)

strategy_cagr = cagr(
    initial_capital,
    final_value,
    years
)

trades = engine.get_trades()

trade_stats = calculate_trade_statistics(
    trades
)

max_dd = maximum_drawdown(
    portfolio["Portfolio"]
)

sharpe = sharpe_ratio(
    portfolio["Portfolio"]
)

buy_hold_start = data["Open"].iloc[1]
buy_hold_end = data["Close"].iloc[-1]

buy_hold_shares = int(initial_capital // buy_hold_start)

buy_hold_cash = (initial_capital - buy_hold_shares*buy_hold_start)

buy_hold_final = (buy_hold_cash + buy_hold_shares*buy_hold_end)

buy_hold_return = total_return(initial_capital,buy_hold_final)


print("\n")
print("=" * 50)
print("        STRATEGY PERFORMANCE")
print("=" * 50)

print(
    f"Initial Capital:     ${initial_capital:,.2f}"
)

print(
    f"Final Portfolio:     ${final_value:,.2f}"
)

print(
    f"Total Return:        {strategy_return:.2f}%"
)

print(
    f"CAGR:                {strategy_cagr:.2f}%"
)

print(
    f"Total Trades:        {trade_stats['total_trades']}"
)

print(
    f"Winning Trades:      {trade_stats['winning_trades']}"
)

print(
    f"Losing Trades:       {trade_stats['losing_trades']}"
)

print(
    f"Win Rate:            {trade_stats['win_rate']:.2f}%"
)

print(
    f"Average Win:         ${trade_stats['average_win']:.2f}"
)

print(
    f"Average Loss:        ${trade_stats['average_loss']:.2f}"
)

print(
    f"Profit Factor:       {trade_stats['profit_factor']:.2f}"
)

print(
    f"Maximum Drawdown:    {max_dd:.2f}%"
)

print(
    f"Sharpe Ratio:        {sharpe:.2f}"
)

print(
    f"Buy & Hold Final:    ${buy_hold_final:,.2f}"
)

print(
    f"Buy & Hold Return:   {buy_hold_return:.2f}%"
)

print("=" * 50)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x = portfolio.index,
        y = portfolio["Portfolio"],
        mode = "lines",
        name = "Strategy"
    )
)

fig.update_layout(
    title = "Strategy Equity Curve",
    xaxis_title = "Date",
    yaxis_title = "Portfolio Value ($)"
)

fig.show()