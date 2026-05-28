# Project Context

## Purpose
Flora is an agentic knowledge-maintenance platform that keeps personal and team notes fresh. It connects to existing knowledge sources, extracts factual claims, detects stale or time-sensitive knowledge, researches authoritative updates, and proposes citation-backed patches through a human-in-the-loop review workflow.

Flora is a maintenance layer for living knowledge bases. It is not a note-taking app.

## Tech Stack
- Backend API: FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2
- Worker: Python process polling PostgreSQL outbox events
- Database: PostgreSQL for durable state and the MVP outbox workflow
- Vector store: Qdrant in local Docker, behind an adapter boundary
- Frontend: Next.js, TypeScript, Tailwind CSS
- Tooling: uv for Python, pnpm for web, Docker Compose for local runtime
- Testing: pytest for backend/core/connectors; frontend component/e2e tests can be added once dashboard workflows stabilize

## Project Conventions

### Code Style
- Keep domain schemas and enums provider-independent in `packages/shared`.
- Keep business workflow in `packages/core`.
- Keep concrete provider reads/writes in `packages/connectors`.
- Avoid hidden writes: all note mutations must pass through explicit approval and connector write-back paths.
- Prefer deterministic services and test fixtures in MVP over external network dependencies.

### Architecture Patterns
- Modular monorepo with a small number of runtime services: web, api, worker, postgres, qdrant.
- PostgreSQL outbox is the MVP async workflow mechanism; do not introduce Redis or Kafka until throughput/locking needs justify it.
- Dependency direction:
  - `apps/api` -> `packages/core` -> `packages/shared`
  - `apps/worker` -> `packages/core` -> `packages/shared`
  - `packages/connectors` -> `packages/shared`
  - `apps/web` -> API contracts
- Core defines connector and research interfaces; concrete connectors and research providers live outside core.

### Testing Strategy
- Validate OpenSpec changes with `openspec validate <change-id> --strict`.
- Use pytest for shared schemas, core services, connector behavior, API endpoints, and worker handlers.
- Use temporary Markdown folders for local connector tests.
- Use deterministic stub evidence in MVP tests so the pipeline can run without API keys.

### Git Workflow
- Use feature branches with the `codex/` prefix for Codex-created work.
- Keep OpenSpec proposal, implementation, and tests aligned in the same branch for MVP bootstrap work.

## Domain Context
Core workflow:
1. User connects a knowledge source.
2. Flora scans provider documents and normalizes them into internal document models.
3. Flora stores document snapshots and extracts factual claims.
4. Flora classifies claims by staleness risk.
5. Flora verifies high-risk claims against evidence.
6. Flora generates citation-backed patch proposals.
7. User approves or rejects proposals in the dashboard.
8. Approved patches are written back through the connector.
9. Flora records audit history for traceability.

## Important Constraints
- MVP MUST NOT automatically apply patches without explicit approval.
- MVP MUST support local Markdown folders and Obsidian vaults as local Markdown.
- MVP SHOULD use stubbed research/evidence behind an interface until a trusted search provider is selected.
- MVP excludes Redis, Kafka, Notion, GitHub Docs, native Obsidian plugin work, real multi-user auth, team permissions, and real-time collaboration.

## External Dependencies
- PostgreSQL for durable source of truth and outbox events.
- Qdrant for local vector-store topology; vector search can remain lightly wired until the approval workflow is runnable.
- Future connectors may include Notion and GitHub Docs, but they are out of MVP scope.
