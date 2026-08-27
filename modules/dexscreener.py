import requests

URL = "https://api.dexscreener.com/token-profiles/latest/v1"


def get_latest_tokens():

    try:

        response = requests.get(
            URL,
            timeout=10
        )

        if response.status_code == 200:
            return response.json()

        print(
            f"[ERROR] DexScreener Status: {response.status_code}"
        )

        return []

    except Exception as e:

        print(
            f"[ERROR] DexScreener: {e}"
        )

        return []


def test_token_address(token):

    print("\n" + "=" * 80)

    print("TOKEN ADDRESS")
    print(token.get("tokenAddress"))

    print("\nCHAIN")
    print(token.get("chainId"))

    print("\nURL")
    print(token.get("url"))

    print("\nDESCRIPTION")
    print(token.get("description"))

    print("=" * 80)