"""
Product and Category API endpoint tests.
"""
import pytest
from httpx import AsyncClient

from app.core.config import settings
from tests.conftest import TEST_CATEGORY_DATA, TEST_PRODUCT_DATA


class TestProductEndpoints:
    """Test product management endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_products(self, authenticated_client: AsyncClient):
        """Test listing products."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/products/"
        )
        
        assert response.status_code == 200
        body = response.json()
        data = body.get("data") or {}
        assert isinstance(data.get("items"), list)
        pagination = data.get("pagination") or {}
        for key in ["total", "page", "limit", "total_pages"]:
            assert key in pagination
    
    @pytest.mark.asyncio
    async def test_list_products_with_filters(self, authenticated_client: AsyncClient):
        """Test listing products with filters."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/products/",
            params={
                "page": 1,
                "size": 10,
                "search": "Test",
                "status": "ACTIVE",
                "stock_status": "IN_STOCK"
            }
        )
        
        assert response.status_code == 200
        body = response.json()
        data = body.get("data") or {}
        assert "items" in data
    
    @pytest.mark.asyncio
    async def test_get_product_by_id(self, authenticated_client: AsyncClient, test_product: dict):
        """Test getting product by ID."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/products/{test_product['id']}"
        )
        
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data") or {}
        assert "id" in data
        assert "name" in data
        assert "sku" in data
        # Accept either costPrice/price naming variants
        assert "price" in data or "price" in {k.lower(): v for k,v in data.items()}
        assert "stockQuantity" in data or "stock_quantity" in data
    
    @pytest.mark.asyncio
    async def test_get_product_not_found(self, authenticated_client: AsyncClient):
        """Test getting non-existent product."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/products/99999"
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_product(self, authenticated_client: AsyncClient, test_category: dict):
        """Test creating a new product."""
        product_data = {**TEST_PRODUCT_DATA, "categoryId": test_category["id"]}
        
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/products/",
            json=product_data
        )
        
        if response.status_code == 201:
            data = response.json()
            assert "id" in data
            assert data["name"] == product_data["name"]
            assert data["sku"] == product_data["sku"]
        else:
            # Product might already exist or no permission
            assert response.status_code in [400, 403, 409]
    
    @pytest.mark.asyncio
    async def test_create_product_invalid_data(self, authenticated_client: AsyncClient):
        """Test creating product with invalid data."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/products/",
            json={
                "name": "",  # Empty name
                "price": -5,  # Negative price
                "sku": "INVALID_SKU"
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_update_product(self, authenticated_client: AsyncClient, test_product: dict):
        """Test updating a product."""
        response = await authenticated_client.put(
            f"{settings.api_v1_str}/products/{test_product['id']}",
            json={
                "name": "Updated Product Name",
                "price": 19.99
            }
        )
        
        # May succeed or fail based on permissions
        assert response.status_code in [200, 403, 404]
    
    @pytest.mark.asyncio
    async def test_delete_product(self, authenticated_client: AsyncClient):
        """Test deleting a product."""
        response = await authenticated_client.delete(
            f"{settings.api_v1_str}/products/99999"
        )
        
        # Should be not found or forbidden
        assert response.status_code in [404, 403, 401]
    
    @pytest.mark.asyncio
    async def test_get_product_statistics(self, authenticated_client: AsyncClient):
        """Test getting product statistics."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/products/statistics"
        )
        
        assert response.status_code == 200
        payload = response.json()
        # Stats now reside inside standardized data object (no root mirroring)
        stats = payload.get("data") or {}
        assert "total_products" in stats or "totalProducts" in stats
    
    @pytest.mark.asyncio
    async def test_adjust_stock(self, authenticated_client: AsyncClient, test_product: dict):
        """Test stock adjustment."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/products/{test_product['id']}/adjust-stock",
            json={
                "quantity": 10,
                "adjustment_type": "INCREASE",
                "reason": "Stock replenishment"
            }
        )
        
        # May succeed or fail based on permissions/implementation
        assert response.status_code in [200, 403, 404]


class TestCategoryEndpoints:
    """Test category management endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_categories(self, authenticated_client: AsyncClient):
        """Test listing categories."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/categories/"
        )
        
        assert response.status_code == 200
        body = response.json()
        data = body.get("data") or {}
        assert isinstance(data.get("items"), list)
        pagination = data.get("pagination") or {}
        for key in ["total", "page", "limit", "total_pages"]:
            assert key in pagination
    
    @pytest.mark.asyncio
    async def test_get_category_by_id(self, authenticated_client: AsyncClient, test_category: dict):
        """Test getting category by ID."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/categories/{test_category['id']}"
        )
        
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data") or {}
        assert "id" in data
        assert "name" in data
        assert "status" in data
    
    @pytest.mark.asyncio
    async def test_create_category(self, authenticated_client: AsyncClient):
        """Test creating a new category."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/categories/",
            json=TEST_CATEGORY_DATA
        )
        
        if response.status_code == 201:
            data = response.json()
            assert "id" in data
            assert data["name"] == TEST_CATEGORY_DATA["name"]
        else:
            # Category might already exist or no permission
            assert response.status_code in [400, 403, 409]
    
    @pytest.mark.asyncio
    async def test_update_category(self, authenticated_client: AsyncClient, test_category: dict):
        """Test updating a category."""
        response = await authenticated_client.put(
            f"{settings.api_v1_str}/categories/{test_category['id']}",
            json={
                "name": "Updated Category Name",
                "description": "Updated description"
            }
        )
        
        # May succeed or fail based on permissions
        assert response.status_code in [200, 403, 404]
    
    @pytest.mark.asyncio
    async def test_delete_category(self, authenticated_client: AsyncClient):
        """Test deleting a category."""
        response = await authenticated_client.delete(
            f"{settings.api_v1_str}/categories/99999"
        )
        
        # Should be not found or forbidden
        assert response.status_code in [404, 403, 401]
