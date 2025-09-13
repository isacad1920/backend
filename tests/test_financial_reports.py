#!/usr/bin/env python3
"""
Test script for financial reports functionality.
Tests all four financial report endpoints to ensure they're working properly.
"""

import requests
import json
from datetime import date, datetime
import os
import pytest

# Skip this script-style test unless a live server is running locally
pytestmark = pytest.mark.skipif(
    os.getenv("LIVE_SERVER") not in ("1", "true", "TRUE"),
    reason="Requires live server at http://localhost:8000",
)

# Configuration
BASE_URL = "http://localhost:8000"
TOKEN_FILE = "working_token.txt"

def get_token():
    """Read the authentication token from file."""
    try:
        with open(TOKEN_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Token file {TOKEN_FILE} not found!")
        return None

def test_financial_report(endpoint, params=None):
    """Test a financial report endpoint."""
    token = get_token()
    if not token:
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{BASE_URL}/api/v1/financial/reports/{endpoint}"
    
    try:
        response = requests.get(url, headers=headers, params=params or {})
        print(f"\n=== {endpoint.upper()} REPORT ===")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS ✅")
            print(f"Response: {json.dumps(data, indent=2, default=str)}")
            return data
        else:
            print("FAILED ❌")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None

def main():
    """Run all financial report tests."""
    print("🏪 SOFinance - Financial Reports Test")
    print("=" * 50)
    
    # Test parameters
    test_params = {
        "start_date": "2025-01-01",
        "end_date": "2025-12-31"
    }
    
    balance_params = {
        "as_of_date": "2025-09-07"
    }
    
    reports = [
        ("income-statement", test_params),
        ("balance-sheet", balance_params),
        ("cash-flow", test_params),
        ("tax-report", test_params)
    ]
    
    results = {}
    for endpoint, params in reports:
        result = test_financial_report(endpoint, params)
        results[endpoint] = result is not None
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FINANCIAL REPORTS SUMMARY")
    print("=" * 50)
    
    for report_name, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{report_name.upper().replace('-', ' ')}: {status}")
    
    total_working = sum(results.values())
    print(f"\nTotal Reports Working: {total_working}/4")
    
    if total_working == 4:
        print("\n🎉 ALL FINANCIAL REPORTS ARE WORKING! 🎉")
        print("The 'Report generation functionality coming soon' has been successfully implemented!")
    else:
        print(f"\n⚠️  {4 - total_working} report(s) need attention.")

if __name__ == "__main__":
    main()
