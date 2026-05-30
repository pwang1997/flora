## Context
Flora should be built incrementally with user supervision. The previous MVP scaffold implemented too many features at once.

## Decisions
- Keep three root-level service folders so future work has a stable place to land.
- Treat `flora-core`, `flora-worker`, and `flora-ui` as standalone projects/microservices with their own manifests and Dockerfiles.
- Remove source, ingestion, claim, verification, patch, audit, persistence, and connector implementations.
- Keep the frontend as a placeholder only; do not add frontend workflows until explicitly requested.
- Keep Docker Compose limited to the three standalone service folders.

## Non-Goals
- No source configuration.
- No document scanning.
- No database schema.
- No outbox worker.
- No local Markdown connector.
- No claim extraction or verification.
- No patch proposal or write-back workflow.
- No feature dashboard.
