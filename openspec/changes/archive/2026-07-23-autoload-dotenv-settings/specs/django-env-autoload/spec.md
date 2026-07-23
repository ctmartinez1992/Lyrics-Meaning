## ADDED Requirements

### Requirement: Settings bootstrap autoloads dotenv values
The system SHALL read repository `.env` values during Django settings initialization and make them available as process environment variables for command/runtime configuration.

#### Scenario: Management command resolves provider key from .env
- **WHEN** `TOGETHER_API_KEY` exists in `.env` and is not exported in the shell
- **THEN** Django settings initialization loads the value and analysis commands can access it through `os.getenv`

### Requirement: Exported environment values take precedence
The system SHALL NOT overwrite environment variables that are already set in the process when loading `.env`.

#### Scenario: Explicit env overrides .env
- **WHEN** a key exists both in process environment and `.env`
- **THEN** the pre-existing process environment value remains unchanged

### Requirement: Dotenv loading is failure-safe
The system SHALL ignore blank lines, comments, and malformed lines that do not follow `KEY=VALUE` format without failing settings import.

#### Scenario: Malformed line does not break startup
- **WHEN** `.env` contains unsupported or malformed lines
- **THEN** settings import continues and only valid key/value lines are applied
