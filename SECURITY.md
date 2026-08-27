# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of **CRYPTO_ALPHA_SNIPER** seriously. If you discover a security vulnerability, please follow these steps:

1. **Do Not Open a Public Issue**: To protect users, please do not post vulnerability details on public GitHub issues or discussions.
2. **Contact the Maintainers**: Send a private report detailing the vulnerability, reproduction steps, and potential exploit vectors to the maintainers.
3. **Disclosure Timeline**:
   - Maintainers will acknowledge your report within 48 hours.
   - A patched release will be prepared and tested.
   - Once resolved, a security advisory will be published acknowledging your responsible disclosure.

## Security Best Practices for Users

- Never commit private `.env` files or API keys to version control.
- Regularly rotate your Telegram Bot Tokens.
- Keep the database file (`data/*.db`) secured and accessible only by the bot process.
- Review smart contract source code independently before executing any on-chain transactions based on bot signals.
