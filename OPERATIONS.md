# OPERATIONS

Operational guidance for deploying and running the SOFinance backend in staging and production.

## 1. Runtime Overview
The service is a stateless FastAPI application. Horizontal scaling is achieved by adding more identical instances behind a load balancer. Shared state (DB, cache, object storage) must live in external services.

## 2. Core Services
- Application: FastAPI (Uvicorn / Gunicorn workers)
- Database: PostgreSQL (managed service recommended)
- Cache / Rate Limiting (recommended for scale): Redis
- Object Storage (uploads/exports): S3 or compatible (MinIO in dev)
- Background Jobs (future): Redis queues / Celery / Dramatiq (not yet required)

## 3. Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | yes | PostgreSQL connection string (Prisma format). |
| `JWT_SECRET` | yes | HMAC secret for JWT signing. Rotate periodically. |
| `JWT_ALGORITHM` | no  | Defaults to HS256. |
| `LOG_LEVEL` | no | `info` (default), `debug`, `warning`, etc. |
| `ENABLE_KEY_MIRRORING` | no | Legacy response shape support. Disable when clients updated. |
| `ENABLE_RESPONSE_ENRICHMENT` | no | Adds extra meta fields when true. |
| `ENABLE_AUDIT_LOGGING` | no | Persist audit events (ensure table / retention). |
| `RATE_LIMIT_PER_MINUTE` | no | Soft per-minute limit (fallback in-memory). |
| `RATE_LIMIT_BURST` | no | Burst window allowance. |
| `REDIS_URL` | no | Enables Redis-backed rate limiting & future caching. |
| `SENTRY_DSN` | no | Error monitoring endpoint (if integrated). |
| `ENVIRONMENT` | no | `development`, `staging`, `production` (affects logging verbosity). |

Keep secrets out of images; inject at runtime (e.g., Kubernetes secrets, ECS task defs, Fly.io secrets, etc.).

## 4. Build & Deployment
### Container (Recommended)
1. Multi-stage Dockerfile (sample skeleton):
```
FROM python:3.13-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt requirements-test.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m appuser && chown -R appuser /app
USER appuser
CMD ["python", "run.py"]
```
2. Build: `docker build -t sofinance-backend:$(git rev-parse --short HEAD) .`
3. Run (dev): `docker run --env-file .env -p 8000:8000 sofinance-backend:latest`

### Gunicorn + Uvicorn Workers
```
gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 60
```
Scale workers = CPU cores * 2 (adjust under load tests).

## 5. Database Migrations
- On deploy: run `prisma migrate deploy` before starting application workers.
- Development: `prisma migrate dev --name <change>` (never on production).
- Rollback Strategy: create forward fix; avoid destructive hot rollbacks unless absolutely necessary.

## 6. Backups & Recovery
| Layer | Strategy | Notes |
|-------|----------|-------|
| PostgreSQL | Managed automated snapshots + PITR | Verify retention window (≥ 7–30 days). |
| Prisma Migrations | Git repository history | Tag releases to map schema states. |
| Uploaded Files | Versioned object storage bucket | Enable lifecycle policies for old versions. |

Disaster drill: at least quarterly restore a snapshot to staging and run smoke tests.

## 7. Observability
| Concern | Tooling |
|---------|---------|
| Metrics | (Pluggable) Prometheus via sidecar / exporter (future) |
| Tracing | OpenTelemetry (future hook points in middleware) |
| Logs | Structured JSON to stdout → aggregated by platform |
| Errors | Sentry (optional) |

Correlation ID middleware (if enabled) tags log lines—ensure load balancer preserves / sets request IDs.

## 8. Rate Limiting & Caching
Default implementation is in-memory (single-instance only). For multi-instance:
1. Deploy Redis.
2. Configure `REDIS_URL` env.
3. Replace in-memory limiter with Redis script / token bucket (extensible placeholder in current limiter module).

Future caching targets: frequently read reference data (tax codes, categories) with short TTL.

## 9. Security Hardening
- Enforce HTTPS at edge (LB / ingress layer).
- Set HSTS header (ingress preferred) & secure cookies (if added later).
- Rotate JWT secret at defined intervals (introduce key versioning claim before rotation).
- Principle of least privilege for DB role (no superuser; restrict DDL in production outside migrations pipeline).
- Periodic dependency scan (e.g., GitHub Dependabot).

## 10. Data Integrity
Financial invariants double-validated (route + service). Consider scheduled discrepancy audits:
- Recalculate sales totals vs. line items.
- Rebuild journal balances.
- Alert deviations (store in an `integrity_events` table or send to monitoring).

## 11. Zero-Downtime Deployment
- Use rolling updates (K8s Deployment, ECS rolling, Fly machines upgrades one-by-one).
- Run migrations in a pre-deploy job; ensure migrations are backward compatible with previous code version when possible.
- Avoid dropping columns/constraints in same release that removes usage—follow additive → migrate data → switch → prune pattern.

## 12. Incident Response Playbook (Starter)
| Symptom | Action |
|---------|--------|
| Elevated 5xx rate | Check logs for unhandled exceptions; correlate recent deploy. |
| DB connection spikes | Inspect slow queries / connection leaks; verify pool size. |
| Latency increase | Profile endpoints; check external dependency latency. |
| Integrity check failure | Isolate offending records, create compensating journal / corrective sale. |

Maintain runbooks in repository or internal wiki for expansion.

## 13. Scheduled Tasks (Future)
Integrate a scheduler (e.g., Celery beat, APScheduler, external cron) for:
- Nightly integrity audits
- Report generation
- Data grooming (archiving old logs)

## 14. Decommissioning Legacy Features
Track feature flags with target sunset dates. Remove code after: flag default = off for ≥ 1 release cycle AND no logs indicating usage.

## 15. Compliance Considerations (Baseline)
- PII minimal collection principle—redact where not required.
- Access logs retained per policy (e.g., 90 days) then archived.
- Ensure DB backups encrypted at rest (managed service usually default).

## 16. Capacity Planning
Start with: 2 small instances (e.g., 2 vCPU / 4GB) and monitor:
- p95 latency < 300ms typical business hours
- CPU < 70% sustained
- DB connections < 70% max
Adjust horizontally first; vertically only if single-worker saturation appears.

## 17. Checklist (Production Readiness)
- [ ] HEALTH endpoint monitored
- [ ] Error rate alert configured
- [ ] Backup restore test verified this quarter
- [ ] Rate limiting backed by Redis (multi-instance)
- [ ] Secrets rotation policy documented
- [ ] Migrations pipeline automated

## 18. Glossary
| Term | Meaning |
|------|---------|
| Envelope | Standardized JSON response structure. |
| Integrity | Consistency of financial invariants (journals balanced, totals reconciled). |
| Defense-in-depth | Repeating critical validations in multiple layers to prevent bypass. |

---
For development process details see `DEVELOPMENT.md`. For architecture internals see `ARCHITECTURE.md`.
