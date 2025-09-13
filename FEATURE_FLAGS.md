## Feature Flags & Configuration Overview

This document enumerates the primary runtime feature flags and configuration toggles exposed via the `Settings` model (`app/core/config.py`). Each flag is intended to be safe to disable/enable at deploy time without code changes unless otherwise noted.

| Env Var / Setting | Default | Purpose | Recommended Production Value |
|-------------------|---------|---------|------------------------------|
| ENABLE_KEY_MIRRORING | true | Legacy: promote selected nested `data` keys to top-level for backward compatibility with older clients/tests. | false (after clients updated) |
| MIRROR_PAGINATION_KEYS | true | Legacy: also mirror pagination fields (`items`, `page`, `size`, `total`). | false |
| ENABLE_RESPONSE_ENRICHMENT | true | Enables correlation ID & app version enrichment in response `meta`. | true |
| INCLUDE_CORRELATION_ID | true | Adds `correlation_id` when enrichment enabled & middleware sets it. | true |
| INCLUDE_APP_VERSION_META | true | Adds `app_version` to meta. | true |
| RESPONSE_ENRICHMENT_ADD_TO_META | false | When true, nests enrichment keys under namespace instead of meta root. | false (unless name collision risk) |
| RESPONSE_ENRICHMENT_META_NAMESPACE | _ctx | Namespace key when previous flag is true. | _ctx |
| ENFORCE_RESTORE_JOB_LIMIT | true | Enforces concurrency guard on async restore jobs to prevent overload. | true |
| MAX_CONCURRENT_RESTORE_JOBS | 2 | Maximum queued/running restore jobs before 429 returned. | Tune per infra (2–5) |
| RATE_LIMIT_PER_MINUTE | 100 | Generic request rate limit (if middleware applied elsewhere). | Tune |
| RATE_LIMIT_BURST | 200 | Burst capacity for leaky-bucket style limiter. | Tune |
| BACKUP_ENABLED | true | Master toggle for automatic backups workflow. | true |
| BACKUP_SCHEDULE | "0 2 * * *" | Cron expression for scheduled backups. | Adjust to maintenance window |
| ENABLE_AUDIT_LOGGING | true | Persist audit trail entries. | true |
| AUDIT_RETENTION_DAYS | 365 | Retention window for audit records (if pruning job implemented). | Adjust compliance |

### Deprecation Path

1. Disable `MIRROR_PAGINATION_KEYS` (stop duplicating pagination).
2. After external consumers adapt, disable `ENABLE_KEY_MIRRORING` (pure envelope responses).
3. Remove mirroring middleware branch in a future major release.

### Correlation & Observability
Correlation IDs are injected by middleware (see `app/main.py`). Ensure upstream ingress (API gateway / load balancer) forwards an incoming header (e.g., `X-Request-ID`) or allow middleware to generate a UUID. When enabled, the ID appears in logs and `meta.correlation_id`.

### Safe Operations Checklist Before Changing Flags
| Change | Validate |
|--------|----------|
| Disabling key mirroring | Frontend pagination & token parsing unaffected |
| Increasing restore job limit | Database write I/O & CPU headroom sufficient |
| Disabling response enrichment | Monitoring dashboards not relying on correlation_id |

### Adding New Flags
Add to `Settings` in `config.py`, document here, and provide a sane default that preserves existing behavior (feature off by default unless low risk / observability related).
