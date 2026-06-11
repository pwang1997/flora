FROM ghcr.io/astral-sh/uv:python3.14-bookworm

WORKDIR /app
COPY flora-worker/pyproject.toml flora-worker/uv.lock ./flora-worker/
COPY flora-worker/src ./flora-worker/src
COPY flora-shared ./flora-shared

WORKDIR /app/flora-worker
RUN uv sync --frozen

CMD ["uv", "run", "python", "src/main.py"]
