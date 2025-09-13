"""
Authentication API endpoint tests.
"""
import pytest
from httpx import AsyncClient
from app.core.config import settings


class TestAuthenticationEndpoints:
    """Test authentication endpoints."""
    
    @pytest.mark.asyncio
    async def test_login_valid_credentials(self, async_client: AsyncClient):
        """Test login with valid credentials."""
        response = await async_client.post(
            f"{settings.api_v1_str}/auth/login",
            json={
                "email": "demo@sofinance.com",
                "password": "DemoPassword123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials."""
        response = await async_client.post(
            f"{settings.api_v1_str}/auth/login",
            json={
                "email": "invalid@test.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_login_missing_fields(self, async_client: AsyncClient):
        """Test login with missing fields."""
        response = await async_client.post(
            f"{settings.api_v1_str}/auth/login",
            json={"email": "test@test.com"}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_refresh_token_valid(self, async_client: AsyncClient):
        """Test refresh token with valid token."""
        # First login to get tokens
        login_response = await async_client.post(
            f"{settings.api_v1_str}/auth/login",
            json={
                "email": "demo@sofinance.com",
                "password": "DemoPassword123!"
            }
        )
        
        assert login_response.status_code == 200
        login_data = login_response.json()
        refresh_token = login_data["refresh_token"]
        
        # Test refresh
        response = await async_client.post(
            f"{settings.api_v1_str}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, async_client: AsyncClient):
        """Test refresh token with invalid token."""
        response = await async_client.post(
            f"{settings.api_v1_str}/auth/refresh",
            json={"refresh_token": "invalid_refresh_token"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_logout(self, authenticated_client: AsyncClient):
        """Test logout endpoint."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/auth/logout"
        )
        
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_logout_unauthorized(self, async_client: AsyncClient):
        """Test logout without authentication."""
        response = await async_client.post(
            f"{settings.api_v1_str}/auth/logout"
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_password_reset_request(self, async_client: AsyncClient):
        """Test password reset request."""
        response = await async_client.post(
            f"{settings.api_v1_str}/auth/password-reset-request",
            json={"email": "demo@sofinance.com"}
        )
        
        # Should accept the request even if email doesn't exist (security)
        assert response.status_code in [200, 202]
    
    @pytest.mark.asyncio
    async def test_password_reset_request_invalid_email(self, async_client: AsyncClient):
        """Test password reset request with invalid email format."""
        response = await async_client.post(
            f"{settings.api_v1_str}/auth/password-reset-request",
            json={"email": "invalid-email"}
        )
        
        assert response.status_code == 422
