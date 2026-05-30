# Flora

Flora is an agentic knowledge-maintenance platform that keeps personal and team notes fresh. It connects to existing knowledge sources, extracts factual claims, detects stale or time-sensitive knowledge, researches authoritative updates, and proposes citation-backed patches through a human-in-the-loop review workflow.

Short version: Flora is a maintenance layer for living knowledge bases.

## Skeleton Runtime

- `flora-core`: standalone FastAPI service with health check only
- `flora-worker`: standalone Python worker service placeholder
- `flora-ui`: standalone Next.js service placeholder kept for later supervised frontend work

## Local Development

```bash
pnpm install
docker compose up --build
```

Run all smoke tests:

```bash
npm test
```

Validate the skeleton OpenSpec change:

```bash
openspec validate bootstrap-flora-skeleton --strict
```

## Architecture

The repo intentionally contains only structure and guardrails. Feature work should start with an OpenSpec change and be implemented under supervision.

- `flora-core`: FastAPI backend, API contracts, and future core domain modules
- `flora-worker`: background worker process and future async/event processing
- `flora-ui`: Next.js dashboard and future user-facing workflows

Each service folder is treated as a separate project/microservice with its own runtime manifest and Dockerfile. Root-level files are only for orchestration, documentation, and OpenSpec governance.

No source ingestion, claim extraction, persistence, outbox workflow, patch review, or write-back behavior exists in this skeleton.
