# SOFinance Full Endpoint Catalog (v1)

> Generated from live OpenAPI schema at generation time. This is a human-readable index. For the authoritative machine spec, use `/openapi.json`.
>
> Legend: (A) = Auth required (Bearer); (P) = Public; Methods grouped per path.
>
> NOTE: Response bodies use the standardized success envelope unless noted (raw report exceptions). Error responses follow Problem+JSON (`application/problem+json`).

## 1. Summary Statistics
- Total paths: ~161
- Security schemes: bearerAuth (JWT), OAuth2 password flow
- Common error codes: 401 (auth), 403 (forbidden), 404 (not found), 422 (validation), 500 (internal)

## 2. Authentication & Session
| Method | Path | Auth | Summary |
|--------|------|------|---------|
| POST | /api/v1/auth/login | P | Login (email/password) |
| POST | /api/v1/auth/token | P | OAuth2 password token |
| POST | /api/v1/auth/refresh | P | Refresh access token |
| POST | /api/v1/auth/register | P* | Registration (if enabled) |
| POST | /api/v1/auth/password-reset-request | P | Start password reset |
| POST | /api/v1/auth/password-reset | P | Complete password reset |

Request (login): `{ "email": str, "password": str }`
Success Data: `{ access_token, refresh_token, token_type, user{...} }`

## 3. Users & Permissions
### Users
| Method | Path | Auth | Summary |
|--------|------|------|---------|
| GET | /api/v1/users | A | List users (pagination) |
| POST | /api/v1/users | A | Create user |
| GET | /api/v1/users/{id} | A | Get user |
| PUT | /api/v1/users/{id} | A | Update user |
| DELETE | /api/v1/users/{id} | A | Delete/deactivate user |
| POST | /api/v1/users/{id}/password | A | Change password |

### Permissions
| Method | Path | Auth | Summary |
|--------|------|------|---------|
| GET | /api/v1/permissions | A | List permissions |
| POST | /api/v1/permissions | A | Create permission |
| POST | /api/v1/permissions/assign | A | Assign permission |
| GET | /api/v1/permissions/available | A | All available permissions |

`AvailablePermissionsResponse`: `{ permissions: [str], grouped_permissions: { group: [perm] } }`

## 4. Branches
| Method | Path | Auth | Summary |
|--------|------|------|---------|
| GET | /api/v1/branches | A | List branches |
| POST | /api/v1/branches | A | Create branch |
| GET | /api/v1/branches/{id} | A | Get branch |
| PUT | /api/v1/branches/{id} | A | Update branch |
| DELETE | /api/v1/branches/{id} | A | Delete branch |
| POST | /api/v1/branches/bulk/status | A | Bulk status update |
| POST | /api/v1/branches/bulk/update | A | Bulk update |

Create Body: `{ name: str, address?, phone?, email?, is_active? }`

## 5. Categories & Products
### Categories
| Method | Path | Auth | Summary |
|--------|------|------|---------|
| GET | /api/v1/categories | A | List categories |
| POST | /api/v1/categories | A | Create category |
| GET | /api/v1/categories/{id} | A | Get category |
| PUT | /api/v1/categories/{id} | A | Update category |
| DELETE | /api/v1/categories/{id} | A | Delete category |

### Products
| Method | Path | Auth | Summary |
|--------|------|------|---------|
| GET | /api/v1/products | A | List products (filters) |
| POST | /api/v1/products | A | Create product |
| GET | /api/v1/products/{id} | A | Product details |
| PUT | /api/v1/products/{id} | A | Update product |
| DELETE | /api/v1/products/{id} | A | Delete product |
| GET | /api/v1/products/stats | A | Product stats |

Create Body (ProductCreateSchema): `{ name, sku, cost, price, description?, barcode?, categoryId?, stockQuantity? }`

## 6. Inventory
| Method | Path | Auth | Summary |
|--------|------|------|---------|
| GET | /api/v1/inventory/stock-levels | A | Stock snapshot |
| GET | /api/v1/inventory/low-stock | A | Low stock items |
| GET | /api/v1/inventory/dead-stock | A | Slow/non-moving items |
| GET | /api/v1/inventory/valuation | A | Inventory valuation |
| GET | /api/v1/inventory/reports/turnover | A | Turnover report |
| GET | /api/v1/inventory/reports/movement | A | Movement report |
| GET | /api/v1/inventory/reports/comprehensive | A | Comprehensive report (raw dict) |
| POST | /api/v1/inventory/adjustments | A | Create single stock adjustment |
| POST | /api/v1/inventory/adjustments/bulk | A | Bulk stock adjustments |

StockAdjustmentCreate: `{ product_id, adjustment_type, quantity, reason, notes?, reference_number? }`

