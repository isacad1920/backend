# SOFinance API Reference

> For a machine-readable schema use `/openapi.json`. For the exhaustive, field-level documentation of every endpoint (inputs, envelopes, pagination) see `API_REFERENCE_FULL.md` (generated via `python scripts/generate_full_api_reference.py`).

![CI](https://github.com/isacad1920/backend/actions/workflows/ci.yml/badge.svg)

Enterprise-grade Point of Sale & Financial Management backend for multi-branch retail, inventory control, customer management, and accounting operations.

## 1. Overview
The SOFinance API is a versioned RESTful API (current version: `v1`) delivering a standardized JSON response envelope. Core domains:
- Authentication & Users
- Permissions & Roles
- Products, Categories, Inventory
- Sales & Payments (supports partial payments / accounts receivable)
- Customers & Credit
- Financial Analytics & Journal
- System Operations (backups, configuration, notifications, health)
- Audit Logging

All endpoints are namespaced under: `/api/v1/` unless explicitly public (e.g. `/health`, `/ping`, `/docs`).

## 2. Standard Response Envelope
Every successful endpoint (unless explicitly documented as a raw pass-through) returns:
```
{
  "success": true,
  "message": "Success",          // Human-friendly summary
  "data": { ... | [...] | value }, // Primary payload
  "meta": {                        // Optional metadata (pagination, context)
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 125,
      "pages": 7
    }
  },
  "timestamp": "2025-09-14T12:34:56.123Z"  // UTC ISO8601
}
```
Failure responses follow a problem+json style (see Errors section) OR a legacy normalized envelope when thrown via `APIError` middleware.

### Transitional Compatibility
A temporary middleware wraps legacy raw JSON into the envelope. New code should always build responses via helper utilities (e.g., `success_response`). Key mirroring is disabled by default (`enable_key_mirroring=false`).

## 3. Authentication & Authorization

### 3.1 Authentication Flows
Supported mechanisms:
- Email + Password (login): `POST /api/v1/auth/login`
- OAuth2 Password Grant (OpenAPI authorize): `POST /api/v1/auth/token`
- Token Refresh: `POST /api/v1/auth/refresh`

All protected endpoints require an `Authorization: Bearer <access_token>` header.

### 3.2 Tokens
- Access Token (short-lived) – JWT with standard claims.
- Refresh Token (longer-lived) – used to obtain new access tokens.

Example login request:
```
POST /api/v1/auth/login
Content-Type: application/json
{
  "email": "demo@sofinance.com",
  "password": "DemoPassword123!"
}
```
Example success response:
```
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "<jwt>",
    "refresh_token": "<jwt>",
    "token_type": "bearer",
    "user": {
      "id": "usr_123",
      "email": "demo@sofinance.com",
      "role": "ADMIN",
      "isActive": true
    }
  },
  "timestamp": "2025-09-14T12:34:56.123Z"
}
```

### 3.3 Authorization Model
- Role Based: `ADMIN`, `MANAGER`, `CASHIER`, `INVENTORY_CLERK`, `ACCOUNTANT`.
- Permission Based: Fine-grained resource/action permissions (e.g., `products:read`, `sales:write`).
- Middleware enforces access; unauthorized access returns a problem+json `Authentication Failed` or `HTTP Error` (403) payload.

### 3.4 Public Endpoints
- `/health`
- `/ping`
- `/docs`, `/redoc`, `/openapi.json`
- `/api/v1/info`
- Auth endpoints (`/api/v1/auth/login`, `/api/v1/auth/token`, etc.)

## 4. Error Handling

### 4.1 Problem+JSON Format
Errors are emitted with media type: `application/problem+json`.
```
{
  "type": "https://sofinance.dev/problems/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Request validation failed",
  "instance": "/api/v1/products",
  "timestamp": "2025-09-14T12:34:56.123Z",
  "errors": [
    {"loc": ["body", "name"], "msg": "Field required", "type": "value_error.missing"}
  ]
}
```

### 4.2 Error Types
| Type URL Suffix | Title | Typical Status | Cause |
|-----------------|-------|----------------|-------|
| authentication | Authentication Failed | 401 | Invalid or expired token |
| api-error | API Error | 4xx/5xx | Business rule violation via `APIError` |
| validation-error | Validation Error | 422 | Input failed schema validation |
| http-error | HTTP Error | 403/404 | Generic HTTP exceptions |
| not-found | Resource Not Found | 404 | Missing resource |
| internal-error | Internal Server Error | 500 | Unhandled exception |

### 4.3 Legacy Envelope Failures (Rare)
Legacy paths may return:
```
{
  "success": false,
  "error": { "code": "FORBIDDEN", "message": "Insufficient permissions" },
  "timestamp": "..."
}
```
Prefer relying on problem+json for all new integrations.

## 5. Endpoint Catalog (Representative)
(For the exhaustive machine-readable spec, use `/openapi.json`). Below are grouped human-readable summaries with sample payloads.

### 5.1 Authentication
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/auth/login | Login with email/password |
| POST | /api/v1/auth/token | OAuth2 password grant |
| POST | /api/v1/auth/refresh | Refresh access token |
| POST | /api/v1/auth/register | Register new user (if enabled) |

### 5.2 Users
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/users | List users (paginated) |
| POST | /api/v1/users | Create user |
| GET | /api/v1/users/{id} | Retrieve user |
| PUT | /api/v1/users/{id} | Update user |
| DELETE | /api/v1/users/{id} | Delete/deactivate user |

Sample list response:
```
{
  "success": true,
  "message": "Users retrieved",
  "data": {
    "items": [
      {"id": "u1", "email": "demo@sofinance.com", "role": "ADMIN", "isActive": true}
    ],
    "pagination": {"page": 1, "size": 20, "total": 1, "pages": 1}
  },
  "timestamp": "2025-09-14T12:34:56.123Z"
}
```

### 5.3 Permissions
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/permissions | List permissions |
| POST | /api/v1/permissions | Create permission |
| POST | /api/v1/permissions/assign | Assign permission to role/user |

### 5.4 Products & Categories
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/categories | List categories |
| POST | /api/v1/categories | Create category |
| GET | /api/v1/products | List products |
| POST | /api/v1/products | Create product |
| GET | /api/v1/products/{id} | Product details |
| PUT | /api/v1/products/{id} | Update product |

Create product request:
```
POST /api/v1/products
{
  "name": "USB-C Cable",
  "sku": "USBC-1M-BLK",
  "category_id": "cat_123",
  "price": "12.99",
  "cost": "7.00",
  "branch_id": "br_1",
  "stockQuantity": 100
}
```
Response:
```
{
  "success": true,
  "message": "Product created",
  "data": {
    "id": "prod_789",
    "name": "USB-C Cable",
    "sku": "USBC-1M-BLK",
    "price": "12.99",
    "cost": "7.00",
    "category": {"id": "cat_123", "name": "Cables"},
    "stockQuantity": 100,
    "isActive": true
  },
  "timestamp": "2025-09-14T12:34:56.123Z"
}
```

### 5.5 Inventory
Representative endpoints:
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/inventory/stock-levels | Current stock snapshot |
| GET | /api/v1/inventory/low-stock | Low stock items |
| GET | /api/v1/inventory/dead-stock | Slow/non-moving inventory |
| GET | /api/v1/inventory/valuation | Inventory valuation |

Low stock example:
```
{
  "success": true,
  "message": "Low stock items",
  "data": [
    {"product_id": "prod_1", "name": "USB-C Cable", "stockQuantity": 3, "threshold": 5}
  ],
  "timestamp": "2025-09-14T12:34:56.123Z"
}
```

### 5.6 Sales & Payments
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/sales | List sales |
| POST | /api/v1/sales | Create sale (items, payments) |
| GET | /api/v1/sales/{id} | Sale details |
| POST | /api/v1/sales/{id}/payments | Add incremental payment |
| POST | /api/v1/sales/{id}/refund | Issue refund |
| GET | /api/v1/sales/statistics | Sales KPIs |

Create sale (partial payment) request:
```
POST /api/v1/sales
{
  "customer_id": "cust_1",
  "items": [
    {"product_id": "prod_789", "quantity": 2, "unit_price": "12.99"}
  ],
  "payments": [
    {"method": "CASH", "amount": "10.00"}
  ]
}
```
Sale detail response (partial):
```
{
  "success": true,
  "message": "Sale created",
  "data": {
    "id": "sale_456",
    "status": "PARTIAL",
    "total_amount": "25.98",
    "paid_amount": "10.00",
    "outstanding_amount": "15.98",
    "items": [
      {"product_id": "prod_789", "quantity": 2, "unit_price": "12.99", "line_total": "25.98"}
    ],
    "payments": [
      {"id": "pay_1", "method": "CASH", "amount": "10.00", "timestamp": "2025-09-14T12:34:56.123Z"}
    ]
  },
  "timestamp": "2025-09-14T12:34:56.123Z"
}
```

Add incremental payment:
```
POST /api/v1/sales/sale_456/payments
{
  "method": "CARD",
  "amount": "15.98"
}
```
Resulting status transitions to `PAID` if fully settled.

### 5.7 Customers
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/customers | List customers |
| POST | /api/v1/customers | Create customer |
| GET | /api/v1/customers/{id} | Customer details |
| GET | /api/v1/customers/{id}/purchase-history | Purchase history |

### 5.8 Financial & Journal
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/financial/summary | Financial KPIs snapshot |
| GET | /api/v1/financial/income-statement | Income statement (raw dict) |
| GET | /api/v1/journal/entries | List journal entries |
| POST | /api/v1/journal/entries | Create journal entry (balanced) |

Journal entry create example:
```
POST /api/v1/journal/entries
{
  "memo": "Inventory purchase",
  "lines": [
    {"account": "INVENTORY", "debit": "500.00"},
    {"account": "CASH", "credit": "500.00"}
  ]
}f
```
Response:
```
{
  "success": true,
  "message": "Journal entry created",
  "data": {
    "id": "je_1001",
    "memo": "Inventory purchase",
    "lines": [
      {"account": "INVENTORY", "debit": "500.00", "credit": "0.00"},
      {"account": "CASH", "debit": "0.00", "credit": "500.00"}
    ],
    "balanced": true
  },
  "timestamp": "2025-09-14T12:34:56.123Z"
}
```

### 5.9 System & Operations
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/info | System info |
| GET | /api/v1/system/backups | List backups (if implemented) |
| POST | /api/v1/system/backups | Trigger backup |
| GET | /health | Liveness + DB check |
| GET | /ping | Lightweight ping |

### 5.10 Audit
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/audit/logs | Query audit logs (filters) |

Audit log record example:
```
{
  "id": "aud_1",
  "actor_id": "usr_123",
  "action": "SALE_CREATED",
  "entity_type": "SALE",
  "entity_id": "sale_456",
  "timestamp": "2025-09-14T12:34:56.123Z",
  "ip": "127.0.0.1",
  "metadata": {"total": "25.98"}
}
```

## 6. Pagination
Endpoints returning collections place items inside `data.items` with a `data.pagination` object:
```
"data": {
  "items": [...],
  "pagination": {"page":1, "size":20, "total":125, "pages":7}
}
```
Query parameters: `?page=1&size=20`.

## 7. Filtering & Searching
Common patterns:
- Text search: `?q=term`
- Date range: `?start=2025-09-01&end=2025-09-14`
- Status filters: `?status=PAID` (sales) / `?role=ADMIN` (users)

## 8. Sorting
If supported: `?sort=created_at:desc` or `?sort=price:asc`. Multiple sorts may be comma-delimited.

## 9. Data Types & Serialization
- Monetary values serialized as strings with 2 decimal places (avoid float drift).
- Timestamps in UTC ISO8601 with trailing `Z`.
- Enums returned as upper-case strings.

## 10. Idempotency & Concurrency (Guidance)
For financial operations (sales creation, journal entries):
- Ensure client-side retries include an idempotency key header (future enhancement).
- Current system trusts single submission; duplicates should be guarded at service layer (not yet formalized).

## 11. Rate Limiting
Global middleware enforces request/minute & burst thresholds. Excluded paths: `/health`, `/ping`, docs & schema endpoints.

## 12. Security Best Practices
- Always use HTTPS in production.
- Rotate `SECRET_KEY` only during maintenance windows—tokens will invalidate.
- Restrict CORS to trusted origins via `BACKEND_CORS_ORIGINS`.
- Use strong password policy (enforced via settings).

## 13. Change Management / Deprecations
Deprecation signals will appear in response `meta` (future) and release notes. Transitional middleware scheduled for removal in a major version once all clients rely on the envelope only.

## 14. Glossary
| Term | Meaning |
|------|---------|
| A/R | Accounts Receivable (outstanding customer balances) |
| SKU | Stock Keeping Unit (product code) |
| Partial Sale | A sale with outstanding balance (status `PARTIAL`) |
| Journal Entry | Balanced double-entry accounting record |

## 15. FAQ (Quick)
| Question | Answer |
|----------|--------|
| Why are money fields strings? | Prevent binary float rounding errors. |
| Why raw dict for income statement? | Historical reporting client; will envelope later. |
| How to detect partial payments? | Check sale `status`, compare `paid_amount` vs `total_amount`. |

## 16. Future Enhancements (Planned)
- Idempotency keys for financial operations
- Structured JSON logging & metrics
- Full deprecation of response compatibility layer
- Token revocation & session concurrency enforcement
- Cached analytics endpoints

---
For machine-generated schema: `GET /openapi.json`.

If something is missing from this reference, open an internal ticket to extend `API_REFERENCE.md`.
