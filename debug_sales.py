#!/usr/bin/env python3

import json

import requests


def test_sales_endpoint():
    """Test sales endpoint with detailed error reporting."""
    
    try:
        # Step 1: Authenticate
        print("🔑 Authenticating...")
        auth_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json={
                "email": "demo@sofinance.com",
                "password": "demo123"
            }
        )
        
        if auth_response.status_code != 200:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            print(f"Response: {auth_response.text}")
            return
            
        auth_data = auth_response.json()
        token = auth_data.get('data', {}).get('token')
        if not token:
            token = auth_data.get('access_token')  # Try alternative token field
            
        if not token:
            print(f"❌ No token in response: {json.dumps(auth_data, indent=2)}")
            return
            
        print("✅ Authentication successful")
        
        # Step 2: Test sales endpoint
        print("\n🔍 Testing sales endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        
        sales_response = requests.get(
            "http://localhost:8000/api/v1/sales/",
            headers=headers
        )
        
        print(f"Status Code: {sales_response.status_code}")
        print(f"Response: {sales_response.text}")
        
        if sales_response.status_code == 500:
            try:
                error_data = sales_response.json()
                print("\n🔍 Error Details:")
                print(json.dumps(error_data, indent=2))
            except:
                print("Could not parse error JSON")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")

if __name__ == "__main__":
    test_sales_endpoint()
