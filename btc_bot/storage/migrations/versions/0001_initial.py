"""Initial schema: candles, predictions, trades, portfolio_snapshots

Revision ID: 0001
Revises:
Create Date: 2026-04-19
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "candles",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("symbol", sa.String, nullable=False),
        sa.Column("interval", sa.String, nullable=False),
        sa.Column("timestamp", sa.DateTime, nullable=False),
        sa.Column("open", sa.Float, nullable=False),
        sa.Column("high", sa.Float, nullable=False),
        sa.Column("low", sa.Float, nullable=False),
        sa.Column("close", sa.Float, nullable=False),
        sa.Column("volume", sa.Float, nullable=False),
        sa.UniqueConstraint("symbol", "interval", "timestamp"),
    )

    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("strategy", sa.String, nullable=False),
        sa.Column("candle_timestamp", sa.DateTime, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("direction", sa.String, nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
    )

    op.create_table(
        "trades",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("strategy", sa.String, nullable=False),
        sa.Column("opened_at", sa.DateTime, nullable=False),
        sa.Column("closed_at", sa.DateTime, nullable=True),
        sa.Column("direction", sa.String, nullable=False),
        sa.Column("entry_price", sa.Float, nullable=False),
        sa.Column("exit_price", sa.Float, nullable=True),
        sa.Column("bet_size", sa.Float, nullable=False),
        sa.Column("pnl", sa.Float, nullable=True),
        sa.Column("outcome", sa.String, nullable=True),
    )

    op.create_table(
        "portfolio_snapshots",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("strategy", sa.String, nullable=False),
        sa.Column("timestamp", sa.DateTime, nullable=False),
        sa.Column("cash", sa.Float, nullable=False),
        sa.Column("total_pnl", sa.Float, nullable=False),
        sa.Column("trade_count", sa.Integer, nullable=False),
        sa.Column("win_count", sa.Integer, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("portfolio_snapshots")
    op.drop_table("trades")
    op.drop_table("predictions")
    op.drop_table("candles")
