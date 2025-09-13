#!/usr/bin/env python3
"""Quick local smoke test for POS sale creation.

Logs in as demo user, fetches first stock item, and posts a sale using stock_id.
"""
import os
import requests

BASE = os.getenv("BASE_URL", "http://127.0.0.1:8000")

def main():
	r = requests.post(f"{BASE}/api/v1/auth/login", json={"email":"demo@sofinance.com","password":"DemoPassword123!"})
	r.raise_for_status()
	token = r.json().get("access_token")
	headers = {"Authorization": f"Bearer {token}"}

	s = requests.get(f"{BASE}/api/v1/inventory/stock-levels", headers=headers)
	s.raise_for_status()
	items = s.json()
	assert items, "No stock items found"
	first = items[0]
	stock_id = first.get("id")
	unit_price = first.get("unit_price") or first.get("unitPrice") or "1.00"

	payload = {
		# branch_id intentionally omitted to test inference from stock
		"payment_type": "FULL",
		"discount": "0",
		"customer_id": None,
		"total_amount": str(unit_price),
		"user_id": 0,
		"items": [
			{"stock_id": stock_id, "quantity": 1, "price": str(unit_price), "subtotal": str(unit_price)}
		]
	}
	print("Posting sale payload:", payload)
	sale = requests.post(f"{BASE}/api/v1/sales/", json=payload, headers=headers)
	print("Status:", sale.status_code)
	print("Body:", sale.text)
	sale.raise_for_status()

if __name__ == "__main__":
	main()

