## ADDED Requirements

### Requirement: Patch Proposal Review
The system SHALL create patch proposals that require explicit user approval or rejection.

#### Scenario: Patch proposal exists
- **WHEN** the dashboard requests patch proposals
- **THEN** pending proposals are returned with original text, proposed text, and citation identifiers

### Requirement: Approved Patch Write-back
The system SHALL write approved patches through the source connector and never apply patches automatically.

#### Scenario: User approves patch
- **WHEN** a client approves a patch proposal
- **THEN** the API records the decision and enqueues `PATCH_APPLICATION_REQUESTED`
