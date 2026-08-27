"""Configuration management using pydantic-settings."""

from functools import lru_cache
from typing import Set

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Telegram Notification Settings
    TELEGRAM_BOT_TOKEN: str = Field(default="", description="Telegram Bot API Token")
    TELEGRAM_CHAT_ID: str = Field(default="", description="Target Telegram Chat / Channel ID")

    # Database Settings
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///data/crypto_alpha_sniper.db",
        description="SQLAlchemy async connection URI"
    )

    # API Endpoints
    DEXSCREENER_API_BASE: str = Field(
        default="https://api.dexscreener.com",
        description="DexScreener API Base URL"
    )
    RUGCHECK_API_BASE: str = Field(
        default="https://api.rugcheck.xyz/v1",
        description="RugCheck API Base URL"
    )

    # Scanner Engine Parameters
    SCAN_INTERVAL_SECONDS: int = Field(default=60, ge=5, le=3600)
    MAX_AGE_MINUTES: int = Field(default=60, ge=1, le=1440)
    MIN_VOLUME_USD: float = Field(default=1000.0, ge=0.0)
    MIN_MARKET_CAP_USD: float = Field(default=1000.0, ge=0.0)
    SUPPORTED_CHAINS: str = Field(default="solana,bsc,ton")
    CONCURRENCY_LIMIT: int = Field(default=10, ge=1, le=50)

    # Scoring Thresholds
    WATCHLIST_SCORE: int = Field(default=40, ge=0, le=100)
    EARLY_SIGNAL_SCORE: int = Field(default=55, ge=0, le=100)
    ALPHA_SIGNAL_SCORE: int = Field(default=70, ge=0, le=100)
    MAX_ALLOWED_RISK_SCORE: int = Field(default=65, ge=0, le=100)

    # Tracker Settings
    TRACKER_INTERVAL_SECONDS: int = Field(default=120, ge=10)
    TRACKER_MAX_BATCH_SIZE: int = Field(default=25, ge=1, le=100)

    # Database Retention & Auto-Cleanup Settings
    DATA_RETENTION_DAYS: int = Field(default=7, ge=1, le=365, description="Days to retain historical records before auto-cleanup")
    AUTO_CLEANUP_ENABLED: bool = Field(default=True, description="Enable automatic periodic purging of old tokens")

    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE_PATH: str = Field(default="logs/crypto_alpha_sniper.log")
    LOG_ROTATION: str = Field(default="10 MB")
    LOG_RETENTION: str = Field(default="14 days")

    @property
    def supported_chains_set(self) -> Set[str]:
        """Returns normalized set of supported chain names."""
        return {chain.strip().lower() for chain in self.SUPPORTED_CHAINS.split(",") if chain.strip()}

    @property
    def has_telegram(self) -> bool:
        """Checks whether Telegram alerts are enabled."""
        return bool(self.TELEGRAM_BOT_TOKEN and self.TELEGRAM_CHAT_ID)


@lru_cache()
def get_settings() -> Settings:
    """Returns cached instance of validated Settings."""
    return Settings()
