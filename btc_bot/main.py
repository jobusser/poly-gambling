"""
Entry point for running a BTC 15m up/down paper-trading backtest.

Usage:
    python -m btc_bot.main           # uses settings.yaml env (default: dev)
    python -m btc_bot.main --env sim # run against the sim database
"""

import argparse
from datetime import datetime, timezone

import yaml
from pathlib import Path

from btc_bot.storage.database import get_session, setup_db
from btc_bot.ingestion import candle_fetcher
from btc_bot.strategy.random_model import RandomModel
from btc_bot.strategy.moving_average import MovingAverageModel
from btc_bot.strategy.signal_generator import Action, SignalGenerator
from btc_bot.strategy.position_sizer import PositionSizer
from btc_bot.execution.paper_broker import PaperBroker
from btc_bot.execution.performance import PerformanceTracker


def load_config() -> dict:
    path = Path(__file__).parent / "config" / "settings.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def run_backtest(env: str | None = None) -> None:
    config = load_config()
    env = env or config["database"]["env"]

    setup_db(env)
    session = get_session(env)

    print(f"[btc_bot] fetching candles (env={env})...")
    df = candle_fetcher.get_or_fetch(
        session=session,
        symbol=config["data"]["symbol"],
        interval=config["data"]["interval"],
        lookback_days=config["data"]["lookback_days"],
    )
    print(f"[btc_bot] {len(df)} candles loaded")

    strategies = [
        RandomModel(),
        MovingAverageModel(**config["strategy"]["moving_average"]),
    ]

    broker_cfg = config["broker"]
    sig_cfg = config["strategy"]["signal"]

    for model in strategies:
        print(f"\n[btc_bot] running strategy: {model.name}")
        session_s = get_session(env)

        broker = PaperBroker(
            strategy=model.name,
            initial_capital=broker_cfg["initial_capital"],
            fee_rate=broker_cfg["fee_rate"],
            payout_multiplier=broker_cfg["payout_multiplier"],
            bet_fraction=broker_cfg["bet_fraction"],
            session=session_s,
        )
        signal_gen = SignalGenerator(sig_cfg["confidence_threshold"])
        sizer = PositionSizer(broker_cfg["bet_fraction"])

        for i in range(len(df) - 1):
            current = df.iloc[i]
            next_candle = df.iloc[i + 1]
            history = df.iloc[: i + 1]

            signal = model.predict(history)
            decision = signal_gen.evaluate(signal)

            if decision.action == Action.TRADE:
                bet_size = sizer.size(broker.portfolio.cash, decision.confidence)
                broker.execute(decision, current, next_candle, bet_size)

        broker.snapshot(datetime.now(timezone.utc).replace(tzinfo=None))
        session_s.commit()

        tracker = PerformanceTracker(session_s)
        tracker.print_summary(model.name)
        session_s.close()

    session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default=None, help="Database environment: dev|test|sim")
    args = parser.parse_args()
    run_backtest(args.env)
