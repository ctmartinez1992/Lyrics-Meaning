## ADDED Requirements

### Requirement: Cross-CLI song analysis skill contract
The system SHALL provide an equivalent song-analysis skill contract for Copilot CLI, Cursor, and Claude Code CLI that accepts a song ID and runs the same Django-backed analysis workflow.

#### Scenario: Trigger by song ID
- **WHEN** an operator runs the skill with a valid `song_id`
- **THEN** the system resolves the target song and lyric version from Django models and starts analysis using the shared workflow contract

#### Scenario: Consistent behavior across tooling surfaces
- **WHEN** the skill is executed from any supported CLI surface
- **THEN** the workflow inputs, persistence behavior, and success/failure output semantics remain equivalent
