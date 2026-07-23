## ADDED Requirements

### Requirement: Lyric lines support separator semantics
The system SHALL allow lyric lines to be marked as separators so canonical lyric sequencing can include intentional spacing lines.

#### Scenario: Create separator lyric line
- **WHEN** an admin creates a lyric line with `is_separator` set to true
- **THEN** the lyric line is persisted in the lyric version sequence as a separator line

### Requirement: Separator lyric lines have conditional text requirements
The system SHALL require text for non-separator lyric lines and allow empty text for separator lyric lines.

#### Scenario: Reject empty non-separator line
- **WHEN** a lyric line is created or updated with `is_separator` set to false and empty text
- **THEN** the system rejects the record as invalid

#### Scenario: Allow empty separator line
- **WHEN** a lyric line is created or updated with `is_separator` set to true and empty text
- **THEN** the system accepts the record as valid
