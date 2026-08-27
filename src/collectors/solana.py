"""Solana network validation and address utilities."""

import re

BASE58_REGEX = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,44}$")


class SolanaValidator:
    """Validator for Solana token addresses and pump.fun signatures."""

    @staticmethod
    def is_valid_address(address: str) -> bool:
        """Validates standard Solana Base58 public key format."""
        if not address or not isinstance(address, str):
            return False
        return bool(BASE58_REGEX.match(address))

    @staticmethod
    def is_pump_fun_token(address: str) -> bool:
        """Checks if the token mint was originated by Pump.fun."""
        return address.endswith("pump")
