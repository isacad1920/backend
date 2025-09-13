import pytest
from httpx import AsyncClient
from app.main import app
from app.core.config import settings


@pytest.mark.asyncio
async def test_login_with_email(async_client: AsyncClient = None):
    """Login with demo email (ensured in non-production)."""
    if async_client is None:
        async with AsyncClient(app=app, base_url="http://test") as c:
            resp = await c.post(f"{settings.api_v1_str}/auth/login", json={"email": "demo@sofinance.com", "password": "DemoPassword123!"})
            assert resp.status_code == 200
            data = resp.json()
            assert "access_token" in data and "refresh_token" in data
            return
    resp = await async_client.post(f"{settings.api_v1_str}/auth/login", json={"email": "demo@sofinance.com", "password": "DemoPassword123!"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data and "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid_username(async_client: AsyncClient = None):
    """Attempt login with non-existent username still providing password."""
    payload = {"username": "__does_not_exist__", "password": "SomePassword123!"}
    if async_client is None:
        async with AsyncClient(app=app, base_url="http://test") as c:
            resp = await c.post(f"{settings.api_v1_str}/auth/login", json=payload)
            assert resp.status_code in (401, 400)
            return
    resp = await async_client.post(f"{settings.api_v1_str}/auth/login", json=payload)
    assert resp.status_code in (401, 400)
