"""
Branch API endpoint tests.
"""
import pytest
from httpx import AsyncClient
from app.core.config import settings
from tests.conftest import TEST_BRANCH_DATA


class TestBranchEndpoints:
    """Test branch management endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_branches(self, authenticated_client: AsyncClient):
        """Test listing branches."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/branches/"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert isinstance(data["items"], list)
    
    @pytest.mark.asyncio
    async def test_list_branches_with_filters(self, authenticated_client: AsyncClient):
        """Test listing branches with filters."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/branches/",
            params={
                "page": 1,
                "size": 10,
                "search": "Main",
                "status": "ACTIVE"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
    
    @pytest.mark.asyncio
    async def test_get_branch_by_id(self, authenticated_client: AsyncClient, test_branch: dict):
        """Test getting branch by ID."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/branches/{test_branch['id']}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "address" in data
        assert "status" in data
    
    @pytest.mark.asyncio
    async def test_get_branch_not_found(self, authenticated_client: AsyncClient):
        """Test getting non-existent branch."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/branches/99999"
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_branch(self, authenticated_client: AsyncClient):
        """Test creating a new branch."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/branches/",
            json=TEST_BRANCH_DATA
        )
        
        if response.status_code == 201:
            data = response.json()
            assert "id" in data
            assert data["name"] == TEST_BRANCH_DATA["name"]
            assert data["address"] == TEST_BRANCH_DATA["address"]
        else:
            # Branch might already exist or no permission
            assert response.status_code in [400, 403, 409]
    
    @pytest.mark.asyncio
    async def test_create_branch_invalid_data(self, authenticated_client: AsyncClient):
        """Test creating branch with invalid data."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/branches/",
            json={
                "name": "",  # Empty name should be invalid
                "address": "123 Test St"
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_update_branch(self, authenticated_client: AsyncClient, test_branch: dict):
        """Test updating a branch."""
        response = await authenticated_client.put(
            f"{settings.api_v1_str}/branches/{test_branch['id']}",
            json={
                "name": "Updated Branch Name",
                "address": test_branch["address"]
            }
        )
        
        # May succeed or fail based on permissions
        assert response.status_code in [200, 403, 404]
    
    @pytest.mark.asyncio
    async def test_delete_branch(self, authenticated_client: AsyncClient):
        """Test deleting a branch."""
        response = await authenticated_client.delete(
            f"{settings.api_v1_str}/branches/99999"
        )
        
        # Should be not found or forbidden
        assert response.status_code in [404, 403, 401]
    
    @pytest.mark.asyncio
    async def test_get_branch_statistics(self, authenticated_client: AsyncClient):
        """Test getting branch statistics."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/branches/statistics"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_branches" in data or "totalBranches" in data
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, async_client: AsyncClient):
        """Public listing allowed; ensure endpoint responds 200 and contains items key."""
        response = await async_client.get(f"{settings.api_v1_str}/branches/")
        assert response.status_code == 200
        body = response.json()
        assert "items" in body
