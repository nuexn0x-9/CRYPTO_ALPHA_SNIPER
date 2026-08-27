# Development and Setup Guide

## Local Development Workflow

### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/nuexn0x-9/CRYPTO_ALPHA_SNIPER.git
cd CRYPTO_ALPHA_SNIPER

# Create virtual environment
python -m venv .venv
# Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
```

### 2. Configuration Setup
```bash
cp .env.example .env
```
Edit `.env` as required. For development without Telegram alerts, leave `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` empty.

### 3. Running Automated Tests
```bash
# Run all tests with verbose output
pytest -v

# Run with coverage (if pytest-cov installed)
pytest --cov=src -v
```

### 4. Running the Scanner
```bash
python -m src.main
```

### 5. Running Legacy Data Migration
```bash
python -m src.database.migration
```

---

## Code Quality Standards

* **PEP 8 Compliance**: Use standard Python formatting.
* **Explicit Type Hints**: All function signatures and returns must include type hints.
* **Logging**: Always use `loguru.logger` rather than standard `print()`.
* **Async/Await**: Ensure network and database operations use non-blocking asynchronous calls.
