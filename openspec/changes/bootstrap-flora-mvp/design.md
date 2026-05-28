## Context
Flora is a maintenance layer for existing knowledge bases. It should preserve user control and traceability while proving that a note can move from source scan to approved patch write-back.

## Goals / Non-Goals
- Goals: runnable local MVP, clean package boundaries, durable outbox workflow, local Markdown connector, auditable approval loop.
- Non-Goals: Redis, Kafka, Notion, GitHub Docs, native Obsidian plugin, real auth, automatic patch application, production-scale vector retrieval.

## Decisions
- Use a modular monorepo, not distributed microservices, for MVP.
- Use PostgreSQL as both durable state and outbox queue to keep workflow state transactional and inspectable.
- Use Qdrant in Docker Compose to reserve the vector-store boundary, but do not make vector search critical to the MVP approval loop.
- Use deterministic stub evidence behind a research interface until trusted source and citation policies are chosen.
- Treat Obsidian vaults as local Markdown folders.

## Runtime Services
- `flora-api`: FastAPI backend for dashboard and workflow commands.
- `flora-worker`: Python outbox worker for long-running processing.
- `flora-web`: Next.js dashboard.
- `postgres`: durable state and outbox.
- `qdrant`: local vector store.

## Outbox Flow
The API writes domain rows and outbox events in one transaction. The worker claims pending events using row locks, executes the handler, emits follow-up events, and records audit entries. Failed events retain error text and retry metadata.

## Connector Boundary
Core code depends on connector interfaces only. Concrete connectors list documents, read normalized content, and apply approved patches. Connectors do not extract claims, research evidence, or make approval decisions.

## Risks / Trade-offs
- Stub evidence is not production research; mitigation is a replaceable research interface and explicit evidence records.
- Simple patch replacement can conflict with changed source content; mitigation is snapshot hashes and connector-level conflict reporting.
- SQLite is allowed for tests and local smoke runs, but PostgreSQL remains the intended runtime store.
