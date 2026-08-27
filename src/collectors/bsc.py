"""BSC (BNB Smart Chain) address validator and helpers."""

import re

ETH_ADDRESS_REGEX = re.compile(r"^0x[a-fA-F0-9]{40}$")


class BSCValidator:
    """Validator for BSC EVM token addresses."""

    @staticmethod
    def is_valid_address(address: str) -> bool:
        """Validates EVM 20-byte hex address."""
        if not address or not isinstance(address, str):
            return False
        return bool(ETH_ADDRESS_REGEX.match(address))
