## ADDED Requirements

### Requirement: Skeleton-Only Runtime
The system SHALL provide only minimal runtime placeholders until a feature is approved through OpenSpec.

#### Scenario: Core health check
- **WHEN** a client requests `GET /health`
- **THEN** `flora-core` returns an OK status

### Requirement: Standalone Service Folders
The system SHALL organize runtime code into standalone service folders named `flora-core`, `flora-worker`, and `flora-ui`.

#### Scenario: Service layout inspection
- **WHEN** a developer inspects the repository root
- **THEN** each runtime service has its own folder, manifest, and Dockerfile

### Requirement: Supervised Feature Gate
The system SHALL require future source, ingestion, claim, verification, patch, audit, persistence, and dashboard work to begin as separate OpenSpec changes.

#### Scenario: New feature request
- **WHEN** a feature beyond skeleton behavior is requested
- **THEN** the implementation plan starts with a dedicated OpenSpec change
