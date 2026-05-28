## ADDED Requirements

### Requirement: Audit Trail
The system SHALL record audit events for scan, sync, claim, evidence, proposal, approval, rejection, and write-back activities.

#### Scenario: Workflow activity occurs
- **WHEN** the API or worker changes workflow state
- **THEN** an audit event records the action, aggregate, and payload
