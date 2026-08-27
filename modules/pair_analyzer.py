import requests


def get_pair_data(token_address):

    url = (
        f"https://api.dexscreener.com/"
        f"latest/dex/tokens/{token_address}"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()

        pairs = data.get(
            "pairs",
            []
        )

        if not pairs:
            return None

        # ==================================
        # PILIH PAIR TERBAIK
        # berdasarkan volume + liquidity
        # ==================================

        best_pair = None
        best_score = 0

        for pair in pairs:

            volume = (
                pair.get("volume", {})
                .get("h1", 0)
            )

            liquidity = (
                pair.get("liquidity", {})
                .get("usd", 0)
            )

            score = (
                volume +
                liquidity
            )

            if score > best_score:

                best_score = score

                best_pair = pair

        return best_pair

    except Exception as e:

        print(
            f"[PAIR ERROR] {e}"
        )

        return None