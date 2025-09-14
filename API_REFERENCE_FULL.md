# SOFinance Full API Reference

> Exhaustive machine-derived reference. For narrative overview see API_REFERENCE.md. Regenerate via `python scripts/generate_full_api_reference.py`.

**Title:** SOFinance POS System  
**Version:** 1.0.0  
**Total Endpoints:** 161

## Conventions

- All responses use the unified envelope unless explicitly stated.
- Pagination indicated where detected.
- Error envelope fields: `success, error_code, message, details, timestamp`.


## Segment: /_test_failure

### GET /_test_failure

**Summary:**  Test Failure

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---


## Segment: /_test_forbidden

### GET /_test_forbidden

**Summary:**  Test Forbidden

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---


## Segment: /api

### GET /api/v1/accounts/

**Summary:** List accounts

**Tags:** 🏦 Accounts, 🏦 Accounts

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| page | query | False | integer |  |
| limit | query | False | integer |  |
| search | query | False |  |  |
| type | query | False |  |  |
| branch_id | query | False |  |  |
| active | query | False |  |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/accounts/

**Summary:** Create account

**Tags:** 🏦 Accounts, 🏦 Accounts

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | True |  |
| type | string | True | Account type enum value |
| currency | string | False | Currency code |
| branch_id | object | False | Owning branch ID |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/accounts/{account_id}

**Summary:** Get account

**Tags:** 🏦 Accounts, 🏦 Accounts

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| account_id | path | True | integer |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PATCH /api/v1/accounts/{account_id}

**Summary:** Update account

**Tags:** 🏦 Accounts, 🏦 Accounts

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| account_id | path | True | integer |  |

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | object | False |  |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/accounts/{account_id}/close

**Summary:** Close (deactivate) account

**Tags:** 🏦 Accounts, 🏦 Accounts

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| account_id | path | True | integer |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/accounts/{account_id}/entries

**Summary:** List journal entries for account

**Tags:** 🏦 Accounts, 🏦 Accounts

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| account_id | path | True | integer |  |
| page | query | False | integer |  |
| limit | query | False | integer |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/audit/logs

**Summary:** List Audit Logs

**Tags:** 🧾 Audit, 🧾 Audit

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| page | query | False | integer |  |
| page_size | query | False | integer |  |
| action | query | False |  | Filter by action enum (e.g. CREATE_USER) |
| entity_type | query | False |  | Filter by entity type |
| user_id | query | False |  | Filter by user id |
| severity | query | False |  | Severity level |
| search | query | False |  | Search entity id contains |
| start | query | False |  | Start ISO timestamp (inclusive) |
| end | query | False |  | End ISO timestamp (exclusive) |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/auth/login

**Summary:** User login

**Tags:** 🔐 Authentication, 🔐 Authentication

**Auth Required:** Maybe

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | object | False | Username |
| email | object | False | Email address |
| password | string | True | Password |
| remember_me | boolean | False | Remember me option |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/auth/logout

**Summary:** Logout current user

**Tags:** 🔐 Authentication, 🔐 Authentication

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/auth/password-reset-request

**Summary:** Request password reset

**Tags:** 🔐 Authentication, 🔐 Authentication

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | True | User email address |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/auth/refresh

**Summary:** Refresh access token

**Tags:** 🔐 Authentication, 🔐 Authentication

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| refresh_token | string | True | Refresh token |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/auth/token

**Summary:** OAuth2 Token

**Tags:** 🔐 Authentication, 🔐 Authentication

**Auth Required:** Maybe

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| grant_type | object | False |  |
| username | string | True |  |
| password | string | True |  |
| scope | string | False |  |
| client_id | object | False |  |
| client_secret | object | False |  |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/branches/

**Summary:** List Branches

**Tags:** 🏢 Branch Management, 🏢 Branches

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| page | query | False | integer | Page number |
| size | query | False | integer | Number of branches to return |
| search | query | False |  | Search term |
| status | query | False |  | Status filter (ACTIVE/INACTIVE) |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/branches/

**Summary:** Create Branch

**Tags:** 🏢 Branch Management, 🏢 Branches

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | True | Branch name |
| address | object | False | Branch address |
| phone | object | False | Branch phone number |
| email | object | False | Branch contact email |
| is_active | boolean | False |  |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/branches/bulk/status

**Summary:** Bulk Update Branch Status

**Tags:** 🏢 Branch Management, 🏢 Branches

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| branch_ids | array[integer] | True | List of branch IDs |
| status | object | True | New status |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/branches/bulk/update

**Summary:** Bulk Update Branches

**Tags:** 🏢 Branch Management, 🏢 Branches

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| branch_ids | array[integer] | True | List of branch IDs |
| updates | object | True | Updates to apply |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/branches/statistics

**Summary:** Get Branch Statistics Alias

**Tags:** 🏢 Branch Management, 🏢 Branches

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/branches/stats/summary

**Summary:** Get Branch Statistics

**Tags:** 🏢 Branch Management, 🏢 Branches

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/branches/summary/light

**Summary:** Get Branches Light Summary

**Tags:** 🏢 Branch Management, 🏢 Branches

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### DELETE /api/v1/branches/{branch_id}

**Summary:** Delete Branch

**Tags:** 🏢 Branch Management, 🏢 Branches

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| branch_id | path | True | integer | Branch ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/branches/{branch_id}

**Summary:** Get Branch Details

**Tags:** 🏢 Branch Management, 🏢 Branches

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| branch_id | path | True | integer | Branch ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/branches/{branch_id}

**Summary:** Update Branch

**Tags:** 🏢 Branch Management, 🏢 Branches

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| branch_id | path | True | integer | Branch ID |

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | object | False |  |
| address | object | False |  |
| phone | object | False |  |
| email | object | False |  |
| manager_name | object | False |  |
| status | object | False |  |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/branches/{branch_id}/inventory

**Summary:** Get Branch Inventory

**Tags:** 🏢 Branch Management, 🏢 Branches

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| branch_id | path | True | integer | Branch ID |
| low_stock_only | query | False | boolean | Show only low stock items |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/branches/{branch_id}/performance

