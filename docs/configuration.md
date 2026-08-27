# Configuration Reference

All settings in **CRYPTO_ALPHA_SNIPER** are loaded and validated using `pydantic-settings`. Configurations can be set via environment variables or a `.env` file in the root directory.

## Environment Variables

### 1. Telegram Alerts
| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | string | `""` | Bot token provided by @BotFather. |
| `TELEGRAM_CHAT_ID` | string | `""` | Target user ID, group ID, or channel ID. |

### 2. Database URI
| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | string | `sqlite+aiosqlite:///data/crypto_alpha_sniper.db` | Async SQLAlchemy database URI. Supports SQLite, PostgreSQL (`postgresql+asyncpg://...`), etc. |

### 3. API Endpoints
| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `DEXSCREENER_API_BASE` | string | `https://api.dexscreener.com` | Base endpoint for DexScreener REST API. |
| `RUGCHECK_API_BASE` | string | `https://api.rugcheck.xyz/v1` | Base endpoint for RugCheck API. |

### 4. Scanner Engine Filters
| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `SCAN_INTERVAL_SECONDS` | int | `60` | Delay between consecutive scanning passes. |
| `MAX_AGE_MINUTES` | int | `60` | Maximum token creation age (in minutes) to be processed. |
| `MIN_VOLUME_USD` | float | `1000.0` | Minimum 1-hour volume ($ USD) required. |
| `MIN_MARKET_CAP_USD` | float | `1000.0` | Minimum market capitalization ($ USD) required. |
| `SUPPORTED_CHAINS` | string | `solana,bsc,ton` | Comma-separated list of target chains. |
| `CONCURRENCY_LIMIT` | int | `10` | Maximum parallel token inspection tasks. |

### 5. Scoring & Risk Thresholds
| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `WATCHLIST_SCORE` | int | `40` | Minimum score for Watchlist tier. |
| `EARLY_SIGNAL_SCORE` | int | `55` | Minimum score for Early Signal tier. |
| `ALPHA_SIGNAL_SCORE` | int | `70` | Minimum score for Alpha Signal tier. |
| `MAX_ALLOWED_RISK_SCORE` | int | `65` | Maximum allowable risk score (0-100) before auto-rejection. |

### 6. Logging
| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `LOG_LEVEL` | string | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `LOG_FILE_PATH` | string | `logs/crypto_alpha_sniper.log` | Path to rotated log file. |
| `LOG_ROTATION` | string | `10 MB` | Log rotation size threshold. |
| `LOG_RETENTION` | string | `14 days` | Time to keep archived log files. |
