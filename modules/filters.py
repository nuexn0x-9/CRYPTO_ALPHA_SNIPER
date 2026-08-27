SUPPORTED_CHAINS = [
    "solana",
    "bsc",
    "ton"
]


def is_supported_chain(token):

    chain = token.get(
        "chainId",
        ""
    ).lower()

    return chain in SUPPORTED_CHAINS


def passes_basic_filter(token):

    return is_supported_chain(
        token
    )