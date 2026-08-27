from modules.tracker import (
    load_candidates,
    save_all_candidates
)

from modules.pair_analyzer import (
    get_pair_data
)

print("=" * 50)
print("TRACKER WORKER")
print("=" * 50)

data = load_candidates()

updated = 0

for item in data:

    if item.get("checked"):
        continue

    token_address = item.get(
        "token_address"
    )

    pair = get_pair_data(
        token_address
    )

    if not pair:
        continue

    current_mcap = pair.get(
        "marketCap",
        0
    )

    original_mcap = item.get(
        "mcap",
        0
    )

    if original_mcap <= 0:
        continue

    pnl = (
        (
            current_mcap
            - original_mcap
        )
        / original_mcap
    ) * 100

    item["current_mcap"] = current_mcap

    item["return_percent"] = round(
        pnl,
        2
    )

    item["checked"] = True

    updated += 1

    print(
        f"{token_address[:12]} "
        f"=> {round(pnl,2)}%"
    )

save_all_candidates(data)

print(
    f"\nUpdated: {updated}"
)