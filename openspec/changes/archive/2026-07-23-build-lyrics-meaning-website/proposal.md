## Why

People searching for song meaning need a reliable place where lyrics context and interpretation live together, instead of fragmented forum threads and low-quality summaries. We need an MVP now to validate demand with a focused, operable platform before expanding into full community discussion features.

## What Changes

- Build a Django-based lyrics meaning website with Tailwind + basic HTML templates for public browsing.
- Introduce structured domain data for bands, albums, songs, and lyrics managed by admins.
- Add background AI analysis jobs that admins trigger manually and that produce a short summary plus key themes for each song.
- Provide anonymous read access for public users and authenticated admin access for content and analysis management.
- Define AWS infrastructure and deployment topology with Terraform, using Postgres as the system of record.
- Explicitly defer comments/discussion to a later phase.

## Capabilities

### New Capabilities
- `lyrics-catalog-management`: Admins can create and maintain canonical band, album, song, and lyric records.
- `public-lyrics-experience`: Anonymous visitors can browse and read lyrics plus available AI meaning analysis.
- `lyrics-ai-analysis`: Admins can trigger asynchronous AI analysis for songs, track job status, and publish summary/theme outputs.
- `platform-infrastructure-baseline`: The platform can run on AWS with Terraform-managed infrastructure, Postgres persistence, and operational baseline controls.

### Modified Capabilities
- None.

## Impact

- Affected code: new Django apps for catalog and analysis domains, admin interfaces, public template views, and worker/job orchestration.
- Affected systems: AWS runtime services, Postgres database, secrets/config management, logging/monitoring setup.
- Dependencies: Django ecosystem packages, Postgres driver, background job stack, AI provider SDK, Terraform AWS provider modules.
