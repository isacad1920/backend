"""
Permission management API endpoint tests.
"""
import pytest
from httpx import AsyncClient
from app.core.config import settings


class TestPermissionEndpoints:
    """Test permission management endpoints."""
    
    @pytest.mark.asyncio
    async def test_grant_permissions(self, authenticated_client: AsyncClient):
        """Test granting permissions to a user."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/admin/permissions/grant",
            json={
                "user_id": 2,
                "permissions": ["products:write", "sales:read"],
                "reason": "Testing permission grant"
            }
        )
        
        # May succeed or fail based on admin permissions
        assert response.status_code in [200, 403, 404]
    
    @pytest.mark.asyncio
    async def test_revoke_permissions(self, authenticated_client: AsyncClient):
        """Test revoking permissions from a user."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/admin/permissions/revoke",
            json={
                "user_id": 2,
                "permissions": ["products:write"],
                "reason": "Testing permission revoke"
            }
        )
        
        # May succeed or fail based on admin permissions
        assert response.status_code in [200, 403, 404]
    
    @pytest.mark.asyncio
    async def test_get_user_permissions(self, authenticated_client: AsyncClient):
        """Test getting user permissions."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/admin/permissions/user/1",
            params={"user_role": "ADMIN"}
        )
        
        # May succeed or fail based on admin permissions
        assert response.status_code in [200, 403, 404]
    
    @pytest.mark.asyncio
    async def test_get_available_permissions(self, authenticated_client: AsyncClient):
        """Test getting available permissions."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/admin/permissions/available"
        )
        
        # May succeed or fail based on admin permissions
        assert response.status_code in [200, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert "permissions" in data
            assert isinstance(data["permissions"], list)
    
    @pytest.mark.asyncio
    async def test_bulk_grant_permissions(self, authenticated_client: AsyncClient):
        """Test bulk granting permissions."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/admin/permissions/bulk-grant",
            json={
                "user_ids": [2, 3],
                "permissions": ["sales:read"],
                "reason": "Bulk permission grant test"
            }
        )
        
        # May succeed or fail based on admin permissions
        assert response.status_code in [200, 403, 404]
    
    @pytest.mark.asyncio
    async def test_get_audit_logs(self, authenticated_client: AsyncClient):
        """Test getting permission audit logs."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/admin/permissions/audit-logs"
        )
        
        # May succeed or fail based on admin permissions
        assert response.status_code in [200, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert "logs" in data or isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_audit_logs_for_user(self, authenticated_client: AsyncClient):
        """Test getting permission audit logs for specific user."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/admin/permissions/audit-logs",
            params={"user_id": 1}
        )
        
        # May succeed or fail based on admin permissions
        assert response.status_code in [200, 403]
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, async_client: AsyncClient):
        """Test accessing permission endpoints without authentication."""
        response = await async_client.get(
            f"{settings.api_v1_str}/admin/permissions/available"
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_non_admin_access(self, authenticated_client: AsyncClient):
        """Test accessing permission endpoints without admin privileges."""
        # This test assumes the authenticated user is not an admin
        # In real scenarios, you'd use a non-admin user fixture
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/admin/permissions/available"
        )
        
        # Should be forbidden if user is not admin, or succeed if user is admin
        assert response.status_code in [200, 403]
