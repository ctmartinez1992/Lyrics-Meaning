## Context

The catalog currently models bands, albums, and songs with minimal metadata and no normalized taxonomy for genre classification. Editors need richer, reusable genre data and the ability to tag both albums and songs with multiple genres. Songs also need explicit bonus-track status. The design must preserve current catalog hierarchy behavior and avoid storing values that can be derived (for example, album track counts).

## Goals / Non-Goals

**Goals:**
- Introduce a first-class `Genre` entity for reuse across catalog records.
- Support hierarchical genre relationships (genre/subgenre) without allowing invalid loops.
- Support many-to-many genre tagging for both albums and songs.
- Add song-level bonus-track metadata (`is_bonus`).
- Keep album-level and song-level genre tagging independent.

**Non-Goals:**
- Adding provider-specific IDs (for example Spotify/ISRC).
- Adding mood tagging, explicit-content flags, or AI taxonomy enrichment.
- Building genre-based search/filter UI in this change.
- Persisting derived album metrics such as total track count.

## Decisions

1. **Use a dedicated `Genre` model instead of free-text fields**
   - **Decision:** Create `Genre` with `name`, `slug`, optional `description`, and optional editorial controls.
   - **Rationale:** Normalized values prevent spelling drift and make taxonomy reusable.
   - **Alternative considered:** Comma-separated text on album/song. Rejected due to inconsistency and weak referential integrity.

2. **Represent subgenres with a nullable self-referential parent**
   - **Decision:** Add `parent_genre` as nullable self `ForeignKey` on `Genre`.
   - **Rationale:** Supports a flexible hierarchy and allows top-level genres.
   - **Alternative considered:** Separate hierarchy table or materialized path. Rejected for unnecessary complexity at current scale.

3. **Use many-to-many relations from both `Album` and `Song` to `Genre`**
   - **Decision:** Add independent M2M fields on both models.
   - **Rationale:** Song-level classification may diverge from album-level classification (bonus tracks, remixes, live cuts).
   - **Alternative considered:** Inherit song genres from album. Rejected because it cannot express divergence cleanly.

4. **Add explicit song bonus-track flag**
   - **Decision:** Add boolean `is_bonus` default `False` on `Song`.
   - **Rationale:** Simple, queryable semantic that does not affect track numbering behavior.
   - **Alternative considered:** Infer bonus status from title patterns. Rejected as brittle.

5. **Avoid storing derived values**
   - **Decision:** Do not add `total_tracks` to `Album`.
   - **Rationale:** Count is derivable from related songs and risks drift if persisted.

## Risks / Trade-offs

- **[Risk] Genre hierarchy cycles (A → B → C → A)** → **Mitigation:** Validate on save/admin form to reject cyclical parent assignments.
- **[Risk] Editorial inconsistency (near-duplicate genres)** → **Mitigation:** Enforce uniqueness on canonical identifiers and document naming conventions in admin guidance.
- **[Risk] Query overhead from extra joins** → **Mitigation:** Use prefetching/index defaults on relation tables where needed in read paths.
- **[Trade-off] Independent album/song tagging adds flexibility but increases curation effort** → **Mitigation:** Keep UI defaults lightweight and allow optional per-song overrides.

## Migration Plan

1. Add migration for new `Genre` model and `Song.is_bonus`.
2. Add migrations for `Album.genres` and `Song.genres` many-to-many relations.
3. Add model/admin validations for hierarchy integrity (no self-parent, no cycle).
4. Deploy schema changes with no required downtime.
5. Backfill is optional; existing records remain valid with empty genre relations and `is_bonus=False`.

Rollback strategy:
- If needed, remove new fields/tables via reverse migrations; existing core catalog records are unaffected.

## Open Questions

- Should sibling genres be unique by `(parent_genre, name)` only, or globally unique by name/slug?
- Do we need an explicit `is_active` field for deprecating genres without deleting them?
- Should admin workflows suggest album genres when creating songs, while still allowing divergence?
