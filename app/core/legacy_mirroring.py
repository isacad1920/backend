"""Legacy response key mirroring utilities.

This module centralizes the large block of conditional logic that promotes
selected keys from the standardized response envelope (or raw data objects)
to the top-level of the JSON response for backwards compatibility with
legacy tests and clients. It is intentionally side-effect free aside from
returning a new JSONResponse when a mutation/mirroring occurs.

Refactoring into a standalone module makes it easier to locate, audit,
and eventually remove or simplify in a future major release.
"""
from __future__ import annotations

import json
from typing import Any

from fastapi.responses import JSONResponse

from app.core.response import success_response


def mirror_and_wrap_response(
    data_obj: Any,
    request_path: str,
    response: JSONResponse,
    app_settings,
):
    """Apply legacy mirroring / wrapping and return a JSONResponse if modified.

    Returns None if no changes performed (caller should keep original response).
    """
    # Inventory list mode heuristic (unchanged from original logic)
    inventory_list_mode = request_path.startswith('/api/v1/inventory/') and any(seg in request_path for seg in (
        'stock-levels','low-stock','low-stock-alerts','valuation','dead-stock','reports/turnover','reports/movement','reports/comprehensive'
    ))

    # Special-case passthroughs ------------------------------------------------
    if request_path.endswith('/api/v1/inventory/reports/comprehensive') and isinstance(data_obj, dict) and 'report_date' in data_obj:
        return JSONResponse(status_code=response.status_code, content=data_obj)
    if request_path.endswith('/api/v1/branches/summary/light') and isinstance(data_obj, list):
        return JSONResponse(status_code=response.status_code, content=data_obj)
    if request_path.endswith('/api/v1/financial/income-statement') and isinstance(data_obj, dict) and 'revenue' in data_obj:
        return JSONResponse(status_code=response.status_code, content=data_obj)

    mirroring_enabled = getattr(app_settings, 'enable_key_mirroring', True)

    # If already standardized shape, operate directly on it
    if isinstance(data_obj, dict) and {'success','data','message'} <= set(data_obj.keys()):
        data_part = data_obj.get('data')
        meta = data_obj.get('meta') or {}
        pagination_meta = meta.get('pagination') if isinstance(meta, dict) else None
        mutated = False

        if inventory_list_mode and isinstance(data_part, list):
            return JSONResponse(status_code=response.status_code, content=data_part)
        if not mirroring_enabled:
            return None

        def mirror_key(src, key, dest=data_obj):
            nonlocal mutated
            if isinstance(src, dict) and key in src and key not in dest:
                dest[key] = src[key]
                mutated = True

        if isinstance(data_part, dict):
            for k in ('access_token','refresh_token','token_type','user'):
                mirror_key(data_part, k)

        # Pagination mirroring removed per new envelope standard

        if isinstance(data_part, dict):
            # Legacy promotion removed: keep envelope strict.
            if 'detail' in data_part and 'detail' not in data_obj:
                data_obj['detail'] = data_part['detail']; mutated = True
        if mutated:
            return JSONResponse(status_code=response.status_code, content=data_obj)
        return None

    # Wrap primitive/list/dict
    if inventory_list_mode and isinstance(data_obj, list):
        return JSONResponse(status_code=response.status_code, content=data_obj)
    wrapped_response = success_response(data=data_obj, message='Success')
    try:
        if hasattr(wrapped_response, 'body') and wrapped_response.body:
            wrapped_payload = json.loads(wrapped_response.body)
        else:
            wrapped_payload = {"success": True, "data": data_obj, "message": "Success"}
    except Exception:  # pragma: no cover
        wrapped_payload = {"success": True, "data": data_obj, "message": "Success"}
    if mirroring_enabled:
        if request_path.startswith('/api/v1/financial/') and not request_path.endswith('/income-statement') and isinstance(wrapped_payload.get('data'), dict):
            for k, v in wrapped_payload['data'].items():
                if isinstance(v, (str, int, float, bool, list, dict)) and k not in wrapped_payload:
                    wrapped_payload[k] = v
        if isinstance(wrapped_payload.get('data'), dict) and 'id' in wrapped_payload['data'] and 'id' not in wrapped_payload:
            wrapped_payload['id'] = wrapped_payload['data']['id']
        if isinstance(wrapped_payload.get('data'), dict) and 'detail' in wrapped_payload['data'] and 'detail' not in wrapped_payload:
            wrapped_payload['detail'] = wrapped_payload['data']['detail']
    return JSONResponse(status_code=response.status_code, content=wrapped_payload)
