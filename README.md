# CRYPTO_ALPHA_SNIPER 🎯⚡

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Async Architecture](https://img.shields.io/badge/architecture-asyncio%20%2B%20httpx-orange.svg)](https://www.encode.io/httpx/)
[![Database: SQLite WAL](https://img.shields.io/badge/database-SQLite%20WAL%20%7C%20SQLAlchemy-red.svg)](https://www.sqlalchemy.org/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-brightgreen.svg)](.github/workflows/tests.yml)
[![Version](https://img.shields.io/badge/version-1.0.0-purple.svg)](src/version.py)

**Open-source Crypto Alpha Discovery and Intelligence Engine**

[Documentation](docs/) • [Getting Started](docs/getting-started.md) • [Architecture](docs/architecture.md) • [Docker Guide](docs/docker-guide.md) • [Contributing](docs/contributing.md)

</div>

---

## 📖 Introduction

**CRYPTO_ALPHA_SNIPER** is a production-grade, asynchronous open-source crypto intelligence and momentum scanner engine. Designed for blockchain researchers, developers, and crypto analysts, it autonomously discovers newly listed tokens across Solana, BSC, and TON, evaluates multi-dimensional momentum and liquidity metrics, conducts automated security and risk audits, and delivers structured real-time signals via Telegram.

### Core Philosophy
* **Research-Driven**: Built for data discovery, pattern evaluation, and risk assessment—not speculative trading guarantees.
* **Security-First**: Every token undergoes automated contract safety checks (Mint/Freeze authority, RugCheck verification, LP token lock/burn, holder concentration) before signal qualification.
* **100% Open Source**: Fully transparent codebase under the MIT License with no hidden proprietary binaries or custodial features.

---

## 🌟 Key Features

### 🔍 Token Discovery
* **DexScreener API Integration**: High-frequency ingestion of newly created token profiles and liquidity pools.
* **Multi-Chain Native**: Support for **Solana** (including pump.fun curves), **BNB Smart Chain (BSC)**, and **The Open Network (TON)**.

### 📊 Intelligence & Scoring Engine
* **Multi-Factor Momentum Scorer**: Evaluates token age, Volume Per Minute (VPM), Buy/Sell transaction ratio, and real-time liquidity depth.
* **Signal Tiering**: Categorizes qualified tokens into `ALPHA_SIGNAL` (≥ 70), `EARLY_SIGNAL` (≥ 55), and `WATCHLIST` (≥ 40).

### 🛡️ Automated Security Layer
* **RugCheck Integration**: Direct analysis of smart contract risk scores, dangerous authorities, and honeypot indicators.
* **Authority Checks**: Automated detection of unrevoked Mint Authority (infinite mint risk) and Freeze Authority (blacklist risk).
* **Top Holder Concentration**: Flags tokens with excessive supply concentration in single wallets.

### 💾 Production Data Infrastructure
* **Async SQLite WAL Mode**: Zero-lock concurrent database operations via SQLAlchemy 2.0 Async ORM.
* **Autonomous Performance Tracker**: Periodically benchmarks spotted tokens over time to measure market cap growth and ROI %.

### 📱 Notification & Observability
* **Rich Telegram Alerts**: Formatted HTML alerts with safety badges, volume statistics, contract addresses, and direct DEX links.
* **Structured Logging**: Powered by `loguru` with automatic log rotation and file retention policies.

---

## 🏛️ Architecture Overview

```
                        ┌─────────────────────────────────┐
                        │   DEX & Blockchain Sources      │
                        │ (DexScreener, RugCheck, RPCs)   │
                        └────────────────┬────────────────┘
                                         │ Async HTTP (httpx)
                                         ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                     CRYPTO_ALPHA_SNIPER ENGINE                            │
│                                                                           │
│  ┌──────────────────────┐    ┌─────────────────────┐    ┌──────────────┐  │
│  │   Token Ingestion    │───▶│   Security Engine   │───▶│ Momentum     │  │
│  │   (DexScreener API)  │    │ (RugCheck & Safety) │    │ Scorer       │  │
│  └──────────────────────┘    └─────────────────────┘    └──────┬───────┘  │
│                                                                │          │
│                                                                ▼          │
│  ┌──────────────────────┐                    ┌─────────────────────────┐  │
│  │  PNL & ROI Tracker   │                    │   Telegram Dispatcher   │  │
│  │  (Background Task)   │                    │     (Async HTML)        │  │
│  └──────────┬───────────┘                    └────────────┬────────────┘  │
└─────────────┼─────────────────────────────────────────────┼───────────────┘
              │                                             │
              ▼                                             ▼
┌───────────────────────────┐                 ┌───────────────────────────┐
│   SQLite Database (WAL)   │                 │   Telegram Subscriber     │
│ (Indexed Tokens & Signals)│                 │   (Channel / Direct Chat) │
└───────────────────────────┘                 └───────────────────────────┘
```

---

## 🚀 Quick Start Guide

### Local Installation

```bash
# 1. Clone the repository
git clone https://github.com/nuexn0x-9/CRYPTO_ALPHA_SNIPER.git
cd CRYPTO_ALPHA_SNIPER

# 2. Set up virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your Telegram bot token & preferences

# 5. Start the scanner engine
python -m src.main
```

### Docker Deployment

```bash
# Start container in detached mode
docker compose up -d --build

# View real-time logs
docker compose logs -f

# Stop gracefully
docker compose down
```

---

## 📚 Complete Documentation

Detailed technical documentation is available in the [`docs/`](docs/) directory:

| Document | Description |
| :--- | :--- |
| [**Getting Started**](docs/getting-started.md) | Step-by-step beginner onboarding guide. |
| [**Installation Guide**](docs/installation.md) | Local, virtual environment, and production installation. |
| [**Configuration Reference**](docs/configuration.md) | Exhaustive parameter reference and `.env` settings. |
| [**Architecture Blueprint**](docs/architecture.md) | Deep dive into async engine subsystems and lifecycle. |
| [**Database Schema**](docs/database.md) | SQLite WAL mode, SQLAlchemy ORM models, and ERD. |
| [**Scanner Engine**](docs/scanner-engine.md) | Inspection pipeline and concurrency controls. |
| [**Scoring System**](docs/scoring-system.md) | Momentum formulas, velocity (VPM), and risk weighting. |
| [**Risk Engine**](docs/risk-engine.md) | RugCheck audit heuristics and safety evaluation. |
| [**Telegram Integration**](docs/telegram-integration.md) | Setting up @BotFather, channels, and alerts. |
| [**Docker Guide**](docs/docker-guide.md) | Multi-stage containerization, volumes, and healthchecks. |
| [**Deployment Guide**](docs/deployment.md) | VPS, Systemd, and server hardening guidelines. |
| [**Development Guide**](docs/development.md) | Contributor workflows, linting, and coding standards. |
| [**Testing Guide**](docs/testing.md) | Unit, integration, and optional live API testing. |
| [**Contributing**](docs/contributing.md) | Community contribution guidelines. |
| [**Security Policy**](docs/security.md) | Responsible disclosure policy and threat model. |
| [**Troubleshooting**](docs/troubleshooting.md) | Common errors, rate limits, and remediation steps. |
| [**FAQ**](docs/faq.md) | Frequently asked questions. |
| [**Roadmap**](docs/roadmap.md) | Project roadmap from v1.0 to v3.0. |

---

## 🧪 Automated Testing & Code Quality

Run the complete test suite:
```bash
pytest -v
```

Run code formatting and lint verification:
```bash
ruff check src/ tests/
```

---

## ⚠️ Legal & Educational Disclaimer

> **IMPORTANT NOTICE**:
> This software is strictly developed and maintained for **educational, academic, and research purposes only**.
> 
> * It does **NOT** constitute financial, investment, legal, or trading advice.
> * Cryptographic tokens and decentralized liquidity pools carry extreme volatility and high risk of capital loss.
> * The maintainers and contributors do **NOT** make any guarantees of profitability, signal accuracy, or contract safety.
> * Users are solely responsible for conducting independent due diligence before interacting with any smart contract.

---

## 📄 License

This project is licensed under the terms of the **MIT License**. See the [`LICENSE`](LICENSE) file for details.
