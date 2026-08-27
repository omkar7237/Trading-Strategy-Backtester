import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0,str(PROJECT_ROOT))

from data.loader import load_data
from data.indicator import sma,ema,rsi,macd,bollinger_bands
from strategy.basic_strategy import generate_signals
from backtest.engine import BacktestEngine

data = load_data("AAPL")

data["SMA_20"] = sma(data,20)

data["SMA_50"] = sma(data, 50)

data["EMA_20"] = ema(data, 20)

data["RSI_14"] = rsi(data)

data["MACD"], data["MACD_Signal"], data["MACD_Hist"] = macd(data)

data["BB_Upper"], data["BB_Middle"], data["BB_Lower"] = (
    bollinger_bands(data)
)

data["Signal"] = generate_signals(data)

engine = BacktestEngine(initial_capital=10000)

portfolio_values = []

for i in range(len(data)-1):

    current_date = data.index[i]

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

    value = engine.portfolio_value(
        next_open
    )

    portfolio_values.append(
        {
            "Date": next_date,
            "Portfolio": value
        }
    )

portfolio = pd.DataFrame(
    portfolio_values
)

portfolio.set_index(
    "Date",
    inplace = True
)

print("\nTrades")

print(
    engine.get_trades()
)

final_price = data["Close"].iloc[-1]

final_value = engine.portfolio_value(
    final_price
)

print(
    f"\nInitial Capital: ${engine.initial_capital:.2f}"
)

print(
    f"Final Portfolio value: ${final_value:.2f}"
)

total_return = (
    (final_value - engine.initial_capital)
    / engine.initial_capital
) * 100

print(
    f"Total Return: {total_return: .2f}%"
)

print(
    engine.get_trades
)



