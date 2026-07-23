## Why

Running Django management commands currently depends on shell-exported environment variables, which causes failures when required keys are only present in `.env`. We need a predictable local configuration loading behavior so commands can run without manual export steps.

## What Changes

- Add repository-level `.env` autoload behavior during Django settings initialization for local workflows.
- Define precedence rules so explicitly exported environment variables continue to override `.env` values.
- Document supported `.env` parsing scope and failure-safe behavior for missing or malformed lines.
- Add validation coverage proving management commands can resolve required provider keys through settings initialization.

## Capabilities

### New Capabilities
- `django-env-autoload`: Automatic loading of local `.env` values into Django process environment during settings bootstrapping.

### Modified Capabilities
- None.

## Impact

- Affected code: `config/settings` bootstrap path and related configuration tests.
- Affected systems: local developer runtime for Django management commands and service entrypoints.
- Dependencies: no new external packages required if implemented with standard library parsing.
