# ==============================================================================
# Multi-stage Dockerfile for CRYPTO_ALPHA_SNIPER
# ==============================================================================

FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ------------------------------------------------------------------------------
# Final Runtime Stage
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS runner

WORKDIR /app

# Create non-root system user for security
RUN groupadd -r sniper && useradd -r -g sniper sniper

# Copy installed wheels from builder
COPY --from=builder /root/.local /home/sniper/.local
ENV PATH=/home/sniper/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy project source
COPY --chown=sniper:sniper src/ ./src/
COPY --chown=sniper:sniper .env.example ./

# Create data and logs directory with appropriate ownership
RUN mkdir -p /app/data /app/logs && chown -R sniper:sniper /app

USER sniper

VOLUME ["/app/data", "/app/logs"]

ENTRYPOINT ["python", "-m", "src.main"]
