import pandas as pd

from btc_bot.strategy.base_model import BaseModel, Direction, Signal


class MovingAverageModel(BaseModel):
    """Simple dual-MA crossover: short MA above long MA → UP, else DOWN.

    Confidence scales with the relative gap between the two MAs.
    Returns confidence=0.5 (abstain) when insufficient history.
    """

    name = "moving_average"

    def __init__(self, short_window: int = 5, long_window: int = 20) -> None:
        self.short_window = short_window
        self.long_window = long_window

    def predict(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.long_window:
            return Signal(direction=Direction.UP, confidence=0.5)

        close = df["close"]
        short_ma = close.iloc[-self.short_window :].mean()
        long_ma = close.iloc[-self.long_window :].mean()

        direction = Direction.UP if short_ma >= long_ma else Direction.DOWN
        # Map relative deviation to a (0.5, 0.95) confidence range
        rel_gap = abs(short_ma - long_ma) / long_ma
        confidence = min(0.5 + rel_gap * 5, 0.95)

        return Signal(direction=direction, confidence=confidence)
