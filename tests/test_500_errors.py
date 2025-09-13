#!/usr/bin/env python3
"""
Quick service method validation script
"""
import os

import pytest
import requests

BASE_URL = "http://localhost:8000"

# Skip this script-style test unless a live server is running locally
pytestmark = pytest.mark.skipif(
    os.getenv("LIVE_SERVER") not in ("1", "true", "TRUE"),
    reason="Requires live server at http://localhost:8000",
)

def get_auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/token",
        data={"username": "demo@sofinance.com", "password": "demo123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Auth failed: {response.status_code} - {response.text}")
        return None

def test_endpoints_for_500_errors():
    """Test endpoints that commonly have 500 errors"""
    token = get_auth_token()
    if not token:
        print("❌ Cannot get auth token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test endpoints that might have service method issues
    test_cases = [
        ("GET", "/api/v1/users/me/profile", "User Profile"),
        ("GET", "/api/v1/users/", "User List"),
        ("GET", "/api/v1/customers/", "Customer List"),
        ("GET", "/api/v1/branches/", "Branch List"), 
        ("GET", "/api/v1/products/", "Product List"),
        ("GET", "/api/v1/sales/", "Sales List"),
        ("GET", "/api/v1/financial/dashboard", "Financial Dashboard"),
        ("GET", "/api/v1/inventory/stock-levels", "Inventory Stock Levels"),
    ]
    
    print("\n🔍 TESTING ENDPOINTS FOR 500 ERRORS")
    print("=" * 50)
    
    results = []
    for method, endpoint, name in test_cases:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            else:
                response = requests.request(method, f"{BASE_URL}{endpoint}", headers=headers)
            
            if response.status_code == 500:
                print(f"❌ {name}: 500 ERROR")
                print(f"   Response: {response.text[:200]}...")
                results.append(f"FAILED: {name} - 500 Error")
            elif response.status_code == 200:
                print(f"✅ {name}: OK")
                results.append(f"PASSED: {name}")
            else:
                print(f"⚠️  {name}: {response.status_code}")
                results.append(f"OTHER: {name} - {response.status_code}")
                
        except Exception as e:
            print(f"❌ {name}: Exception - {str(e)}")
            results.append(f"ERROR: {name} - {str(e)}")
    
    print(f"\n📊 SUMMARY: {len([r for r in results if r.startswith('PASSED')])} passed, {len([r for r in results if r.startswith('FAILED')])} failed")
    
    return results

if __name__ == "__main__":
    test_endpoints_for_500_errors()
