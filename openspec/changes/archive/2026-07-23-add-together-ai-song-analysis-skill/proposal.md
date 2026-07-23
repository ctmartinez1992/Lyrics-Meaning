## Why

The current analysis pipeline only produces heuristic summary/themes and does not support deep, source-grounded interpretation. We need a proposal to define an implementation-ready path for a reusable AI skill that works across Copilot CLI, Cursor, and Claude Code CLI while persisting analysis output through Django models.

## What Changes

- Define a cross-CLI skill contract that accepts a song ID and runs the same analysis workflow in all three environments.
- Add a provider-backed in-depth analysis flow using Together AI inference, with web context collection for band/artist/album and canonical lyrics from the database.
- Extend analysis output requirements from basic summary/themes to structured in-depth sections plus citations.
- Keep asynchronous job lifecycle, idempotency, and publication behavior compatible with the existing analysis pipeline.

## Capabilities

### New Capabilities
- `cross-cli-song-analysis-skill`: A shared skill definition and execution contract for Copilot CLI, Cursor, and Claude Code CLI that triggers DB-backed song analysis by song ID.

### Modified Capabilities
- `lyrics-ai-analysis`: Expand output requirements to include in-depth structured analysis and source citations, and define Together AI as the inference provider target for this change.

## Impact

- Affected code: `analysis` app services/models/tests, command/entrypoint integration, public analysis rendering surface, and skill definition directories for `.github`, `.cursor`, and `.claude`.
- Affected systems: Together AI API integration, outbound web context fetching, and existing async worker processing.
- Dependencies: Together AI API credentials/configuration, robust JSON response validation, and migration-safe schema evolution for analysis results.