**Summary:** Get Branch Performance

**Tags:** 🏢 Branch Management, 🏢 Branches

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| branch_id | path | True | integer | Branch ID |
| days | query | False | integer | Number of days to analyze |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/categories/

**Summary:** List categories

**Tags:** 📂 Product Categories, 📂 Categories

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| page | query | False | integer | Page number |
| size | query | False | integer | Page size |
| search | query | False |  | Search term |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/categories/

**Summary:** Create category

**Tags:** 📂 Product Categories, 📂 Categories

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | True | Category name |
| description | object | False | Category description |

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | True | Category name |
| description | object | False | Category description |
| id | integer | True | Category ID |
| status | object | False | Category status |
| createdAt | string | True | Created timestamp |
| updatedAt | string | True | Updated timestamp |
| product_count | integer | False | Number of products in category |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### DELETE /api/v1/categories/{category_id}

**Summary:** Delete category

**Tags:** 📂 Product Categories, 📂 Categories

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| category_id | path | True | integer |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/categories/{category_id}

**Summary:** Get category

**Tags:** 📂 Product Categories, 📂 Categories

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| category_id | path | True | integer |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/categories/{category_id}

**Summary:** Update category

**Tags:** 📂 Product Categories, 📂 Categories

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| category_id | path | True | integer |  |

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | object | False |  |
| description | object | False |  |

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | True | Category name |
| description | object | False | Category description |
| id | integer | True | Category ID |
| status | object | False | Category status |
| createdAt | string | True | Created timestamp |
| updatedAt | string | True | Updated timestamp |
| product_count | integer | False | Number of products in category |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/customers/

**Summary:** List Customers

**Tags:** 🤝 Customer Management, 👤 Customers

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| search | query | False |  | Search customers by name, email, or phone |
| customer_type | query | False |  | Filter by customer type |
| status | query | False |  | Filter by customer status |
| page | query | False | integer | Page number |
| size | query | False | integer | Number of customers to return |
| expand | query | False |  | Comma separated expansions: ar_summary,stats |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/customers/

**Summary:** Create Customer

**Tags:** 🤝 Customer Management, 👤 Customers

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | True | Customer name |
| email | object | False | Customer email address |
| phone | object | False | Customer phone number |
| address | object | False | Customer address |
| customer_type | object | False | Customer type |
| credit_limit | object | False | Credit limit |
| balance | object | False | Current balance |
| total_purchases | object | False | Total purchases |
| status | object | False | Customer status |
| notes | object | False | Additional notes |
| firstName | object | False |  |
| lastName | object | False |  |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/customers/bulk-update

**Summary:** Bulk Update Customers Alias

**Tags:** 🤝 Customer Management, 👤 Customers

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

``{
  "type": "object",
  "title": "Payload"
}``

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/customers/bulk/status

**Summary:** Bulk Update Customer Status

**Tags:** 🤝 Customer Management, 👤 Customers

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| customer_ids | array[integer] | True | List of customer IDs |
| status | object | True | New status for all customers |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/customers/bulk/update

**Summary:** Bulk Update Customers

**Tags:** 🤝 Customer Management, 👤 Customers

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| customer_ids | array[integer] | True | List of customer IDs to update |
| update_data | object | True | Updates to apply |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/customers/statistics

**Summary:** Get Customer Statistics Alias

**Tags:** 🤝 Customer Management, 👤 Customers

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/customers/stats/summary

**Summary:** Get Customer Statistics

**Tags:** 🤝 Customer Management, 👤 Customers

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### DELETE /api/v1/customers/{customer_id}

**Summary:** Delete Customer

**Tags:** 🤝 Customer Management, 👤 Customers

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| customer_id | path | True | integer | Customer ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/customers/{customer_id}

**Summary:** Get Customer Details

**Tags:** 🤝 Customer Management, 👤 Customers

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| customer_id | path | True | integer | Customer ID |
| expand | query | False |  | Comma separated expansions: ar_summary,stats |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/customers/{customer_id}

**Summary:** Update Customer

**Tags:** 🤝 Customer Management, 👤 Customers

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| customer_id | path | True | integer | Customer ID |

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | object | False | Customer name |
| email | object | False | Customer email address |
| phone | object | False | Customer phone number |
| address | object | False | Customer address |
| type | object | False | Customer type |
| credit_limit | object | False | Credit limit |
| status | object | False | Customer status |
| notes | object | False | Additional notes |
| firstName | object | False |  |
| lastName | object | False |  |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/customers/{customer_id}/ar/summary

**Summary:** Get Customer Ar Summary

**Tags:** 🤝 Customer Management, 👤 Customers

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| customer_id | path | True | integer | Customer ID |
| branch_id | query | False |  | Optional branch filter (currently unused placeholder) |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/customers/{customer_id}/balance

**Summary:** Get Customer Balance

**Tags:** 🤝 Customer Management, 👤 Customers

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| customer_id | path | True | integer | Customer ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/customers/{customer_id}/balance/adjust

**Summary:** Adjust Customer Balance

**Tags:** 🤝 Customer Management, 👤 Customers

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| customer_id | path | True | integer | Customer ID |
| amount | query | True | number | Amount to adjust (positive or negative) |
| reason | query | True | string | Reason for balance adjustment |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/customers/{customer_id}/history

**Summary:** Get Customer Purchase History

**Tags:** 🤝 Customer Management, 👤 Customers

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| customer_id | path | True | integer | Customer ID |
| limit | query | False | integer | Number of purchases to return |
| offset | query | False | integer | Number of purchases to skip |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/customers/{customer_id}/purchase-history

**Summary:** Get Customer Purchase History Alias

**Tags:** 🤝 Customer Management, 👤 Customers

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| customer_id | path | True | integer | Customer ID |
| page | query | False | integer | Page number |
| size | query | False | integer | Page size |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/alerts

**Summary:** Get Financial Alerts

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/analytics/inventory

**Summary:** Get Inventory Analytics

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/analytics/sales

