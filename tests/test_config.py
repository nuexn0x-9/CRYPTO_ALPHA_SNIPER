"""Unit tests for Settings and environment variable validation."""

import pytest
from pydantic import ValidationError

from src.config.settings import Settings


def test_settings_defaults():
    """Verifies that default settings load with expected valid parameters."""
    settings = Settings(
        TELEGRAM_BOT_TOKEN="mock_token",
        TELEGRAM_CHAT_ID="12345678",
        _env_file=None,
    )
    assert settings.SCAN_INTERVAL_SECONDS == 60
    assert settings.MAX_AGE_MINUTES == 60
    assert settings.MIN_VOLUME_USD == 1000.0
    assert settings.has_telegram is True
    assert "solana" in settings.supported_chains_set


def test_settings_missing_telegram():
    """Verifies has_telegram returns False when tokens are missing."""
    settings = Settings(
        TELEGRAM_BOT_TOKEN="",
        TELEGRAM_CHAT_ID="",
        _env_file=None,
    )
    assert settings.has_telegram is False


def test_settings_invalid_range_validation():
    """Verifies that out-of-range parameters raise validation errors."""
    with pytest.raises(ValidationError):
        # SCAN_INTERVAL_SECONDS must be >= 5
        Settings(SCAN_INTERVAL_SECONDS=2, _env_file=None)

    with pytest.raises(ValidationError):
        # WATCHLIST_SCORE must be <= 100
        Settings(WATCHLIST_SCORE=150, _env_file=None)
