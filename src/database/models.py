"""SQLAlchemy models for CRYPTO_ALPHA_SNIPER."""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def utc_now() -> datetime:
    """Returns current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class Token(Base):
    """Represents a discovered crypto token."""
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String(128), unique=True, nullable=False, index=True)
    chain = Column(String(32), nullable=False, index=True)
    symbol = Column(String(32), nullable=True)
    name = Column(String(128), nullable=True)
    pair_address = Column(String(128), nullable=True)
    url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    # Relationships
    market_data = relationship("MarketData", back_populates="token", cascade="all, delete-orphan")
    signals = relationship("Signal", back_populates="token", cascade="all, delete-orphan")
    tracking = relationship("Tracking", back_populates="token", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Token(id={self.id}, address='{self.address}', chain='{self.chain}')>"


class MarketData(Base):
    """Historical and real-time market snapshots."""
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token_id = Column(Integer, ForeignKey("tokens.id", ondelete="CASCADE"), nullable=False, index=True)
    price_usd = Column(Float, nullable=True, default=0.0)
    liquidity_usd = Column(Float, nullable=True, default=0.0)
    volume_h1 = Column(Float, nullable=True, default=0.0)
    market_cap = Column(Float, nullable=True, default=0.0)
    buys_h1 = Column(Integer, nullable=True, default=0)
    sells_h1 = Column(Integer, nullable=True, default=0)
    vpm = Column(Float, nullable=True, default=0.0)
    buy_sell_ratio = Column(Float, nullable=True, default=0.0)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    # Relationship
    token = relationship("Token", back_populates="market_data")

    def __repr__(self) -> str:
        return f"<MarketData(id={self.id}, token_id={self.token_id}, mcap={self.market_cap})>"


class Signal(Base):
    """Generated signals with momentum & risk scores."""
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token_id = Column(Integer, ForeignKey("tokens.id", ondelete="CASCADE"), nullable=False, index=True)
    momentum_score = Column(Integer, nullable=False)
    risk_score = Column(Integer, nullable=False, default=0)
    final_score = Column(Integer, nullable=False)
    signal_tier = Column(String(32), nullable=False, index=True)  # ALPHA, EARLY, WATCHLIST
    age_minutes = Column(Integer, nullable=True, default=0)
    alert_sent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    # Relationship
    token = relationship("Token", back_populates="signals")

    def __repr__(self) -> str:
        return f"<Signal(id={self.id}, tier='{self.signal_tier}', final_score={self.final_score})>"


class Tracking(Base):
    """Tracks ROI / PNL performance of spotted candidate tokens."""
    __tablename__ = "tracking"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token_id = Column(Integer, ForeignKey("tokens.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    entry_market_cap = Column(Float, nullable=False, default=0.0)
    current_market_cap = Column(Float, nullable=True)
    highest_market_cap = Column(Float, nullable=True)
    roi_percent = Column(Float, nullable=True)
    checked = Column(Boolean, default=False, nullable=False, index=True)
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationship
    token = relationship("Token", back_populates="tracking")

    def __repr__(self) -> str:
        return f"<Tracking(id={self.id}, token_id={self.token_id}, roi={self.roi_percent}%)>"
