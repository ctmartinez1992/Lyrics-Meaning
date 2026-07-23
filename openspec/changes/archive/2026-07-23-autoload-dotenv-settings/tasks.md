## 1. Settings bootstrap dotenv loading

- [x] 1.1 Add `.env` loading logic to Django settings bootstrap before env-specific settings import
- [x] 1.2 Implement safe line parsing for `KEY=VALUE` with support for comments/blank lines and optional quotes
- [x] 1.3 Ensure loaded values use non-overriding behavior so existing process env variables keep precedence

## 2. Verification and docs

- [x] 2.1 Add tests proving management commands can read keys loaded from `.env` when shell exports are absent
- [x] 2.2 Add tests proving exported environment variables are not overwritten by `.env` loader
- [x] 2.3 Update environment setup documentation/examples to clarify automatic `.env` loading behavior and supported syntax
