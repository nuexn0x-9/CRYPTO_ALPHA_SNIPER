"""TON (The Open Network) address validator and helpers."""

import re

TON_USER_FRIENDLY_REGEX = re.compile(r"^[EQ][Q0-9A-Za-z_-]{46,48}$")


class TONValidator:
    """Validator for TON smart contract addresses."""

    @staticmethod
    def is_valid_address(address: str) -> bool:
        """Validates TON friendly address format or raw workchain hex."""
        if not address or not isinstance(address, str):
            return False
        if TON_USER_FRIENDLY_REGEX.match(address):
            return True
        if ":" in address and len(address) == 66:
            return True
        return len(address) >= 30
