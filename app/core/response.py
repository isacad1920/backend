"""Standardized response schemas and utilities for SOFinance POS System.
Provides consistent success and error response formats across all modules.

Added convenience helpers success_response() and error_response() for direct
usage inside route handlers, returning JSONResponse objects. These sit atop
ResponseBuilder so existing code remains compatible.
"""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Generic, TypeVar

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# Data models (lightweight) -------------------------------------------------

class ErrorResponseModel(BaseModel):
    success: bool = False
    message: str
    error: dict[str, Any]
    path: str | None = None
    method: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    @classmethod
    def create(cls, code: str, message: str, details: dict[str, Any] | None, path: str | None, method: str | None):
        return cls(
            message="Request failed",
            error={
                "code": code,
                "message": message,
                "details": details or {}
            },
            path=path,
            method=method
        )


# ResponseBuilder class -----------------------------------------------------

def build_success_payload(
    data: Any | None = None,
    message: str = "Success",
    status_code: int = 200,
    meta: dict[str, Any] | None = None,
    force_success: bool | None = None,
) -> dict[str, Any]:
    """Build the standardized success-style payload.

    success flag logic:
      - If force_success is explicitly provided, honor it.
      - Else infer success = status_code < 400.
    This fixes the previous issue where 4xx/5xx responses inadvertently had success=True
    when some code paths reused success_response with non-200 codes (e.g. 401).
    """
    inferred_success = True if force_success is None else force_success
    if force_success is None:
        inferred_success = status_code < 400
    from app.core.config import settings as app_settings
    payload_meta = meta.copy() if isinstance(meta, dict) else {}

    # Observability enrichment (correlation id, version)
    correlation_id = None
    if getattr(app_settings, 'enable_response_enrichment', False):
        try:
            # Correlation ID could be set in contextvar by middleware; attempt import lazily
            from contextvars import ContextVar
            _corr_var: ContextVar[str] = globals().get('_correlation_id_var')  # middleware may register
            if _corr_var:
                correlation_id = _corr_var.get(None)  # type: ignore[arg-type]
        except Exception:
            correlation_id = None
        if getattr(app_settings, 'include_correlation_id', True) and correlation_id:
            payload_meta['correlation_id'] = correlation_id
        if getattr(app_settings, 'include_app_version_meta', True):
            try:
                from app.core.config import settings as _s
                payload_meta['app_version'] = _s.app_version
            except Exception:
                pass

    error_obj: dict[str, Any] | None = None
    if not inferred_success:
        # Attempt to derive a structured error from data if present
        if isinstance(data, dict):
            if 'error' in data and isinstance(data['error'], dict):
                error_obj = data['error']
            elif 'detail' in data:
                # Typical FastAPI error shape
                detail = data.get('detail')
                if isinstance(detail, dict) and 'msg' in detail:
                    error_obj = {
                        'code': detail.get('type', 'ERROR'),
                        'message': detail.get('msg'),
                        'details': {k: v for k, v in detail.items() if k not in ('msg', 'type')}
                    }
                else:
                    error_obj = {'code': 'ERROR', 'message': str(detail), 'details': {}}
        if error_obj is None:
            error_obj = {}

    # Base envelope. For failure responses we now omit top-level `message` and `data`
    if inferred_success:
        base = {
            "success": True,
            "message": message,
            "data": data,
            "error": None,
            "meta": payload_meta,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    else:
        base = {
            "success": False,
            "error": error_obj or {},
            "meta": payload_meta,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    # Optionally nest enrichment meta under namespace if configured
    if getattr(app_settings, 'enable_response_enrichment', False) and getattr(app_settings, 'response_enrichment_add_to_meta', False):
        ns = getattr(app_settings, 'response_enrichment_meta_namespace', '_ctx')
        # Move enrichment keys into a namespaced dict to avoid polluting meta root
        enrichment_keys = ['correlation_id', 'app_version']
        enriched = {k: base['meta'].pop(k) for k in list(base['meta'].keys()) if k in enrichment_keys}
        if enriched:
            base['meta'][ns] = {**enriched, **base['meta'].get(ns, {})}
    return base


class ResponseBuilder:
    @staticmethod
    def success(
        data: Any | None = None,
        message: str = "Success",
        status_code: int = 200,
        meta: dict[str, Any] | None = None,
        force_success: bool | None = None,
    ) -> JSONResponse:
        payload = build_success_payload(
            data=data,
            message=message,
            status_code=status_code,
            meta=meta,
            force_success=force_success,
        )
        return JSONResponse(status_code=status_code, content=jsonable_encoder(payload))

    @staticmethod
    def error(
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        status_code: int = 500,
        path: str | None = None,
        method: str | None = None
    ) -> JSONResponse:
        err = ErrorResponseModel.create(code, message, details, path, method)
        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(err.model_dump())
        )

    # Legacy convenience wrappers (still referenced in some routes/tests)
    @staticmethod
    def already_exists(message: str = "Resource already exists") -> JSONResponse:
        return ResponseBuilder.error(code="ALREADY_EXISTS", message=message, status_code=409)

    @staticmethod
    def not_found(message: str = "Resource not found") -> JSONResponse:
        return ResponseBuilder.error(code="NOT_FOUND", message=message, status_code=404)

    @staticmethod
    def validation_error(message: str = "Validation error", details: dict[str, Any] | None = None) -> JSONResponse:
        return ResponseBuilder.error(code="VALIDATION_ERROR", message=message, details=details, status_code=422)

    # Newly added legacy-compatible helpers referenced in routes but previously absent
    @staticmethod
    def unauthorized(message: str = "Unauthorized") -> JSONResponse:
        """Return a 401 unauthorized error response (legacy helper)."""
        return ResponseBuilder.error(code="UNAUTHORIZED", message=message, status_code=401)

    @staticmethod
    def database_error(message: str = "Database error") -> JSONResponse:
        """Return a 500 internal/database error response (legacy helper)."""
        return ResponseBuilder.error(code="INTERNAL_ERROR", message=message, status_code=500)


class ErrorCodes(str, Enum):
    BAD_REQUEST = "BAD_REQUEST"
    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"


# Convenience wrappers for simplified route usage

def success_response(
    data: Any | None = None,
    message: str = "Success",
    status_code: int = 200,
    meta: dict[str, Any] | None = None,
    force_success: bool | None = None,
) -> JSONResponse:
    payload = build_success_payload(
        data=data,
        message=message,
        status_code=status_code,
        meta=meta,
        force_success=force_success,
    )
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(payload)
    )

