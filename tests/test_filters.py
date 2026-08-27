"""Unit tests for chain validators and filters."""

from src.collectors.bsc import BSCValidator
from src.collectors.solana import SolanaValidator
from src.collectors.ton import TONValidator
from src.config.settings import Settings


def test_solana_validator():
    """Tests Solana address validation and pump.fun suffix detection."""
    valid_sol = "6BeyohhmEkxxBsKsne2rLUjkVpx1uQ1jw4KVB9uTpump"
    invalid_sol = "0xInvalidSolanaAddress"

    assert SolanaValidator.is_valid_address(valid_sol) is True
    assert SolanaValidator.is_pump_fun_token(valid_sol) is True
    assert SolanaValidator.is_valid_address(invalid_sol) is False


def test_bsc_validator():
    """Tests BSC EVM address validation."""
    valid_bsc = "0x4d54Aac033F43D6D456182fc2c493b239bC7fffF"
    invalid_bsc = "InvalidBSCAddress"

    assert BSCValidator.is_valid_address(valid_bsc) is True
    assert BSCValidator.is_valid_address(invalid_bsc) is False


def test_ton_validator():
    """Tests TON address validation."""
    valid_ton = "EQBvW8m5e6Z8r6gK2h-SampleTONAddress11111111111"
    assert TONValidator.is_valid_address(valid_ton) is True
    assert TONValidator.is_valid_address("") is False


def test_supported_chains_settings():
    """Tests chain normalization in Settings."""
    settings = Settings(SUPPORTED_CHAINS="Solana, BSC, ton, Base ")
    assert "solana" in settings.supported_chains_set
    assert "bsc" in settings.supported_chains_set
    assert "ton" in settings.supported_chains_set
    assert "base" in settings.supported_chains_set
