# ── Builder stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install uv

# Copy lockfile + manifest first (layer cache: only re-run sync when deps change)
COPY pyproject.toml uv.lock ./

# Install dependencies only (not the project itself) — fast cache layer
RUN uv sync --no-dev --frozen --no-install-project

# Copy source and install project
COPY src/ ./src/
RUN uv sync --no-dev --frozen

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

RUN addgroup --system app && adduser --system --group app && \
    mkdir -p /data/chroma && chown -R app:app /data/chroma

COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
RUN chown -R app:app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
