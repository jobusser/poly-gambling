from sqlalchemy.orm import Session

from btc_bot.storage.models import Trade


class PerformanceTracker:
    """Reads resolved trades from the DB and computes summary statistics."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_summary(self, strategy: str) -> dict:
        trades = (
            self.session.query(Trade)
            .filter(Trade.strategy == strategy, Trade.outcome.isnot(None))
            .all()
        )

        if not trades:
            return {"strategy": strategy, "trades": 0}

        wins = [t for t in trades if t.outcome == "WIN"]
        total_pnl = sum(t.pnl for t in trades)
        win_rate = len(wins) / len(trades)

        return {
            "strategy": strategy,
            "trades": len(trades),
            "wins": len(wins),
            "losses": len(trades) - len(wins),
            "win_rate": round(win_rate, 4),
            "total_pnl": round(total_pnl, 2),
            "avg_pnl": round(total_pnl / len(trades), 2),
        }

    def print_summary(self, strategy: str) -> None:
        s = self.get_summary(strategy)
        print(f"\n{'=' * 40}")
        print(f"  {s['strategy']}")
        print(f"{'=' * 40}")
        print(f"  Trades     : {s.get('trades', 0)}")
        print(f"  Win Rate   : {s.get('win_rate', 0):.1%}")
        print(f"  Total P&L  : ${s.get('total_pnl', 0):,.2f}")
        print(f"  Avg P&L    : ${s.get('avg_pnl', 0):.2f}")
