import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.loader import load_data
from data.indicator import sma,ema,rsi,macd,bollinger_bands
from strategy.basic_strategy import generate_signals
from backtest.engine import BacktestEngine

def prepare_data(symbol, fast_period, slow_period):

    data = load_data(symbol)

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

    data["BB_Upper"], data["BB_Middle"], data["BB_Lower"] = (
        bollinger_bands(data)
    )

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

    final_price = data["Close"].iloc[-1]

    return engine.portfolio_value(final_price)

data = prepare_data(
    "AAPL",
    20,
    50
)

final_value = run_backtest(data)

print(
    f"SMA 20/50: ${final_value:.2f}"
)

parameter_sets = [
    (10, 30),
    (20, 50),
    (30, 60),
    (50, 100)
]

results = []

for fast, slow in parameter_sets:

    data = prepare_data(
        "AAPL",
        fast,
        slow
    )

    final_value = run_backtest(data)

    total_return = (
        (final_value - 10000)
        / 10000
    ) * 100

    results.append({
        "Fast SMA": fast,
        "Slow SMA": slow,
        "Final Value": final_value,
        "Return": total_return
    })

results = pd.DataFrame(results)

print(results)

best = results.loc[
    results["Return"].idxmax()
]

print("\nBest Parameters:")
print(best)