**Summary:** Get Sales Analytics

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| start_date | query | False |  | Analytics start date |
| end_date | query | False |  | Analytics end date |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/balance-sheet

**Summary:** Generate Balance Sheet

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| start_date | query | False |  | Balance sheet start date |
| end_date | query | False |  | Balance sheet end date |
| branch_id | query | False |  | Filter by branch ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/balance-sheet/export.pdf

**Summary:** Export Balance Sheet Pdf

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| end_date | query | False |  |  |
| branch_id | query | False |  |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/budget-comparison

**Summary:** Get Budget Comparison

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/cash-flow

**Summary:** Generate Cash Flow Statement

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| start_date | query | False |  | Cash flow start date |
| end_date | query | False |  | Cash flow end date |
| branch_id | query | False |  | Filter by branch ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/cash-flow/export.pdf

**Summary:** Export Cash Flow Pdf

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| start_date | query | False |  |  |
| end_date | query | False |  |  |
| branch_id | query | False |  |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/customer-analytics

**Summary:** Get Customer Analytics Alias

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/dashboard

**Summary:** Get Dashboard Summary

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/financial/export

**Summary:** Export Financial Data

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| report_type | object | True | Type of report to generate |
| period | object | False | Report period |
| start_date | object | False | Start date for custom period |
| end_date | object | False | End date for custom period |
| branch_id | object | False | Specific branch ID for branch reports |
| include_details | boolean | False | Include detailed breakdown |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/income-statement

**Summary:** Generate Income Statement

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| start_date | query | False |  | Income statement start date |
| end_date | query | False |  | Income statement end date |
| period | query | False |  | Report period (e.g., MONTHLY) |
| year | query | False |  | Year for period-based queries |
| month | query | False |  | Month for period-based queries |
| branch_id | query | False |  | Filter by branch ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/income-statement/export.pdf

**Summary:** Export Income Statement Pdf

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| start_date | query | False |  |  |
| end_date | query | False |  |  |
| branch_id | query | False |  |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/inventory-analytics

**Summary:** Get Inventory Analytics Alias

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/performance

**Summary:** Get Performance Metrics

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/profit-loss

**Summary:** Get Profit Loss Report

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| start_date | query | False |  | P&L start date |
| end_date | query | False |  | P&L end date |
| branch_id | query | False |  | Filter by branch ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/profit-loss/export.pdf

**Summary:** Export Profit Loss Pdf

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| start_date | query | False |  |  |
| end_date | query | False |  |  |
| branch_id | query | False |  |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/ratios

**Summary:** Get Financial Ratios

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| start_date | query | False |  | Ratios calculation start date |
| end_date | query | False |  | Ratios calculation end date |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/sales-analytics

**Summary:** Get Sales Analytics Alias

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/summary

**Summary:** Get Financial Summary

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| start_date | query | False |  | Summary start date |
| end_date | query | False |  | Summary end date |
| branch_id | query | False |  | Filter by branch ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/tax-report

**Summary:** Generate Tax Report Alias

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| period | query | False |  |  |
| year | query | True | integer |  |
| quarter | query | False |  |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/tax/report

**Summary:** Generate Tax Report

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| tax_year | query | True | integer | Tax year for the report |
| quarter | query | False |  | Specific quarter (1-4) |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/financial/today/metrics

**Summary:** Get Today Metrics

**Tags:** 📈 Financial Analytics, 📊 Financial

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/info

**Summary:** Api Info

**Tags:** ℹ️ System Information

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/inventory/dashboard

**Summary:** Get Inventory Dashboard

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/inventory/dead-stock

**Summary:** Get Dead Stock Analysis

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| days_threshold | query | False | integer | Days without sales to consider dead stock |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/inventory/dead-stock/latest

**Summary:** Get Dead Stock Latest

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/inventory/dead-stock/scan

**Summary:** Trigger Dead Stock Scan

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| days_threshold | query | False |  |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/inventory/items

**Summary:** Unified Inventory Items

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| status | query | False | string |  |
| search | query | False |  |  |
| category_id | query | False |  |  |
| branch_id | query | False |  |  |
| page | query | False | integer |  |
| size | query | False | integer |  |
| low_stock_threshold | query | False |  |  |
| expand | query | False |  | Comma separated expansions: valuation,sales_timeseries |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/inventory/low-stock

**Summary:** Get Low Stock Alias

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/inventory/low-stock-alerts

**Summary:** Get Low Stock Alerts

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/inventory/low-stock/batch

**Summary:** Get Low Stock Batch

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| page | query | False | integer |  |
| page_size | query | False | integer |  |
| threshold | query | False |  | Override default low stock threshold |
| search | query | False |  | Search by product name or SKU |
| category_id | query | False |  | Filter by category id |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/inventory/reorder-points/{product_id}

**Summary:** Update Reorder Point

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| product_id | path | True | integer |  |

**Request Body Schema**

``{
  "type": "object",
  "title": "Body"
}``

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/inventory/reports/comprehensive

**Summary:** Get Comprehensive Inventory Report

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| days | query | False | integer | Report period in days |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/inventory/reports/movement

**Summary:** Get Stock Movements

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| product_id | query | False |  | Filter by product ID |
| branch_id | query | False |  | Filter by branch ID |
| limit | query | False | integer | Number of movements to return |
| offset | query | False | integer | Number of movements to skip |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/inventory/reports/turnover

**Summary:** Get Inventory Stats

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/inventory/sales-timeseries

**Summary:** Get Sales Timeseries

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| product_id | query | True | integer | Product ID to fetch sales timeseries for |
| days | query | False | integer | Number of days (inclusive) |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/inventory/stock-adjustments

**Summary:** List Stock Adjustments

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| page | query | False | integer |  |
| page_size | query | False | integer |  |
| product_id | query | False |  | Filter by product id |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/inventory/stock-adjustments

**Summary:** Adjust Stock

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| product_id | integer | True | Product ID to adjust |
| adjustment_type | object | True | Type of adjustment |
| quantity | integer | True | Quantity to adjust |
| reason | string | True | Reason for adjustment |
| notes | object | False | Additional notes |
| reference_number | object | False | Reference number |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/inventory/stock-levels