def iso_utc(dt) -> str:
    """Return an ISO-8601 UTC string with 'Z' suffix from a datetime-like object.

    Falls back to current UTC time if serialization fails.
    """
    try:
        if dt is None:
            return datetime.utcnow().replace(tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')
        if hasattr(dt, 'isoformat'):
            return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
        return str(dt)
    except Exception:
        return datetime.utcnow().replace(tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')



def set_json_body(response: JSONResponse, payload: dict[str, Any]):
    """Safely replace the JSON body of an existing JSONResponse and update Content-Length.

    Many routes mutate `resp.body` directly after calling `success_response` to
    mirror certain keys at the top-level for legacy test compatibility. Direct
    mutation leaves the original `content-length` header (set during initial
    JSONResponse construction) which can cause runtime errors like:

        RuntimeError: Response content longer than Content-Length

    This helper centralizes the mutation pattern, re-serializes the payload,
    assigns the new body bytes, and recalculates the Content-Length header to
    maintain correctness with Uvicorn/Starlette streaming machinery.

    It is intentionally lightweight (no validation). Routes should already
    have ensured `payload` is JSON-serializable. If serialization fails we
    fall back to the original response body.
    """
    try:
        import json
        body_bytes = json.dumps(payload).encode('utf-8')
        response.body = body_bytes  # type: ignore[attr-defined]
        # Reset headers that depend on body size
        response.headers['content-length'] = str(len(body_bytes))
        # Ensure correct media type
        if 'content-type' not in response.headers:
            response.headers['content-type'] = 'application/json'
        # Deprecation hint: detect legacy top-level mirroring beyond envelope keys
        try:
            envelope_keys = {"success", "message", "data", "error", "meta", "timestamp"}
            extra_keys = set(payload.keys()) - envelope_keys
            # ignore harmless additions inside meta; only consider if data keys were promoted
            if extra_keys:
                logger.debug(
                    "[DEPRECATION] Detected non-standard top-level keys %s in response payload. "
                    "These should eventually reside inside 'data' once legacy tests updated.",
                    list(extra_keys)
                )
        except Exception:  # pragma: no cover - defensive
            pass
    except Exception:  # pragma: no cover - defensive
        logger.exception("Failed to set JSON body on response; leaving original body intact")
    return response


def error_response(
    code: str,
    message: str,
    status_code: int = 500,
    details: dict[str, Any] | None = None,
    path: str | None = None,
    method: str | None = None,
) -> JSONResponse:
    """Return a standardized error JSONResponse.

    Example:
        return error_response(code="NOT_FOUND", message="Item not found", status_code=404)
    """
    return ResponseBuilder.error(
        code=code,
        message=message,
        details=details,
        status_code=status_code,
        path=path,
        method=method,
    )

def failure_response(
    message: str,
    status_code: int = 400,
    errors: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
    code: str | None = None,
) -> JSONResponse:
    """Unified failure helper returning standardized envelope.

    Args:
        message: Human-readable error message.
        status_code: HTTP status to return.
        errors: Optional detailed error dict (validation issues, field errors, etc.).
        meta: Optional meta additions.
        code: Optional machine-friendly error code (default derived from status_code).
    """
    # Derive a simple code if not provided
    default_code_map = {
        400: 'BAD_REQUEST',
        401: 'UNAUTHORIZED',
        403: 'FORBIDDEN',
        404: 'NOT_FOUND',
        409: 'CONFLICT',
        422: 'VALIDATION_ERROR',
        429: 'RATE_LIMITED',
        500: 'INTERNAL_ERROR',
    }
    err_code = code or default_code_map.get(status_code, 'ERROR')
    error_body: dict[str, Any] = {
        'code': err_code,
        'message': message,
        'details': errors or {},
    }
    payload = build_success_payload(
        data=None,
        message=message,
        status_code=status_code,
        meta=meta,
        force_success=False,
    )
    # build_success_payload for failures already returns shape without message/data keys; ensure error merged
    payload['error'] = error_body
    return JSONResponse(status_code=status_code, content=jsonable_encoder(payload))


def paginated_response(
    items: list[Any],
    total: int,
    page: int = 1,
    limit: int = 10,
    message: str = "Success",
    meta_extra: dict[str, Any] | None = None,
) -> JSONResponse:
    """Return a standardized paginated success response.

    meta_extra: optional dict merged into meta alongside pagination.
    Backwards compatible: existing callers ignoring new parameter get identical structure.
    """
    total_pages = (total + limit - 1) // limit if limit else 1
    meta = {
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
    if meta_extra:
        # shallow merge; pagination key preserved
        meta.update(meta_extra)
    # New canonical shape: data is an object containing items + pagination
    data_obj = {"items": items, "pagination": meta["pagination"]}
    return success_response(
        data=data_obj,
        message=message,
        status_code=200,
        meta={k: v for k, v in meta.items() if k != 'pagination'} or None,
    )

# ---------------------------------------------------------------------------
# Backwards compatibility models (legacy imports present in modules/tests)
# These were previously imported but not defined after refactor; we reintroduce
# lightweight Pydantic models to avoid breaking older code or tests expecting
# these names. They wrap the same structure produced by success_response/error_response.

T = TypeVar('T')

class SuccessResponse(BaseModel, Generic[T]):
    """Generic success envelope model used only for OpenAPI/response_model typing.

    Runtime responses are produced via success_response(); this model exists for
    backward compatibility where routes declare response_model=SuccessResponse[SomeType].
    """
    success: bool = True
    message: str = "Success"
    data: T | None = None
    error: dict[str, Any] | None = None
    meta: dict[str, Any] = {}
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    @classmethod
    def create(cls, data: T | None = None, message: str = "Success", meta: dict[str, Any] | None = None):
        return cls(data=data, message=message, meta=meta or {})


class ErrorResponse(BaseModel, Generic[T]):
    success: bool = False
    message: str = "Request failed"
    error: dict[str, Any]
    meta: dict[str, Any] = {}
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    @classmethod
    def create(cls, code: str, message: str, details: dict[str, Any] | None = None):
        return cls(error={"code": code, "message": message, "details": details or {}}, message="Request failed")


# ---------------------------------------------------------------------------
# TEST COMPATIBILITY SHIM
# Some existing legacy tests expect the API to return flat dictionaries with
# keys like `access_token`, `refresh_token`, `items`, `page`, `size`, etc.
# After standardization, responses are wrapped inside the unified envelope:
# {"success": true, "message": ..., "data": {...}, "error": null, ...}
# To avoid rewriting many test assertions at once, we provide a lightweight
# helper to "flatten" the standardized envelope into the legacy shape when
# explicitly invoked by tests (they can import flatten_legacy for assertions).

def flatten_legacy(response_json: dict[str, Any]) -> dict[str, Any]:
    """Flatten a standardized response envelope into legacy shape.

    Rules:
      - If top-level has keys success/message/data -> treat as envelope.
      - Promote data's keys to top-level (non-destructive).
      - If data is a list representing paginated results, attempt to map to
        expected legacy fields (items, total, page, size) using meta.pagination.
      - If data is already a primitive or list and not a dict, just return it
        in a dict under 'data'.
      - Preserve original envelope keys where they don't collide.
    """
    if not isinstance(response_json, dict):
        return {"data": response_json}

    # Detect envelope
    if {"success", "data", "message"}.issubset(response_json.keys()):
        flat = {}
        data_part = response_json.get("data")
        meta = response_json.get("meta") or {}

        # Pagination mapping if list with pagination meta
        pagination = None
        if isinstance(meta, dict):
            pagination = meta.get("pagination")

        if isinstance(data_part, dict):
            flat.update(data_part)
        elif isinstance(data_part, list):
            # List response; provide legacy pagination keys if available
            flat["items"] = data_part
            if isinstance(pagination, dict):
                flat["total"] = pagination.get("total")
                flat["page"] = pagination.get("page")
                flat["size"] = pagination.get("limit") or pagination.get("size")
        else:
            flat["data"] = data_part

        # Add tokens inside data promoted to top-level for legacy tests
        if isinstance(data_part, dict):
            for key in ("access_token", "refresh_token", "token_type"):
                if key in data_part:
                    flat[key] = data_part[key]

        # Preserve primary message if legacy tests looked for it
        if "message" not in flat and "message" in response_json:
            flat["message"] = response_json["message"]

        return flat

    # Not an envelope; return as-is
    return response_json

