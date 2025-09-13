# API v2 Migration Guide

This document maps legacy v1 endpoints to the new consolidated v2 structure and explains patterns used to minimize surface area without losing functionality.

## Core Principles
- Single collection endpoints with filtering & pagination instead of many specialized list variants.
- Expansion flags (`expand=` / `include=`) hydrate optional heavy data on-demand.
- Unified reports dispatcher (`/api/v2/reports?type=`) and domain-specific sub-dispatchers (`/api/v2/sales/reports`).
- Dedicated but optional specialized domains (e.g. `/api/v2/ar`) for permission boundaries.
- Consistent envelopes: `{ items, page, size, total, page_count, ... }` or resource object with `expansions` list.
- Deprecation signaled via `Deprecation: true`, `Sunset` and `Link` headers on all `/api/v1/*` responses.

## Versioning
- v1 and v2 run in parallel. Feature parity endpoints should prefer v2.
- Clients SHOULD send requests to `/api/v2/*` where available.

## Endpoint Mapping

### Inventory
| Legacy v1 | New v2 |
|-----------|--------|
| GET /api/v1/inventory/stock-levels | GET /api/v2/inventory/items |
| GET /api/v1/inventory/low-stock, /low-stock-alerts, /low-stock/batch | GET /api/v2/inventory/items?status=low_stock |
| GET /api/v1/inventory/dead-stock | GET /api/v2/inventory/items?status=dead_stock OR /api/v2/inventory/dead-stock |
| POST /api/v1/inventory/stock-adjustments | POST /api/v2/inventory/items/{id}/adjustments |
| GET /api/v1/inventory/stock-adjustments | (Batch adjustments listing not yet collapsed; implement if needed) |
| GET /api/v1/inventory/sales-timeseries | GET /api/v2/inventory/items?expand=sales_timeseries (per item sparkline) |
| GET /api/v1/inventory/valuation | GET /api/v2/inventory/items?expand=valuation |
| GET /api/v1/inventory/dashboard | GET /api/v2/inventory/summary (light) + expansions roadmap |
| GET /api/v1/inventory/reports/* (turnover, comprehensive) | Use `/api/v2/reports?type=inventory_summary` (extended types WIP) |
| GET /api/v1/inventory/{id} | GET /api/v2/inventory/items/{id} |
| PUT /api/v1/inventory/reorder-points/{id} | (Fold into PATCH on item detail – pending) |

### Sales
| Legacy v1 | New v2 |
|-----------|--------|
| GET /api/v1/sales (various variants) | GET /api/v2/sales |
| POST /api/v1/sales | POST /api/v2/sales |
| GET /api/v1/sales/{id} | GET /api/v2/sales/{id}?expand=items,payments,customer |
| PUT /api/v1/sales/{id} | PUT /api/v2/sales/{id} |
| POST /api/v1/sales/{id}/payments | POST /api/v2/sales/{id}/payments |
| GET /api/v1/sales/{id}/payments | GET /api/v2/sales/{id}/payments |
| GET /api/v1/sales/stats | GET /api/v2/sales/reports?type=stats |
| GET /api/v1/sales/reports/daily | GET /api/v2/sales/reports?type=daily |
| GET /api/v1/sales/ar/summary | GET /api/v2/sales/reports?type=ar_summary OR /api/v2/ar/summary |
| GET /api/v1/sales/ar/aging | GET /api/v2/sales/reports?type=ar_aging OR /api/v2/ar/aging |
| GET /api/v1/sales/today/summary | GET /api/v2/sales/summary?period=today (extend includes) |

### Customers
| Legacy v1 | New v2 |
|-----------|--------|
| GET /api/v1/customers | GET /api/v2/customers |
| GET /api/v1/customers/statistics | GET /api/v2/customers/summary |
| GET /api/v1/customers/{id} | GET /api/v2/customers/{id}?expand=ar_summary,aging,purchase_history,balance |
| GET /api/v1/customers/{id}/history | Covered by purchase_history expansion |
| POST /api/v1/customers | (Not yet re-implemented in v2 – add if create in scope) |
| PUT /api/v1/customers/{id} | (Pending if needed) |
| DELETE /api/v1/customers/{id} | (Pending if needed) |

### Accounts Receivable (optional domain split)
| Legacy v1 | New v2 |
|-----------|--------|
| /api/v1/sales/ar/* | /api/v2/ar/summary, /api/v2/ar/aging OR sales/reports variants |

### Reports (Unified Dispatcher)
| Legacy v1 | New v2 |
|-----------|--------|
| Multiple /inventory/reports/* /sales/reports/* endpoints | GET /api/v2/reports?type=inventory_summary|sales_summary|customer_ar|daily_sales |
| Daily sales | /api/v2/sales/reports?type=daily or dispatcher |

### System / Backups
| Legacy v1 | New v2 |
|-----------|--------|
| GET /api/v1/system/backups | GET /api/v2/system/backups |
| POST /api/v1/system/backups | POST /api/v2/system/backups |
| GET /api/v1/system/backups/{id} | GET /api/v2/system/backups/{id} |
| DELETE /api/v1/system/backups/{id} | DELETE /api/v2/system/backups/{id} |
| POST /api/v1/system/backups/{id}/restore | POST /api/v2/system/backups/{id}/restore |
| GET /api/v1/system/backups/stats | GET /api/v2/system/backups/summary |

### Audit
| Legacy v1 | New v2 |
|-----------|--------|
| GET /api/v1/audit/logs | GET /api/v2/audit/logs |

### Security / Permissions
| Legacy v1 | New v2 |
|-----------|--------|
| /api/v1/permissions/* (various) | /api/v2/security/permissions, /api/v2/security/users/{id}/permissions, batch endpoints |

### Notifications
| Legacy v1 | New v2 |
|-----------|--------|
| /api/v1/notifications (list/mark) | /api/v2/notifications, /api/v2/notifications/{id}/read, /api/v2/notifications/read-all |

## Expansion & Include Flags
- Sales: `expand=items,payments,customer`
- Customers: `expand=ar_summary,aging,purchase_history,balance`
- Inventory: `expand=valuation,sales_timeseries`
- Sales summary: `include=ar,aging`

## Deprecation Timeline
- v1 marked deprecated immediately (headers present).
- Sunset target: 2025-12-31 (adjust per release planning).
- After sunset: remove v1 mounting or gate behind feature flag.

## Recommended Migration Steps
1. Inventory lists -> switch to `/api/v2/inventory/items` + relevant `status` + expansions.
2. Replace sales stats/daily endpoints with `/api/v2/sales/reports` or dispatcher.
3. Migrate AR dashboards to `/api/v2/sales/reports?type=ar_summary|ar_aging` (or dedicated `/api/v2/ar/*`).
4. Consolidate customer detail + history calls into single detail request with `expand=purchase_history`.
5. Update permissions UI to use `/api/v2/security/...` endpoints.
6. Move backup management to `/api/v2/system/backups` simplified flow.
7. Remove legacy low-stock / dead-stock calls in favor of items endpoint filters.

## Pending / Future Enhancements
- Creation & mutation endpoints for products/customers in v2 (if full CRUD parity needed).
- Async export/report jobs with job status endpoints (e.g. `/api/v2/reports/jobs`).
- PDF/XLSX format negotiation (`?format=csv|pdf|xlsx`).
- Standard error schema unification & problem+json profile.
- Accurate valuation computations (current placeholders) and turnover metrics.
- Full financial statements (trial balance, P&L, balance sheet) via dispatcher.

## Error Handling Changes
- Simplified 404/400 direct raises; future iteration can wrap in standardized response envelope if required.

## Testing Notes
- Expect `X-API-Version: v2` header for new endpoints.
- V1 requests still respond with `Deprecation` header to surface migration necessity.

---
For questions or to propose additions open a ticket under `migration-v2` label.