**Summary:** List Inventory

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| branch_id | query | False |  | Filter by branch ID |
| low_stock_only | query | False | boolean | Show only low stock items |
| status_filter | query | False |  | Filter by stock status |
| category_id | query | False |  | Filter by category |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/inventory/summary

**Summary:** Unified Inventory Summary

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/inventory/valuation

**Summary:** Get Inventory Valuation

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| category_id | query | False |  | Filter by category ID (accepts string or id) |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/inventory/{product_id}

**Summary:** Get Product Stock

**Tags:** 📊 Inventory Management, 📦 Inventory

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| product_id | path | True | integer | Product ID |
| branch_id | query | False |  | Specific branch inventory |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/journal/account-balances

**Summary:** Get Account Balances

**Tags:** 📚 Journal Entries, 📒 Journal

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| account_code | query | False |  | Specific account code |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/journal/audit-trail

**Summary:** Get Audit Trail

**Tags:** 📚 Journal Entries, 📒 Journal

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| start_date | query | False |  | Audit trail start date |
| end_date | query | False |  | Audit trail end date |
| user_id | query | False |  | Filter by user ID |
| limit | query | False | integer | Number of audit entries to return |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/journal/chart-of-accounts

**Summary:** Get Chart Of Accounts

**Tags:** 📚 Journal Entries, 📒 Journal

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/journal/entries

**Summary:** Get Journal Entries

**Tags:** 📚 Journal Entries, 📒 Journal

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| start_date | query | False |  | Filter entries from this date |
| end_date | query | False |  | Filter entries up to this date |
| entry_type | query | False |  | Filter by entry type |
| limit | query | False | integer | Number of entries to return |
| offset | query | False | integer | Number of entries to skip |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| success | boolean | False |  |
| message | string | False |  |
| data | object | False |  |
| error | object | False |  |
| meta | object | False |  |
| timestamp | string | False |  |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/journal/entries

**Summary:** Create Journal Entry

**Tags:** 📚 Journal Entries, 📒 Journal

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| reference_type | object | False | Type of business transaction |
| reference_id | object | False | ID of the business record |
| lines | array[JournalEntryLineSchema-Input] | True |  |
| date | object | False |  |

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| success | boolean | False |  |
| message | string | False |  |
| data | object | False |  |
| error | object | False |  |
| meta | object | False |  |
| timestamp | string | False |  |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### DELETE /api/v1/journal/entries/{entry_id}

**Summary:** Delete Journal Entry

**Tags:** 📚 Journal Entries, 📒 Journal

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| entry_id | path | True | integer | Journal entry ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/journal/entries/{entry_id}

**Summary:** Get Journal Entry Details

**Tags:** 📚 Journal Entries, 📒 Journal

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| entry_id | path | True | integer | Journal entry ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| success | boolean | False |  |
| message | string | False |  |
| data | object | False |  |
| error | object | False |  |
| meta | object | False |  |
| timestamp | string | False |  |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/journal/entries/{entry_id}

**Summary:** Update Journal Entry

**Tags:** 📚 Journal Entries, 📒 Journal

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| entry_id | path | True | integer | Journal entry ID |

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| reference_type | object | False |  |
| reference_id | object | False |  |
| lines | object | False |  |
| date | object | False |  |

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| success | boolean | False |  |
| message | string | False |  |
| data | object | False |  |
| error | object | False |  |
| meta | object | False |  |
| timestamp | string | False |  |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/journal/entries/{entry_id}/export.pdf

**Summary:** Export Journal Entry Pdf

**Tags:** 📚 Journal Entries, 📒 Journal

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| entry_id | path | True | integer |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/journal/trial-balance

**Summary:** Get Trial Balance

**Tags:** 📚 Journal Entries, 📒 Journal

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| as_of_date | query | False |  | Trial balance as of this date |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| success | boolean | False |  |
| message | string | False |  |
| data | object | False |  |
| error | object | False |  |
| meta | object | False |  |
| timestamp | string | False |  |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/journal/trial-balance/export.pdf

**Summary:** Export Trial Balance Pdf

**Tags:** 📚 Journal Entries, 📒 Journal

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| as_of_date | query | False |  |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/notifications

**Summary:** Get User Notifications

**Tags:** 🔔 Notifications, 🔔 Notifications

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| unread_only | query | False | boolean | Show only unread notifications |
| limit | query | False | integer | Number of notifications to return |
| offset | query | False | integer | Notifications offset for pagination |
| cursor | query | False |  | Cursor (notification id) for pagination |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/notifications

**Summary:** Create Notification

**Tags:** 🔔 Notifications, 🔔 Notifications

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

``{
  "type": "object",
  "title": "Payload"
}``

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/notifications/

**Summary:** Get User Notifications

**Tags:** 🔔 Notifications, 🔔 Notifications

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| unread_only | query | False | boolean | Show only unread notifications |
| limit | query | False | integer | Number of notifications to return |
| offset | query | False | integer | Notifications offset for pagination |
| cursor | query | False |  | Cursor (notification id) for pagination |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/notifications/

**Summary:** Create Notification

**Tags:** 🔔 Notifications, 🔔 Notifications

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

``{
  "type": "object",
  "title": "Payload"
}``

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/notifications/mark-all-read

**Summary:** Mark All Read

**Tags:** 🔔 Notifications, 🔔 Notifications

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/notifications/send

**Summary:** Send Notification

**Tags:** 🔔 Notifications, 🔔 Notifications

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| user_id | query | True | integer | Target user ID |
| title | query | True | string | Notification title |
| message | query | True | string | Notification message |
| type | query | False | string | Notification type |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/notifications/unread/count

**Summary:** Get Unread Count

**Tags:** 🔔 Notifications, 🔔 Notifications

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### DELETE /api/v1/notifications/{notification_id}

**Summary:** Delete Notification

**Tags:** 🔔 Notifications, 🔔 Notifications

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| notification_id | path | True | string | Notification ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/notifications/{notification_id}/read

