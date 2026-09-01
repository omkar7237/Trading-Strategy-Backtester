from backtest.engine import BacktestEngine


def test_buy_and_sell():

    engine = BacktestEngine(
        initial_capital=10000,
        commission=0.001,
        slippage=0
    )

    engine.buy(
        "2024-01-01",
        100
    )

    assert engine.position == 100

    engine.sell(
        "2024-01-02",
        110
    )

    assert engine.position == 0

    assert engine.cash == 11000