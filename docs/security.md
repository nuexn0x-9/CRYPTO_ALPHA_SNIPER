# Security Policy and Best Practices

Security is paramount in crypto data engineering. This document details our threat model, vulnerability reporting protocol, and operational security recommendations.

---

## 🛡️ Responsible Vulnerability Disclosure

If you identify a security flaw or vulnerability within **CRYPTO_ALPHA_SNIPER**:

1. **Do NOT open a public GitHub issue.**
2. Email a detailed vulnerability report privately to the maintainers.
3. Include:
   - Vulnerability classification (e.g. Injection, Buffer Exhaustion, Secret Exposure).
   - Step-by-step reproduction instructions or Proof of Concept (PoC).
   - Potential impact assessment.
4. **Timeline**: Maintainers will respond within 48 hours and work with you on a private patch before public disclosure.

---

## 🔒 Threat Model & Defenses

| Threat Vector | Potential Impact | Built-in Mitigation |
| :--- | :--- | :--- |
| **API Credential Leakage** | Compromised Telegram bot or private channel hijacking | `.env` strictly excluded in `.gitignore`; `.env.example` contains only blank placeholders. |
| **API Denial of Service (429)** | Process lockup or permanent IP blacklisting | Exponential backoff retry with jitter and `Retry-After` header parsing in `httpx` clients. |
| **Database Corruption / Race Condition** | Corrupted signal logs or lost candidate records | SQLite configured in Write-Ahead Logging (`WAL`) mode with busy timeouts; atomic transactions. |
| **Honeypot / Malicious Contracts** | False alpha signals leading users into scams | RugCheck verification, Mint/Freeze authority checks, and LP lock status verification. |
| **Container Privilege Escalation** | Host server compromise | Docker image runs under unprivileged user `sniper` (non-root). |

---

## 💡 Operational Security Recommendations for Users

* **Telegram Tokens**: Treat `TELEGRAM_BOT_TOKEN` as a private key. Never share it or post logs containing it.
* **Server Isolation**: Run the scanner on a dedicated low-cost VPS without sensitive private keys or hot wallet credentials stored on the same machine.
* **Smart Contract Due Diligence**: Always verify smart contract source code on block explorers (e.g. Solscan, Etherscan) before conducting any on-chain transaction.