## 7. Sales & Payments
| Method | Path | Auth | Summary |
|--------|------|------|---------|
| GET | /api/v1/sales | A | List sales (pagination & filters) |
| POST | /api/v1/sales | A | Create sale (items + optional payments) |
| GET | /api/v1/sales/{sale_id} | A | Sale details |
| PUT | /api/v1/sales/{sale_id} | A | Update sale |
| POST | /api/v1/sales/{sale_id}/payments | A | Add incremental payment |
| GET | /api/v1/sales/{sale_id}/payments | A | List sale payments (cursor) |
| POST | /api/v1/sales/{sale_id}/refund | A | Create refund |
| GET | /api/v1/sales/{sale_id}/receipt | A | Generate receipt |
| GET | /api/v1/sales/stats | A | Sales statistics |
| GET | /api/v1/sales/today/summary | A | Today summary |
| GET | /api/v1/sales/ar/summary | A | Accounts receivable summary |
| GET | /api/v1/sales/ar/aging | A | A/R aging report |
| GET | /api/v1/sales/reports/daily | A | Daily sales report |
| GET | /api/v1/sales/refunds | A | List refunds/returns |

SaleCreateSchema Items: `{ items: [{ product_id|stock_id, quantity, price, subtotal }], payments? / payment? }`
PaymentCreateSchema: `{ amount, account_id?, currency?, reference? }`

## 8. Customers
| Method | Path | Auth | Summary |
|--------|------|------|---------|
| GET | /api/v1/customers | A | List customers |
| POST | /api/v1/customers | A | Create customer |
| GET | /api/v1/customers/{id} | A | Customer details |
| PUT | /api/v1/customers/{id} | A | Update customer |
| DELETE | /api/v1/customers/{id} | A | Delete customer |
| GET | /api/v1/customers/{id}/purchase-history | A | Purchase history |
| POST | /api/v1/customers/bulk-update | A | Bulk update |
| POST | /api/v1/customers/bulk-status | A | Bulk status change |

CustomerCreate: `{ name, email?, phone?, address?, customer_type?, credit_limit?, notes? }`

