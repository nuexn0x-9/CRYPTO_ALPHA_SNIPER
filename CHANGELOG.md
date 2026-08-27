# Changelog

All notable changes to the **CRYPTO_ALPHA_SNIPER** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-08-27

### Initial Public Open Source Release

#### Added
- **Asynchronous Pipeline**: Built on Python `asyncio` and `httpx.AsyncClient` with semaphore-controlled concurrency.
- **Production Database**: Async SQLite database using SQLAlchemy 2.0 ORM with WAL (Write-Ahead Logging) mode and indexed tables (`tokens`, `market_data`, `signals`, `tracking`).
- **Automated Data Retention**: Autonomous periodic purging (`src/database/cleanup.py`) of expired tokens and cascaded historical records to maintain database efficiency.
- **Security & Risk Engine**: Automated verification of Solana tokens via RugCheck API, checking Mint Authority, Freeze Authority, LP Burn/Lock, and Top Holder Concentration.
- **Structured Scoring**: Multi-factor momentum scorer evaluating token age, Volume Per Minute (VPM), Buy/Sell transaction ratios, liquidity depth, and social presence.
- **Autonomous ROI/PNL Tracker**: Background worker updating price and market cap metrics over time to benchmark signal profitability.
- **Rich Telegram Dispatcher**: HTML-formatted alerts containing safety metrics, token statistics, and direct DEX links.
- **Config & Logging**: Strict environment validation with `pydantic-settings` and structured log rotation via `loguru`.
- **Packaging & Deployment**: Multi-stage lightweight `Dockerfile` and `docker-compose.yml`.
- **Comprehensive Documentation**: Complete architecture, database ERD, configuration, development, and contribution guides in `docs/`.
- **Automated Test Suite**: 16 unit and integration tests with 100% pass rate.

#### Migrated
- Migrated legacy single-threaded `requests` scripts to non-blocking `httpx` async collectors.
- Migrated legacy `candidates.json` (>13,800 records) and `processed_tokens.json` (>14,000 addresses) to indexed SQLite tables.
- Replaced unformatted `print()` output with structured logging and file rotation.

#### Security
- Comprehensive credential protection: sanitized `.env.example`, strict `.gitignore`, non-root Docker execution user (`sniper`), and automatic risk rejection threshold.