**Summary:** Mark Notification Read

**Tags:** 🔔 Notifications, 🔔 Notifications

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| notification_id | path | True | string | Notification ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/permissions/

**Summary:** List Permissions

**Tags:** 🛡️ Permissions & Admin, 🔑 Permissions

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| success | boolean | False |  |
| message | string | False |  |
| data | object | False |  |
| error | object | False |  |
| meta | object | False |  |
| timestamp | string | False |  |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/permissions/check

**Summary:** Check Permission

**Tags:** 🛡️ Permissions & Admin, 🔑 Permissions

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| permission | query | True | string | Permission to check |
| user_id | query | False |  | User ID (defaults to current user) |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/permissions/roles/

**Summary:** List Roles

**Tags:** 🛡️ Permissions & Admin, 🔑 Permissions

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/permissions/user/{user_id}

**Summary:** Get User Permissions

**Tags:** 🛡️ Permissions & Admin, 🔑 Permissions

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| user_id | path | True | integer | User ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| success | boolean | False |  |
| message | string | False |  |
| data | object | False |  |
| error | object | False |  |
| meta | object | False |  |
| timestamp | string | False |  |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/permissions/user/{user_id}/assign-role

**Summary:** Assign Role To User

**Tags:** 🛡️ Permissions & Admin, 🔑 Permissions

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| user_id | path | True | integer | User ID |
| role_id | query | True | integer | Role ID to assign |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/permissions/user/{user_id}/grant

**Summary:** Grant Permission

**Tags:** 🛡️ Permissions & Admin, 🔑 Permissions

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| user_id | path | True | integer | User ID |
| permission | query | True | string | Permission to grant in form 'resource:action' |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/permissions/user/{user_id}/grant/batch

**Summary:** Grant Permissions Batch

**Tags:** 🛡️ Permissions & Admin, 🔑 Permissions

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| user_id | path | True | integer | User ID |
| permissions | query | True | array | Repeated permission parameters e.g. ?permissions=resource:action |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### DELETE /api/v1/permissions/user/{user_id}/revoke

**Summary:** Revoke Permission

**Tags:** 🛡️ Permissions & Admin, 🔑 Permissions

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| user_id | path | True | integer | User ID |
| permission | query | True | string | Permission to revoke in form 'resource:action' |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/permissions/user/{user_id}/revoke/batch

**Summary:** Revoke Permissions Batch

**Tags:** 🛡️ Permissions & Admin, 🔑 Permissions

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| user_id | path | True | integer | User ID |
| permissions | query | True | array | Repeated permission parameters e.g. ?permissions=resource:action |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/products/

**Summary:** List products

**Tags:** 📦 Product Management, 🛍️ Products

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| page | query | False | integer | Page number |
| size | query | False | integer | Page size |
| search | query | False |  | Search term |
| category_id | query | False |  | Filter by category ID |
| status | query | False |  | Filter by status |
| stock_status | query | False |  | Filter by stock status |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| items | array[ProductResponseSchema] | True | List of products |
| total | integer | True | Total number of products |
| page | integer | True | Current page |
| size | integer | True | Page size |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/products/

**Summary:** Create Product

**Tags:** 📦 Product Management, 🛍️ Products

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | True | Product name |
| description | object | False | Product description |
| sku | string | True | Stock Keeping Unit |
| barcode | object | False | Product barcode |
| categoryId | object | False | Category ID |
| cost | object | True | Cost price |
| price | object | True | Selling price |
| stockQuantity | integer | False | Initial stock quantity |

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | True | Product name |
| description | object | False | Product description |
| sku | string | True | Stock Keeping Unit |
| barcode | object | False | Product barcode |
| categoryId | object | False | Category ID |
| costPrice | string | True | Cost price |
| sellingPrice | string | True | Selling price |
| id | integer | True | Product ID |
| stockStatus | object | True | Current stock status |
| profitMargin | string | True | Profit margin percentage |
| createdAt | string | True | Creation timestamp |
| updatedAt | string | True | Last update timestamp |
| categoryName | object | False | Category name |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/products/statistics

**Summary:** Get product statistics (alias)

**Tags:** 📦 Product Management, 🛍️ Products

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| totalProducts | integer | True | Total number of products |
| categoriesCount | integer | True | Number of categories |
| productsByCategory | object | True | Products count by category |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/products/stats

**Summary:** Get product statistics

**Tags:** 📦 Product Management, 🛍️ Products

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| totalProducts | integer | True | Total number of products |
| categoriesCount | integer | True | Number of categories |
| productsByCategory | object | True | Products count by category |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/products/stock/adjust

**Summary:** Adjust stock

**Tags:** 📦 Product Management, 🛍️ Products

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| product_id | integer | True | Product ID |
| quantity_change | integer | True | Quantity change (positive for increase, negative for decrease) |
| reason | string | True | Reason for adjustment |
| notes | object | False | Additional notes |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/products/stock/bulk-adjust

**Summary:** Bulk adjust stock

**Tags:** 📦 Product Management, 🛍️ Products

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| adjustments | array[StockAdjustmentSchema] | True | List of stock adjustments |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### DELETE /api/v1/products/{product_id}

**Summary:** Delete product

**Tags:** 📦 Product Management, 🛍️ Products

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| product_id | path | True | integer |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/products/{product_id}

**Summary:** Get product

**Tags:** 📦 Product Management, 🛍️ Products

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| product_id | path | True | integer |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/products/{product_id}

**Summary:** Update product

**Tags:** 📦 Product Management, 🛍️ Products

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| product_id | path | True | integer |  |

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | object | False |  |
| description | object | False |  |
| sku | object | False |  |
| barcode | object | False |  |
| categoryId | object | False |  |
| cost | object | False |  |
| price | object | False |  |
| status | object | False |  |

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | True | Product name |
| description | object | False | Product description |
| sku | string | True | Stock Keeping Unit |
| barcode | object | False | Product barcode |
| categoryId | object | False | Category ID |
| costPrice | string | True | Cost price |
| sellingPrice | string | True | Selling price |
| id | integer | True | Product ID |
| stockStatus | object | True | Current stock status |
| profitMargin | string | True | Profit margin percentage |
| createdAt | string | True | Creation timestamp |
| updatedAt | string | True | Last update timestamp |
| categoryName | object | False | Category name |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/products/{product_id}/adjust-stock

