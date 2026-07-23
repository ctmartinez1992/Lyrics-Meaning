## Context

The current catalog model stores canonical lyrics in two forms: `LyricVersion.lyrics_text` (full text) and `LyricLine` (ordered line-level records). Today each `LyricLine` expects meaningful text content, which makes intentional blank spacer lines hard to represent without fake placeholder text. Public song rendering already prefers line-level rendering when lines exist, so introducing separator semantics belongs in the existing `LyricLine` abstraction rather than in view-only logic.

## Goals / Non-Goals

**Goals:**
- Add first-class separator support to lyric lines while preserving existing line ordering behavior.
- Enforce clear validation rules for when lyric text is required versus optional.
- Keep public lyric rendering deterministic: separator lines render as spacing, normal lines render as numbered text.
- Maintain compatibility with existing lyric data and current analysis display behavior.

**Non-Goals:**
- Introducing rich formatting markup or section-label semantics beyond separator spacing.
- Changing `LyricVersion` versioning semantics or analysis job orchestration.
- Retrofitting historical lyric data beyond compatibility with new defaults.

## Decisions

1. **Represent separators directly on `LyricLine`**
   - Decision: Add `is_separator` boolean field to `LyricLine` with default `False`.
   - Rationale: Keeps separators as first-class ordered records, preserving stable line identity and sequence.
   - Alternatives considered:
     - Derive blank lines from `lyrics_text`: rejected because line structure becomes parsing-dependent and unstable.
     - Store separators in a separate table: rejected due to unnecessary complexity and join overhead.

2. **Apply conditional text validation**
   - Decision: Keep `text` present for normal lines and optional for separator lines via model-level validation.
   - Rationale: Matches authoring intent while preventing empty non-separator lines.
   - Alternatives considered:
     - Make `text` always optional: rejected because it weakens lyric data quality guarantees.
     - Keep `text` always required and use placeholders: rejected because placeholders pollute canonical content.

3. **Render separators as visual spacing**
   - Decision: Update public song template rendering branch so separator lines output spacing-only markup while preserving list order.
   - Rationale: Separators are semantic spacing, not content; rendering should reflect this directly.
   - Alternatives considered:
     - Omit separator lines during rendering: rejected because it changes authored lyric structure.
     - Render empty numbered lines: rejected because visible numbering for separators is noisy UX.

4. **Keep analysis behavior unchanged**
   - Decision: No changes to analysis result retrieval/display in this change.
   - Rationale: Separator support is a catalog/rendering concern and should remain narrowly scoped.

## Risks / Trade-offs

- **[Validation drift between admin/forms and model]** → Mitigation: enforce rules in model validation so all entry paths share behavior.
- **[Template branching introduces inconsistent line presentation]** → Mitigation: keep rendering logic binary (`is_separator` vs standard text line) with predictable markup.
- **[Existing assumptions about non-empty text in downstream code]** → Mitigation: audit lyric-line consumers and gate text usage behind `is_separator` checks where needed.
- **[Future ambiguity about separator meaning]** → Mitigation: document separators as spacing-only, not structural section metadata.

## Migration Plan

1. Add schema migration for `LyricLine.is_separator` (default `False`) and adjust `text` null/blank behavior as required by validation rules.
2. Update model validation logic and any admin/form behavior that persists `LyricLine`.
3. Update public song lyric rendering to display separator spacing.
4. Update tests for catalog validation and public lyric rendering scenarios.
5. Deploy migration and application changes together; rollback by reverting app changes and schema migration if necessary.

## Open Questions

- Should separator lines consume visible line numbers in UI, or should numbering skip separators while preserving storage order?
- Should admin editing UI label separator lines with dedicated helper text to reduce accidental misuse?
