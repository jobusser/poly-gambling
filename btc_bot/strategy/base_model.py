from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

import pandas as pd


class Direction(Enum):
    UP = "UP"
    DOWN = "DOWN"


@dataclass
class Signal:
    direction: Direction
    confidence: float  # 0.5 = coin flip, 1.0 = certain


class BaseModel(ABC):
    """All prediction strategies implement this interface.

    predict() receives the full candle history available at decision time
    and returns a Signal. Strategies must not peek at future candles.
    """

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def predict(self, df: pd.DataFrame) -> Signal: ...
