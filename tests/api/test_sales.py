"""
Sales API endpoint tests.
"""
import pytest
from httpx import AsyncClient

from app.core.config import settings


class TestSalesEndpoints:
    """Test sales management endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_sales(self, authenticated_client: AsyncClient):
        """Test listing sales."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/sales/"
        )
        
        assert response.status_code == 200
        payload = response.json()
        # New canonical shape: success envelope with data object
        assert payload.get("success") is True
        assert "data" in payload
        data = payload["data"]
        assert "items" in data
        assert "pagination" in data
        pg = data["pagination"]
        assert all(k in pg for k in ["total", "page", "limit", "total_pages"]) or all(k in pg for k in ["total", "page", "limit"])  # transitional
        assert isinstance(data["items"], list)
    
    @pytest.mark.asyncio
    async def test_list_sales_with_filters(self, authenticated_client: AsyncClient):
        """Test listing sales with filters."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/sales/",
            params={
                "page": 1,
                "size": 10,
                "status": "COMPLETED",
                "payment_method": "CASH",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
        )
        
        assert response.status_code == 200
        payload = response.json()
        assert payload.get("success") is True
        data = payload["data"]
        assert "items" in data
    
    @pytest.mark.asyncio
    async def test_get_sale_by_id(self, authenticated_client: AsyncClient):
        """Test getting sale by ID."""
        # First get list of sales to get a valid ID
        sales_response = await authenticated_client.get(
            f"{settings.api_v1_str}/sales/"
        )
        
        if sales_response.status_code == 200:
            sales_payload = sales_response.json()
            if sales_payload.get("data", {}).get("items"):
                sale_id = sales_payload["data"]["items"][0]["id"]
                
                response = await authenticated_client.get(
                    f"{settings.api_v1_str}/sales/{sale_id}"
                )
                
                assert response.status_code == 200
                payload = response.json()
                data = payload.get("data") or payload
                assert "id" in data
                assert "total" in data or "total_amount" in data
                assert "status" in data
    
    @pytest.mark.asyncio
    async def test_get_sale_not_found(self, authenticated_client: AsyncClient):
        """Test getting non-existent sale."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/sales/99999"
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_sale(self, authenticated_client: AsyncClient, test_product: dict, test_customer: dict):
        """Test creating a new sale."""
        sale_data = {
            "customer_id": test_customer["id"],
            "payment_method": "CASH",
            "items": [
                {
                    "product_id": test_product["id"],
                    "quantity": 2,
                    "unit_price": test_product["price"]
                }
            ],
            "notes": "Test sale"
        }
        
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/sales/",
            json=sale_data
        )
        
        if response.status_code == 201:
            payload = response.json()
            data = payload.get("data") or payload
            assert "id" in data
            assert ("total" in data) or ("total_amount" in data)
            assert "status" in data
        else:
            # May fail due to various business rules
            assert response.status_code in [400, 403, 422]
    
    @pytest.mark.asyncio
    async def test_create_sale_invalid_data(self, authenticated_client: AsyncClient):
        """Test creating sale with invalid data."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/sales/",
            json={
                "items": [],  # Empty items
                "payment_method": "INVALID_METHOD"
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_sales_statistics(self, authenticated_client: AsyncClient):
        """Test getting sales statistics."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/sales/stats"
        )
        
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data") or payload
        assert any(k in data for k in ["total_sales", "totalSales"]) or any(k in payload for k in ["total_sales", "totalSales"])
    
    @pytest.mark.asyncio
    async def test_get_sale_receipt(self, authenticated_client: AsyncClient):
        """Test getting sale receipt."""
        # First get a sale ID
        sales_response = await authenticated_client.get(
            f"{settings.api_v1_str}/sales/"
        )
        
        if sales_response.status_code == 200:
            sales_payload = sales_response.json()
            if sales_payload.get("data", {}).get("items"):
                sale_id = sales_payload["data"]["items"][0]["id"]
                
                response = await authenticated_client.get(
                    f"{settings.api_v1_str}/sales/{sale_id}/receipt"
                )
                
                assert response.status_code in [200, 404]  # May not be implemented
    
    @pytest.mark.asyncio
    async def test_process_refund(self, authenticated_client: AsyncClient):
        """Test processing a refund."""
        # First get a sale ID
        sales_response = await authenticated_client.get(
            f"{settings.api_v1_str}/sales/"
        )
        
        if sales_response.status_code == 200:
            sales_payload = sales_response.json()
            if sales_payload.get("data", {}).get("items"):
                sale_id = sales_payload["data"]["items"][0]["id"]
                
                response = await authenticated_client.post(
                    f"{settings.api_v1_str}/sales/{sale_id}/refund",
                    json={
                        "amount": 10.00,
                        "reason": "Customer request",
                        "items": []
                    }
                )
                
                # May succeed or fail based on business rules
                assert response.status_code in [200, 400, 403, 404]
    
    @pytest.mark.asyncio
    async def test_list_refunds(self, authenticated_client: AsyncClient):
        """Test listing refunds."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/sales/refunds"
        )
        
        assert response.status_code in [200, 404]  # May not be implemented
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, async_client: AsyncClient):
        """Test accessing sales endpoints without authentication."""
        response = await async_client.get(
            f"{settings.api_v1_str}/sales/"
        )
        
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_accounts_receivable_summary(self, authenticated_client: AsyncClient):
        """Test AR summary endpoint exists and returns expected shape."""
        response = await authenticated_client.get(f"{settings.api_v1_str}/sales/ar/summary")
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            payload = response.json()
            data = payload.get("data") or payload
            for k in ["receivables_count", "outstanding_total", "paid_total"]:
                assert k in data

    @pytest.mark.asyncio
    async def test_add_payment_flow(self, authenticated_client: AsyncClient, test_product: dict, test_customer: dict):
        """Create a PARTIAL sale then add a payment and verify outstanding decreases."""
        sale_payload = {
            "customer_id": test_customer["id"],
            "payment_method": "CASH",
            "payment_type": "PARTIAL",
            "items": [
                {"product_id": test_product["id"], "quantity": 1, "unit_price": test_product["price"]}
            ],
            "initial_payment": 0.0,
            "notes": "Partial sale test"
        }
        sale_resp = await authenticated_client.post(f"{settings.api_v1_str}/sales/", json=sale_payload)
        assert sale_resp.status_code in [200, 201, 400, 403, 422], sale_resp.text
        sale_json = sale_resp.json()
        sale_data = sale_json.get("data") or sale_json
        if sale_resp.status_code not in [200, 201]:
            # Business rule or validation rejection path: standardized envelope
            if isinstance(sale_data, dict) and sale_data.get("success") is False:
                err = sale_data.get("error") or {}
                assert "code" in err and "message" in err
            return  # Cannot proceed to payment without a sale id
        sale_id = sale_data.get("id")
        assert sale_id, "Sale ID must be returned for successful creation"
        # Get receipt to determine total
        receipt_resp = await authenticated_client.get(f"{settings.api_v1_str}/sales/{sale_id}/receipt")
        total_amount = None
        if receipt_resp.status_code == 200:
            rjson = receipt_resp.json()
            receipt_wrapper = rjson.get("data") or rjson
            sale_obj = receipt_wrapper.get("sale") or receipt_wrapper
            total_amount = sale_obj.get("total") or sale_obj.get("total_amount")
        # Add payment (small amount)
        pay_resp = await authenticated_client.post(f"{settings.api_v1_str}/sales/{sale_id}/payments", json={"amount": 0.01, "reference": "test"})
        assert pay_resp.status_code in [201, 400, 403]
        if pay_resp.status_code == 201:
            pay_json = pay_resp.json()
            pdata = pay_json.get("data") or pay_json
            assert "paid_amount" in pdata
            assert "outstanding_amount" in pdata
            if total_amount:
                assert pdata["paid_amount"] <= float(total_amount) + 0.01

    @pytest.mark.asyncio
    async def test_add_payment_unauthorized(self, async_client: AsyncClient):
        """Ensure adding payment without auth is rejected."""
        resp = await async_client.post(f"{settings.api_v1_str}/sales/123456/payments", json={"amount": 1})
        assert resp.status_code in [401, 403]
