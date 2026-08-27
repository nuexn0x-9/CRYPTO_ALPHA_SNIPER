# Telegram Alert Integration Guide

**CRYPTO_ALPHA_SNIPER** features an asynchronous Telegram notification service (`src/services/telegram.py`) that broadcasts high-priority alpha signals, momentum breakdowns, and safety indicators directly to your private chat, group, or channel.

---

## 🛠️ Step-by-Step Setup

### Step 1: Create a Telegram Bot
1. Open Telegram and search for [@BotFather](https://t.me/BotFather).
2. Send the command: `/newbot`.
3. Choose a display name (e.g., `My Alpha Sniper Bot`).
4. Choose a unique username ending in `bot` (e.g., `my_alpha_sniper_alert_bot`).
5. **Copy the HTTP API Token** provided by BotFather (format: `1234567890:ABCdefGhIJKlmNoPQRstuvWxyz`).

---

### Step 2: Retrieve Your Telegram Chat ID

#### Option A: For Private Messages (Direct to You)
1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot) or [@IDBot](https://t.me/myidbot).
2. Start the bot to obtain your numeric `Id` (e.g., `5009408813`).
3. Send `/start` to your newly created bot from Step 1 so it has permission to message you.

#### Option B: For Telegram Channels / Groups
1. Create a Telegram Channel or Group.
2. Add your bot as an **Administrator** with permission to **Post Messages**.
3. Forward a message from your channel to [@userinfobot](https://t.me/userinfobot) to get the channel ID (usually starts with `-100`, e.g., `-1001234567890`).

---

### Step 3: Configure `.env`

Add your credentials to `.env`:

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGhIJKlmNoPQRstuvWxyz
TELEGRAM_CHAT_ID=5009408813
```

---

## 📱 Alert Message Format

Alerts are sent in clean HTML format with direct copyable addresses and interactive hyperlinks:

```text
🔥 ALPHA SIGNAL (ALPHA)

⛓️ Chain: SOLANA
⭐ Alpha Score: 85/100 (Momentum: 85)
🛡️ Safety: 🟢 Low Risk (15/100)

⏳ Age: 5 mins
📊 Volume (1h): $75,000
⚡ VPM: $15,000.0/min
📈 Buy/Sell Ratio: 3.20
💧 Liquidity (LP): $30,000
💰 Market Cap: $60,000
🟢 Buys: 140  |  🔴 Sells: 44

🏦 Pair: 675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8
📍 CA: 6BeyohhmEkxxBsKsne2rLUjkVpx1uQ1jw4KVB9uTpump

🔗 View on DexScreener
```

---

## ⚡ Rate Limiting & Backoff

The Telegram service natively handles HTTP 429 errors from the Telegram Bot API:
* When a flood rate limit occurs, the service inspects the `Retry-After` response header and automatically suspends outbound requests for the specified duration before retrying.
