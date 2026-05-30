# Project Context

## Purpose
Flora is an agentic knowledge-maintenance platform that keeps personal and team notes fresh. It connects to existing knowledge sources, extracts factual claims, detects stale or time-sensitive knowledge, researches authoritative updates, and proposes citation-backed patches through a human-in-the-loop review workflow.

Flora is a maintenance layer for living knowledge bases. It is not a note-taking app.

## Tech Stack
- `flora-core`: FastAPI, Pydantic v2, uv
- `flora-worker`: Python worker process placeholder, uv
- `flora-ui`: Next.js, TypeScript, Tailwind CSS, pnpm, currently placeholder only
- Tooling: Docker Compose for local multi-service runtime
- Testing: pytest for skeleton smoke tests

## Project Conventions

### Code Style
- Add no production feature behavior without an approved OpenSpec change.
- Keep skeleton modules small and dependency-light until a feature requires more.
- Keep shared schemas provider-independent once they are introduced.
- Avoid hidden writes: future note mutations must pass through explicit approval and connector write-back paths.

### Architecture Patterns
- Modular monorepo with root-level service folders.
- Each service folder is a standalone project/microservice and MUST NOT be folded into a shared `apps/` folder.
- Do not introduce persistence, queues, vector stores, or provider SDKs without a supervised feature proposal.
- Service ownership:
  - `flora-core`: API contracts and future core domain behavior
  - `flora-worker`: future async/event processing
  - `flora-ui`: API-backed dashboard
- Cross-service coupling should happen through HTTP/event contracts or explicit package decisions proposed through OpenSpec.

### Testing Strategy
- Validate OpenSpec changes with `openspec validate <change-id> --strict`.
- Use service-local pytest suites for Python services.
- Use `pnpm --dir flora-ui lint` and Next.js build checks for UI changes.
- Each feature proposal should define its own acceptance tests before implementation.

### Git Workflow
- Use feature branches with the `codex/` prefix for Codex-created work.
- Keep OpenSpec proposal, implementation, and tests aligned in the same branch for MVP bootstrap work.

## Domain Context
Intended future workflow:
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
- Current repo state is skeleton-only.
- Runtime service folders are `flora-core`, `flora-worker`, and `flora-ui`.
- Each feature MUST be proposed and approved before implementation.
- Future implementations MUST NOT automatically apply patches without explicit approval.
- Frontend feature work is paused until explicitly requested.

## External Dependencies
- No runtime external data services are required by the skeleton.
- Future feature proposals may add PostgreSQL, Qdrant, Notion, GitHub Docs, or research providers.
