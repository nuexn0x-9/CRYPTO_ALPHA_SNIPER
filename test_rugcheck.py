import json

from modules.rugcheck import (
    check_token
)

result = check_token(
    "solana",
    "7Fs1F5u9y8mFWRhRqntbpyYTeiwotAgU3wxUCnTHpump"
)

print(
    json.dumps(
        result,
        indent=4
    )
)