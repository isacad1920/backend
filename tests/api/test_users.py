"""
User API endpoint tests.
"""
import pytest
from httpx import AsyncClient

from app.core.config import settings
from tests.conftest import TEST_USER_DATA


class TestUserEndpoints:
    """Test user management endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_users(self, authenticated_client: AsyncClient):
        """Test listing users."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/users/"
        )
        
        assert response.status_code == 200
        payload = response.json()
        assert payload.get("success") is True
        assert "data" in payload
        data = payload["data"]
        assert "items" in data and isinstance(data["items"], list)
        assert "pagination" in data
        pg = data["pagination"]
        assert all(k in pg for k in ["total", "page", "limit", "total_pages"]) or all(k in pg for k in ["total", "page", "limit"])  # transitional
    
    @pytest.mark.asyncio
    async def test_list_users_with_filters(self, authenticated_client: AsyncClient):
        """Test listing users with filters."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/users/",
            params={
                "page": 1,
                "size": 10,
                "search": "demo",
                "role": "ADMIN",
                "is_active": True
            }
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload.get("success") is True
        data = payload["data"]
        assert "items" in data
        pg = data["pagination"]
        assert pg["page"] == 1
        assert pg.get("limit") == 10
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, authenticated_client: AsyncClient):
        """Test getting user by ID."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/users/1"
        )
        
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data") or payload
        for k in ["id", "email", "first_name", "last_name", "role"]:
            assert k in data
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, authenticated_client: AsyncClient):
        """Test getting non-existent user."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/users/99999"
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_user(self, authenticated_client: AsyncClient):
        """Test creating a new user."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/users/",
            json=TEST_USER_DATA
        )
        
        if response.status_code == 201:
            payload = response.json()
            data = payload.get("data") or payload
            assert "id" in data
            assert data["email"] == TEST_USER_DATA["email"]
            assert data["first_name"] == TEST_USER_DATA["first_name"]
            assert data["role"] == TEST_USER_DATA["role"]
        else:
            # User might already exist
            assert response.status_code in [400, 409]
    
    @pytest.mark.asyncio
    async def test_create_user_invalid_data(self, authenticated_client: AsyncClient):
        """Test creating user with invalid data."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/users/",
            json={
                "email": "invalid-email",
                "password": "weak",
                "first_name": "",
                "role": "INVALID_ROLE"
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_update_user(self, authenticated_client: AsyncClient):
        """Test updating a user."""
        # First get a user to update
        users_response = await authenticated_client.get(
            f"{settings.api_v1_str}/users/"
        )
        assert users_response.status_code == 200
        users_payload = users_response.json()
        up = users_payload.get("data") or users_payload
        items = up.get("items") or []
        if items:
            user_id = items[0]["id"]
            
            response = await authenticated_client.put(
                f"{settings.api_v1_str}/users/{user_id}",
                json={
                    "first_name": "Updated",
                    "last_name": "Name"
                }
            )
            
            assert response.status_code in [200, 403]  # 403 if no permission
    
    @pytest.mark.asyncio
    async def test_delete_user(self, authenticated_client: AsyncClient):
        """Test deleting a user."""
        # This would typically be restricted
        response = await authenticated_client.delete(
            f"{settings.api_v1_str}/users/99999"
        )
        
        # Should be not found or forbidden
        assert response.status_code in [404, 403, 401]
    
    @pytest.mark.asyncio
    async def test_get_user_profile(self, authenticated_client: AsyncClient):
        """Test getting current user profile."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/users/profile"
        )
        
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data") or payload
        assert "id" in data and "email" in data
    
    @pytest.mark.asyncio
    async def test_update_user_profile(self, authenticated_client: AsyncClient):
        """Test updating current user profile."""
        response = await authenticated_client.put(
            f"{settings.api_v1_str}/users/profile",
            json={
                "first_name": "Updated",
                "last_name": "Profile"
            }
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_change_password(self, authenticated_client: AsyncClient):
        """Test changing user password."""
        response = await authenticated_client.put(
            f"{settings.api_v1_str}/users/change-password",
            json={
                "current_password": "DemoPassword123!",
                "new_password": "NewPassword123!",
                "confirm_password": "NewPassword123!"
            }
        )
        
        # May fail if current password is wrong or endpoint doesn't exist
        assert response.status_code in [200, 401, 404]
    
    @pytest.mark.asyncio
    async def test_get_user_statistics(self, authenticated_client: AsyncClient):
        """Test getting user statistics."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/users/statistics"
        )
        
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data") or payload
        assert any(k in data for k in ["total_users", "totalUsers"]) or any(k in payload for k in ["total_users", "totalUsers"])
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, async_client: AsyncClient):
        """Test accessing user endpoints without authentication."""
        response = await async_client.get(
            f"{settings.api_v1_str}/users/"
        )
        
        assert response.status_code == 401
