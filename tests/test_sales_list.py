"""Minimal test for sales list endpoint.

Ensures /api/v1/sales returns a 200 and basic paging shape after seeding.
"""
import os
import pytest
from httpx import AsyncClient
from fastapi import status

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
    assert "items" in data and isinstance(data["items"], list)
    assert "total" in data
    # Each item minimal keys
    if data["items"]:
        first = data["items"][0]
        for k in ["id", "total"]:
            assert k in first
