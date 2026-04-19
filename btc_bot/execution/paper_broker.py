from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd

from btc_bot.storage.models import PortfolioSnapshot, Trade
from btc_bot.strategy.base_model import Direction
from btc_bot.strategy.signal_generator import TradeDecision
from sqlalchemy.orm import Session


def _to_naive_utc(ts) -> datetime:
    """Convert pandas Timestamp or datetime to a timezone-naive UTC datetime."""
    if isinstance(ts, pd.Timestamp):
        ts = ts.to_pydatetime()
    if hasattr(ts, "tzinfo") and ts.tzinfo is not None:
        ts = ts.replace(tzinfo=None)
    return ts


@dataclass
class Portfolio:
    strategy: str
    cash: float
    trades: list = field(default_factory=list)

    @property
    def total_pnl(self) -> float:
        return sum(t.pnl for t in self.trades if t.pnl is not None)

    @property
    def win_count(self) -> int:
        return sum(1 for t in self.trades if t.outcome == "WIN")

    @property
    def trade_count(self) -> int:
        return sum(1 for t in self.trades if t.outcome is not None)


class PaperBroker:
    """Simulates Polymarket-style binary prediction trades.

    Each call to execute() places a bet on the outcome of the next 15m candle.
    Payout is `bet_size * payout_multiplier` on a WIN, -`bet_size` on a LOSS,
    minus the fee both ways.
    """

    def __init__(
        self,
        strategy: str,
        initial_capital: float,
        fee_rate: float,
        payout_multiplier: float,
        bet_fraction: float,
        session: Session,
    ) -> None:
        self.portfolio = Portfolio(strategy=strategy, cash=initial_capital)
        self.fee_rate = fee_rate
        self.payout_multiplier = payout_multiplier
        self.bet_fraction = bet_fraction
        self.session = session

    def execute(
        self,
        decision: TradeDecision,
        current: pd.Series,
        next_candle: pd.Series,
        bet_size: float,
    ) -> Trade:
        price_went_up = float(next_candle["close"]) > float(current["close"])
        predicted_up = decision.direction == Direction.UP
        correct = price_went_up == predicted_up

        fee = bet_size * self.fee_rate
        if correct:
            pnl = bet_size * (self.payout_multiplier - 1) - fee
            outcome = "WIN"
        else:
            pnl = -bet_size - fee
            outcome = "LOSS"

        self.portfolio.cash += pnl

        trade = Trade(
            strategy=self.portfolio.strategy,
            opened_at=_to_naive_utc(current.name),
            closed_at=_to_naive_utc(next_candle.name),
            direction=decision.direction.value,
            entry_price=float(current["close"]),
            exit_price=float(next_candle["close"]),
            bet_size=bet_size,
            pnl=pnl,
            outcome=outcome,
        )
        self.portfolio.trades.append(trade)
        self.session.add(trade)
        return trade

    def snapshot(self, timestamp: datetime) -> PortfolioSnapshot:
        snap = PortfolioSnapshot(
            strategy=self.portfolio.strategy,
            timestamp=_to_naive_utc(timestamp),
            cash=self.portfolio.cash,
            total_pnl=self.portfolio.total_pnl,
            trade_count=self.portfolio.trade_count,
            win_count=self.portfolio.win_count,
        )
        self.session.add(snap)
        return snap
