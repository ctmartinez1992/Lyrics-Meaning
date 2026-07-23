## 1. Project foundation

- [x] 1.1 Initialize Django project structure with apps for `core`, `catalog`, `analysis`, and `public_site`
- [x] 1.2 Configure environment-driven settings for local/dev/prod, including Postgres connectivity and secret loading
- [x] 1.3 Add Tailwind + base HTML template pipeline for shared layout, typography, and page shells

## 2. Catalog and lyric data model

- [x] 2.1 Implement Postgres-backed models and migrations for Band, Album, Song, LyricVersion, and LyricLine with relational constraints
- [x] 2.2 Configure Django admin for catalog CRUD with staff-only access and archive-safe behavior for dependent records
- [x] 2.3 Implement canonical lyric version selection rules so exactly one current lyric version exists per song

## 3. Public lyrics experience

- [x] 3.1 Implement anonymous-read routes and views for band, album, and song pages
- [x] 3.2 Render song detail pages with canonical lyrics and explicit analysis availability states
- [x] 3.3 Add tests for anonymous access and content rendering behavior across catalog hierarchy

## 4. AI analysis pipeline

- [x] 4.1 Implement analysis domain models and migrations for AnalysisJob and AnalysisResult with run metadata fields
- [x] 4.2 Implement staff-only trigger action to enqueue analysis jobs for a selected song and lyric version
- [x] 4.3 Implement asynchronous worker processing with lifecycle transitions (queued, running, succeeded, failed, canceled)
- [x] 4.4 Persist summary + key theme outputs and expose latest published successful result to public song pages
- [x] 4.5 Add failure logging and retry-safe job handling with idempotency protections

## 5. AWS and Terraform baseline

- [x] 5.1 Create Terraform modules for networking, app runtime, Postgres, IAM, and secret management
- [x] 5.2 Define environment stacks (dev/staging/prod) and remote state conventions
- [x] 5.3 Provision logging and health observability baseline for web and worker services

## 6. Security and operational hardening

- [x] 6.1 Enforce staff authentication and permissions for all write/trigger/admin surfaces
- [x] 6.2 Add structured operational telemetry for request failures and analysis job failures
- [x] 6.3 Document deployment, rollback, and runbook procedures for incidents in analysis processing
