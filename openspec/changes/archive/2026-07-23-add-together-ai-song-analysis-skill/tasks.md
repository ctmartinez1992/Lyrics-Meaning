## 1. Analysis data and provider integration

- [x] 1.1 Extend `analysis.AnalysisResult` schema and migrations for structured in-depth analysis sections and citation storage
- [x] 1.2 Implement Together AI inference client integration with env-driven model/API configuration and strict JSON response validation
- [x] 1.3 Persist provider/model metadata, prompt version, and failure reasons in existing async job lifecycle transitions

## 2. Context enrichment and pipeline orchestration

- [x] 2.1 Implement bounded online context collection for band/artist/album with normalized citation records
- [x] 2.2 Refactor `analysis.services.process_job` to compose DB lyrics + metadata + online context into Together AI prompts
- [x] 2.3 Preserve idempotency, cancellation checks, and retry-safe behavior while swapping heuristic generation for provider-backed generation

## 3. Cross-CLI skill parity and UX surfaces

- [x] 3.1 Add equivalent `song-in-depth-analysis` skill definitions in `.github/skills`, `.cursor/skills`, and `.claude/skills` with a shared song-ID contract
- [x] 3.2 Add/update the analysis trigger entrypoint contract used by skills to run song analysis through Django models
- [x] 3.3 Update public song analysis rendering to safely display structured in-depth sections and citations while preserving empty-state behavior

## 4. Verification and hardening

- [x] 4.1 Add/adjust tests for Together AI success/failure paths, malformed model output handling, and external context fetch failure handling
- [x] 4.2 Add/adjust tests for structured analysis persistence and latest published result retrieval behavior
- [x] 4.3 Add/adjust cross-surface integration checks to ensure the same skill behavior contract across Copilot CLI, Cursor, and Claude Code CLI
