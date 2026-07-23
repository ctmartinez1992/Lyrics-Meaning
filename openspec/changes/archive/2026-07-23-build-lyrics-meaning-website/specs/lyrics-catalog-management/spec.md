## ADDED Requirements

### Requirement: Admins manage music catalog hierarchy
The system SHALL allow authenticated staff users to create, update, and archive bands, albums, and songs while preserving hierarchy integrity.

#### Scenario: Create song under album
- **WHEN** an admin creates a song and selects a valid album
- **THEN** the song is persisted and linked to that album and its band

#### Scenario: Prevent orphaned catalog nodes
- **WHEN** an admin attempts to delete a band or album that has dependent records
- **THEN** the system prevents hard deletion and requires an archive action

### Requirement: Admins manage canonical lyrics with versioning
The system SHALL store lyrics as versioned records for each song, including full text and structured line-level segments.

#### Scenario: Publish new lyric version
- **WHEN** an admin submits updated lyrics for an existing song
- **THEN** the system creates a new lyric version and marks exactly one version as current

#### Scenario: Preserve prior lyric versions
- **WHEN** a new lyric version is published
- **THEN** prior versions remain stored and queryable for audit and re-analysis