**Summary:** Adjust stock for a product

**Tags:** 📦 Product Management, 🛍️ Products

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| product_id | path | True | integer |  |

**Request Body Schema**

``{
  "type": "object",
  "title": "Payload"
}``

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/sales

**Summary:** Get Sales

**Tags:** 💰 Sales Management, 💳 Sales

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| page | query | False | integer | Page number |
| size | query | False | integer | Page size |
| branch_id | query | False |  | Filter by branch ID |
| customer_id | query | False |  | Filter by customer ID |
| start_date | query | False |  | Filter sales from this date (date or datetime) |
| end_date | query | False |  | Filter sales until this date (date or datetime) |
| payment_method | query | False |  | Filter by payment method |
| status | query | False |  | Filter by sale status |
| include_deleted | query | False | boolean | Include soft deleted sales |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/sales/

**Summary:** Get Sales Protected

**Tags:** 💰 Sales Management, 💳 Sales

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| page | query | False | integer | Page number |
| size | query | False | integer | Page size |
| branch_id | query | False |  | Filter by branch ID |
| customer_id | query | False |  | Filter by customer ID |
| start_date | query | False |  | Filter sales from this date (date or datetime) |
| end_date | query | False |  | Filter sales until this date (date or datetime) |
| payment_method | query | False |  | Filter by payment method |
| status | query | False |  | Filter by sale status |
| include_deleted | query | False | boolean | Include soft deleted sales |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/sales/

**Summary:** Create Sale

**Tags:** 💰 Sales Management, 💳 Sales

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| required | query | False | boolean |  |

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| branch_id | object | False |  |
| total_amount | object | False |  |
| discount | object | False | Discount amount |
| payment_type | object | False | Payment type (FULL, PARTIAL, UNPAID, SPLIT) |
| customer_id | object | False |  |
| user_id | object | False |  |
| items | array[SaleItemCreateSchema] | True | Sale items |
| payment | object | False | Single payment line |
| payments | object | False | Multiple payment lines |
| customer_name | object | False | Customer full name (pay later) |
| customer_email | object | False | Customer email (pay later) |
| customer_phone | object | False | Customer phone (pay later) |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/sales/ar/aging

**Summary:** Get Accounts Receivable Aging

**Tags:** 💰 Sales Management, 💳 Sales

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| branch_id | query | False |  | Filter by branch ID |
| bucket_days | query | False | string | Comma-separated aging bucket thresholds (days) |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/sales/ar/summary

**Summary:** Get Accounts Receivable Summary

**Tags:** 💰 Sales Management, 💳 Sales

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| branch_id | query | False |  | Filter by branch ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/sales/refunds

**Summary:** List Returns

**Tags:** 💰 Sales Management, 💳 Sales

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| start_date | query | False |  | Filter returns from this date |
| end_date | query | False |  | Filter returns up to this date |
| limit | query | False | integer | Number of returns to return |
| offset | query | False | integer | Number of returns to skip |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/sales/reports/daily

**Summary:** Get Daily Sales Report

**Tags:** 💰 Sales Management, 💳 Sales

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| start_date | query | False |  | Report start date |
| end_date | query | False |  | Report end date |
| branch_id | query | False |  | Filter by branch ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| success | boolean | False |  |
| message | string | False |  |
| data | object | False |  |
| error | object | False |  |
| meta | object | False |  |
| timestamp | string | False |  |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/sales/stats

**Summary:** Get Sales Statistics

**Tags:** 💰 Sales Management, 💳 Sales

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| start_date | query | False |  | Statistics from this date |
| end_date | query | False |  | Statistics up to this date |
| branch_id | query | False |  | Filter by branch ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| total_sales | integer | True | Total number of sales |
| total_revenue | number | True | Total revenue |
| total_discount | number | True | Total discount given |
| average_sale_value | number | True | Average sale amount |
| payment_method_breakdown | object | True | Payment method breakdown |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/sales/summary

**Summary:** Sales Summary

**Tags:** 💰 Sales Management, 💳 Sales

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| range_days | query | False | integer |  |
| include | query | False |  | Comma separated includes: top |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/sales/today/summary

**Summary:** Get Today Summary

**Tags:** 💰 Sales Management, 💳 Sales

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| branch_id | query | False |  | Filter by branch ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/sales/{sale_id}

**Summary:** Get Sale Details

**Tags:** 💰 Sales Management, 💳 Sales

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| sale_id | path | True | integer | Sale ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/sales/{sale_id}

**Summary:** Update Sale

**Tags:** 💰 Sales Management, 💳 Sales

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| sale_id | path | True | integer | Sale ID |

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| customer_name | object | False |  |
| customer_email | object | False |  |
| customer_phone | object | False |  |
| discount_amount | object | False |  |
| tax_amount | object | False |  |
| notes | object | False |  |
| status | object | False |  |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/sales/{sale_id}/payments

**Summary:** List Sale Payments

**Tags:** 💰 Sales Management, 💳 Sales

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| sale_id | path | True | integer | Sale ID |
| limit | query | False | integer | Page size |
| cursor | query | False |  | Cursor (payment id) for pagination |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/sales/{sale_id}/payments

**Summary:** Add Payment To Sale

**Tags:** 💰 Sales Management, 💳 Sales

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| sale_id | path | True | integer | Sale ID |

**Request Body Schema**

``{
  "type": "object",
  "title": "Payload"
}``

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/sales/{sale_id}/receipt

**Summary:** Get Sale Receipt

**Tags:** 💰 Sales Management, 💳 Sales

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| sale_id | path | True | integer | Sale ID |
| print_format | query | False | boolean | Format for printing |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| success | boolean | False |  |
| message | string | False |  |
| data | object | False |  |
| error | object | False |  |
| meta | object | False |  |
| timestamp | string | False |  |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/stock-requests

