# Flora

Flora is an agentic knowledge-maintenance platform that keeps personal and team notes fresh. It connects to existing knowledge sources, extracts factual claims, detects stale or time-sensitive knowledge, researches authoritative updates, and proposes citation-backed patches through a human-in-the-loop review workflow.

Short version: Flora is a maintenance layer for living knowledge bases.

## MVP Runtime

- `flora-web`: Next.js dashboard
- `flora-api`: FastAPI backend API
- `flora-worker`: Python worker polling the PostgreSQL outbox
- `postgres`: durable source of truth and outbox workflow
- `qdrant`: local vector-store topology

## Local Development

```bash
uv sync
pnpm install
docker compose up --build
```

Run backend tests:

```bash
uv run pytest
```

Validate the MVP OpenSpec change:

```bash
openspec validate bootstrap-flora-mvp --strict
```

## Architecture

The MVP uses a modular monorepo with clean service boundaries:

- `apps/api`: FastAPI routes and request/response boundary
- `apps/worker`: outbox polling and event handlers
- `apps/web`: dashboard and review UI
- `packages/shared`: Pydantic DTOs, enums, common types
- `packages/core`: domain services and workflow logic
- `packages/connectors`: provider-specific read/write adapters

PostgreSQL is the async workflow mechanism in MVP. Redis, Kafka, Notion, GitHub Docs, real auth, and automatic patch application are intentionally deferred.
