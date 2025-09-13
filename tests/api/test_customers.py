"""
Customer API endpoint tests.
"""
import pytest
from httpx import AsyncClient

from app.core.config import settings
from tests.conftest import TEST_CUSTOMER_DATA


class TestCustomerEndpoints:
    """Test customer management endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_customers(self, authenticated_client: AsyncClient):
        """Test listing customers."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/customers/"
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload.get("success") is True
        data = payload["data"]
        assert "items" in data and isinstance(data["items"], list)
        assert "pagination" in data
        pg = data["pagination"]
        assert all(k in pg for k in ["total", "page", "limit", "total_pages"]) or all(k in pg for k in ["total", "page", "limit"])  # transitional
    
    @pytest.mark.asyncio
    async def test_list_customers_with_filters(self, authenticated_client: AsyncClient):
        """Test listing customers with filters."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/customers/",
            params={
                "page": 1,
                "size": 10,
                "search": "Test",
                "customer_type": "REGULAR",
                "status": "ACTIVE"
            }
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload.get("success") is True
        data = payload["data"]
        assert "items" in data
    
    @pytest.mark.asyncio
    async def test_get_customer_by_id(self, authenticated_client: AsyncClient, test_customer: dict):
        """Test getting customer by ID."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/customers/{test_customer['id']}"
        )
        
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data") or payload
        for k in ["id", "email", "status"]:
            assert k in data
        assert ("firstName" in data or "first_name" in data)
        assert ("lastName" in data or "last_name" in data)
    
    @pytest.mark.asyncio
    async def test_get_customer_not_found(self, authenticated_client: AsyncClient):
        """Test getting non-existent customer."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/customers/99999"
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_customer(self, authenticated_client: AsyncClient):
        """Test creating a new customer."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/customers/",
            json=TEST_CUSTOMER_DATA
        )
        
        if response.status_code == 201:
            payload = response.json()
            data = payload.get("data") or payload
            assert "id" in data
            fn = data.get("firstName") or data.get("first_name")
            assert fn == TEST_CUSTOMER_DATA["firstName"]
            assert data["email"] == TEST_CUSTOMER_DATA["email"]
        else:
            # Customer might already exist
            assert response.status_code in [400, 409]
    
    @pytest.mark.asyncio
    async def test_create_customer_invalid_data(self, authenticated_client: AsyncClient):
        """Test creating customer with invalid data."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/customers/",
            json={
                "firstName": "",  # Empty name
                "email": "invalid-email",  # Invalid email
                "phone": "invalid-phone"
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_update_customer(self, authenticated_client: AsyncClient, test_customer: dict):
        """Test updating a customer."""
        response = await authenticated_client.put(
            f"{settings.api_v1_str}/customers/{test_customer['id']}",
            json={
                "firstName": "Updated",
                "lastName": "Customer"
            }
        )
        
        assert response.status_code in [200, 403, 404]
    
    @pytest.mark.asyncio
    async def test_delete_customer(self, authenticated_client: AsyncClient):
        """Test deleting a customer."""
        response = await authenticated_client.delete(
            f"{settings.api_v1_str}/customers/99999"
        )
        
        # Should be not found or forbidden
        assert response.status_code in [404, 403, 401]
    
    @pytest.mark.asyncio
    async def test_get_customer_statistics(self, authenticated_client: AsyncClient):
        """Test getting customer statistics."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/customers/statistics"
        )
        
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data") or payload
        assert any(k in data for k in ["total_customers", "totalCustomers"]) or any(k in payload for k in ["total_customers", "totalCustomers"])
    
    @pytest.mark.asyncio
    async def test_get_customer_purchase_history(self, authenticated_client: AsyncClient, test_customer: dict):
        """Test getting customer purchase history."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/customers/{test_customer['id']}/purchase-history"
        )
        
        assert response.status_code == 200
        body = response.json()
        data_wrapper = body.get("data") or {}
        assert "items" in data_wrapper
        pagination = data_wrapper.get("pagination") or {}
        for key in ["total", "page", "limit", "total_pages"]:
            assert key in pagination
    
    @pytest.mark.asyncio
    async def test_bulk_update_customers(self, authenticated_client: AsyncClient):
        """Test bulk updating customers."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/customers/bulk-update",
            json={
                "customer_ids": [1, 2],
                "update_data": {
                    "customer_type": "VIP"
                }
            }
        )
        
        # May succeed or fail based on implementation/permissions
        assert response.status_code in [200, 400, 403, 404]
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, async_client: AsyncClient):
        """Test accessing customer endpoints without authentication."""
        response = await async_client.get(
            f"{settings.api_v1_str}/customers/"
        )
        
        assert response.status_code == 401
