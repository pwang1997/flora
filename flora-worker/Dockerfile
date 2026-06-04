FROM ghcr.io/astral-sh/uv:python3.13-bookworm

WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY src ./src

RUN uv sync --frozen

CMD ["uv", "run", "python", "-m", "flora_worker.main"]
