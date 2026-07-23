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
The system SHALL store lyrics as versioned records for each song, including full text and structured line-level segments, where line segments can be either textual lyric lines or separator lines.

#### Scenario: Publish new lyric version
- **WHEN** an admin submits updated lyrics for an existing song
- **THEN** the system creates a new lyric version and marks exactly one version as current

#### Scenario: Preserve prior lyric versions
- **WHEN** a new lyric version is published
- **THEN** prior versions remain stored and queryable for audit and re-analysis

#### Scenario: Persist separator lines in canonical sequence
- **WHEN** an admin saves line-level lyrics that include separator lines
- **THEN** the system persists separator lines in the same ordered sequence as textual lines for that lyric version

### Requirement: Admins assign multiple genres to albums and songs
The system SHALL allow authenticated staff users to assign zero or more genres to each album and each song using many-to-many relationships.

#### Scenario: Assign multiple genres to an album
- **WHEN** an admin edits an album and selects multiple genres
- **THEN** the system persists all selected album-genre associations

#### Scenario: Assign multiple genres to a song
- **WHEN** an admin edits a song and selects multiple genres
- **THEN** the system persists all selected song-genre associations

#### Scenario: Song genres differ from album genres
- **WHEN** a song is assigned genres that are different from its album's genres
- **THEN** the system accepts and preserves both sets independently

### Requirement: Songs include explicit bonus-track metadata
The system SHALL store whether a song is a bonus track as structured boolean metadata.

#### Scenario: Mark song as bonus track
- **WHEN** an admin marks a song as bonus
- **THEN** the system persists the song with bonus-track status set to true

#### Scenario: Default non-bonus status
- **WHEN** a new song is created without explicitly setting bonus status
- **THEN** the system persists the song with bonus-track status set to false

### Requirement: Derived album track totals are not persisted
The system SHALL treat album track totals as derived data computed from related songs rather than stored catalog fields.

#### Scenario: Add song without updating album total field
- **WHEN** an admin creates a new song under an album
- **THEN** the system does not require or persist an album total-tracks value
