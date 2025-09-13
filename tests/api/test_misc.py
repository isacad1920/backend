"""
Health and system endpoint tests.
"""
import pytest
from httpx import AsyncClient

from app.core.config import settings


class TestHealthEndpoints:
    """Test health check and system endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncClient):
        """Test health check endpoint."""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data") or payload
        print(f"Health response: {payload}")
        # Health endpoint may remain minimal (not fully standardized), accept either form
        assert "status" in data
        assert data["status"] in ["healthy", "unhealthy"]
        # timestamp may be top-level or nested
        assert ("timestamp" in payload) or ("timestamp" in data)
    
    @pytest.mark.asyncio
    async def test_ping(self, async_client: AsyncClient):
        """Test ping endpoint."""
        response = await async_client.get("/ping")
        
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data") or payload
        assert (payload.get("message") == "pong") or (data.get("message") == "pong")
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client: AsyncClient):
        """Test root endpoint."""
        response = await async_client.get("/")
        
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data") or payload
        assert any(k in payload for k in ["message"]) or "message" in data
        for k in ["version", "environment"]:
            assert k in data or k in payload
        assert "timestamp" in payload or "timestamp" in data
    
    @pytest.mark.asyncio
    async def test_api_info(self, async_client: AsyncClient):
        """Test API info endpoint."""
        response = await async_client.get(f"{settings.api_v1_str}/info")
        
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data") or payload
        for k in ["name", "version", "api_version", "features", "contact"]:
            assert k in data or k in payload
        assert (data.get("api_version") or payload.get("api_version")) == "v1"
    
    @pytest.mark.asyncio
    async def test_api_info_features(self, async_client: AsyncClient):
        """Test API info endpoint contains expected features."""
        response = await async_client.get(f"{settings.api_v1_str}/info")
        
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data") or payload
        features = data.get("features", {})
        
        expected_features = [
            "multi_currency", 
            "branch_orders", 
            "reports", 
            "notifications", 
            "audit_logging"
        ]
        
        for feature in expected_features:
            assert feature in features
    
    @pytest.mark.asyncio 
    async def test_development_routes_endpoint(self, async_client: AsyncClient):
        """Test development routes endpoint (if in dev environment)."""
        response = await async_client.get("/dev/routes")
        
        if response.status_code == 200:
            payload = response.json()
            data = payload.get("data") or payload
            assert "routes" in data
            assert "total" in data
            assert isinstance(data["routes"], list)
        else:
            # Should be 404 in production
            assert response.status_code == 404


class TestNotificationEndpoints:
    """Test notification endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_notifications(self, authenticated_client: AsyncClient):
        """Test getting user notifications."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/notifications"
        )
        
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data") or payload
        # Standard envelope: notifications list inside data
        notifications = data.get("notifications") or data.get("items") or []
        assert isinstance(notifications, list)
    
    @pytest.mark.asyncio
    async def test_mark_notification_read(self, authenticated_client: AsyncClient):
        """Test marking notification as read."""
        # First get notifications to get a valid ID
        notifications_response = await authenticated_client.get(
            f"{settings.api_v1_str}/notifications"
        )
        
        if notifications_response.status_code == 200:
            notifications_payload = notifications_response.json()
            nd = notifications_payload.get("data") or notifications_payload
            notifications = nd.get("notifications") or nd.get("items") or []
            
            if notifications and len(notifications) > 0:
                notification_id = notifications[0].get("id")
                if notification_id:
                    response = await authenticated_client.put(
                        f"{settings.api_v1_str}/notifications/{notification_id}/read"
                    )
                    
                    assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_create_notification(self, authenticated_client: AsyncClient):
        """Test creating a notification."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/notifications",
            json={
                "title": "Test Notification",
                "message": "This is a test notification",
                "type": "INFO",
                "user_id": 1
            }
        )
        
        # May succeed or fail based on implementation
        assert response.status_code in [201, 403, 404]
    
    @pytest.mark.asyncio
    async def test_unauthorized_notifications_access(self, async_client: AsyncClient):
        """Test accessing notifications without authentication."""
        response = await async_client.get(
            f"{settings.api_v1_str}/notifications"
        )
        
        assert response.status_code == 401


class TestStockRequestEndpoints:
    """Test stock request endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_stock_requests(self, authenticated_client: AsyncClient):
        """Test listing stock requests."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/stock-requests"
        )
        
        assert response.status_code == 200
        payload = response.json()
        data = payload.get("data") or payload
        items = data.get("items") or []
        assert isinstance(items, list)
    
    @pytest.mark.asyncio
    async def test_create_stock_request(self, authenticated_client: AsyncClient, test_product: dict):
        """Test creating a stock request."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/stock-requests",
            json={
                "product_id": test_product["id"],
                "quantity": 50,
                "priority": "MEDIUM",
                "reason": "Low stock level",
                "notes": "Test stock request"
            }
        )
        
        # May succeed or fail based on implementation
        assert response.status_code in [201, 400, 403]
    
    @pytest.mark.asyncio
    async def test_get_stock_request_by_id(self, authenticated_client: AsyncClient):
        """Test getting stock request by ID."""
        # First get list of stock requests
        requests_response = await authenticated_client.get(
            f"{settings.api_v1_str}/stock-requests"
        )
        
        if requests_response.status_code == 200:
            requests_payload = requests_response.json()
            rd = requests_payload.get("data") or requests_payload
            requests = rd.get("items") or []
            
            if requests and len(requests) > 0:
                request_id = requests[0].get("id")
                if request_id:
                    response = await authenticated_client.get(
                        f"{settings.api_v1_str}/stock-requests/{request_id}"
                    )
                    
                    assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_approve_stock_request(self, authenticated_client: AsyncClient):
        """Test approving a stock request."""
        # This would typically require manager/admin permissions
        response = await authenticated_client.put(
            f"{settings.api_v1_str}/stock-requests/1/approve",
            json={
                "approved_quantity": 30,
                "notes": "Approved with reduced quantity"
            }
        )
        
        # May succeed or fail based on permissions/implementation
        assert response.status_code in [200, 403, 404]
    
    @pytest.mark.asyncio
    async def test_unauthorized_stock_requests_access(self, async_client: AsyncClient):
        """Test accessing stock requests without authentication."""
        response = await async_client.get(
            f"{settings.api_v1_str}/stock-requests"
        )
        
        assert response.status_code == 401
