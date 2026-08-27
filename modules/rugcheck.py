import requests


def check_token(chain, token_address):

    if chain.lower() != "solana":

        return {
            "score": 50,
            "status": "UNKNOWN"
        }

    url = (
        f"https://api.rugcheck.xyz/v1/tokens/"
        f"{token_address}/report"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code != 200:

            return {
                "score": 0,
                "status": "ERROR"
            }

        data = response.json()

        return {
            "score": data.get(
                "score",
                0
            ),
            "status": "OK"
        }

    except Exception:

        return {
            "score": 0,
            "status": "ERROR"
        }