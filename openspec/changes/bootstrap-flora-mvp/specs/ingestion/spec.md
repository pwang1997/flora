## ADDED Requirements

### Requirement: Scan Request
The system SHALL create a job and outbox event when a source scan is requested.

#### Scenario: User starts scan
- **WHEN** a client requests a scan for a configured source
- **THEN** the API creates a job and enqueues `SOURCE_SCAN_REQUESTED`

### Requirement: Document Snapshot
The system SHALL store normalized document snapshots by content hash.

#### Scenario: Worker syncs changed document
- **WHEN** a connector reads Markdown content
- **THEN** the worker stores a document row and a snapshot containing the content hash
