from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Candle(Base):
    __tablename__ = "candles"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    interval = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint("symbol", "interval", "timestamp"),)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    strategy = Column(String, nullable=False)
    candle_timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    direction = Column(String, nullable=False)   # UP | DOWN
    confidence = Column(Float, nullable=False)


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    strategy = Column(String, nullable=False)
    opened_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    direction = Column(String, nullable=False)   # UP | DOWN
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    bet_size = Column(Float, nullable=False)
    pnl = Column(Float, nullable=True)
    outcome = Column(String, nullable=True)      # WIN | LOSS


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(Integer, primary_key=True)
    strategy = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    cash = Column(Float, nullable=False)
    total_pnl = Column(Float, nullable=False)
    trade_count = Column(Integer, nullable=False)
    win_count = Column(Integer, nullable=False)
