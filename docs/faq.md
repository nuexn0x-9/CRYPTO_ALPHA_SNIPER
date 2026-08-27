# Frequently Asked Questions (FAQ)

---

### Q1: Does CRYPTO_ALPHA_SNIPER guarantee trading profits?
**A**: **No.** CRYPTO_ALPHA_SNIPER is a quantitative research and discovery tool. It identifies mathematical anomalies in volume velocity, liquidity depth, and buy pressure. It does not provide trading signals, investment advice, or guaranteed financial outcomes. All trading decisions carry risk.

---

### Q2: Is it safe to run on my own computer or server?
**A**: **Yes.** The software is completely open source under the MIT License. It does not require access to your crypto wallets, private keys, or seed phrases. It only performs read-only public API queries and sends outbound Telegram messages.

---

### Q3: Which blockchain networks are currently supported?
**A**: **v1.0.0** supports:
1. **Solana (`solana`)**: Full DexScreener ingestion and RugCheck security audits.
2. **BNB Smart Chain (`bsc`)**: EVM token discovery and liquidity heuristics.
3. **The Open Network (`ton`)**: TON smart contract tracking.

Support for **Base**, **Arbitrum**, and **Ethereum** is scheduled for v1.5.

---

### Q4: Can I run the scanner without Telegram alerts?
**A**: **Yes.** Simply leave `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` empty in `.env`. The scanner will log all qualified tokens to stdout and persist records directly to the SQLite database.

---

### Q5: What database does the bot use?
**A**: By default, it uses **SQLite in WAL (Write-Ahead Logging) mode** via `aiosqlite` and SQLAlchemy. Because SQLAlchemy 2.0 Async ORM is used, you can easily switch to **PostgreSQL** or **MySQL** simply by changing the `DATABASE_URL` connection string in `.env`.

---

### Q6: How does the bot calculate Return on Investment (ROI)?
**A**: When a token is spotted, its initial market cap is saved as `entry_market_cap`. The background `PerformanceTracker` worker checks the token's current market cap over time ($15\text{m}$, $1\text{h}$, $4\text{h}$, $24\text{h}$) to compute:

$$\text{ROI \%} = \frac{\text{Current Market Cap} - \text{Entry Market Cap}}{\text{Entry Market Cap}} \times 100$$
