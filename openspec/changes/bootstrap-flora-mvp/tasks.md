## 1. OpenSpec
- [x] 1.1 Initialize OpenSpec and fill project context.
- [x] 1.2 Add `bootstrap-flora-mvp` proposal, design, tasks, and spec deltas.
- [x] 1.3 Validate the change with `openspec validate bootstrap-flora-mvp --strict`.

## 2. Runtime Scaffold
- [x] 2.1 Create monorepo folders for API, worker, web, core, connectors, and shared packages.
- [x] 2.2 Add Python, web, Docker Compose, environment, and README configuration.

## 3. Backend, Worker, and Persistence
- [x] 3.1 Define Pydantic contracts, enums, SQLAlchemy models, and Alembic migration.
- [x] 3.2 Implement FastAPI routes for sources, jobs, claims, patch proposals, approvals, and audit.
- [x] 3.3 Implement outbox polling and event handlers.

## 4. Domain Workflow
- [x] 4.1 Implement local Markdown connector and Obsidian-as-folder behavior.
- [x] 4.2 Implement document snapshots, claim extraction, staleness classification, stub evidence, patch proposals, approvals, write-back, and audit records.

## 5. Dashboard
- [x] 5.1 Add Next.js routes for sources, scans, claims, patches, patch detail, audit, and settings.
- [x] 5.2 Add API client helpers and review-oriented UI sections.

## 6. Verification
- [x] 6.1 Add pytest coverage for contracts, connectors, core workflow, API endpoints, and worker handlers.
- [x] 6.2 Run OpenSpec validation and Python tests.
