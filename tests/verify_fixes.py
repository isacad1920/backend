#!/usr/bin/env python3
"""
Verification script to test all the authentication and authorization fixes
"""
import sys

import requests

BASE_URL = "http://localhost:8000"

def test_authentication():
    """Test authentication endpoint"""
    print("🔐 Testing Authentication...")
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", 
                           json={"email": "demo@sofinance.com", "password": "demo123"})
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Authentication successful")
        return data.get('access_token')
    else:
        print(f"❌ Authentication failed: {response.status_code}")
        return None

def test_protected_endpoint(token, endpoint_name, endpoint_path):
    """Test a protected endpoint"""
    print(f"🧪 Testing {endpoint_name}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}{endpoint_path}", headers=headers)
    
    if response.status_code == 200:
        print(f"✅ {endpoint_name} endpoint working")
        return True
    else:
        print(f"❌ {endpoint_name} endpoint failed: {response.status_code}")
        if response.status_code == 500:
            try:
                error_detail = response.json().get('detail', 'Unknown error')
                print(f"   Error: {error_detail}")
            except Exception:
                print(f"   Error: {response.text[:100]}")
        return False

def main():
    print("🚀 Starting SOFinance API Fix Verification")
    print("=" * 50)
    
    # Test authentication
    token = test_authentication()
    if not token:
        print("❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # Test protected endpoints
    endpoints = [
        ("Users", "/api/v1/users/"),
        ("Branches", "/api/v1/branches/"),
        ("Products", "/api/v1/products/"),
        ("Customers", "/api/v1/customers/"),
    ]
    
    success_count = 0
    for name, path in endpoints:
        if test_protected_endpoint(token, name, path):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {success_count}/{len(endpoints)} endpoints working")
    
    if success_count == len(endpoints):
        print("🎉 All fixes verified successfully!")
        print("\n✅ Fixed Issues:")
        print("   - Permission system dependency errors")
        print("   - Prisma query field naming (created_at → createdAt)")
        print("   - Service method name mismatches")
        print("   - Schema type conversion (int → string for IDs)")
        print("   - require_role function parameter handling")
        return 0
    else:
        print("⚠️ Some endpoints still have issues")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)
