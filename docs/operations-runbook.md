# Deployment and Incident Runbook

## Deployment flow
1. Apply Terraform changes in target environment (`infra/environments/<env>`).
2. Deploy Django web container.
3. Deploy worker container that runs `python manage.py process_analysis_jobs --limit <n>`.
4. Run migrations: `python manage.py migrate`.
5. Confirm `/healthz/` and CloudWatch log streams for web and worker.

## Rollback strategy
1. Roll app image to previous stable revision.
2. Keep database schema backward-compatible by using additive migrations first.
3. If a migration causes issues, deploy app rollback and run explicit reverse migration only when safe.
4. Temporarily disable analysis trigger surface by restricting staff access or scaling worker to zero.

## Analysis pipeline incidents
- **Jobs stuck queued**: check worker deployment and task role permissions.
- **Jobs repeatedly failing**: inspect `analysis_job_failed` log lines and `error_reason` in admin.
- **Unexpected analysis output**: enqueue a new run after prompt/model update, then verify latest published result.

## Observability checkpoints
- Web 5xx alarm from `modules/app_runtime` should remain below threshold.
- Worker and web log groups:
  - `/lyrics-meaning/<env>/web`
  - `/lyrics-meaning/<env>/worker`

## Local environment bootstrap
- Django settings autoload repository `.env` during settings initialization.
- Precedence rule: already-exported process environment variables win over `.env` values.
- Supported `.env` line format is `KEY=VALUE`; blank lines, comments (`#`), and malformed lines are ignored.
