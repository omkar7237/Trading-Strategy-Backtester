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

    data[f"SMA_{fast_period}"] = sma(data, fast_period)
    data[f"SMA_{slow_period}"] = sma(data, slow_period)

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

def walk_forward_test(data, parameter_sets):

    results = []

    train_size = 500
    test_size = 100

    start = 0

    while start + train_size + test_size <= len(data):

        train_data = data.iloc[
            start:start + train_size
        ].copy()

        test_data = data.iloc[
            start + train_size:
            start + train_size + test_size
        ].copy()

        print("\n" + "=" * 50)

        print(
            f"Training: {train_data.index[0].date()} "
            f"→ {train_data.index[-1].date()}"
        )

        print(
            f"Testing:  {test_data.index[0].date()} "
            f"→ {test_data.index[-1].date()}"
        )

        best_params = None
        best_return = float("-inf")

        # -------------------------
        # TRAIN
        # -------------------------

        for fast_period, slow_period in parameter_sets:

            train_prepared = prepare_data(
                train_data,
                fast_period,
                slow_period
            )

            _, train_return = run_backtest(train_prepared)

            print(
                f"Params ({fast_period}, {slow_period}) "
                f"Train Return: {train_return:.2f}%"
            )

            if train_return > best_return:

                best_return = train_return
                best_params = (fast_period, slow_period)

        # -------------------------
        # TEST
        # -------------------------

        fast_period, slow_period = best_params

        test_prepared = prepare_data(
            test_data,
            fast_period,
            slow_period
        )

        test_value, test_return = run_backtest(test_prepared)

        print(
            f"Best Parameters: {best_params}"
        )

        print(
            f"Test Return: {test_return:.2f}%"
        )

        results.append({
            "Train Start": train_data.index[0],
            "Train End": train_data.index[-1],
            "Test Start": test_data.index[0],
            "Test End": test_data.index[-1],
            "Fast SMA": fast_period,
            "Slow SMA": slow_period,
            "Train Return": best_return,
            "Test Return": test_return,
            "Test Final Value": test_value
        })

        # Move forward

        start += test_size

    return pd.DataFrame(results)

data = load_data("AAPL")

parameter_sets = [
    (10, 30),
    (20, 50),
    (30, 60),
    (50, 100)
]

results = walk_forward_test(
    data,
    parameter_sets
)

print("\n")
print("=" * 60)
print("WALK-FORWARD RESULTS")
print("=" * 60)

print(results.to_string(index=False))

print("\nAverage Train Return:")
print(
    f"{results['Train Return'].mean():.2f}%"
)

print("\nAverage Test Return:")
print(
    f"{results['Test Return'].mean():.2f}%"
)