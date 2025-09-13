"""
Authentication API endpoint tests.
"""
import pytest
from httpx import AsyncClient

from app.core.config import settings


def _unwrap(json_obj: dict):
    """Return inner data object if present, else original."""
    if isinstance(json_obj, dict) and isinstance(json_obj.get("data"), dict):
        return json_obj["data"]
    return json_obj


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
        payload = response.json()
        data = _unwrap(payload)
        # Token fields now live inside envelope.data
        assert "access_token" in data
        assert "refresh_token" in data
        assert data.get("token_type") == "bearer"
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
        # Unified error envelope: success false + error object
        assert data.get("success") is False
        assert "error" in data and isinstance(data["error"], dict)
        err = data["error"]
        # Accept either generic UNAUTHORIZED code or fallback HTTP status message
        assert err.get("code") in ("UNAUTHORIZED", "AUTH_INVALID_CREDENTIALS", "HTTP_401")
        assert isinstance(err.get("message"), str) and err.get("message")
    
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
        login_payload = login_response.json()
        login_data = _unwrap(login_payload)
        refresh_token = login_data["refresh_token"]
        
        # Test refresh
        response = await async_client.post(
            f"{settings.api_v1_str}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        payload = response.json()
        data = _unwrap(payload)
        assert "access_token" in data
        assert data.get("token_type") == "bearer"
    
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
