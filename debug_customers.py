#!/usr/bin/env python3

import requests
import json

def test_customers_endpoint():
    """Test customers endpoint with detailed error reporting."""
    
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
            
        print(f"✅ Authentication successful")
        
        # Step 2: Test customers endpoint
        print("\n🔍 Testing customers endpoint...")
        headers = {"Authorization": f"Bearer {token}"}
        
        customers_response = requests.get(
            "http://localhost:8000/api/v1/customers/",
            headers=headers
        )
        
        print(f"Status Code: {customers_response.status_code}")
        print(f"Response: {customers_response.text}")
        
        if customers_response.status_code == 500:
            try:
                error_data = customers_response.json()
                print(f"\n🔍 Error Details:")
                print(json.dumps(error_data, indent=2))
            except:
                print("Could not parse error JSON")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")

if __name__ == "__main__":
    test_customers_endpoint()