**Summary:** List Stock Requests

**Tags:** 📋 Stock Requests, 📥 Stock Requests

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| status_filter | query | False |  | Filter by request status |
| from_branch_id | query | False |  | Filter by source branch |
| to_branch_id | query | False |  | Filter by destination branch |
| limit | query | False | integer | Number of requests to return |
| offset | query | False | integer | Number of requests to skip |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/stock-requests

**Summary:** Create Stock Request

**Tags:** 📋 Stock Requests, 📥 Stock Requests

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

``{
  "type": "object",
  "title": "Request Data"
}``

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/stock-requests/

**Summary:** List Stock Requests

**Tags:** 📋 Stock Requests, 📥 Stock Requests

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| status_filter | query | False |  | Filter by request status |
| from_branch_id | query | False |  | Filter by source branch |
| to_branch_id | query | False |  | Filter by destination branch |
| limit | query | False | integer | Number of requests to return |
| offset | query | False | integer | Number of requests to skip |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/stock-requests/

**Summary:** Create Stock Request

**Tags:** 📋 Stock Requests, 📥 Stock Requests

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

``{
  "type": "object",
  "title": "Request Data"
}``

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/stock-requests/branches/{branch_id}/requests

**Summary:** Get Branch Requests

**Tags:** 📋 Stock Requests, 📥 Stock Requests

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| branch_id | path | True | integer | Branch ID |
| request_type | query | False | string | Type: 'incoming' or 'outgoing' |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/stock-requests/stats/summary

**Summary:** Get Stock Request Stats

**Tags:** 📋 Stock Requests, 📥 Stock Requests

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/stock-requests/status/approved

**Summary:** Get Approved Requests

**Tags:** 📋 Stock Requests, 📥 Stock Requests

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| branch_id | query | False |  | Filter by branch ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/stock-requests/status/pending

**Summary:** Get Pending Requests

**Tags:** 📋 Stock Requests, 📥 Stock Requests

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| branch_id | query | False |  | Filter by branch ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/stock-requests/{request_id}

**Summary:** Get Stock Request Details

**Tags:** 📋 Stock Requests, 📥 Stock Requests

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| request_id | path | True | integer | Stock request ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/stock-requests/{request_id}/approve

**Summary:** Approve Stock Request

**Tags:** 📋 Stock Requests, 📥 Stock Requests

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| request_id | path | True | integer | Stock request ID |

**Request Body Schema**

``{
  "type": "object",
  "title": "Approval Data"
}``

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/stock-requests/{request_id}/fulfill

**Summary:** Fulfill Stock Request

**Tags:** 📋 Stock Requests, 📥 Stock Requests

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| request_id | path | True | integer | Stock request ID |
| fulfillment_notes | query | False |  | Fulfillment notes |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/stock-requests/{request_id}/reject

**Summary:** Reject Stock Request

**Tags:** 📋 Stock Requests, 📥 Stock Requests

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| request_id | path | True | integer | Stock request ID |
| rejection_reason | query | True | string | Reason for rejection |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/system/backup/create

**Summary:** Create System Backup

**Tags:** ⚙️ System Management, 🛠️ System

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| include_logs | query | False | boolean | Include recent audit logs |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/system/backup/create/stream

**Summary:** Stream System Backup

**Tags:** ⚙️ System Management, 🛠️ System

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/system/backups

**Summary:** List backups

**Tags:** ⚙️ System Management

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| page | query | False | integer | Page number |
| per_page | query | False | integer | Items per page |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

``{
  "type": "array",
  "items": {
    "$ref": "#/components/schemas/BackupResponseSchema"
  },
  "title": "Response List Backups Api V1 System Backups Get"
}``

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/system/backups

**Summary:** Create backup

**Tags:** ⚙️ System Management

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | object | True | Type of backup: FULL, INCREMENTAL, FILES, DB |
| location | object | False | Target path or storage URI |

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | True |  |
| type | BackupType | True |  |
| location | string | True |  |
| fileName | object | False |  |
| sizeMB | object | False |  |
| status | BackupStatus | True |  |
| errorLog | object | False |  |
| createdById | object | False |  |
| createdAt | string | True |  |
| completedAt | object | False |  |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/system/backups/stats

**Summary:** Get backup statistics

**Tags:** ⚙️ System Management

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| total | integer | True |  |
| successful | integer | True |  |
| failed | integer | True |  |
| pending | integer | True |  |
| total_size_mb | number | True |  |
| last_backup_at | object | True |  |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### DELETE /api/v1/system/backups/{backup_id}

**Summary:** Delete backup

**Tags:** ⚙️ System Management

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| backup_id | path | True | integer | Backup ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/system/backups/{backup_id}

**Summary:** Get backup details

**Tags:** ⚙️ System Management

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| backup_id | path | True | integer | Backup ID |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | True |  |
| type | BackupType | True |  |
| location | string | True |  |
| fileName | object | False |  |
| sizeMB | object | False |  |
| status | BackupStatus | True |  |
| errorLog | object | False |  |
| createdById | object | False |  |
| createdAt | string | True |  |
| completedAt | object | False |  |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/system/backups/{backup_id}/download

**Summary:** Download Backup

**Tags:** ⚙️ System Management, 🛠️ System

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| backup_id | path | True | string |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/system/backups/{backup_id}/restore

**Summary:** Restore Backup

**Tags:** ⚙️ System Management, 🛠️ System

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| backup_id | path | True | string |  |
| apply | query | False | boolean | Apply restore (default dry-run) |
| dry_run | query | False | boolean | Alternative dry_run flag used by standardized tests |
| tables | query | False |  | Comma separated tables subset to restore (test synthetic) |
| confirm_token | query | False |  | Confirmation token required when apply=true |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/system/backups/{backup_id}/restore/async

**Summary:** Start Async Restore

**Tags:** ⚙️ System Management, 🛠️ System

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| backup_id | path | True | string |  |
| confirm_token | query | False |  |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/system/backups/{backup_id}/restore2

