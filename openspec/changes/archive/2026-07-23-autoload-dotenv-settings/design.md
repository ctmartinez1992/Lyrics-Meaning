## Context

The project reads configuration from `os.getenv` but does not automatically ingest values from `.env`, which forces manual shell export and causes command-time failures for keys like `TOGETHER_API_KEY`. The desired behavior is reliable local startup for management commands without adding user-side bootstrapping commands.

## Goals / Non-Goals

**Goals:**
- Load `.env` automatically during Django settings bootstrap when running local workflows.
- Preserve explicit environment variable precedence over `.env` values.
- Keep implementation dependency-free using the Python standard library.
- Ensure non-critical `.env` formatting issues do not crash settings import.

**Non-Goals:**
- Replacing production secret management with `.env` files.
- Implementing full `.env` specification parsing (exports, interpolation, multiline).
- Introducing external libraries solely for dotenv loading.

## Decisions

1. **Load `.env` in `config/settings/__init__.py` before environment selection**
   - Decision: Parse `.env` and inject missing keys into `os.environ` before importing env-specific settings modules.
   - Rationale: This ensures every settings profile (`local/dev/prod`) gets consistent env availability.
   - Alternatives considered:
     - Load in `manage.py` only: rejected because it misses non-manage entrypoints.
     - Add `python-dotenv`: rejected to avoid extra dependency for a narrow use case.

2. **Use non-overriding semantics**
   - Decision: Use `os.environ.setdefault(key, value)` for parsed entries.
   - Rationale: Explicitly exported variables should remain the highest-priority source.
   - Alternatives considered:
     - Always overwrite env: rejected due to surprising behavior and reduced operator control.

3. **Implement minimal, safe parser**
   - Decision: Support `KEY=VALUE` lines, skip comments/blank lines, trim optional single/double quotes.
   - Rationale: Covers project needs while keeping bootstrap deterministic and auditable.
   - Alternatives considered:
     - Full dotenv grammar: rejected as unnecessary complexity.

## Risks / Trade-offs

- **[Divergence from full dotenv behavior]** → Mitigation: document supported subset explicitly.
- **[Accidental reliance on local `.env` in non-local contexts]** → Mitigation: keep precedence with real env vars and avoid requiring `.env` in production.
- **[Malformed lines silently ignored]** → Mitigation: limit parsing to strict `KEY=VALUE` lines and rely on downstream required-key validation.

## Migration Plan

1. Add dotenv autoload bootstrap logic in `config/settings/__init__.py`.
2. Add tests verifying `.env` values are read when env vars are absent and that exported vars override `.env`.
3. Update environment documentation examples to include Together key in `.env`.
4. Rollback strategy: remove the loader block from settings bootstrap with no schema/data impact.

## Open Questions

- Should malformed dotenv lines emit warnings in local mode for easier debugging?
