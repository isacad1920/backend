"""Minimal test for sales list endpoint.

Ensures /api/v1/sales returns a 200 and basic paging shape after seeding.
"""
import os

import pytest
from fastapi import status
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_sales_list_basic():
    # Arrange: ensure auth header using seeded admin token if available or skip if missing
    token = os.getenv("TEST_ADMIN_TOKEN", "")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/api/v1/sales", params={"size": 5}, headers=headers)
    assert resp.status_code == status.HTTP_200_OK, resp.text
    data = resp.json()
    wrapper = data.get("data") or {}
    assert isinstance(wrapper.get("items"), list)
    pagination = wrapper.get("pagination") or {}
    for key in ["total", "page", "limit", "total_pages"]:
        assert key in pagination
    # Each item minimal keys
    if wrapper.get("items"):
        first = wrapper["items"][0]
        for k in ["id", "total"]:
            assert k in first
