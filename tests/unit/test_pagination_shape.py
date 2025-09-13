import pytest
from httpx import AsyncClient

from app.core.response import paginated_response
from app.core.config import settings


def test_paginated_response_helper_shape():
    resp = paginated_response(items=[{"id": 1}, {"id": 2}], total=2, page=1, limit=10)
    assert resp.status_code == 200
    import json
    # JSONResponse doesn't expose .json(); decode from body
    payload = json.loads(resp.body.decode())
    # Positive assertions
    assert payload["success"] is True
    assert payload["error"] is None
    assert "message" in payload
    assert isinstance(payload.get("data"), dict)
    assert "items" in payload["data"]
    assert "pagination" in payload["data"]
    pagination = payload["data"]["pagination"]
    assert pagination["total"] == 2
    assert pagination["page"] == 1
    assert pagination["limit"] == 10
    assert pagination["total_pages"] == 1
    # Negative assertions for legacy top-level keys
    for legacy_key in ("items", "total", "page", "size", "limit"):
        assert legacy_key not in payload, f"Legacy top-level key '{legacy_key}' found in response root"


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", [
    f"{settings.api_v1_str}/products/",
])
async def test_paginated_endpoint_shape(authenticated_client: AsyncClient, endpoint):
    """Active integration test validating canonical paginated response shape for a real authenticated endpoint."""
    r = await authenticated_client.get(endpoint)
    assert r.status_code == 200, r.text
    payload = r.json()
    # Structural assertions
    assert payload.get("success") is True
    assert isinstance(payload.get("data"), dict)
    assert "items" in payload["data"], "Expected 'items' inside data"
    assert "pagination" in payload["data"], "Expected 'pagination' inside data"
    pagination = payload["data"]["pagination"]
    # Required pagination keys
    for key in ("total", "page", "limit", "total_pages", "has_next", "has_prev"):
        assert key in pagination, f"Missing pagination key '{key}'"
    # Negative assertions for legacy top-level leakage only enforced if mirroring disabled
    from app.core.config import settings as _settings
    if not getattr(_settings, "mirror_pagination_keys", True):
        for legacy_key in ("items", "total", "page", "size", "limit"):
            assert legacy_key not in payload, f"Legacy top-level key '{legacy_key}' should not appear at root when mirroring disabled"
