# Role-Based Access Control (RBAC) System

This document describes the new normalized RBAC implementation replacing the legacy `PermissionManager` and ad‑hoc permission arrays.

## Goals
- Centralize permission definitions in the database
- Support role → permission mapping + user-level overrides (ALLOW / DENY)
- Deterministic precedence order
- Consistent backend enforcement + ergonomic frontend consumption
- Idempotent seeding for reproducible environments

## Data Model
Tables (see `prisma/schema.prisma`):
- `Permission` (id, resource, action, description?)
- `RolePermission` (role enum, permissionId)
- `UserPermissionOverride` (userId, permissionId, type: ALLOW | DENY)
- Users have a `role` (enum `UserRole`) – `ADMIN` short‑circuits all checks

### Permission Code Format
```
{resource}:{action}
# examples
products:read
products:write
products:delete
sales:read
```

## Precedence Order
1. ADMIN role → allow everything (includes virtual wildcard `*:*` internally)
2. User DENY override → explicit block (cannot be re-enabled by role)
3. User ALLOW override → explicit grant
4. RolePermission mapping → grant
5. Otherwise → deny

Rationale: explicit user intent beats inherited role; DENY beats ALLOW to enable emergency revocation without role surgery.

## Backend Enforcement
Core utilities in `app/core/permissions.py`:
- `get_user_effective_permissions(user_id, db)` → Set[str]
- `check_permission(user, resource, action, db)` → bool (applies precedence)
- `require_permission(resource, action)` FastAPI dependency for a single permission
- `ensure_permissions(user, required, db)` for bulk checks

For multiple permissions use a list with `ensure_permissions` in custom dependencies, or chain dependencies if clarity is preferred.

### Route Usage Example
```python
from fastapi import APIRouter, Depends
from app.core.permissions import require_permission

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/stats", dependencies=[Depends(require_permission("products", "read"))])
async def product_stats():
    ...
```

> NOTE: Some modules expose `require_permissions("products:read")` helper wrapper; both styles are acceptable as long as the normalized system is used.

### Middleware
The authorization middleware now resolves effective permissions once per request (unless ADMIN) and attaches them / uses them for dynamic checks.

## Seeding
Script: `scripts/seed_permissions.py`
- Idempotently inserts the canonical permission set and role mappings.
- Safe to run multiple times; uses upserts / existence checks.

Run it after migrations:
```
python scripts/seed_permissions.py
```

## Overrides Workflow
| Scenario | Action |
|----------|--------|
| Temporarily revoke a specific permission from a user | Insert DENY override row |
| Grant a one-off capability without modifying role | Insert ALLOW override row |
| Restore normal role behavior | Delete override row |

No table update to roles needed for emergency changes.

## Frontend Consumption
Provided by `PermissionsContext` (`frontend/context/PermissionsContext.tsx`).
- Fetches effective permissions via `/permissions/users/{id}` (fallback: `/permissions/mine`) on mount and on auth state changes.
- Exposes `permissions`, `loading`, `has(perm | perms, { any })`.
- Provides `<Permission perm="code|[codes]" any fallback>` component for conditional rendering.

### Examples
```tsx
import { Permission } from '../context/PermissionsContext';

<Permission perm="products:write">
  <Button onClick={create}>Add Product</Button>
</Permission>

<Permission perm={["sales:read", "inventory:read"]} any fallback={<p>No visibility</p>}>
  <AnalyticsPanel />
</Permission>
```

### Gated UI Instances Added
- `ProductsPage`: Add Product button (products:write), row Edit/Adjust (products:write), Delete (products:delete), details actions (products:write)
- `InventoryPage`: Add Product (products:write), Reorder Selected + per-row Reorder (products:write)

## Testing
Backend tests (`tests/unit/test_rbac_precedence.py`) cover:
- Admin omnipotence
- User DENY override precedence
- User ALLOW override
- Role permission allow
- Default deny

Frontend tests:
- `PermissionsContext.test.tsx` base allow/deny
- `PermissionGuardIntegration.test.tsx` any/all logic + fallback rendering

## Migration / Legacy Removal
- Legacy `PermissionManager` replaced with stubs raising `RuntimeError` if referenced.
- All new code must import from `app/core/permissions.py`.
- Remove residual calls by searching for `PermissionManager` or outdated permission arrays.

## Operational Notes
- Adding a new permission: insert into `Permission`, map to roles via `RolePermission`, optionally extend seeding script.
- Revoking system wide: remove `RolePermission` entries + adjust overrides if needed.
- Auditing: (Planned / existing) endpoints expose permission assignments & overrides; integrate with audit log module.

## Future Enhancements (Backlog)
- Cache effective permissions per user with invalidation on override/role change.
- Bulk evaluation helper for performance on permission-heavy pages.
- Grouped permission metadata endpoint for dynamic UI building.
- Self-service admin UI for managing overrides.

## Quick Reference
| Task | Location |
|------|----------|
| Define new permission | DB `Permission` table / seeding script |
| Map permission to role | `RolePermission` row / seeding script |
| Grant temporary access | `UserPermissionOverride` type=ALLOW |
| Emergency revoke | `UserPermissionOverride` type=DENY |
| Frontend check | `usePermission('code')` or `<Permission perm="code"/>` |

---
This RBAC system is now the authoritative permission layer. All legacy patterns are deprecated.
