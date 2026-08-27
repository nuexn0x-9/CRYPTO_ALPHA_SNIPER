"""Live API test for Telegram alert service."""

import os

import pytest

from src.services.telegram import TelegramService

LIVE_ENABLED = os.getenv("ENABLE_LIVE_TEST", "false").lower() == "true"


@pytest.mark.skipif(not LIVE_ENABLED, reason="Live external API tests disabled by default. Set ENABLE_LIVE_TEST=true to run.")
@pytest.mark.asyncio
async def test_live_telegram_send():
    """Attempts to send a live test message if credentials are set in environment."""
    service = TelegramService()
    if service.settings.has_telegram:
        result = await service.send_message("🧪 <b>CRYPTO_ALPHA_SNIPER</b> - Live Test Verification")
        assert result is True
    await service.close()
