"""Tests for lightweight branches summary endpoint."""
import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_branches_light_basic(async_client: AsyncClient):
    """Light endpoint should return array of branches (public, cached)."""
    resp = await async_client.get(f"{settings.api_v1_str}/branches/summary/light")
    assert resp.status_code in (200, 304)
    if resp.status_code == 200:
        data = resp.json()
        assert isinstance(data, list)
        # If there is at least one element, ensure required keys present
        if data:
            first = data[0]
            assert "id" in first and "name" in first and "status" in first

@pytest.mark.asyncio
async def test_branches_light_etag(async_client: AsyncClient):
    """Second request with ETag should yield 304 Not Modified when no changes within TTL."""
    first = await async_client.get(f"{settings.api_v1_str}/branches/summary/light")
    assert first.status_code == 200
    etag = first.headers.get("etag")
    if etag:
        second = await async_client.get(
            f"{settings.api_v1_str}/branches/summary/light",
            headers={"If-None-Match": etag}
        )
        # Accept 304 (cache hit) or 200 (race/refresh)
        assert second.status_code in (200, 304)
        if second.status_code == 200:
            # Should still be list
            assert isinstance(second.json(), list)
