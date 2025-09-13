#!/usr/bin/env python3
"""
Simple export test script to test the financial report export functionality.
"""

import json
import os

import pytest
import requests

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
        with open(TOKEN_FILE) as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Token file {TOKEN_FILE} not found!")
        return None

def test_export(report_type, format_type="json"):
    """Test exporting a financial report."""
    token = get_token()
    if not token:
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test export endpoint
    export_url = f"{BASE_URL}/api/v1/financial/export/{report_type}"
    params = {
        "format": format_type,
        "start_date": "2025-01-01",
        "end_date": "2025-12-31"
    }
    
    try:
        print(f"\n=== Testing {report_type} export as {format_type} ===")
        response = requests.get(export_url, headers=headers, params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS ✅")
            print(f"Export info: {json.dumps(data, indent=2, default=str)}")
            return data
        else:
            print("FAILED ❌")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None

def main():
    """Test export functionality."""
    print("🏪 SOFinance - Financial Report Export Test")
    print("=" * 60)
    
    # Test different report types and formats
    test_cases = [
        ("income-statement", "json"),
        ("balance-sheet", "json"),
        ("cash-flow", "csv"),
        ("tax-report", "excel")
    ]
    
    results = {}
    for report_type, format_type in test_cases:
        result = test_export(report_type, format_type)
        results[f"{report_type}-{format_type}"] = result is not None
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 EXPORT TEST SUMMARY")
    print("=" * 60)
    
    for test_name, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{test_name.upper().replace('-', ' ')}: {status}")
    
    total_working = sum(results.values())
    print(f"\nTotal Working: {total_working}/{len(test_cases)}")
    
    if total_working == len(test_cases):
        print("\n🎉 ALL EXPORT TESTS PASSED! 🎉")
        print("Financial report export functionality is working!")
    else:
        print(f"\n⚠️  {len(test_cases) - total_working} test(s) failed.")

if __name__ == "__main__":
    main()
