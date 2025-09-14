## Unreleased

### Added
- Frontend inventory service (`frontend/services/inventory.ts`) with unified items + summary endpoints integration.
- Sales service extension (`getTodaySummary`) consuming `/sales/today/summary`.
- Authentication & authorization implementation:
	- Real login flow replacing mock (`LoginPage` + `AuthService`).
	- `AuthContext` with session persistence, proactive refresh scheduling, and permission helpers.
	- Automatic access token refresh & single-flight retry in `apiClient` for 401s.
	- Permission-based navigation filtering and `PermissionGuard` component.
	- Versioned stored session schema (`StoredAuthSession`).
- Customers module integration (frontend):
	- Real customer list retrieval with search, pagination, permission gate (`customers:view`).
	- Refactored `CustomersPage` to remove hardcoded mock data, added loading/error/empty states.

### Changed
- Replaced all mock data paths in `dashboardService` with real backend API calls (`/sales/today/summary`, `/inventory/summary`, financial analytics endpoints).
- Updated `Dashboard` component to consume aggregated live data instead of static mocks.
- Strengthened TypeScript typing across multiple pages (customers, branches, categories, settings, calendar icons) eliminating implicit `any` usage surfaced by build.

### Security
- Added structured token handling with expiry computation and pre-expiry refresh (60s margin).
- Centralized logout clearing tokens & session atomically.

### Fixed
- Build-time TypeScript errors (implicit any, never type issues) uncovered after integration.

### Pending / Follow-ups
- Replace temporary `any` types for sales & inventory analytics with finalized interfaces once backend shape finalized.
- Implement real low stock alert retrieval for dashboard (currently placeholder empty list).
- Integrate customer / product counts with real endpoints when exposed.
- Align provisional frontend permission codes with canonical backend permission registry.

---
Generated on: 2025-09-14