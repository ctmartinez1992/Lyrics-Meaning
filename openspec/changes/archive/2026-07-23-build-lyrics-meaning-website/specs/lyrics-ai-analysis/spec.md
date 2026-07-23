## ADDED Requirements

### Requirement: Admins trigger lyric analysis jobs
The system SHALL allow authenticated staff users to enqueue analysis jobs for a selected song and lyric version.

#### Scenario: Trigger analysis from admin surface
- **WHEN** an admin requests analysis for a song lyric version
- **THEN** the system creates a queued analysis job with references to song and lyric version

### Requirement: Analysis jobs run asynchronously with explicit lifecycle states
The system SHALL process analysis jobs asynchronously and persist lifecycle states including queued, running, succeeded, failed, and canceled.

#### Scenario: Successful analysis completion
- **WHEN** a worker finishes analysis without errors
- **THEN** the job status becomes succeeded and the output is persisted

#### Scenario: Analysis failure handling
- **WHEN** a worker encounters an unrecoverable provider or validation error
- **THEN** the job status becomes failed and an error reason is recorded

### Requirement: Analysis outputs are versioned and auditable
The system SHALL store generated summary/themes with run metadata including model identifier, prompt version, timestamps, and originating job ID.

#### Scenario: Display latest published analysis
- **WHEN** multiple analysis runs exist for a song
- **THEN** the system can resolve and display the latest published successful result
