"""Tests for the normalized RBAC permission endpoints (no legacy compat)."""
import pytest
from httpx import AsyncClient
from app.core.config import settings


@pytest.mark.asyncio
async def test_list_permissions(authenticated_client: AsyncClient):
    r = await authenticated_client.get(f"{settings.api_v1_str}/permissions")
    assert r.status_code == 200
    data = r.json()["data"]
    assert "permissions" in data


@pytest.mark.asyncio
async def test_create_and_delete_permission(authenticated_client: AsyncClient):
    create = await authenticated_client.post(f"{settings.api_v1_str}/permissions", json={"resource": "tempres", "action": "tempact"})
    assert create.status_code == 200
    pid = create.json()["data"]["id"]
    delete = await authenticated_client.delete(f"{settings.api_v1_str}/permissions/{pid}")
    assert delete.status_code == 200


@pytest.mark.asyncio
async def test_role_permission_assignment_flow(authenticated_client: AsyncClient):
    # create permission
    cp = await authenticated_client.post(f"{settings.api_v1_str}/permissions", json={"resource": "assign", "action": "read"})
    assert cp.status_code == 200
    perm_id = cp.json()["data"]["id"]
    # assign to role
    assign = await authenticated_client.post(f"{settings.api_v1_str}/permissions/roles/ADMIN/{perm_id}")
    assert assign.status_code == 200
    # list role perms
    rp = await authenticated_client.get(f"{settings.api_v1_str}/permissions/roles/ADMIN")
    assert rp.status_code == 200
    # unassign
    un = await authenticated_client.delete(f"{settings.api_v1_str}/permissions/roles/ADMIN/{perm_id}")
    assert un.status_code == 200


@pytest.mark.asyncio
async def test_user_override_flow(authenticated_client: AsyncClient):
    # Get current user id
    me = await authenticated_client.get(f"{settings.api_v1_str}/auth/me")
    assert me.status_code == 200
    user_id = me.json()["data"]["id"]
    # Create permission
    cp = await authenticated_client.post(f"{settings.api_v1_str}/permissions", json={"resource": "ovr", "action": "test"})
    assert cp.status_code == 200
    perm_id = cp.json()["data"]["id"]
    # Apply ALLOW override
    allow = await authenticated_client.post(f"{settings.api_v1_str}/permissions/users/{user_id}/{perm_id}", json={"type": "ALLOW"})
    assert allow.status_code == 200
    # Effective list should contain it
    eff = await authenticated_client.get(f"{settings.api_v1_str}/permissions/effective/{user_id}")
    assert eff.status_code == 200
    # Remove override
    rem = await authenticated_client.delete(f"{settings.api_v1_str}/permissions/users/{user_id}/{perm_id}")
    assert rem.status_code == 200


@pytest.mark.asyncio
async def test_user_permission_detail(authenticated_client: AsyncClient):
    me = await authenticated_client.get(f"{settings.api_v1_str}/auth/me")
    assert me.status_code == 200
    user_id = me.json()["data"]["id"]
    detail = await authenticated_client.get(f"{settings.api_v1_str}/permissions/users/{user_id}")
    assert detail.status_code == 200
    payload = detail.json()["data"]
    assert set(["effective", "role_permissions", "allowed_overrides", "denied_overrides"]).issubset(payload.keys())


@pytest.mark.asyncio
async def test_unauthorized_access(async_client: AsyncClient):
    r = await async_client.get(f"{settings.api_v1_str}/permissions")
    assert r.status_code == 401
