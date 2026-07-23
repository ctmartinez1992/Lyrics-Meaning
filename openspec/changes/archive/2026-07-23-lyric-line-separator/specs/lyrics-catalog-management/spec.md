## MODIFIED Requirements

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
