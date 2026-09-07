import pandas as pd

from strategy.base_strategy import Strategy


class MovingAverageStrategy(Strategy):

    def __init__(
        self,
        short_window=20,
        long_window=50
    ):

        self.short_window = short_window

        self.long_window = long_window


    def generate_signals(self, data):

        signals = pd.Series(
            0,
            index=data.index
        )

        signals[
            data["SMA_20"]
            >
            data["SMA_50"]
        ] = 1

        signals[
            data["SMA_20"]
            <
            data["SMA_50"]
        ] = -1

        return signals