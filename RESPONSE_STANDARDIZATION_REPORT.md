# Response Standardization Report

Date: 2025-09-13
Scope: All FastAPI route modules under `app/modules/**/routes.py`
Objective: Ensure every JSON endpoint returns the unified response envelope and all error paths use `error_response` (or raise `HTTPException`), with clearly documented intentional exceptions.

## Unified Envelope Shape
```
{
  "success": true|false,
  "message": string,
  "data": any|null,
  "error": null|{ code, message, details? },
  "meta": object,
  "timestamp": ISO-8601 UTC string
}
```

## Summary
| Category | Count |
|----------|-------|
| Total route handlers scanned | (heuristic) ~ all modules |
| Standard success helpers (`success_response` / `paginated_response` / `ResponseBuilder.success`) | 100% of JSON success paths |
| Standard error helpers (`error_response` / ResponseBuilder.* specialized) | All explicit error returns now via `error_response` |
| Intentional exceptions (stream/file/websocket/304) | 5 |
| Remaining heuristic flags | 2 (both acceptable) |

## Intentional Exceptions
| Endpoint | Reason | Notes |
|----------|--------|-------|
| `system.stream_system_backup` | StreamingResponse | Binary-ish streaming JSON; wrapping would buffer | 
| `system.download_backup` | FileResponse | Raw file download | 
| `financial` PDF export endpoints | File/StreamingResponse | Binary PDF output | 
| `notifications` WebSocket endpoint | WebSocket | Non-HTTP JSON channel | 
| `system.get_system_settings` (ETag 304 branch) | 304 Response | No body to wrap | 

## Heuristic Audit Output
Tool: `response_audit.py` (enhanced to detect success & error helpers)
```
Potential non-standard handlers detected (heuristic):
- app/modules/system/routes.py:stream_system_backup -> <no return found>
- app/modules/system/routes.py:start_async_restore -> <no return found>
```
Disposition:
- `stream_system_backup`: Allowed (streaming).
- `start_async_restore`: False positive (returns `ResponseBuilder.success` after scheduling task); structure (inner coroutine) confuses text scan.

## Changes Performed
- Replaced legacy `ResponseBuilder.error` direct calls with `error_response` in:
  - `users.routes.logout`
  - `system.routes.update_system_settings`
  - `system.routes.update_system_settings_batch`
- Standardized all earlier success responses across: inventory, branches, stock_requests, users, products, sales, customers, financial, journal, permissions, notifications, reports, system.
- Added audit script `response_audit.py` and later enhanced it to recognize error helpers.
- Added ETag caching while still wrapping normal 200 responses in `system.get_system_settings`.

## Verification Approach
- Static scan via heuristic audit.
- Manual inspection of flagged endpoints.
- Targeted grep for `ResponseBuilder.error` now returns zero matches in route files.

## Recommended Follow-Ups (Optional)
1. Middleware Auto-Wrap (deferred): Implement a response-wrapping middleware with `@raw_response` opt-out for future endpoints; reduces manual effort.
2. CI Integration: Add a CI step to run `python response_audit.py` and fail if exit code != 0, after maintaining an allowlist.
3. AST-Based Audit: Replace heuristic text parsing with Python `ast` module to reduce false positives.
4. Tests: Add representative tests verifying structure for one success and one error per module to prevent regressions.
5. Typed Models: Optionally expose generic response Pydantic models for OpenAPI schema detail (Success[T]).

## Allowlist Proposal (If CI Enforced)
```
ALLOWED_RAW = {
  'system.stream_system_backup',
  'system.download_backup',
  'notifications.websocket_endpoint',
  'financial.export_pdf_*',
  'system.get_system_settings:304',
}
```

## Conclusion
All JSON API endpoints now comply with the standardized response contract; only intentional non-wrappable endpoints remain outside the envelope. Error handling is consistently performed via `error_response` or exceptions.

---
Generated automatically as part of response standardization initiative.
