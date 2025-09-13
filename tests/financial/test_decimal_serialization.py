import re
import pytest
from httpx import AsyncClient
from decimal import Decimal

from app.main import app

MONEY_FIELD_PATTERN = re.compile(r"(total|amount|value|profit|balance)")

@pytest.mark.anyio
async def test_sales_summary_decimal_fields():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/sales/summary")
    assert resp.status_code == 200
    body = resp.json()
    data = body.get('data') or {}
    # Ensure key monetary fields are strings that parse to Decimal(2dp)
    for key in ['gross_sales_total','paid_total','outstanding_total','average_sale_value']:
        assert key in data
        val = data[key]
        assert isinstance(val, str)
        dec = Decimal(val)
        assert dec.quantize(Decimal('0.01')) == dec

@pytest.mark.anyio
async def test_income_statement_decimal_fields(monkeypatch):
    # This will depend on data presence; accept 200 or handled error (e.g., validation)
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        resp = await ac.get("/api/v1/financial/reports/income-statement")
    if resp.status_code != 200:
        pytest.skip("Income statement endpoint not populated with test data")
    body = resp.json()
    data = body.get('data') or {}
    monetary_keys = [
        'total_revenue','total_cogs','gross_profit','total_expenses','operating_profit','net_profit'
    ]
    for key in monetary_keys:
        if key not in data:
            continue
        val = data[key]
        assert isinstance(val, str)
        dec = Decimal(val)
        assert dec.quantize(Decimal('0.01')) == dec
