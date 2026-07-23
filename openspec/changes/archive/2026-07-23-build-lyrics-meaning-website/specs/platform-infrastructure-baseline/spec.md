## ADDED Requirements

### Requirement: Infrastructure is provisioned through Terraform
The platform SHALL define and provision AWS infrastructure through Terraform modules and environment-specific variables.

#### Scenario: Reproducible environment provisioning
- **WHEN** infrastructure is applied for a target environment
- **THEN** networking, runtime, database, and required IAM resources are created from versioned Terraform code

### Requirement: Postgres is the authoritative transactional store
The system SHALL use PostgreSQL as the primary data store for catalog and analysis records.

#### Scenario: Application persistence
- **WHEN** the web app and workers read or write domain data
- **THEN** all transactional domain operations use Postgres as the source of truth

### Requirement: Operational baseline supports production diagnostics
The platform SHALL emit structured logs and service health signals sufficient to diagnose failed web requests and failed analysis jobs.

#### Scenario: Failed analysis observability
- **WHEN** an analysis job fails
- **THEN** operators can identify the failure from centralized logs and job status metadata
