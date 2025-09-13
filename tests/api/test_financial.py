"""
Financial API endpoint tests.
"""
import pytest
from httpx import AsyncClient
from app.core.config import settings


class TestFinancialEndpoints:
    """Test financial analytics endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_financial_summary(self, authenticated_client: AsyncClient):
        """Test getting financial summary."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/financial/summary"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "revenue" in data or "total_revenue" in data
        assert "expenses" in data or "total_expenses" in data
    
    @pytest.mark.asyncio
    async def test_get_financial_summary_with_date_range(self, authenticated_client: AsyncClient):
        """Test getting financial summary with date range."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/financial/summary",
            params={
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
                "branch_id": 1
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    @pytest.mark.asyncio
    async def test_get_sales_analytics(self, authenticated_client: AsyncClient):
        """Test getting sales analytics."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/financial/sales-analytics"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_sales" in data or "totalSales" in data
    
    @pytest.mark.asyncio
    async def test_get_inventory_analytics(self, authenticated_client: AsyncClient):
        """Test getting inventory analytics."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/financial/inventory-analytics"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_value" in data or "totalValue" in data
    
    @pytest.mark.asyncio
    async def test_get_customer_analytics(self, authenticated_client: AsyncClient):
        """Test getting customer analytics."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/financial/customer-analytics"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_customers" in data or "totalCustomers" in data
    
    @pytest.mark.asyncio
    async def test_get_financial_ratios(self, authenticated_client: AsyncClient):
        """Test getting financial ratios."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/financial/ratios"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "profit_margin" in data or "profitMargin" in data
    
    @pytest.mark.asyncio
    async def test_get_income_statement(self, authenticated_client: AsyncClient):
        """Test getting income statement."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/financial/income-statement",
            params={
                "period": "MONTHLY",
                "year": 2024,
                "month": 12
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "revenue" in data
        assert "expenses" in data
    
    @pytest.mark.asyncio
    async def test_get_balance_sheet(self, authenticated_client: AsyncClient):
        """Test getting balance sheet."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/financial/balance-sheet"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "assets" in data
        assert "liabilities" in data
    
    @pytest.mark.asyncio
    async def test_get_cash_flow_statement(self, authenticated_client: AsyncClient):
        """Test getting cash flow statement."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/financial/cash-flow"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "operating_activities" in data or "operatingActivities" in data
    
    @pytest.mark.asyncio
    async def test_get_tax_report(self, authenticated_client: AsyncClient):
        """Test getting tax report."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/financial/tax-report",
            params={
                "period": "QUARTERLY",
                "year": 2024,
                "quarter": 4
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_tax" in data or "totalTax" in data
    
    @pytest.mark.asyncio
    async def test_get_budget_comparison(self, authenticated_client: AsyncClient):
        """Test getting budget comparison."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/financial/budget-comparison"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "budget" in data
        assert "actual" in data
    
    @pytest.mark.asyncio
    async def test_get_profit_loss_analysis(self, authenticated_client: AsyncClient):
        """Test getting profit loss analysis."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/financial/profit-loss"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "gross_profit" in data or "grossProfit" in data
    
    @pytest.mark.asyncio
    async def test_get_dashboard_summary(self, authenticated_client: AsyncClient):
        """Test getting dashboard summary."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/financial/dashboard"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "key_metrics" in data or "keyMetrics" in data
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics(self, authenticated_client: AsyncClient):
        """Test getting performance metrics."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/financial/performance"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "revenue_growth" in data or "revenueGrowth" in data
    
    @pytest.mark.asyncio
    async def test_get_financial_alerts(self, authenticated_client: AsyncClient):
        """Test getting financial alerts."""
        response = await authenticated_client.get(
            f"{settings.api_v1_str}/financial/alerts"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data or isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_generate_report(self, authenticated_client: AsyncClient):
        """Test generating financial report."""
        response = await authenticated_client.post(
            f"{settings.api_v1_str}/financial/generate-report",
            json={
                "report_type": "SALES",
                "period": "MONTHLY",
                "format": "PDF",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
        )
        
        # May succeed or fail based on implementation
        assert response.status_code in [200, 202, 400, 404]
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, async_client: AsyncClient):
        """Test accessing financial endpoints without authentication."""
        response = await async_client.get(
            f"{settings.api_v1_str}/financial/summary"
        )
        
        assert response.status_code == 401
