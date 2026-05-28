## ADDED Requirements

### Requirement: Stub Evidence Verification
The system SHALL verify high-risk claims through a research interface that can return deterministic stub evidence in MVP.

#### Scenario: High-risk claim is verified
- **WHEN** the worker processes `CLAIM_VERIFICATION_REQUESTED`
- **THEN** it stores evidence items linked to the claim without requiring external API keys

### Requirement: Evidence Traceability
The system SHALL keep evidence records available to the patch review workflow.

#### Scenario: Patch proposal references evidence
- **WHEN** a patch proposal is created
- **THEN** it includes citation references to stored evidence items
