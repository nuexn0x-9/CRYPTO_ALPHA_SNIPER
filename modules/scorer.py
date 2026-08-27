from datetime import datetime


def calculate_score(token, pair):

    score = 0

    created = pair.get(
        "pairCreatedAt"
    )

    age_minutes = 9999

    if created:

        age_minutes = (
            datetime.now().timestamp()
            - (created / 1000)
        ) / 60

    volume = (
        pair.get("volume", {})
        .get("h1", 0)
    )

    liquidity = (
        pair.get("liquidity", {})
        .get("usd", 0)
    )

    market_cap = pair.get(
        "marketCap",
        0
    )

    buys = (
        pair.get("txns", {})
        .get("h1", {})
        .get("buys", 0)
    )

    sells = (
        pair.get("txns", {})
        .get("h1", {})
        .get("sells", 0)
    )

    effective_age = max(
        age_minutes,
        1
    )

    volume_per_minute = (
        volume / effective_age
    )

    ratio = 0

    if sells > 0:

        ratio = buys / sells

    elif buys > 0:

        ratio = buys

    # =====================
    # AGE
    # =====================

    if age_minutes <= 10:

        score += 25

    elif age_minutes <= 30:

        score += 20

    elif age_minutes <= 60:

        score += 10

    # =====================
    # VOLUME
    # =====================

    if volume >= 100000:

        score += 20

    elif volume >= 50000:

        score += 15

    elif volume >= 20000:

        score += 10

    # =====================
    # MOMENTUM
    # =====================

    if volume_per_minute >= 5000:

        score += 30

    elif volume_per_minute >= 3000:

        score += 25

    elif volume_per_minute >= 2000:

        score += 20

    elif volume_per_minute >= 1000:

        score += 10

    # =====================
    # BUY PRESSURE
    # =====================

    if ratio >= 2:

        score += 20

    elif ratio >= 1.5:

        score += 15

    elif ratio >= 1.2:

        score += 10

    # =====================
    # LIQUIDITY BONUS
    # =====================

    if liquidity >= 20000:

        score += 10

    elif liquidity >= 10000:

        score += 5

    # =====================
    # SOCIAL BONUS
    # =====================

    links = token.get(
        "links",
        []
    )

    if len(links) >= 2:

        score += 5

    return {
        "score": score,
        "volume": volume,
        "liquidity": liquidity,
        "market_cap": market_cap,
        "buys": buys,
        "sells": sells,
        "ratio": round(
            ratio,
            2
        ),
        "volume_per_minute": round(
            volume_per_minute,
            2
        ),
        "age_minutes": int(
            age_minutes
        )
    }