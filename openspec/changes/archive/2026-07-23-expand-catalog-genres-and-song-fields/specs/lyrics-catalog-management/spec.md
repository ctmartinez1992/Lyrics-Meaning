## ADDED Requirements

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
