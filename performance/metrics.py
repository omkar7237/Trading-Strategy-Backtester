import numpy as np
import pandas as pd

def total_return(initial_capacity, final_value):

    return (
        (final_value-initial_capacity) / initial_capacity
    ) * 100

def cagr(initial_capacity, final_value, years):

    if years<=0:
        return 0

    return (
        (final_value/initial_capacity) ** (1/years) - 1
    ) * 100

def calculate_trade_statistics(trades):

    completed_trades = []

    entry_price = None
    entry_shares = None

    for _,trade in trades.iterrows():

        if trade["Type"] == "BUY":

            entry_price = trade["Price"]
            entry_shares = trade["Shares"]

        elif trade["Type"] == "SELL":

            if entry_price is not None:

                pnl = (
                    trade["Price"] - entry_price
                ) * entry_shares

                completed_trades.append(pnl)

                entry_price = None
                entry_shares = None

    if len(completed_trades) == 0:

        return {
            "total_trades": 0,
            "winning_trades" : 0,
            "losing_trades" : 0,
            "win_rate": 0,
            "average_win": 0,
            "average_loss": 0,
            "profit_factor": 0
        }

    profits = [
        pnl for pnl in completed_trades
        if pnl > 0
    ]

    losses = [
        pnl for pnl in completed_trades
        if pnl < 0
    ]

    total_trades = len(completed_trades)

    winning_trades = len(profits)

    losing_trades = len(losses)

    win_rate = (winning_trades / total_trades) * 100

    average_win = (
        np.mean(profits)
        if profits
        else 0
    )

    average_loss = (
        np.mean(losses)
        if losses
        else 0
    )

    gross_profit = sum(profits)
    gross_loss = abs(sum(losses))

    if gross_loss > 0:

        profit_factor = (gross_profit/gross_loss)

    else:

        profit_factor = float("inf")

    return {
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": win_rate,
        "average_win": average_win,
        "average_loss": average_loss,
        "profit_factor": profit_factor
    }

def drawdown_series(portfolio):

    peak = portfolio.cummax()

    drawdown = (
        portfolio - peak
    ) / peak

    return drawdown

def maximum_drawdown(portfolio):

    drawdown = drawdown_series(portfolio)

    return drawdown.min() * 100

def sharpe_ratio(portfolio):

    returns = portfolio.pct_change().dropna()

    if returns.std() == 0:
        return 0

    return (
        returns.mean()/ returns.std()
    ) * np.sqrt(252)

