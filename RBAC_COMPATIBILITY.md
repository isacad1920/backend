## RBAC Compatibility Layer (Removed)

The legacy `/api/v1/admin/permissions/*` compatibility endpoints have been removed.

Use the normalized RBAC endpoints exclusively:

| Operation | Endpoint |
| --------- | -------- |
| List permissions | `GET /api/v1/permissions` |
| Create permission | `POST /api/v1/permissions` |
| Delete permission | `DELETE /api/v1/permissions/{id}` |
| List role permissions | `GET /api/v1/permissions/roles/{ROLE}` |
| Assign role permission | `POST /api/v1/permissions/roles/{ROLE}/{permission_id}` |
| Remove role permission | `DELETE /api/v1/permissions/roles/{ROLE}/{permission_id}` |
| User detailed permissions | `GET /api/v1/permissions/users/{user_id}` |
| Set user override | `POST /api/v1/permissions/users/{user_id}/{permission_id}` |
| Delete user override | `DELETE /api/v1/permissions/users/{user_id}/{permission_id}` |
| Effective list (lightweight) | `GET /api/v1/permissions/effective/{user_id}` |

Any remaining references to `/admin/permissions` must be removed from clients and tests.

Last updated: Compatibility layer removal finalized.
