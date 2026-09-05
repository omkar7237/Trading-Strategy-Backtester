import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.loader import load_data
from data.indicator import sma, ema, rsi, macd, bollinger_bands
from strategy.basic_strategy import generate_signals
from backtest.engine import BacktestEngine

def prepare_data(data, fast_period, slow_period):

    data = data.copy()

    data[f"SMA_{fast_period}"] = sma(
        data,
        fast_period
    )

    data[f"SMA_{slow_period}"] = sma(
        data,
        slow_period
    )

    data["EMA_20"] = ema(data, 20)

    data["RSI_14"] = rsi(data)

    data["MACD"], data["MACD_Signal"], data["MACD_Hist"] = macd(data)

    data["BB_Upper"], data["BB_Middle"], data["BB_Lower"] = bollinger_bands(data)

    data["Signal"] = generate_signals(
        data,
        fast_period,
        slow_period
    )

    return data

def run_backtest(data):

    engine = BacktestEngine(
        initial_capital=10000,
        commission=0.001,
        slippage=0,
        position_size=0.5
    )

    for i in range(1, len(data)):

        signal = data["Signal"].iloc[i]
        price = data["Open"].iloc[i]
        date = data.index[i]

        if signal == 1:
            engine.buy(date, price)

        elif signal == -1:
            engine.sell(date, price)

    final_price = data["Close"].iloc[-1]

    final_value = engine.portfolio_value(final_price)

    total_return = (
        (final_value - engine.initial_capital)
        / engine.initial_capital
    ) * 100

    return final_value, total_return

symbols = [
    "AAPL",
    "GOOGL",
    "MSFT"
]

parameter_sets = [
    (10, 30),
    (20, 50),
    (30, 60),
    (50, 100)
]

results = []

for symbol in symbols:

    print("\n" + "=" * 60)
    print(f"TESTING {symbol}")
    print("=" * 60)

    data = load_data(
        f"{symbol}"
    )

    for fast_period, slow_period in parameter_sets:

        prepared_data = prepare_data(
            data,
            fast_period,
            slow_period
        )

        final_value, total_return = run_backtest(
            prepared_data
        )

        results.append({
            "Symbol": symbol,
            "Fast SMA": fast_period,
            "Slow SMA": slow_period,
            "Final Value": final_value,
            "Return": total_return
        })

        print(
            f"{symbol} | "
            f"SMA {fast_period}/{slow_period} | "
            f"Return: {total_return:.2f}%"
        )

results_df = pd.DataFrame(results)

print("\n")
print("=" * 70)
print("ROBUSTNESS RESULTS")
print("=" * 70)

print(
    results_df.to_string(index=False)
)

best = results_df.loc[
    results_df["Return"].idxmax()
]

worst = results_df.loc[
    results_df["Return"].idxmin()
]

print("\nBEST RESULT")
print(best)

print("\nWORST RESULT")
print(worst)

print("\nAVERAGE RETURN BY STOCK")

stock_summary = (
    results_df
    .groupby("Symbol")["Return"]
    .agg(["mean", "max", "min"])
)

print(stock_summary)

print("\nAVERAGE RETURN BY PARAMETERS")

parameter_summary = (
    results_df
    .groupby(["Fast SMA", "Slow SMA"])["Return"]
    .agg(["mean", "max", "min"])
)

print(parameter_summary)