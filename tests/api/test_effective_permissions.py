import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_effective_permissions_basic(authenticated_client: AsyncClient):
    # Use the authenticated test user (created by fixture) -> fetch its effective permissions
    base_url = f"{settings.api_v1_str}/permissions"
    # Get user info (fixture likely stores user id in token, but test fixtures usually set user id = 62 or similar)
    # We'll call /auth/me to get current user id
    r = await authenticated_client.get(f"{settings.api_v1_str}/auth/me")
    assert r.status_code == 200
    user_id = r.json()["data"]["id"]

    resp = await authenticated_client.get(f"{base_url}/effective/{user_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert data["user_id"] == user_id
    assert isinstance(data["effective"], list)
    # Should at least contain some permissions via role (ADMIN test user normally)
    assert data["count"] == len(data["effective"])  # count matches length
    assert set(data["override_counts"].keys()) == {"allow", "deny"}

@pytest.mark.asyncio
async def test_effective_permissions_with_override(authenticated_client: AsyncClient):
    # Create a dummy permission, assign via override, ensure appears
    base_url = f"{settings.api_v1_str}/permissions"
    r = await authenticated_client.get(f"{settings.api_v1_str}/auth/me")
    assert r.status_code == 200
    user_id = r.json()["data"]["id"]

    # Create new permission
    create = await authenticated_client.post(f"{base_url}", json={"resource": "dummy", "action": "temporary"})
    assert create.status_code == 200
    perm = create.json()["data"]

    # Apply ALLOW override
    ov = await authenticated_client.post(f"{base_url}/users/{user_id}/{perm['id']}", json={"type": "ALLOW"})
    assert ov.status_code == 200

    eff = await authenticated_client.get(f"{base_url}/effective/{user_id}")
    assert eff.status_code == 200
    eff_data = eff.json()["data"]
    key = f"{perm['resource']}:{perm['action']}"
    assert key in eff_data["effective"]

    # Clean up override removal
    delete = await authenticated_client.delete(f"{base_url}/users/{user_id}/{perm['id']}")
    assert delete.status_code == 200
