# Installation Guide

This document outlines system requirements, local installation, virtual environment setup, and production deployment options.

---

## 🖥️ System Requirements

| Component | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **Operating System** | Linux (Ubuntu 20.04+), macOS 12+, Windows 10/11 | Linux (Ubuntu 22.04 LTS) |
| **Python** | 3.11 or higher | 3.11 / 3.12 |
| **Memory (RAM)** | 512 MB | 2 GB+ |
| **Disk Space** | 200 MB free space | 2 GB+ (for long-term log retention) |
| **Network** | Stable outbound internet (HTTPS/TLS) | Low-latency connection to DEX endpoints |

---

## 🛠️ Method 1: Local Virtual Environment (Recommended for Development)

### 1. Clone Source Code
```bash
git clone https://github.com/nuexn0x-9/CRYPTO_ALPHA_SNIPER.git
cd CRYPTO_ALPHA_SNIPER
```

### 2. Create Virtual Environment
```bash
# Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

# Windows:
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Package Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify Installation
Execute the automated test suite to confirm all modules are properly linked:
```bash
pytest -v
```

---

## 🐳 Method 2: Docker Installation (Recommended for Production)

Docker provides an isolated, reproducible container environment.

### Prerequisites
* [Docker Engine](https://docs.docker.com/engine/install/) (v24.0+)
* [Docker Compose](https://docs.docker.com/compose/install/) (v2.20+)

### 1. Configure Environment
```bash
cp .env.example .env
# Configure your settings in .env
```

### 2. Build & Launch
```bash
docker compose up -d --build
```

### 3. Check Container Status
```bash
docker compose ps
docker compose logs -f crypto_alpha_sniper
```

---

## 📦 Method 3: Development Tools Installation

If you intend to contribute code, install optional development dependencies (linting, type checking):

```bash
pip install ruff black mypy pytest-cov
```

Run linter check:
```bash
ruff check src/ tests/
```
