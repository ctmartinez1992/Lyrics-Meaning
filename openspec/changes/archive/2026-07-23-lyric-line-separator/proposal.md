## Why

Lyric formatting sometimes includes intentional blank spacer lines that separate sections, but the current model requires text for every stored line. We need a first-class way to represent separators so canonical lyrics preserve structure without inserting fake content.

## What Changes

- Add a boolean separator flag to lyric lines so a line can be explicitly marked as a spacer.
- Update lyric-line validation rules so text is required for normal lines and optional for separator lines.
- Update public lyric rendering so separator lines display as visual spacing while preserving line order.
- Keep separator lines as persisted lyric lines, not derived presentation-only artifacts.

## Capabilities

### New Capabilities
- `lyric-line-separators`: Represent, validate, and render separator lyric lines while preserving canonical sequence.

### Modified Capabilities
- `lyrics-catalog-management`: Canonical lyric line requirements now support separator lines with conditional text requirements.
- `public-lyrics-experience`: Song lyric rendering requirements now include visible spacing behavior for separator lines.

## Impact

- Affected code: `catalog` models/migrations/admin flows for lyric line data entry, `public_site` lyric rendering, and related tests.
- Data model impact: `LyricLine` schema and validation behavior change.
- API/view impact: Song page lyric display logic changes for separator lines.
- Operational impact: Existing lyrics remain valid; newly created separator lines can omit text.
