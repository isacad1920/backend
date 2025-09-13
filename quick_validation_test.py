#!/usr/bin/env python3
"""
Quick validation script to test authentication and core endpoints after fixes.
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_auth_and_endpoints():
    """Test authentication and a few core endpoints to validate fixes."""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🔍 Testing Authentication with Different Passwords...")
        
        # List of possible passwords to try
        passwords = [
            "demo123", 
            "demo23",
            "SecureDemo2024!",
            "admin123", 
            "password",
            "demo",
            "test123"
        ]
        
        token = None
        auth_headers = {}
        
        # Try different passwords
        for password in passwords:
            try:
                print(f"   Trying password: {password}")
                response = await client.post(
                    f"{BASE_URL}/api/v1/auth/token",
                    data={
                        "username": "demo@sofinance.com",
                        "password": password,
                        "grant_type": "password"
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    token = result.get("access_token")
                    auth_headers = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                    print(f"   ✅ SUCCESS with password: {password}")
                    break
                else:
                    print(f"   ❌ Failed: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        if not token:
            print("❌ Could not authenticate with any password!")
            return
        
        print(f"\n🎉 Authenticated successfully! Testing endpoints...")
        
        # Test some endpoints that were failing
        test_endpoints = [
            ("GET", "/api/v1/stock-requests/", "Stock Requests List"),
            ("GET", "/api/v1/notifications/", "Notifications List"),
            ("GET", "/api/v1/financial/balance-sheet", "Balance Sheet"),
            ("GET", "/api/v1/branches/", "Branches List"),
            ("GET", "/api/v1/products/", "Products List"),
        ]
        
        results = {"passed": 0, "failed": 0}
        
        for method, endpoint, description in test_endpoints:
            try:
                if method == "GET":
                    response = await client.get(f"{BASE_URL}{endpoint}", headers=auth_headers)
                
                if response.status_code in [200, 201]:
                    print(f"✅ {description}: {response.status_code}")
                    results["passed"] += 1
                else:
                    print(f"❌ {description}: {response.status_code} - {response.text[:100]}")
                    results["failed"] += 1
                    
            except Exception as e:
                print(f"❌ {description}: Exception - {str(e)}")
                results["failed"] += 1
        
        total = results["passed"] + results["failed"]
        success_rate = (results["passed"] / total * 100) if total > 0 else 0
        
        print(f"\n📊 QUICK VALIDATION RESULTS:")
        print(f"   ✅ Passed: {results['passed']}")
        print(f"   ❌ Failed: {results['failed']}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate > 50:
            print("🎉 Major improvements! Most endpoints are working.")
        else:
            print("⚠️  Still need more fixes, but progress made!")

if __name__ == "__main__":
    asyncio.run(test_auth_and_endpoints())
