## ADDED Requirements

### Requirement: Job Status
The system SHALL expose job status for long-running scan workflows.

#### Scenario: Dashboard checks scan job
- **WHEN** a client requests a job by identifier
- **THEN** the API returns its current status and timestamps

### Requirement: Outbox Retry Metadata
The system SHALL track attempts, availability, locking metadata, processed time, and error text for outbox events.

#### Scenario: Event handler fails
- **WHEN** an outbox event cannot be processed
- **THEN** the worker records the error and schedules retry metadata