## 9. Financial Analytics & Reports
| Method | Path | Auth | Summary |
|--------|------|------|---------|
| GET | /api/v1/financial/summary | A | Financial summary |
| GET | /api/v1/financial/dashboard | A | Dashboard metrics |
| GET | /api/v1/financial/income-statement | A | Income statement (raw dict) |
| GET | /api/v1/financial/balance-sheet | A | Balance sheet |
| GET | /api/v1/financial/cash-flow | A | Cash flow statement |
| GET | /api/v1/financial/profit-loss | A | Profit & loss analysis |
| GET | /api/v1/financial/analytics/sales | A | Sales analytics |
| GET | /api/v1/financial/analytics/inventory | A | Inventory analytics |
| GET | /api/v1/financial/ratios | A | Financial ratios |
| GET | /api/v1/financial/alerts | A | Financial alerts |
| GET | /api/v1/financial/tax/report | A | Tax report (year or quarter) |
| GET | /api/v1/financial/today/metrics | A | Today metrics |
| POST | /api/v1/financial/export | A | Export reports (request body) |
| (PDF) GET | /api/v1/financial/*/export.pdf | A | PDF export variants |

FinancialReportRequest: `{ report_type, period?, start_date?, end_date?, branch_id?, include_details? }`

## 10. Journal & Accounting
| Method | Path | Auth | Summary |
|--------|------|------|---------|
| GET | /api/v1/journal/entries | A | List journal entries |
| POST | /api/v1/journal/entries | A | Create journal entry (balanced) |
| GET | /api/v1/journal/entries/{entry_id} | A | Entry details |
| PUT | /api/v1/journal/entries/{entry_id} | A | Update entry |
| DELETE | /api/v1/journal/entries/{entry_id} | A | Delete entry |
| GET | /api/v1/journal/trial-balance | A | Trial balance |
| GET | /api/v1/journal/chart-of-accounts | A | Chart of accounts |
| GET | /api/v1/journal/account-balances | A | Account balances |
| GET | /api/v1/journal/audit-trail | A | Journal audit trail |
| (PDF) GET | /api/v1/journal/entries/{entry_id}/export.pdf | A | Entry PDF |
| (PDF) GET | /api/v1/journal/trial-balance/export.pdf | A | Trial balance PDF |

JournalEntryCreate: `{ reference_type?, reference_id?, date?, lines: [{ account_id, debit?, credit?, description? } ... ] }`

## 11. Accounts (Chart of Accounts API)
| Method | Path | Auth | Summary |
|--------|------|------|---------|
| GET | /api/v1/accounts/ | A | List accounts |
| POST | /api/v1/accounts/ | A | Create account |
| GET | /api/v1/accounts/{account_id} | A | Account details |
| PATCH | /api/v1/accounts/{account_id} | A | Update account |
| POST | /api/v1/accounts/{account_id}/close | A | Close/deactivate account |
| GET | /api/v1/accounts/{account_id}/entries | A | Entries for account |

AccountCreate: `{ name, type, currency?, branch_id? }`

## 12. Audit Logs
| Method | Path | Auth | Summary |
|--------|------|------|---------|
| GET | /api/v1/audit/logs | A | Query audit logs (filters, pagination) |

Query Parameters: `page, page_size, action, entity_type, user_id, severity, search, start, end`

## 13. Notifications
| Method | Path | Auth | Summary |
|--------|------|------|---------|
| GET | /api/v1/notifications | A | List notifications |
| POST | /api/v1/notifications | A | Create notification |
| GET | /api/v1/notifications/unread/count | A | Unread count |
| PUT | /api/v1/notifications/mark-all-read | A | Mark all read |
| PUT | /api/v1/notifications/{notification_id}/read | A | Mark one read |
| DELETE | /api/v1/notifications/{notification_id} | A | Delete notification |
| POST | /api/v1/notifications/send | A | Send (direct) |

Notification Create Body: `{ title, message, type?, user_id? (if system create) }`

## 14. System & Operations
| Method | Path | Auth | Summary |
|--------|------|------|---------|
| GET | /api/v1/info | P | API/system info |
| GET | /health | P | Health (DB ping) |
| GET | /ping | P | Lightweight ping |
| GET | /api/v1/system/info | A | System info (config) |
| PUT | /api/v1/system/info | A | Update info (query params) |
| GET | /api/v1/system/settings | A | Get settings |
| PUT | /api/v1/system/settings | A | Update single setting |
| PUT | /api/v1/system/settings/batch | A | Batch update settings |
| GET | /api/v1/system/health | A | System health (extended) |
| GET | /api/v1/system/stats | A | System statistics |
| GET | /api/v1/system/logs | A | System logs |
| GET | /api/v1/system/backup/create | A | Create backup (sync) |
| GET | /api/v1/system/backup/create/stream | A | Stream backup |
| GET | /api/v1/system/backups | A | List backups |
| POST | /api/v1/system/backups | A | Create backup (body) |
| GET | /api/v1/system/backups/{backup_id} | A | Backup details |
| DELETE | /api/v1/system/backups/{backup_id} | A | Delete backup |
| GET | /api/v1/system/backups/{backup_id}/download | A | Download backup |
| POST | /api/v1/system/backups/{backup_id}/restore | A | Restore (params) |
| POST | /api/v1/system/backups/{backup_id}/restore/async | A | Async restore |
| GET | /api/v1/system/restore-jobs/{job_id} | A | Restore job status |
| POST | /api/v1/system/restore-jobs/{job_id}/cancel | A | Cancel restore job |
| GET | /api/v1/system/backups/{backup_id}/verify | A | Verify checksum |
| GET | /api/v1/system/restore/confirm-token | A | Generate confirm token |
| GET | /api/v1/system/backups/stats | A | Backup stats summary |

Backup Restore Params (key subset): `apply, dry_run, tables, confirm_token`

## 15. Development Utilities (Non-Production)
| Method | Path | Auth | Summary |
|--------|------|------|---------|
| GET | /dev/routes | A* | List all routes (dev mode) |
| GET | /dev/config | A* | Show runtime config |
| GET | /_test_forbidden | P | Test 403 path |
| GET | /_test_failure | P | Test failure response |

## 16. Common Request/Response Schema References
(Selected)
- ProductResponseSchema: Product metadata + pricing + stock status.
- SaleDetailResponseSchema: Includes payments array and outstanding amount.
- JournalEntrySchema: `lines[]` with debit/credit strings, `is_balanced` boolean.
- TrialBalanceSchema: Totals & `is_balanced` flag.
- BackupResponseSchema: `status`, `type`, `sizeMB`, timestamps.

## 17. Pagination Patterns
List endpoints typically accept: `page` (default 1), `size|limit` (defaults vary), or `cursor` for some payment/notification lists. Responses: `data.items` + optional `data.pagination` or domain-specific counters.

## 18. Error Responses
Standard validation: 422 Problem+JSON with `errors` array.
Auth failures: 401 Problem+JSON (`Authentication Failed`).
Forbidden: 403 Problem+JSON (`HTTP Error`).
Not found: 404 Problem+JSON (`Resource Not Found`).
Internal: 500 Problem+JSON (`Internal Server Error`).

## 19. Security Notes
All endpoints marked (A) require one of: `Authorization: Bearer <access_token>` or OAuth2 session obtained via `/api/v1/auth/token` flow. Public endpoints intentionally exclude security requirements in OpenAPI.

## 20. Deprecation / Transitional Behavior
- Raw responses still present: inventory comprehensive report, income statement (will be enveloped later).
- Transitional response normalization middleware still wraps legacy outputs; new clients should rely solely on `data`.

## 21. Change Tracking
Regenerate this document whenever models or routes change:
1. Start server.
2. Fetch `/openapi.json`.
3. Run internal script (future enhancement) to rebuild `ENDPOINTS_FULL.md`.

---
Auto-generated reference complete. For schema property-level details, inspect `components.schemas` in `/openapi.json`.
