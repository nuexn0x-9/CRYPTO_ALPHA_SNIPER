# Contributing to CRYPTO_ALPHA_SNIPER

Thank you for your interest in contributing to **CRYPTO_ALPHA_SNIPER**! We welcome contributions from developers, crypto researchers, and data engineers.

## Code of Conduct

Please be respectful, collaborative, and constructive in all issues and pull requests.

## How to Contribute

1. **Fork the Repository**: Create a personal fork on GitHub.
2. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/awesome-new-feature
   ```
3. **Set Up Local Development**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Follow Coding Standards**:
   - Python 3.11+ syntax.
   - Clean Architecture and modular structure.
   - Type hints on all function signatures.
   - Clear docstrings explaining inputs, outputs, and edge cases.
   - Use `loguru` for structured logging (avoid `print()`).
5. **Run Tests**:
   Ensure all tests pass before submitting a PR:
   ```bash
   pytest -v
   ```
6. **Submit a Pull Request**:
   - Provide a concise title and detailed explanation of changes.
   - Reference any relevant issues.

## Reporting Bugs

Please open an issue on GitHub with:
- Operating system & Python version.
- Exact error traceback from `logs/crypto_alpha_sniper.log`.
- Minimal steps to reproduce the issue.
