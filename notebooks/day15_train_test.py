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


INITIAL_CAPITAL = 10000


# --------------------------------------------------
# PREPARE DATA
# --------------------------------------------------

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

    data["MACD"], data["MACD_Signal"], data["MACD_Hist"] = (
        macd(data)
    )

    data["BB_Upper"], data["BB_Middle"], data["BB_Lower"] = (
        bollinger_bands(data)
    )

    data["Signal"] = generate_signals(
        data,
        fast_period,
        slow_period
    )

    return data


# --------------------------------------------------
# RUN BACKTEST
# --------------------------------------------------

def run_backtest(data):

    engine = BacktestEngine(
        initial_capital=INITIAL_CAPITAL,
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

    final_value = engine.portfolio_value(
        final_price
    )

    return final_value


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

data = load_data("AAPL")


# --------------------------------------------------
# TRAIN / TEST SPLIT
# --------------------------------------------------

split_index = int(len(data) * 0.70)

train_data = data.iloc[:split_index].copy()

test_data = data.iloc[split_index:].copy()


print("=" * 60)
print("DATA SPLIT")
print("=" * 60)

print(
    f"Training: {train_data.index[0].date()} "
    f"→ {train_data.index[-1].date()}"
)

print(
    f"Testing:  {test_data.index[0].date()} "
    f"→ {test_data.index[-1].date()}"
)


# --------------------------------------------------
# PARAMETER TESTING ON TRAINING DATA
# --------------------------------------------------

parameter_sets = [
    (10, 30),
    (20, 50),
    (30, 60),
    (50, 100)
]

train_results = []


for fast, slow in parameter_sets:

    prepared_train = prepare_data(
        train_data,
        fast,
        slow
    )

    final_value = run_backtest(
        prepared_train
    )

    total_return = (
        (final_value - INITIAL_CAPITAL)
        / INITIAL_CAPITAL
    ) * 100

    train_results.append({
        "Fast SMA": fast,
        "Slow SMA": slow,
        "Final Value": final_value,
        "Return": total_return
    })


train_results = pd.DataFrame(
    train_results
)


# --------------------------------------------------
# FIND BEST PARAMETERS
# --------------------------------------------------

best_row = train_results.loc[
    train_results["Return"].idxmax()
]

best_fast = int(best_row["Fast SMA"])
best_slow = int(best_row["Slow SMA"])


print("\n")
print("=" * 60)
print("TRAINING RESULTS")
print("=" * 60)

print(train_results)

print("\nBest Parameters:")

print(
    f"Fast SMA: {best_fast}"
)

print(
    f"Slow SMA: {best_slow}"
)


# --------------------------------------------------
# TEST BEST PARAMETERS
# --------------------------------------------------

prepared_test = prepare_data(
    test_data,
    best_fast,
    best_slow
)

test_final_value = run_backtest(
    prepared_test
)

test_return = (
    (test_final_value - INITIAL_CAPITAL)
    / INITIAL_CAPITAL
) * 100


# --------------------------------------------------
# FINAL REPORT
# --------------------------------------------------

print("\n")
print("=" * 60)
print("OUT-OF-SAMPLE TEST")
print("=" * 60)

print(
    f"Parameters: SMA {best_fast} / SMA {best_slow}"
)

print(
    f"Initial Capital: ${INITIAL_CAPITAL:,.2f}"
)

print(
    f"Final Portfolio: ${test_final_value:,.2f}"
)

print(
    f"Test Return: {test_return:.2f}%"
)

print("=" * 60)