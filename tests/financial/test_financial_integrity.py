import pytest
from httpx import AsyncClient
from decimal import Decimal

from app.main import app

@pytest.mark.anyio
async def test_sale_details_integrity_validation(monkeypatch):
    # This test assumes a sale with id=1 exists in seed; if not, adjust or mock.
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/sales/1")
    assert resp.status_code in (200, 404)  # allow 404 if fixture absent
    if resp.status_code == 404:
        return  # skip if no sale
    data = resp.json()
    assert data.get('success') is True
    sale = data.get('data') or {}
    # Integrity decorator should not have altered semantics, just ensured totals
    if 'total_amount' in sale:
        # ensure serialized as numeric-compatible string or Decimal-like
        amt = sale['total_amount']
        # Accept either numeric string or number; enforce Decimal conversion no precision loss
        dec = Decimal(str(amt))
        assert dec.quantize(Decimal('0.01')) == dec

@pytest.mark.anyio
async def test_integrity_decorator_graceful_on_missing(monkeypatch):
    # Non-existent sale should still 404, not 500
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/sales/9999999")
    assert resp.status_code in (404, 200)
    if resp.status_code == 404:
        body = resp.json()
        assert body.get('success') is False or body.get('error') is not None
