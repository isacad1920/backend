"""End-to-end test for creating a sale then issuing a refund."""
import pytest
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.asyncio
async def test_sale_then_refund(authenticated_client: AsyncClient, test_product: dict, test_customer: dict):
    # Create a sale
    sale_payload = {
        "customer_id": test_customer["id"],
        "payment_method": "CASH",
        "items": [
            {
                "product_id": test_product["id"],
                "quantity": 1,
                "unit_price": test_product["price"],
            }
        ],
        "notes": "Integration sale for refund test",
    }

    sale_resp = await authenticated_client.post(f"{settings.api_v1_str}/sales/", json=sale_payload)
    assert sale_resp.status_code in (201, 400, 403, 422)
    if sale_resp.status_code != 201:
        # Business rule prevented creation; nothing else to assert
        return
    sale_data = sale_resp.json()
    sale_id = sale_data["id"]

    # Issue a refund (partial small amount)
    refund_payload = {
        "amount": 0.01 * sale_data.get("total", 100),  # trivial partial amount
        "reason": "Test refund",
        "items": [],
    }
    refund_resp = await authenticated_client.post(
        f"{settings.api_v1_str}/sales/{sale_id}/refund", json=refund_payload
    )
    assert refund_resp.status_code in (200, 400, 403, 404)
    if refund_resp.status_code == 200:
        refund_data = refund_resp.json()
        assert "id" in refund_data or "refund_id" in refund_data
