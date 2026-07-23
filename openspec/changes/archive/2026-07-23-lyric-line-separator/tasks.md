## 1. Schema and model updates

- [x] 1.1 Add a migration for `LyricLine.is_separator` with default `False`, and adjust `text` field persistence constraints to support empty separator lines.
- [x] 1.2 Update `LyricLine` model validation so non-separator lines require text and separator lines allow empty text.
- [x] 1.3 Ensure admin/data-entry surfaces for lyric lines expose `is_separator` and align with model validation outcomes.

## 2. Public lyric rendering updates

- [x] 2.1 Update song detail lyric rendering logic/templates so separator lines render as visual spacing while preserving line sequence.
- [x] 2.2 Keep existing fallback behavior for versions without structured lines (`lyrics_text`) unchanged.

## 3. Test coverage

- [x] 3.1 Add/adjust model tests for conditional lyric line validation (`is_separator` true vs false).
- [x] 3.2 Add/adjust public site tests to verify separator lines render as spacing and standard lines still render text/numbering.