**Summary:** Restore backup

**Tags:** ⚙️ System Management

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| backup_id | path | True | integer | Backup ID |
| dry_run | query | False | boolean | If true, only simulate restoration |
| tables | query | False |  | Comma separated table names to limit restore |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| backupId | integer | True |  |
| mode | string | True |  |
| dryRun | boolean | True |  |
| restored_tables | array[string] | True |  |
| skipped_tables | array[string] | True |  |
| message | string | True |  |

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/system/backups/{backup_id}/verify

**Summary:** Verify Backup Checksum

**Tags:** ⚙️ System Management, 🛠️ System

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| backup_id | path | True | string |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/system/health

**Summary:** Health Check

**Tags:** ⚙️ System Management, 🛠️ System

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/system/info

**Summary:** Get System Info

**Tags:** ⚙️ System Management, 🛠️ System

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/system/info

**Summary:** Update System Info

**Tags:** ⚙️ System Management, 🛠️ System

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| company_name | query | True | string | Company name |
| company_address | query | True | string | Company address |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/system/logs

**Summary:** Get System Logs

**Tags:** ⚙️ System Management, 🛠️ System

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| log_level | query | False | string | Log level filter |
| limit | query | False | integer | Number of log entries to return |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/system/restore-jobs/{job_id}

**Summary:** Get Restore Job

**Tags:** ⚙️ System Management, 🛠️ System

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| job_id | path | True | string |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/system/restore-jobs/{job_id}/cancel

**Summary:** Cancel Restore Job

**Tags:** ⚙️ System Management, 🛠️ System

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| job_id | path | True | string |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/system/restore/confirm-token

**Summary:** Generate Restore Confirm Token

**Tags:** ⚙️ System Management, 🛠️ System

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/system/settings

**Summary:** Get System Settings

**Tags:** ⚙️ System Management, 🛠️ System

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/system/settings

**Summary:** Update System Settings

**Tags:** ⚙️ System Management, 🛠️ System

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| setting_name | query | True | string | Setting name to update |
| setting_value | query | True | string | New setting value |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/system/settings/batch

**Summary:** Update System Settings Batch

**Tags:** ⚙️ System Management, 🛠️ System

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

``{
  "type": "object",
  "title": "Payload"
}``

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/system/stats

**Summary:** Get System Stats

**Tags:** ⚙️ System Management, 🛠️ System

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/users/

**Summary:** List users

**Tags:** 👥 User Management, 👥 User Management

**Auth Required:** Yes

**Paginated:** True

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| page | query | False | integer | Page number |
| size | query | False | integer | Page size |
| search | query | False |  | Search term |
| role | query | False |  | Filter by role |
| status | query | False |  | Filter by status |
| is_active | query | False |  | Filter by active status |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/users/

**Summary:** Create user

**Tags:** 👥 User Management, 👥 User Management

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | object | False | Username |
| email | string | True | User email address |
| password | string | True | Password |
| first_name | string | True | First name |
| last_name | string | True | Last name |
| role | object | True | User role |
| isActive | boolean | False | User active status |
| branch_id | object | False | Branch ID |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/users/change-password

**Summary:** Change current user password

**Tags:** 👥 User Management, 👥 User Management

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| current_password | string | True | Current password |
| new_password | string | True | New password |
| confirm_password | string | True | Confirm new password |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/users/me

**Summary:** Get current user profile

**Tags:** 👥 User Management, 👥 User Management

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/users/profile

**Summary:** Get current user profile (alias)

**Tags:** 👥 User Management, 👥 User Management

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/users/profile

**Summary:** Update current user profile

**Tags:** 👥 User Management, 👥 User Management

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | object | False |  |
| email | object | False |  |
| first_name | object | False |  |
| last_name | object | False |  |
| role | object | False |  |
| isActive | object | False |  |
| branch_id | object | False |  |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/users/statistics

**Summary:** Get user statistics

**Tags:** 👥 User Management, 👥 User Management

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### DELETE /api/v1/users/{user_id}

**Summary:** Delete user

**Tags:** 👥 User Management, 👥 User Management

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| user_id | path | True | integer |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /api/v1/users/{user_id}

**Summary:** Get user by ID

**Tags:** 👥 User Management, 👥 User Management

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| user_id | path | True | integer |  |

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### PUT /api/v1/users/{user_id}

**Summary:** Update user

**Tags:** 👥 User Management, 👥 User Management

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| user_id | path | True | integer |  |

**Request Body Schema**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | object | False |  |
| email | object | False |  |
| first_name | object | False |  |
| last_name | object | False |  |
| role | object | False |  |
| isActive | object | False |  |
| branch_id | object | False |  |

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### POST /api/v1/users/{user_id}/reset-password

**Summary:** Admin: reset a user's password

**Tags:** 👥 User Management, 👥 User Management

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

| Name | In | Required | Type | Description |
|------|----|----------|------|-------------|
| user_id | path | True | integer |  |

**Request Body Schema**

``{
  "type": "object",
  "description": "Payload with new_password field",
  "title": "Payload"
}``

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---


## Segment: /dev

### GET /dev/config

**Summary:** Show Config

**Tags:** Development

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---

### GET /dev/routes

**Summary:** List Routes

**Tags:** Development

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---


## Segment: /health

### GET /health

**Summary:** Health Check

**Tags:** 🏥 Health & Monitoring

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---


## Segment: /ping

### GET /ping

**Summary:** Ping

**Tags:** 🏥 Health & Monitoring

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---


## Segment: /root

### GET /

**Summary:** Root

**Tags:** ℹ️ System Information

**Auth Required:** Yes

**Paginated:** False

**Path & Query Parameters**

None

**Request Body Schema**

None

**Success Response Schema (Envelope `data` field focus)**

None

**Error Envelope**

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false on error |
| error_code | string | Stable machine error code |
| message | string | Human-readable summary |
| details | object|array|null | Extra validation or domain details |
| timestamp | string | ISO-8601 UTC timestamp |

---
