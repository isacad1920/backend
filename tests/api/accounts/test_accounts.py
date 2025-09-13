import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def create_account(client: AsyncClient, name: str = "Cash Box", type_: str = "ASSET"):
    resp = await client.post("/api/v1/accounts/", json={
        "name": name,
        "type": type_,
        "currency": "USD"
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    return data

async def test_account_crud_flow(authenticated_client: AsyncClient):
    # Create
    created = await create_account(authenticated_client, name="Test Revenue", type_="REVENUE")
    acc_id = created["id"]

    # Get
    r = await authenticated_client.get(f"/api/v1/accounts/{acc_id}")
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "Test Revenue"

    # List
    r = await authenticated_client.get("/api/v1/accounts/?limit=5")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert any(item["id"] == acc_id for item in body["data"]["items"]) or any(item.get("id") == acc_id for item in body["data"].get("items", []))

    # Update
    r = await authenticated_client.patch(f"/api/v1/accounts/{acc_id}", json={"name": "Updated Revenue"})
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "Updated Revenue"

    # Close
    r = await authenticated_client.post(f"/api/v1/accounts/{acc_id}/close")
    assert r.status_code == 200
    assert r.json()["data"]["active"] is False

async def test_inactive_account_rejects_journal(authenticated_client: AsyncClient):
    # Create + close
    acc = await create_account(authenticated_client, name="Temp Asset", type_="ASSET")
    acc_id = acc["id"]
    await authenticated_client.post(f"/api/v1/accounts/{acc_id}/close")

    # Create a second active account for balancing entry
    active_acc = await create_account(authenticated_client, name="Active Asset", type_="ASSET")
    active_id = active_acc["id"]

    # Attempt journal entry using closed account
    payload = {
        "reference_type": "Manual",
        "reference_id": 0,
        "lines": [
            {"account_id": acc_id, "debit": 100, "credit": 0, "description": "Inactive test"},
            {"account_id": active_id, "debit": 0, "credit": 100, "description": "Active balancing"}
        ]
    }
    r = await authenticated_client.post("/api/v1/journal/entries", json=payload)
    assert r.status_code == 400
    assert "Inactive accounts" in r.text or "inactive" in r.text.lower()
