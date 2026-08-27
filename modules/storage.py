import json
import os

FILE_PATH = "data/processed_tokens.json"


def load_tokens():

    if not os.path.exists(FILE_PATH):
        return set()

    try:

        with open(FILE_PATH, "r") as f:
            data = json.load(f)

        return set(data)

    except:
        return set()


def save_tokens(tokens):

    with open(FILE_PATH, "w") as f:
        json.dump(
            list(tokens),
            f,
            indent=4
        )