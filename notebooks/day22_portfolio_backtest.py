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

from backtest.portfolio import Portfolio

def prepare_data(symbol):

    data = load_data(symbol)

    data = data.copy()

    data["SMA_20"] = sma(
        data,
        20
    )

    data["SMA_50"] = sma(
        data,
        50
    )

    data["EMA_20"] = ema(
        data,
        20
    )

    data["RSI_14"] = rsi(
        data
    )

    (
        data["MACD"],
        data["MACD_Signal"],
        data["MACD_Hist"]
    ) = macd(data)

    (
        data["BB_Upper"],
        data["BB_Middle"],
        data["BB_Lower"]
    ) = bollinger_bands(data)

    data["Signal"] = generate_signals(
        data
    )

    return data

symbols = [
    "AAPL",
    "GOOGL",
    "MSFT"
]

datasets = {}

for symbol in symbols:

    print(
        f"Loading {symbol}..."
    )

    datasets[symbol] = prepare_data(
        symbol
    )

portfolio = Portfolio(
    initial_capital=10000
)

allocation = (
    portfolio.initial_capital
    / len(symbols)
)

common_dates = datasets[symbols[0]].index

for symbol in symbols:

    common_dates = common_dates.intersection(
        datasets[symbol].index
    )

common_dates = common_dates.sort_values()

portfolio_values = []

for i in range(
    len(common_dates) - 1
):

    current_date = common_dates[i]

    next_date = common_dates[i + 1]

    current_prices = {}

    for symbol in symbols:

        data = datasets[symbol]

        signal = data.loc[
            current_date,
            "Signal"
        ]

        next_open = data.loc[
            next_date,
            "Open"
        ]

        current_prices[symbol] = next_open

        if signal == 1:

            portfolio.buy(
                symbol=symbol,
                date=next_date,
                price=next_open,
                amount=allocation
            )

        elif signal == -1:

            portfolio.sell(
                symbol=symbol,
                date=next_date,
                price=next_open
            )


    value = portfolio.value(
        current_prices
    )

    portfolio_values.append({

        "Date": next_date,

        "Portfolio": value

    })

portfolio_df = pd.DataFrame(
    portfolio_values
)

portfolio_df.set_index(
    "Date",
    inplace=True
)

initial = portfolio.initial_capital

final = portfolio_df[
    "Portfolio"
].iloc[-1]

return_pct = (
    (final - initial)
    / initial
) * 100

print("\n")
print("=" * 60)
print("MULTI-ASSET PORTFOLIO")
print("=" * 60)

print(
    f"Initial Capital: "
    f"${initial:,.2f}"
)

print(
    f"Final Portfolio: "
    f"${final:,.2f}"
)

print(
    f"Total Return: "
    f"{return_pct:.2f}%"
)

print("\nPositions:")

print(
    portfolio.positions
)

print("\nTrades:")

print(
    portfolio.get_trades()
)

print("=" * 60)