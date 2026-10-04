"""Tests for the strategy classes in strategy/basic_strategy.py.

These replace an earlier test module that imported a module-level
`generate_signals(data)` helper which no longer exists. Signal generation is
now a method on each strategy class taking (data, params), so the tests
target that API.
"""

import pandas as pd
import pytest

from strategy.basic_strategy import (
    MACrossoverStrategy,
    RSIStrategy,
    MACDStrategy,
    CombinedStrategy,
)


def _frame(rows):
    """Build a Close-only frame with a RangeIndex from a list of prices."""
    return pd.DataFrame({"Close": rows}, dtype="float64")


class TestMACrossoverStrategy:
    def test_buy_on_upward_cross(self):
        # Sustained rally from a downtrend: the short MA ends up above the
        # long MA, and the buy fires on the bar where that flip happens.
        prices = [10, 9, 8, 7, 6, 5, 4, 3, 20, 30]
        strategy = MACrossoverStrategy()
        signals = strategy.generate_signals(
            _frame(prices), {"short_window": 2, "long_window": 4}
        )

        assert 1 in signals.values
        # The signal belongs to the crossing bar, not the final one.
        assert signals.iloc[-2] == 1

    def test_sell_on_downward_cross(self):
        # Mirror image: a run-up followed by a collapse pushes the short MA
        # back below the long MA.
        prices = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 5, 4, 3, 2]
        strategy = MACrossoverStrategy()
        signals = strategy.generate_signals(
            _frame(prices), {"short_window": 2, "long_window": 4}
        )

        assert -1 in signals.values

    def test_flat_market_produces_no_signals(self):
        # A constant series has short MA == long MA, so nothing triggers.
        prices = [10] * 20
        strategy = MACrossoverStrategy()
        signals = strategy.generate_signals(
            _frame(prices), {"short_window": 3, "long_window": 6}
        )

        assert (signals == 0).all()

    def test_precomputed_sma_columns_are_used(self):
        # When SMA_<window> columns already exist the strategy uses them
        # rather than recomputing from Close: the short MA crosses above the
        # long MA on the 4th bar even though Close never moves.
        data = pd.DataFrame(
            {
                "Close": [10.0] * 5,
                "SMA_2": [8.0, 8.0, 9.0, 12.0, 15.0],
                "SMA_4": [9.0, 9.0, 9.0, 9.0, 9.0],
            }
        )
        strategy = MACrossoverStrategy()
        signals = strategy.generate_signals(data, {"short_window": 2, "long_window": 4})

        assert signals.iloc[3] == 1

    def test_param_schema_declares_both_windows(self):
        schema = MACrossoverStrategy().get_param_schema()
        names = [p["name"] for p in schema]

        assert names == ["short_window", "long_window"]


class TestRSIStrategy:
    def test_buy_when_oversold(self):
        # A persistent downtrend drives RSI to its floor, below the
        # oversold threshold, which must produce a buy.
        prices = [100 - i for i in range(30)]
        strategy = RSIStrategy()
        signals = strategy.generate_signals(
            _frame(prices), {"rsi_period": 14, "oversold_threshold": 30}
        )

        assert 1 in signals.values

    def test_sell_when_overbought(self):
        prices = [100 + i for i in range(30)]
        strategy = RSIStrategy()
        signals = strategy.generate_signals(
            _frame(prices), {"rsi_period": 14, "overbought_threshold": 70}
        )

        assert -1 in signals.values

    def test_neutral_rsi_produces_no_signals(self):
        # Alternating prices keep RSI near 50, between both thresholds.
        prices = [100 + (1 if i % 2 else -1) for i in range(40)]
        strategy = RSIStrategy()
        signals = strategy.generate_signals(
            _frame(prices),
            {"rsi_period": 14, "oversold_threshold": 30, "overbought_threshold": 70},
        )

        assert (signals == 0).all()

    def test_param_schema_declares_period_and_thresholds(self):
        names = [p["name"] for p in RSIStrategy().get_param_schema()]

        assert names == [
            "rsi_period",
            "oversold_threshold",
            "overbought_threshold",
        ]


class TestMACDStrategy:
    def test_buy_on_bullish_cross(self):
        # Sustained rally: MACD line moves above its signal line.
        prices = [100 + i * 2 for i in range(60)]
        strategy = MACDStrategy()
        signals = strategy.generate_signals(_frame(prices), {})

        assert 1 in signals.values

    def test_sell_on_bearish_cross(self):
        prices = [200 - i * 2 for i in range(60)]
        strategy = MACDStrategy()
        signals = strategy.generate_signals(_frame(prices), {})

        assert -1 in signals.values

    def test_supplied_macd_columns_are_used(self):
            data = pd.DataFrame(
                {
                    "Close": [10.0] * 3,
                    "MACD": [-1.0, -1.0, 2.0],
                    "MACD_Signal": [0.0, 0.0, 1.0],
                }
            )
            strategy = MACDStrategy()
            signals = strategy.generate_signals(data, {})

            # MACD crosses above its signal line on the final bar.
            assert signals.iloc[-1] == 1

    def test_param_schema_declares_three_periods(self):
        names = [p["name"] for p in MACDStrategy().get_param_schema()]

        assert names == ["fast_period", "slow_period", "signal_period"]


class TestCombinedStrategy:
    def test_signals_align_with_input_index(self):
        prices = [100 + i for i in range(60)]
        data = _frame(prices)
        signals = CombinedStrategy().generate_signals(data, {})

        assert len(signals) == len(data)

    def test_only_values_in_valid_range(self):
        prices = [100 + (i % 7) for i in range(60)]
        signals = CombinedStrategy().generate_signals(_frame(prices), {})

        assert set(signals.unique()).issubset({-1, 0, 1})

    def test_param_schema_declares_five_params(self):
        names = [p["name"] for p in CombinedStrategy().get_param_schema()]

        assert len(names) == 5


class TestSignalSeriesContract:
    @pytest.mark.parametrize(
        "strategy",
        [
            MACrossoverStrategy(),
            RSIStrategy(),
            MACDStrategy(),
            CombinedStrategy(),
        ],
        ids=["ma", "rsi", "macd", "combined"],
    )
    def test_every_strategy_returns_series_named_signal(self, strategy):
        # The backtest engine keys off the "Signal" name and the -1/0/1 range,
        # so every strategy must honour that contract regardless of config.
        signals = strategy.generate_signals(_frame([10.0] * 60), {})

        assert isinstance(signals, pd.Series)
        assert signals.name == "Signal"
        assert set(signals.unique()).issubset({-1, 0, 1})