## 1. Catalog schema updates

- [x] 1.1 Add `Genre` model with canonical fields (`name`, `slug`, optional `description`) and self-referential `parent_genre`.
- [x] 1.2 Add hierarchy validation rules to `Genre` (no self-parent, no cyclical ancestry).
- [x] 1.3 Add `is_bonus` boolean field to `Song` with default `False`.
- [x] 1.4 Add many-to-many relations for `Album.genres` and `Song.genres`.
- [x] 1.5 Create and review Django migrations for `Genre`, song field updates, and new relation tables.

## 2. Admin and validation behavior

- [x] 2.1 Update catalog admin configuration to manage genres, parent/subgenre relationships, and album/song genre assignment.
- [x] 2.2 Ensure admin-level validation surfaces clear errors for invalid genre hierarchy edits.
- [x] 2.3 Confirm album and song genre assignments remain independent in forms and persistence behavior.

## 3. Test coverage and regression safety

- [x] 3.1 Add model tests for genre hierarchy constraints, including self-parent and cycle rejection.
- [x] 3.2 Add model/admin tests for multi-genre assignment on albums and songs.
- [x] 3.3 Add tests for `Song.is_bonus` default and explicit true/false persistence.
- [x] 3.4 Add tests confirming no persisted album `total_tracks` field is introduced and track totals remain derivable from related songs.
