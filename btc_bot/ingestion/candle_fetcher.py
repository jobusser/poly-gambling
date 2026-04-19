from datetime import datetime, timedelta, timezone

import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session

from btc_bot.storage.models import Candle


def _to_naive_utc(ts) -> datetime:
    if isinstance(ts, pd.Timestamp):
        ts = ts.to_pydatetime()
    if hasattr(ts, "tzinfo") and ts.tzinfo is not None:
        ts = ts.replace(tzinfo=None)
    return ts


def _download(symbol: str, interval: str, lookback_days: int) -> pd.DataFrame:
    df = yf.download(
        tickers=symbol,
        interval=interval,
        period=f"{lookback_days}d",
        progress=False,
        auto_adjust=True,
    )
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    df = df.rename(columns=str.lower)
    df = df[["open", "high", "low", "close", "volume"]].dropna()
    return df


def fetch_and_store(
    session: Session, symbol: str, interval: str, lookback_days: int
) -> pd.DataFrame:
    """Download candles from yfinance and upsert new rows into the DB."""
    df = _download(symbol, interval, lookback_days)

    existing_ts = set(
        row.timestamp
        for row in session.query(Candle.timestamp).filter(
            Candle.symbol == symbol, Candle.interval == interval
        )
    )

    new_rows = [
        Candle(
            symbol=symbol,
            interval=interval,
            timestamp=_to_naive_utc(ts),
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row["volume"]),
        )
        for ts, row in df.iterrows()
        if _to_naive_utc(ts) not in existing_ts
    ]
    session.add_all(new_rows)
    session.commit()
    return df


def load_from_db(
    session: Session,
    symbol: str,
    interval: str,
    start: datetime | None = None,
    end: datetime | None = None,
) -> pd.DataFrame:
    """Load candles from the DB as a DataFrame indexed by timestamp."""
    q = session.query(Candle).filter(
        Candle.symbol == symbol, Candle.interval == interval
    )
    if start:
        q = q.filter(Candle.timestamp >= start)
    if end:
        q = q.filter(Candle.timestamp <= end)

    rows = q.order_by(Candle.timestamp).all()
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(
        [
            {
                "timestamp": r.timestamp,
                "open": r.open,
                "high": r.high,
                "low": r.low,
                "close": r.close,
                "volume": r.volume,
            }
            for r in rows
        ]
    ).set_index("timestamp")
    return df


def get_or_fetch(
    session: Session, symbol: str, interval: str, lookback_days: int
) -> pd.DataFrame:
    """Return DB candles if fresh enough, otherwise re-fetch from yfinance."""
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=lookback_days)
    df = load_from_db(session, symbol, interval, start=cutoff)
    if df.empty:
        df = fetch_and_store(session, symbol, interval, lookback_days)
    return df
