## ADDED Requirements

### Requirement: Claim Extraction
The system SHALL extract factual claim candidates from document snapshots through a replaceable service interface.

#### Scenario: Snapshot contains dated sentence
- **WHEN** a Markdown snapshot contains a sentence with a year or time-sensitive phrase
- **THEN** the worker records a claim linked to that snapshot

### Requirement: Staleness Classification
The system SHALL classify claims by staleness risk.

#### Scenario: Claim uses time-sensitive wording
- **WHEN** a claim includes phrases such as latest, current, today, or as of
- **THEN** the claim is classified as high risk
