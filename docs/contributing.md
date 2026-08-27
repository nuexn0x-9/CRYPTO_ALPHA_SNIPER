# Community Contribution Guidelines

We are thrilled to welcome contributions to **CRYPTO_ALPHA_SNIPER**! Whether you are submitting bug fixes, new features, or architectural enhancements, please review our contribution process.

## Pull Request Guidelines

1. **Keep PRs Focused**: Each pull request should address a single feature or bug fix.
2. **Include Unit Tests**: Any new scoring formula, collector integration, or safety heuristic must include tests in `tests/`.
3. **Update Documentation**: If modifying environment parameters or adding features, update corresponding documentation in `docs/` and `README.md`.
4. **Clean Git History**: Write descriptive commit messages following the Conventional Commits format (e.g. `feat: add Base chain support`, `fix: handle DexScreener 429 backoff`).

## Areas Open for Community Contribution

- **Additional Chain Collectors**: Integration with Base, Arbitrum, Ethereum DEXes.
- **On-chain RPC Verifications**: Direct Solana / EVM RPC calls for liquidity locker status.
- **Web UI & Dashboard**: Developing a FastAPI REST / WebSocket backend with React frontend.
- **Alternative Alert Channels**: Discord webhooks, Slack webhooks, and Matrix integrations.
