---
name: song-in-depth-analysis
description: Run in-depth AI song analysis by song ID. Fetches online context, analyzes lyrics from Django models, and persists structured analysis output with citations.
license: MIT
compatibility: Django project with analysis and catalog apps.
---

Perform in-depth analysis for a song using Together AI inference and persist the result through Django models.

## Inputs
- `song_id` (required): ID of the `catalog.Song` row to analyze.
- `lyric_version_id` (optional): Explicit lyric version. If omitted, use current lyric version.
- `refresh` (optional): When true, force reprocessing an existing job/result.

## Steps
1. Validate the song exists and resolve lyric version (`is_current=True` when no explicit lyric version is provided).
2. Fetch live web context for band/artist/album and normalize citation records.
3. Run Together AI in-depth analysis against:
   - canonical lyrics from the database
   - song/album/band metadata from the database
   - gathered web context
4. Persist/update:
   - `analysis.AnalysisJob` lifecycle state
   - `analysis.AnalysisResult` summary, key themes, detailed analysis sections, citations, provider metadata
5. Return the final job ID, status, and result ID.

## Command entrypoint
Use:
```bash
python manage.py analyze_song --song-id <song_id> [--lyric-version-id <id>] [--refresh]
```

## Required environment
- `TOGETHER_API_KEY`
- Optional: `TOGETHER_MODEL` (default: `meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo`)

## Expected output
Concise operator summary including:
- song ID and lyric version ID used
- analysis job ID + final status
- analysis result ID (if succeeded)
- failure reason (if failed)
