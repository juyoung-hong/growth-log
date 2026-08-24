# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder
WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 의존성 레이어만 먼저 캐싱 (src가 바뀌어도 이 레이어는 재사용됨)
COPY pyproject.toml uv.lock README.md .python-version ./
RUN uv sync --frozen --no-dev --no-install-project

# 앱 소스를 넣고 나서 프로젝트 자체를 설치
COPY src ./src
RUN uv sync --frozen --no-dev


FROM python:3.13-slim-bookworm AS runtime
WORKDIR /app

# non-root 사용자. HOME=/app 이어야 STEP 5의 ~/.oci 마운트 경로와 맞는다
RUN groupadd --system app && useradd --system --gid app --home /app app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src ./src
COPY alembic ./alembic
COPY alembic.ini ./

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=2)" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]