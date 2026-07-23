## Why

The catalog model is currently too minimal to represent meaningful music taxonomy and release context for albums and songs. We need richer, structured metadata now so editors can classify content consistently and future discovery/analysis features can rely on first-class genre relationships.

## What Changes

- Add a dedicated `Genre` model to the catalog with stable identity fields and editorial metadata.
- Support hierarchical genres by allowing a genre to reference a parent genre (subgenre relationship).
- Allow albums to be tagged with multiple genres.
- Allow songs to be tagged with multiple genres.
- Add `is_bonus` to songs to identify bonus-track status.
- Keep album and song genre assignments independent so tracks can diverge from album-level genre tagging.
- Keep derived values out of storage (for example, do not store album total tracks).

## Capabilities

### New Capabilities
- `genre-taxonomy-management`: Staff can create and maintain reusable genre entities, including parent/child relationships for subgenres.

### Modified Capabilities
- `lyrics-catalog-management`: Extend band/album/song catalog management to support album and song multi-genre tagging and song bonus-track metadata.

## Impact

- **Affected code**: `catalog/models.py`, admin forms/configuration, catalog migrations, and related tests.
- **Data model**: New `Genre` table and new many-to-many join tables for album-genre and song-genre relationships; new song boolean field.
- **Behavioral impact**: Catalog editing workflows add genre taxonomy and multi-select genre tagging for albums and songs.
