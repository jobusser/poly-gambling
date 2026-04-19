from dataclasses import dataclass
from enum import Enum

from btc_bot.strategy.base_model import Direction, Signal


class Action(Enum):
    TRADE = "TRADE"
    SKIP = "SKIP"


@dataclass
class TradeDecision:
    action: Action
    direction: Direction
    confidence: float


class SignalGenerator:
    """Converts a raw model Signal into a trade/skip decision."""

    def __init__(self, confidence_threshold: float = 0.55) -> None:
        self.confidence_threshold = confidence_threshold

    def evaluate(self, signal: Signal) -> TradeDecision:
        action = (
            Action.TRADE
            if signal.confidence >= self.confidence_threshold
            else Action.SKIP
        )
        return TradeDecision(
            action=action,
            direction=signal.direction,
            confidence=signal.confidence,
        )
