# Troubleshooting & Common Issues

This guide provides fast diagnosis and resolution steps for common setup and runtime issues.

---

## 🛑 Common Issues & Solutions

### 1. `DexScreener Status: 429` (Rate Limited)
* **Symptom**: Logs display `DexScreener rate limit (429). Backing off for X.Xs...`.
* **Cause**: Sending too many requests per minute from a single IP.
* **Solution**:
  1. Increase `SCAN_INTERVAL_SECONDS` in `.env` (e.g. from `60` to `90` or `120`).
  2. Reduce `CONCURRENCY_LIMIT` in `.env` (e.g. from `10` to `5`).

---

### 2. Telegram Alert Errors (`HTTP 400` / `HTTP 401` / `HTTP 404`)
* **`HTTP 401 Unauthorized`**:
  * **Cause**: Incorrect `TELEGRAM_BOT_TOKEN`.
  * **Solution**: Verify the token copied from @BotFather in `.env`. Ensure no leading/trailing spaces exist.
* **`HTTP 400 Bad Request: chat not found`**:
  * **Cause**: The bot has not been started by the user or is not an administrator in the target channel.
  * **Solution**: Send `/start` to your bot in private chat, or add the bot as an Admin with "Post Messages" permission in your channel.

---

### 3. SQLite Database Locked (`sqlite3.OperationalError: database is locked`)
* **Symptom**: Errors stating the database file is busy or locked.
* **Cause**: Multiple processes attempting concurrent synchronous writes on standard SQLite mode.
* **Solution**:
  * Ensure the database is running in **WAL mode** (CRYPTO_ALPHA_SNIPER enables WAL automatically).
  * If accessing the `.db` file externally via third-party GUI tools (like DBeaver or DB Browser), ensure they connect in read-only mode.

---

### 4. RugCheck API Connection Timeout
* **Symptom**: `RugCheck lookup error: ReadTimeout`.
* **Cause**: Public RugCheck API temporarily experiencing high traffic.
* **Solution**: The engine automatically catches timeouts and defaults to a baseline heuristic safety score without crashing the main scanner cycle.

---

### 5. `ModuleNotFoundError: No module named 'src'`
* **Symptom**: Python cannot locate the `src` package.
* **Cause**: Executing scripts from subdirectories instead of project root.
* **Solution**: Always run the application from the root directory using module notation:
  ```bash
  python -m src.main
  ```
