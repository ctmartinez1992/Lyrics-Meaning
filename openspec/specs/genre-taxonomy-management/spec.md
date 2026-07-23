## ADDED Requirements

### Requirement: Admins manage reusable genres
The system SHALL allow authenticated staff users to create, update, and archive reusable genre entities with canonical identity fields.

#### Scenario: Create a top-level genre
- **WHEN** an admin creates a genre with a unique name
- **THEN** the system persists the genre as a top-level taxonomy node

#### Scenario: Maintain stable genre identity
- **WHEN** an admin edits a genre description or hierarchy position
- **THEN** the system preserves the genre identity used by related albums and songs

### Requirement: Genres support hierarchical subgenre relationships
The system SHALL allow a genre to be assigned as a subgenre of another genre using a nullable parent relationship while preventing invalid hierarchy states.

#### Scenario: Assign parent genre
- **WHEN** an admin assigns a valid parent genre to a genre
- **THEN** the system stores the child-to-parent relationship

#### Scenario: Prevent self-parent assignment
- **WHEN** an admin attempts to set a genre as its own parent
- **THEN** the system rejects the change with a validation error

#### Scenario: Prevent cyclical hierarchy
- **WHEN** an admin attempts to create a parent chain that introduces a cycle
- **THEN** the system rejects the change with a validation error
