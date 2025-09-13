# ARCHITECTURE

High-level design of the SOFinance backend.

## Overview
A modular FastAPI application layered into:
- **API Layer (Routers)**: Input parsing, auth/permission enforcement, mapping service results to standard response envelopes.
- **Service Layer**: Business logic, integrity rules, orchestration of persistence calls.
- **Persistence Layer (Prisma ORM)**: PostgreSQL access via generated client.
- **Core Infrastructure**: Configuration, error & response normalization, middleware utilities.

## Module Layout
```
app/
  core/          # config, errors, response helpers, security utils
  middlewares/   # authentication, rate limiting, correlation, normalization
  modules/
    users/
    sales/
    journal/
    inventory/
    ... domain modules
  utils/         # shared helpers (serialization, currency, ids, hashing)
```

Each domain module typically contains:
- `schema.py` (Pydantic request/response models)
- `service.py` (business logic)
- `routes.py` (FastAPI router wiring)
- `validators.py` or `logic.py` (optional specialized helpers)

## Request Lifecycle
1. **Incoming HTTP Request**
2. Security / auth middleware extracts and validates JWT; permissions verified in dependency layer.
3. Correlation ID middleware tags request (if enabled).
4. Rate limiting enforces burst & sustained quotas.
5. Router handler executes: parses Pydantic model, performs early validations (fast-fail semantics), delegates to service.
6. Service layer applies integrity rules (defense-in-depth) & persists via Prisma.
7. Response envelope produced (success or failure). Error middleware intercepts exceptions and converts to canonical `failure_response`.
8. Response normalization middleware (temporary) ensures backward-compatible shape.

## Error Handling & Normalization
Custom exception hierarchy (root `APIError`) defines `code`, `http_status`, `message`, optional `details`. Middleware path:
- If already a structured failure envelope, pass through untouched (checked via header `x-normalized-error`).
- If raw unhandled error, convert to `INTERNAL_SERVER_ERROR` envelope (omit internal stack traces to caller).

## Financial Integrity
Critical invariants (e.g., balanced journals, sales totals consistency) enforced in two layers:
- **Route Early Check**: Fast user feedback with specific 400 error code (`VALIDATION_ERROR`).
- **Service Re-check**: Protect against bypass if route code changes.
Decorators / helpers may recalculate derived totals and compare against payload-supplied amounts.

## Response Envelope Contract
```
{
  "success": true | false,
  "code": "SOME_CODE",          # machine readable
  "message": "Human summary",
  "data": { ... },               # success payload OR echo of invalid input subset
  "meta": { ... }                # optional (pagination, timing, flags)
}
```
Failing responses set `success=false` and may include `errors` (list or object) when domain-specific granularity is useful. New endpoints should NOT add deprecated mirrored keys.

## Middleware Stack (Typical Order)
1. Security Headers
2. Correlation ID (optional flag)
3. Rate Limiter
4. Authentication / Permission dependencies
5. Error Normalization Middleware
6. Response Normalization Middleware (legacy shim)

Order matters: error middleware must wrap inner logic; normalization runs after to adjust shape only if needed.

## Data Model (Prisma)
- Defined in `prisma/schema.prisma`.
- Each service consumes generated Prisma client for type-safe queries.
- Prefer relational integrity (FKs) and DB constraints; mirror essential rules at service layer for clearer API errors.

## Transactions
Financial operations requiring atomicity should leverage explicit transactions (Prisma supports interactive transactions). Batch writes for a single logical event (sale with line items, journal with entries) should serialize within one transaction boundary.

## Extensibility Patterns
- Add new domain: create module folder with `routes.py`, `service.py`, `schema.py`.
- Register router in `app/main.py` with appropriate prefix & tags.
- Use shared helpers from `app/utils` rather than duplicating logic.

## Feature Flags
Flags toggle non-breaking enhancements. They should not create divergent persistence schemas—prefer runtime behavioral changes only. Document each flag’s intent and planned sunset timeline.

## Performance & Scaling Considerations
- Horizontal scaling supported (stateless app). Sticky sessions not required.
- Rate limiting backend (in-memory default) should be replaced with Redis for multi-instance deployment.
- Heavy read endpoints should implement pagination + selective field projection.

## Logging & Audit
Audit logging (when enabled) records key domain events (sales, journal entries). Ensure personally identifiable information (PII) handling respects compliance requirements—mask or omit sensitive fields where possible.

## Security Posture
- JWT with role/permission claims.
- Principle of least privilege for endpoints.
- Input validation via Pydantic prevents injection of unexpected fields.
- Planned enhancements: stricter CSP, mTLS for internal service calls (future multi-service architecture).

## Deprecation & Migration Strategy
1. Introduce new pattern in parallel (e.g., envelope normalization).
2. Dual-run with shim middleware.
3. Remove shim after all clients updated (tracked by feature flag metrics / logs).

## Known Transitional Elements
- Response Normalization Middleware: scheduled for removal once all endpoints handcraft envelopes.
- Key mirroring for legacy clients: disable via flag when safe.

## Future Directions
- Event sourcing / append-only ledger for high fidelity financial traceability.
- Background job queue for async reconciliation & report generation.
- Fine-grained permission matrix with dynamic policy evaluation.

---
For implementation specifics, see `DEVELOPMENT.md` and inline docstrings.
