FROM ghcr.io/astral-sh/uv:python3.14-bookworm

WORKDIR /app
COPY flora-core/pyproject.toml flora-core/uv.lock ./flora-core/
COPY flora-core/alembic.ini ./flora-core/
COPY flora-core/alembic ./flora-core/alembic
COPY flora-core/src ./flora-core/src
COPY flora-shared ./flora-shared

WORKDIR /app/flora-core
RUN uv sync --frozen

CMD ["uv", "run", "uvicorn", "main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]
