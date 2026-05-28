## ADDED Requirements

### Requirement: Source Registration
The system SHALL allow users to register local Markdown knowledge sources with provider metadata.

#### Scenario: Register local Markdown source
- **WHEN** a client submits a source name, provider type, and root path
- **THEN** the API persists the source and returns its identifier

### Requirement: Source Listing
The system SHALL list configured sources for the dashboard.

#### Scenario: List configured sources
- **WHEN** a client requests sources
- **THEN** the API returns all known sources with provider type and status metadata
