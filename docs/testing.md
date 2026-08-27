# Automated Testing Strategy

**CRYPTO_ALPHA_SNIPER** enforces a strict automated testing regimen using `pytest` and `pytest-asyncio`.

---

## 🧪 Test Suite Hierarchy

```
tests/
├── conftest.py                 # Async in-memory SQLite fixtures
├── test_config.py              # Settings validation & default fallbacks
├── test_database.py            # Async CRUD, schema integrity & relationships
├── test_dexscreener.py         # Response parsing & best pair selection logic
├── test_filters.py             # Chain address regex validation (Solana/BSC/TON)
├── test_migration.py           # Legacy JSON deduplication & SQLite import
├── test_risk_engine.py         # RugCheck parsing & security score heuristics
├── test_scanner_engine.py      # End-to-end scanner pipeline integration test
├── test_scorer.py              # Mathematical scoring formulas, VPM, & ratio
├── test_telegram.py            # HTML alert formatting validation
│
└── live/                       # Live External API Tests (Optional)
    ├── test_live_dexscreener.py
    ├── test_live_rugcheck.py
    └── test_live_telegram.py
```

---

## 🏃 Running Tests

### Standard Test Run
Runs all offline unit and integration tests:

```bash
pytest -v
```

### Running with Code Coverage
```bash
pytest --cov=src --cov-report=term-missing -v
```

### Running Live External API Tests
Live tests make actual outbound HTTP requests to DexScreener and RugCheck. They are **disabled by default** to keep CI deterministic and avoid hitting third-party rate limits.

To enable live tests:
```bash
# Linux / macOS:
ENABLE_LIVE_TEST=true pytest tests/live/ -v

# Windows (PowerShell):
$env:ENABLE_LIVE_TEST="true"; pytest tests/live/ -v
```

---

## ✍️ Writing New Tests

When contributing a new feature or algorithm adjustment:
1. Place unit tests under `tests/test_<feature>.py`.
2. Use `@pytest.mark.asyncio` for asynchronous functions.
3. Use the `in_memory_db_session` fixture from `conftest.py` for database operations to ensure test isolation.
4. Mock external network requests using `unittest.mock.AsyncMock` or `pytest-mock`.
