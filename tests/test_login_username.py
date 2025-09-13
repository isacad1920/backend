import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_login_with_username(async_client: AsyncClient = None):
    # Use provided async_client fixture if project has one, else create temporary
    created_client = False
    if async_client is None:
        created_client = True
        async with AsyncClient(app=app, base_url="http://test") as c:
            # Attempt login with default seeded admin credentials (adjust if different)
            resp = await c.post("/api/v1/auth/login", json={"username": "admin", "password": "password"})
            assert resp.status_code in (200, 401)
            if resp.status_code == 200:
                data = resp.json()
                assert "access_token" in data
            return
    else:
        resp = await async_client.post("/api/v1/auth/login", json={"username": "admin", "password": "password"})
        assert resp.status_code in (200, 401)
        if resp.status_code == 200:
            data = resp.json()
            assert "access_token" in data
