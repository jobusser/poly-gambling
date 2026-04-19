import random
import pandas as pd

from btc_bot.strategy.base_model import BaseModel, Direction, Signal


class RandomModel(BaseModel):
    """Baseline strategy: random direction, random confidence."""

    name = "random"

    def predict(self, _df: pd.DataFrame) -> Signal:
        return Signal(
            direction=random.choice([Direction.UP, Direction.DOWN]),
            confidence=random.uniform(0.5, 1.0),
        )
