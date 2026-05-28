# Change: Bootstrap Flora MVP

## Why
Flora needs a runnable foundation that proves the full knowledge-maintenance loop: source connection, scan, claim extraction, stale-claim verification, patch proposal, user approval, connector write-back, and audit history.

The MVP should use a small runtime topology and a durable PostgreSQL outbox instead of starting with distributed queues or many microservices.

## What Changes
- Add a modular monorepo with `apps/api`, `apps/worker`, `apps/web`, `packages/core`, `packages/connectors`, and `packages/shared`.
- Add FastAPI endpoints for sources, jobs, claims, patch proposals, approvals, and audit data.
- Add a PostgreSQL-backed domain schema and outbox event workflow.
- Add local Markdown and Obsidian-as-folder connector support.
- Add deterministic claim extraction, staleness classification, stub evidence verification, patch proposal generation, approval, and Markdown write-back.
- Add a Next.js dashboard shell for sources, scans, claims, patch review, audit, and settings.

## Impact
- Affected specs: sources, ingestion, claims, verification, patches, audit, jobs
- Affected code: API app, worker app, shared schemas, core services, connectors, database migrations, dashboard
- External services: PostgreSQL and Qdrant in Docker Compose
