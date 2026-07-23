## MODIFIED Requirements

### Requirement: Song pages show canonical lyrics and analysis state
The system SHALL display the current canonical lyrics and the latest available AI analysis summary/themes for each song, rendering separator lyric lines as visual spacing while preserving lyric order.

#### Scenario: Analysis available
- **WHEN** a visitor opens a song that has a published analysis result
- **THEN** the page shows lyrics, analysis summary, and key themes

#### Scenario: Analysis unavailable
- **WHEN** a visitor opens a song with no completed analysis
- **THEN** the page shows lyrics and a clear "analysis not yet available" state

#### Scenario: Separator lines render as space
- **WHEN** current canonical lyrics include separator lines
- **THEN** the song page renders those lines as blank visual spacing rather than textual lyric content
