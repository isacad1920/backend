# Inventory Feature Guide

This document describes the inventory feature architecture: services, query keys, hooks, mutations, optimistic update strategy, and permission model.

## Overview
The inventory module provides real-time insight into product stock levels, valuation metrics, and actionable operations (adjustments & stock threshold updates) using React Query + FastAPI backend endpoints.

## Core Data Endpoints
| Purpose | Endpoint | Notes |
|---------|----------|------|
| Summary | `GET /inventory/summary` | Aggregate counts (products, low, dead, cost & retail totals). |
| Items | `GET /inventory/items` | Supports `status`, `search`, `category_id`, pagination, `low_stock_threshold`. |
| Low Stock Batch | `GET /inventory/low-stock/batch` | Returns items below threshold + threshold metadata. |
| Dead Stock | `GET /inventory/items?status=dead_stock` | Convenience wrapper via `inventoryService.getDeadStock`. |
| Movements | `GET /inventory/movements` | Recent stock inflow/outflow (fallback to empty list if missing). |
| Valuation | `GET /inventory/valuation` | Falls back to summary with `valuationDerived: true` if endpoint fails. |
| Adjust Stock | `POST /products/{id}/adjust` | Handled through `productService.adjustProductStock`. |
| Update Product | `PATCH /products/{id}` | Used to update min/max/reorder thresholds. |

## Query Key Factory (Representative)
```
['inventory','items', { page, size, status, search, category_id }]
['inventory','summary']
['inventory','valuation']
['inventory','dead', { page, size, search }]
['inventory','movements', { page, size, productId }]
['inventory','low-batch', { page, page_size, threshold }]
```
Stable keys allow selective invalidation (`summary` & `valuation` after adjustments; `items` after threshold updates).

## Hooks
| Hook | Responsibility | Notes |
|------|----------------|------|
| `useInventoryItems` | Paginated list (optionally status filtered) | Preserves previous data via `placeholderData` for smoother pagination. |
| `useInventoryLowBatch` | Compact low-stock batch feed | Accepts override threshold. |
| `useInventoryDead` | Dead stock list | Delegates to `getDeadStock`. |
| `useInventoryMovements` | Movements feed | Gracefully handles missing endpoint. |
| `useInventorySummary` | Aggregated summary | `staleTime=30s`. |
| `useInventoryValuation` | Cost & retail totals | `staleTime=60s`, fallback sets `valuationDerived`. |
| `useAdjustInventoryStock` | Optimistic stock quantity delta | Adjusts cached items + summary totals; rollback on error. |
| `useUpdateInventoryStockSettings` | Optimistic min/max/reorder update | Shadow-updates fields on matching items. |

## Optimistic Adjustment Flow
1. Cancel relevant queries: items, summary, valuation.
2. Snapshot previous caches (`getQueriesData`).
3. Apply delta to each cached item matching `product_id` & adjust summary quantity if present.
4. On error: restore snapshots, emit error toast.
5. On settle: invalidate summary & valuation keys.

## Stock Settings Update Flow
- Cancel item queries, snapshot, optimistic field update per matching item.
- Rollback on error, notify via toast.
- Invalidate `['inventory','items']` post-settle.

## Permission Model
| Action | Required Permission(s) | ADMIN Bypass |
|--------|------------------------|-------------|
| View Inventory | `inventory:read` (fallback permissive if partial) | Yes |
| Adjust Stock | `inventory:adjust` OR `products:update` | Yes |
| Update Thresholds | `products:update` | Yes |
| Create Product | `products:write` | Yes |
- The `Require` component short-circuits for ADMIN role.
- Sidebar uses permissive mode if permission payload incomplete to avoid hiding navigation.

## Modals
| Modal | Purpose | Mutation |
|-------|---------|----------|
| `AdjustStockModal` | Apply quantity delta with reason | `useAdjustInventoryStock` |
| `UpdateStockSettingsModal` | Edit min/max/reorder thresholds | `useUpdateInventoryStockSettings` |

## KPI Calculations
- Profit Margin % = `(retail - cost) / retail * 100` (clamped at 0 when retail <= cost or missing)
- In-Stock % approximated as `100 - low% - dead%`.
- Low% = `low_stock_count / total_products`.
- Dead% = `dead_stock_cached / total_products`.

## Fallback Behaviors
| Scenario | Fallback |
|----------|----------|
| Valuation endpoint error | Use summary totals + `valuationDerived` flag. |
| Movements endpoint missing | Empty list with synthetic pagination. |
| Missing permission list | Permissive sidebar until full set retrieved. |

## Invalidation Strategy
| Trigger | Invalidated Keys |
|---------|------------------|
| Stock Adjustment | `summary`, `valuation` |
| Stock Settings Update | `items` |
| Threshold Change (future) | `low-batch`, maybe `summary` |

## Testing Guidelines
- Mock `apiClient.get` for valuation to test fallback path.
- Simulate `adjustProductStock` rejection to assert rollback calls restore snapshots.
- Validate that `useInventoryItems` retains previous data shape with `placeholderData`.

## Future Enhancements
- Add batch adjustment actions.
- Add export with server-side filters.
- Integrate category distribution & turnover rate real metrics.
- Add background revalidation toast badge when stale.

## Troubleshooting
| Symptom | Likely Cause | Resolution |
|---------|--------------|-----------|
| No valuation numbers | Valuation endpoint failing | Check backend logs; confirm fallback shows `valuationDerived`. |
| Buttons not showing | Missing permissions | Verify `Require` prop anyOf; inspect permission payload debug logs. |
| Quantities jump back | Adjustment error rollback | Inspect toast for backend error; retry once network stable. |

---
Document version: 1.0
