import time
from datetime import datetime

from config import (
    SCAN_INTERVAL,
    MAX_AGE_MINUTES,
    MIN_VOLUME,
    MIN_MARKET_CAP,
    WATCHLIST_SCORE,
    EARLY_SIGNAL_SCORE,
    ALPHA_SIGNAL_SCORE
)

from modules.dexscreener import (
    get_latest_tokens
)

from modules.filters import (
    passes_basic_filter
)

from modules.storage import (
    load_tokens,
    save_tokens
)

from modules.telegram import (
    send_message
)

from modules.pair_analyzer import (
    get_pair_data
)

from modules.scorer import (
    calculate_score
)

from modules.tracker import (
    save_candidate,
    create_candidate_record
)

processed_tokens = load_tokens()

print("=" * 60)
print("ALPHA SNIPER V3.0 MOMENTUM HUNTER")
print("=" * 60)

while True:

    print(
        f"\n[{datetime.now().strftime('%H:%M:%S')}] SCANNING..."
    )

    tokens = get_latest_tokens()

    if not tokens:

        print("[INFO] No data")

        time.sleep(
            SCAN_INTERVAL
        )

        continue

    candidate_count = 0

    for token in tokens:

        if not passes_basic_filter(token):

            print(
                "[FILTER] BASIC"
            )

            continue

        token_address = token.get(
            "tokenAddress"
        )

        if not token_address:
            continue

        if token_address in processed_tokens:
            continue

        pair = get_pair_data(
            token_address
        )

        if not pair:

            print(
                "[FILTER] NO PAIR"
            )

            continue

        pair_address = pair.get(
            "pairAddress",
            "-"
        )

        url = pair.get(
            "url",
            "-"
        )

        result = calculate_score(
            token,
            pair
        )

        print(
            f"AGE={result['age_minutes']} | "
            f"VOL={int(result['volume'])} | "
            f"VPM={result['volume_per_minute']} | "
            f"LP={int(result['liquidity'])} | "
            f"MCAP={int(result['market_cap'])} | "
            f"RATIO={result['ratio']}"
        )

        age = result[
            "age_minutes"
        ]

        volume = result[
            "volume"
        ]

        market_cap = result[
            "market_cap"
        ]

        if age > MAX_AGE_MINUTES:

            print(
                f"[FILTER] AGE {age}"
            )

            continue

        if volume < MIN_VOLUME:

            print(
                f"[FILTER] VOL {volume}"
            )

            continue

        if market_cap < MIN_MARKET_CAP:

            print(
                f"[FILTER] MCAP {market_cap}"
            )

            continue

        score = result[
            "score"
        ]

        print(
            f"[CHECK] "
            f"ALPHA={score}"
        )

        signal = None

        if score >= ALPHA_SIGNAL_SCORE:

            signal = (
                "🔥 ALPHA SIGNAL"
            )

        elif score >= EARLY_SIGNAL_SCORE:

            signal = (
                "🚀 EARLY SIGNAL"
            )

        elif score >= WATCHLIST_SCORE:

            signal = (
                "👀 WATCHLIST"
            )

        else:

            print(
                f"[FILTER] SCORE {score}"
            )

            continue

        candidate_count += 1

        candidate = (
            create_candidate_record(
                token_address=token_address,
                chain=token.get(
                    "chainId",
                    "unknown"
                ),
                score=score,
                age=age,
                volume=volume,
                vpm=result[
                    "volume_per_minute"
                ],
                mcap=market_cap
            )
        )

        save_candidate(
            candidate
        )

        chain = token.get(
            "chainId",
            "unknown"
        )

        message = (
            f"{signal}\n\n"

            f"⛓️ Chain : "
            f"{chain.upper()}\n"

            f"⭐ Alpha Score : "
            f"{score}/100\n\n"

            f"⏳ Age : "
            f"{age} menit\n"

            f"📊 Volume : "
            f"${int(volume)}\n"

            f"⚡ VPM : "
            f"{result['volume_per_minute']}\n"

            f"📈 Ratio : "
            f"{result['ratio']}\n"

            f"💧 LP : "
            f"${int(result['liquidity'])}\n"

            f"💰 MCAP : "
            f"${int(market_cap)}\n"

            f"🟢 Buys : "
            f"{result['buys']}\n"

            f"🔴 Sells : "
            f"{result['sells']}\n\n"

            f"🏦 Pair :\n"
            f"{pair_address}\n\n"

            f"📍 CA :\n"
            f"{token_address}\n\n"

            f"🔗 {url}"
        )

        send_message(
            message
        )

        processed_tokens.add(
            token_address
        )

    save_tokens(
        processed_tokens
    )

    print(
        f"[INFO] Candidate: "
        f"{candidate_count}"
    )

    time.sleep(
        SCAN_INTERVAL
    )