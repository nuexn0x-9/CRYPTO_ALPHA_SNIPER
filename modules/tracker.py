import json
import os
from datetime import datetime

FILE_PATH = "data/candidates.json"


def load_candidates():

    if not os.path.exists(FILE_PATH):
        return []

    try:

        with open(
            FILE_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return []


def save_all_candidates(data):

    with open(
        FILE_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2
        )


def save_candidate(candidate):

    data = load_candidates()

    data.append(candidate)

    save_all_candidates(data)


def create_candidate_record(
    token_address,
    chain,
    score,
    age,
    volume,
    vpm,
    mcap
):

    return {
        "token_address": token_address,
        "chain": chain,
        "score": score,
        "age": age,
        "volume": volume,
        "vpm": vpm,
        "mcap": mcap,
        "found_at": datetime.utcnow().isoformat(),
        "checked": False,
        "current_mcap": None,
        "return_percent": None
    }