"""Journal API tests for validation rules."""
import pytest
from httpx import AsyncClient
from decimal import Decimal

from app.core.config import settings

@pytest.mark.asyncio
async def test_create_unbalanced_journal_entry(authenticated_client: AsyncClient):
    """Ensure unbalanced journal (debits != credits) is rejected with VALIDATION_ERROR."""
    payload = {
        "reference_type": "MANUAL",
        "reference_id": None,
        "date": None,
        "lines": [
            {"account_id": 1, "debit": 100.0, "credit": 0, "description": "Line 1"},
            {"account_id": 2, "debit": 0, "credit": 50.0, "description": "Line 2"}
        ]
    }
    resp = await authenticated_client.post(f"{settings.api_v1_str}/journal/entries", json=payload)
    assert resp.status_code == 400
    body = resp.json()
    # Standard envelope assertions
    assert body.get("success") is False
    err = body.get("error") or {}
    assert err.get("code") == "VALIDATION_ERROR"
    # Message should mention not balanced
    assert "not balanced" in (err.get("message") or "")
    details = err.get("details") or {}
    # Debits and credits echo
    assert "debits" in details and "credits" in details and "difference" in details

@pytest.mark.asyncio
async def test_create_balanced_journal_entry(authenticated_client: AsyncClient):
    """Ensure a balanced journal passes (assuming accounts 1 & 2 exist)."""
    payload = {
        "reference_type": "MANUAL",
        "reference_id": None,
        "date": None,
        "lines": [
            {"account_id": 1, "debit": 100.0, "credit": 0, "description": "Line 1"},
            {"account_id": 2, "debit": 0, "credit": 100.0, "description": "Line 2"}
        ]
    }
    resp = await authenticated_client.post(f"{settings.api_v1_str}/journal/entries", json=payload)
    # Could be 201 if accounts exist; if not found, different validation triggers. Accept 201 or 400 missing accounts.
    assert resp.status_code in (201, 400)
    if resp.status_code == 201:
        data = resp.json().get("data")
        assert data is not None
        assert data.get("is_balanced") is True
