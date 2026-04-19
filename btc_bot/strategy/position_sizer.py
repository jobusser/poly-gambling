class PositionSizer:
    """Fixed-fraction position sizing, scaled by signal confidence.

    At minimum confidence (threshold) the bet is `bet_fraction * capital`.
    At maximum confidence (1.0) it doubles to `2 * bet_fraction * capital`.
    """

    def __init__(self, bet_fraction: float = 0.02) -> None:
        self.bet_fraction = bet_fraction

    def size(self, capital: float, confidence: float) -> float:
        # confidence in [0.5, 1.0] → scale in [1.0, 2.0]
        scale = 1.0 + (confidence - 0.5) * 2.0
        return capital * self.bet_fraction * scale
