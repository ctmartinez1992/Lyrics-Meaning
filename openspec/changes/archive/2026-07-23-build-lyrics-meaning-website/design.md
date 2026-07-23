## Context

The MVP is a new Django web platform focused on storing music catalog data and presenting AI-assisted lyric meaning. There is no existing application code in this repository, so the design must define both product architecture and delivery boundaries. The selected stack is Django, Postgres, Tailwind, AWS, and Terraform, with background processing for AI analysis.

Key constraints:
- MVP scope is intentionally narrow: no public discussion/comments yet.
- Content quality must be controlled by admins/editors only.
- AI analysis is admin-triggered and asynchronous.
- Public users can read without authentication.

## Goals / Non-Goals

**Goals:**
- Deliver a production-capable Django architecture for catalog + lyric meaning analysis.
- Keep complexity low via a modular monolith with clear app boundaries.
- Provide reliable asynchronous analysis jobs with explicit status and retry behavior.
- Codify AWS infrastructure and baseline operations in Terraform.

**Non-Goals:**
- Building comments, threaded discussions, or community moderation workflows in MVP.
- Supporting user-submitted lyric edits in MVP.
- Implementing fully automated analysis on publish in MVP.
- Implementing advanced line-by-line or reference-heavy AI interpretation in MVP.

## Decisions

1. **Modular monolith in Django**
   - Decision: Use a single Django project with domain apps (`catalog`, `analysis`, `public_site`, `core`).
   - Rationale: Faster delivery and simpler operations for MVP while preserving separation for future extraction.
   - Alternatives considered:
     - Microservices: rejected due to higher operational overhead and slower MVP iteration.
     - Single flat app: rejected due to poor long-term maintainability.

2. **Normalized relational model in Postgres**
   - Decision: Model `Band -> Album -> Song -> LyricVersion -> LyricLine`, plus AI analysis entities.
   - Rationale: Strong integrity guarantees and queryability for hierarchical music data.
   - Alternatives considered:
     - Denormalized JSON-heavy model: rejected for weaker constraints and harder indexing.
     - Non-relational database: rejected because relationships are first-class.

3. **Admin-triggered asynchronous AI pipeline**
   - Decision: Persist `AnalysisJob` records and process them in background workers; store model/prompt metadata with each result.
   - Rationale: Avoid blocking admin workflows and preserve auditability/reproducibility.
   - Alternatives considered:
     - Synchronous request-time analysis: rejected due to timeout/risk/cost unpredictability.
     - Auto-analysis on publish: rejected for MVP cost and control reasons.

4. **Anonymous public read + restricted admin surface**
   - Decision: Public endpoints are read-only and unauthenticated; Django admin requires authenticated staff.
   - Rationale: Lowest-friction discovery experience with controlled write operations.
   - Alternatives considered:
     - Full user account system at launch: rejected as unnecessary for MVP goals.

5. **Terraform-managed AWS baseline**
   - Decision: Define infrastructure modules for network, app runtime, Postgres, secrets, logging/metrics, and IAM boundaries.
   - Rationale: Reproducible environments and safer operational changes.
   - Alternatives considered:
     - Manual console provisioning: rejected due to drift risk.
     - Ad-hoc scripts: rejected for weak change management.

## Risks / Trade-offs

- **[AI quality variance]** → Mitigation: store run metadata and allow re-run with updated prompt/model versions.
- **[Operational complexity from async workers]** → Mitigation: start with one queue/workload class and clear job state machine.
- **[Licensing/content rights concerns for lyrics data]** → Mitigation: add explicit source/provenance fields and admin policy checks.
- **[Schema rigidity as features evolve]** → Mitigation: keep lyric/version abstractions and additive migration strategy.
- **[Cost unpredictability from model usage]** → Mitigation: admin-only trigger, rate limits per batch, and job-level usage metrics.

## Migration Plan

1. Provision AWS baseline infrastructure via Terraform for dev/staging/prod.
2. Boot Django project and apply initial migrations for catalog + analysis models.
3. Configure worker runtime and queue backend; deploy web and worker services.
4. Seed admin users and initial catalog content.
5. Enable public browsing routes and analysis display once initial analyses are generated.
6. Rollback strategy: deploy app revisions independently from schema migrations; use backward-compatible additive migrations and disable analysis trigger endpoint if worker incidents occur.

## Open Questions

- Which AWS runtime pairing should be default for MVP (e.g., ECS/Fargate vs. EC2-managed services)?
- Which queue backend should be used first for job processing?
- Which AI provider/model family should be primary, and what are fallback contracts?
