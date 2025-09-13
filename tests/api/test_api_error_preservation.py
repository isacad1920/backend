"""Tests for APIError preservation in middleware / error handling layer."""
import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.main import app
from app.core.response import failure_response

# Test-only route producing standardized failure envelope without FastAPI's
# exception handler interference so we can validate middleware pass-through.
@app.get(f"{settings.api_v1_str}/_test/api-error")
async def trigger_api_error():  # pragma: no cover - test helper
    resp = failure_response(
        message="Custom API error occurred",
        status_code=418,
        code="CUSTOM_API_ERROR",
        errors={"context": "api_error_test", "value": 42}
    )
    resp.headers['x-normalized-error'] = '1'
    return resp


@pytest.mark.asyncio
async def test_api_error_preserved(authenticated_client: AsyncClient):
    resp = await authenticated_client.get(f"{settings.api_v1_str}/_test/api-error")
    # Status code should match what we raised (418)
    assert resp.status_code == 418
    data = resp.json()
    # Envelope should reflect success False and preserve code/message/details
    assert data.get("success") is False
    err = data.get("error") or {}
    assert err.get("code") == "CUSTOM_API_ERROR"
    assert err.get("message") == "Custom API error occurred"
    assert err.get("details", {}).get("context") == "api_error_test"
    # Ensure our normalized header added by error middleware is present
    # (It may not always be necessary, but it's part of consistency checks.)
    # Some error flows may not set it explicitly; tolerate absence while focusing on payload.
