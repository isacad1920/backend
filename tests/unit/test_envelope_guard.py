"""Guard tests ensuring strict response envelope structure.

These tests verify that representative endpoints do NOT leak legacy
root-level keys (e.g., items, total_revenue) outside the canonical
success/message/data/error/meta/timestamp set.
"""
import pytest
from httpx import AsyncClient

from app.core.config import settings

ALLOWED_TOP_KEYS = {"success", "message", "data", "error", "meta", "timestamp"}

@pytest.mark.asyncio
async def test_sales_list_envelope(authenticated_client: AsyncClient):
    resp = await authenticated_client.get(f"{settings.api_v1_str}/sales")
    assert resp.status_code == 200
    payload = resp.json()
    leaked = [k for k in payload.keys() if k not in ALLOWED_TOP_KEYS]
    # Accept empty list only
    assert leaked == [], f"Unexpected leaked top-level keys: {leaked}"
    assert isinstance(payload.get("data", {}).get("items", []), list)

@pytest.mark.asyncio
async def test_products_list_envelope(authenticated_client: AsyncClient):
    # Follow redirect if trailing slash enforced
    resp = await authenticated_client.get(f"{settings.api_v1_str}/products", follow_redirects=True)
    assert resp.status_code == 200
    payload = resp.json()
    leaked = [k for k in payload.keys() if k not in ALLOWED_TOP_KEYS]
    assert leaked == [], f"Unexpected leaked top-level keys: {leaked}"

@pytest.mark.asyncio
async def test_financial_sales_analytics_envelope(authenticated_client: AsyncClient):
    resp = await authenticated_client.get(f"{settings.api_v1_str}/financial/sales-analytics")
    assert resp.status_code == 200
    payload = resp.json()
    leaked = [k for k in payload.keys() if k not in ALLOWED_TOP_KEYS]
    assert leaked == [], f"Unexpected leaked top-level keys: {leaked}"
    assert "total_sales" in (payload.get("data") or {}), "Expected nested total_sales metric"

# New extended coverage tests
@pytest.mark.asyncio
async def test_categories_list_envelope(authenticated_client: AsyncClient):
    resp = await authenticated_client.get(f"{settings.api_v1_str}/categories/", follow_redirects=True)
    assert resp.status_code == 200
    payload = resp.json()
    leaked = [k for k in payload.keys() if k not in ALLOWED_TOP_KEYS]
    assert leaked == []
    assert isinstance(payload.get("data", {}).get("items", []), list)

@pytest.mark.asyncio
async def test_product_detail_envelope(authenticated_client: AsyncClient, test_product: dict):
    resp = await authenticated_client.get(f"{settings.api_v1_str}/products/{test_product['id']}")
    assert resp.status_code == 200
    payload = resp.json()
    leaked = [k for k in payload.keys() if k not in ALLOWED_TOP_KEYS]
    assert leaked == []
    assert (payload.get("data") or {}).get("id") == test_product["id"]

@pytest.mark.asyncio
async def test_error_response_envelope(authenticated_client: AsyncClient):
    # Request a non-existent product to produce 404
    resp = await authenticated_client.get(f"{settings.api_v1_str}/products/99999999")
    assert resp.status_code == 404
    payload = resp.json()
    # Error envelope should still only include allowed keys
    leaked = [k for k in payload.keys() if k not in ALLOWED_TOP_KEYS]
    assert leaked == [], f"Unexpected leaked keys on error: {leaked}"
    assert payload.get("success") is False
    assert payload.get("error") and isinstance(payload["error"], dict)

@pytest.mark.asyncio
async def test_inventory_analytics_envelope(authenticated_client: AsyncClient):
    resp = await authenticated_client.get(f"{settings.api_v1_str}/financial/inventory-analytics")
    assert resp.status_code == 200
    payload = resp.json()
    leaked = [k for k in payload.keys() if k not in ALLOWED_TOP_KEYS]
    assert leaked == []
    assert "total_value" in (payload.get("data") or {})
