import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SCAN_INTERVAL = int(
    os.getenv("SCAN_INTERVAL_SECONDS", 60)
)

# ==================================
# ALPHA SNIPER V2.1
# ==================================

MAX_AGE_MINUTES = 60

MIN_VOLUME = 1000

MIN_MARKET_CAP = 1000

WATCHLIST_SCORE = 40

EARLY_SIGNAL_SCORE = 55

ALPHA_SIGNAL_SCORE = 70