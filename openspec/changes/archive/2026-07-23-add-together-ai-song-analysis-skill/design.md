## Context

The repository already includes a Django `analysis` pipeline with asynchronous job lifecycle states and heuristic result generation. The requested change introduces provider-backed in-depth analysis and a reusable operator skill that can be used consistently in Copilot CLI, Cursor, and Claude Code CLI. The design must preserve existing job safety properties (idempotency, explicit status transitions, auditable result metadata) while expanding output depth and introducing outbound dependencies (Together AI inference and web context lookups).

## Goals / Non-Goals

**Goals:**
- Define a single analysis workflow contract driven by `song_id` and rooted in Django models.
- Specify Together AI as the inference provider for this change, including provider metadata capture.
- Expand persisted analysis output to structured in-depth sections and citations while keeping published-result lookup behavior stable.
- Define a cross-CLI skill surface that invokes the same workflow and persistence semantics across `.github`, `.cursor`, and `.claude` skill directories.

**Non-Goals:**
- Replacing the async job state machine or moving analysis to synchronous request-time execution.
- Building a generalized multi-provider routing layer in this change.
- Expanding into user-generated annotation/discussion workflows.

## Decisions

1. **Provider-specific inference path for Together AI**
   - Decision: Integrate Together AI chat-completion inference directly in the analysis execution service for this change.
   - Rationale: The user explicitly selected Together AI and the scope is one concrete provider, not provider abstraction.
   - Alternatives considered:
     - Abstract multi-provider layer now: rejected due to extra complexity without immediate requirement.
     - Keep heuristic-only analysis: rejected because it cannot meet in-depth analysis goals.

2. **Structured persisted output (not summary-only)**
   - Decision: Persist summary, themes, structured analysis sections, citations, and run metadata in `AnalysisResult`.
   - Rationale: Public rendering and auditability need machine-readable structure, not a single opaque text blob.
   - Alternatives considered:
     - Long-form plain text only: rejected because it weakens rendering flexibility and downstream QA.
     - Store everything in provider metadata: rejected due to poor domain clarity.

3. **Context composition from DB + web sources**
   - Decision: Build prompts from canonical lyrics and catalog metadata in DB, plus bounded online context for band/artist/album with source records.
   - Rationale: In-depth interpretation quality improves with reliable contextual grounding and explicit citations.
   - Alternatives considered:
     - DB-only context: rejected for weaker historical/cultural interpretation coverage.
     - Unbounded web crawling: rejected due to reliability and cost risk.

4. **Cross-CLI skill parity**
   - Decision: Keep identical skill intent/contract in `.github`, `.cursor`, and `.claude`.
   - Rationale: Consistent operator behavior prevents divergence between developer tools.
   - Alternatives considered:
     - Single-surface skill only: rejected because user requested all three environments.

## Risks / Trade-offs

- **[Provider output schema drift]** → Mitigation: strict JSON validation and explicit failed job state with reason.
- **[External dependency latency/failures]** → Mitigation: request timeouts, bounded source counts, and retry-safe job processing.
- **[Analysis quality variance by model revision]** → Mitigation: persist model identifier and prompt version per result for repeatability.
- **[Higher implementation complexity vs MVP heuristic]** → Mitigation: retain existing async/job architecture and change only analysis-specific surfaces.

## Migration Plan

1. Define new/modified spec requirements for `lyrics-ai-analysis` and new `cross-cli-song-analysis-skill` capability.
2. Implement model/service/template/test deltas behind existing job orchestration path.
3. Add/update skill files in all three directories with the same command contract.
4. Validate analysis triggering, failure behavior, and public rendering for no-result and published-result states.
5. Rollback strategy: keep backward-compatible schema migration strategy and allow disabling provider-backed execution by configuration while preserving job records.

## Open Questions

- Which Together model should be the default production model versus fallback model for cost control?
- Should source collection remain provider-adjacent in analysis service or move to a dedicated reusable context module in a follow-up change?
