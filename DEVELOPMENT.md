# DEVELOPMENT

Guidance for contributors and maintainers of the SOFinance backend.

## Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-test.txt
cp .env.example .env  # edit DATABASE_URL, secrets, flags
prisma generate
```

Recommended Python: 3.13 (project targets latest CPython). Use `pyenv` or system package manager if needed.

## Tooling
- **FastAPI** for API layer
- **Prisma** for database access (PostgreSQL)
- **Pytest** for tests (`tests/` directory)
- **ruff / black** (optional) for style; adhere to existing style patterns

## Running the Server
```bash
python run.py
# or if using uvicorn directly
uvicorn app.main:app --reload
```

## Configuration
All configuration centralised in `app/core/config.py` (`Settings`). Environment variables override defaults. Keep new flags **opt-in** unless they are purely additive & safe.

Key toggles:
- `ENABLE_AUDIT_LOGGING`
- `ENABLE_KEY_MIRRORING` (legacy compatibility; disable when clients migrated)
- `RATE_LIMIT_PER_MINUTE`, `RATE_LIMIT_BURST`
- `ENABLE_RESPONSE_ENRICHMENT`

## Database & Migrations
1. Modify `prisma/schema.prisma`.
2. Run: `prisma migrate dev --name <change>`.
3. Commit the generated migration folder & updated client artifacts (if applicable).

Avoid manual SQL unless absolutely required—prefer Prisma schema evolution.

## Coding Conventions
- Return standardized envelopes via `success_response` / `failure_response`.
- Use `Decimal` for monetary values; serialize using existing helpers.
- Keep business logic in `service.py`, thin controllers in `routes.py`.
- Add defensive validations at both route and service layers when correctness is critical (e.g. journal balance).
- Raise domain-specific `APIError` subclasses for predictable error handling.

## Testing
```bash
pytest -q
```

Test categories:
- API route tests (HTTP layer)
- Integrity tests (financial decorators, reconciliation)
- Error normalization & envelope shape
- Journal balance & validation

Add tests with each new feature; failing tests should block merges.

## Response Normalization Middleware
A temporary shim still wraps raw responses for legacy tests. New code **must** return envelopes directly to accelerate deprecation. Avoid adding new mirrored keys.

## Logging & Observability
- Logging configured in `app/main.py`.
- Correlation IDs added via middleware when enabled.
- Structured error envelopes simplify log parsing.

## Performance Considerations
- Prefer paginated queries; avoid unbounded list endpoints.
- Leverage Prisma filters instead of post-filtering in Python.
- Use async I/O for external calls (currently minimal external integrations).

## Security
- Guard new endpoints with appropriate permission dependency.
- Never expose raw secrets in responses or logs.
- Validate input rigorously; rely on Pydantic schemas.

## Adding Feature Flags
1. Add field to `Settings` with sensible default.
2. Document in README (Environment section) or a future consolidated ops doc.
3. Use the flag in code with clear fallback behavior.

## Deprecation Workflow
1. Introduce new capability behind flag (default off).
2. Ship & monitor.
3. Flip default when stable.
4. Remove legacy path in a major version / controlled release.

## Release Checklist
- [ ] All tests green
- [ ] Migration files committed
- [ ] No stray debug or quick scripts added
- [ ] README & docs updated if public behavior changed
- [ ] Flags documented

## Contributing
Feature branches should remain focused. Submit PRs with:
- Summary of change
- Rationale / business or integrity impact
- Tests demonstrating correctness

---
Questions or clarifications: open a PR or issue in the repository.

## Operations (Deployment & Production)

### Runtime Model
Stateless FastAPI service; scale horizontally behind a load balancer. Shared state (PostgreSQL, Redis, object storage) externalized.

### Core Services
- App: Uvicorn/Gunicorn workers
- DB: PostgreSQL (managed preferred)
- Cache / Rate Limit: Redis (for multi-instance)
- Object Storage: S3/MinIO (uploads, exports)
- Background Jobs: (Future) Celery / Dramatiq / custom worker

### Key Environment Variables
| Variable | Required | Purpose |
|----------|----------|---------|
| DATABASE_URL | yes | Prisma/PostgreSQL DSN |
| JWT_SECRET | yes | Token signing secret (rotate) |
| RATE_LIMIT_PER_MINUTE / RATE_LIMIT_BURST | no | Basic throttling |
| REDIS_URL | no | Enables distributed rate limiting |
| ENABLE_KEY_MIRRORING | no | Legacy envelope mirroring |
| ENABLE_AUDIT_LOGGING | no | Persist audit events |
| SENTRY_DSN | no | Error monitoring |
| ENVIRONMENT | no | deployment stage tag |

### Deployment (Container Example)
```
FROM python:3.13-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt requirements-test.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER nobody
CMD ["python", "run.py"]
```

Run migrations before starting app workers:
```
prisma migrate deploy
```

### Gunicorn Pattern
```
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:8000 --timeout 60
```

### Backups & Recovery
| Layer | Strategy |
|-------|----------|
| PostgreSQL | Managed snapshots + PITR |
| Prisma Migrations | Git history & tags |
| Uploads | Versioned bucket + lifecycle rules |

Quarterly disaster drill: restore snapshot to staging and smoke test.

### Observability
- Logs: structured JSON to stdout
- Metrics: (future) Prometheus exporter
- Tracing: OpenTelemetry (planned)
- Errors: Sentry optional

### Rate Limiting & Caching
In-memory default (single instance). Configure `REDIS_URL` to enable distributed strategy. Future caching targets: reference data with short TTL.

### Security Hardening
- Enforce HTTPS & HSTS at edge
- Rotate JWT secret; adopt key versioning claim before rotation
- Principle of least privilege DB role
- Dependency vulnerability scanning (Dependabot)

### Data Integrity & Audits
Double validation (route + service). Consider scheduled tasks to recompute sales/journal aggregates and log discrepancies.

### Zero-Downtime Strategy
Rolling deploy + pre-deploy `prisma migrate deploy`. Avoid destructive DDL paired with code removal in the same release (adopt additive → migrate → prune).

### Incident Playbook (Starter)
| Symptom | First Action |
|---------|--------------|
| Spike 5xx | Check logs & recent deploy diff |
| High DB connections | Inspect pool config & long running queries |
| Latency increase | Trace slow endpoints / external waits |
| Integrity failure | Quarantine records; create compensating journal |

### Capacity Planning Baseline
- Start: 2× (2 vCPU / 4GB)
- Watch: p95 < 300ms, CPU < 70%, DB connections < 70% limit
- Scale horizontally first.

### Production Readiness Checklist
- [ ] Health check monitored
- [ ] Error alerting configured
- [ ] Backup restore tested this quarter
- [ ] Redis-backed rate limiting (if >1 instance)
- [ ] Secrets rotation policy documented
- [ ] Migrations automated in pipeline

### Feature Flag Retirement
Flag default off ≥ one release + no usage logs → remove code.

### Compliance (Baseline)
- Minimize PII storage; redact unnecessary fields
- Encrypt data at rest (managed PG + bucket policies)
- Retention policies for logs / audits per regulation

### Glossary
| Term | Definition |
|------|------------|
| Envelope | Standard JSON response wrapper |
| Integrity | Financial invariant correctness |
| Defense-in-depth | Multi-layered validation pattern |

