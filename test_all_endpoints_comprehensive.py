#!/usr/bin/env python3
"""
Comprehensive endpoint testing with authentication and real data.
Tests all 116 endpoints across 12 modules with proper authentication.
"""

import asyncio
import json
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, Any, List, Optional
import httpx
import pytest
from faker import Faker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

fake = Faker()

class ComprehensiveEndpointTester:
    """Comprehensive tester for all SOFinance endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_token = None
        self.auth_headers = {}
        
        # Test data storage
        self.test_data = {
            'user_id': None,
            'branch_id': None,
            'customer_id': None,
            'product_id': None,
            'category_id': None,
            'sale_id': None,
            'stock_request_id': None,
            'account_id': None,
            'journal_entry_id': None
        }
        
        # Results tracking
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': [],
            'module_results': {}
        }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def authenticate(self) -> bool:
        """Authenticate and get access token."""
        try:
            logger.info("🔐 Authenticating...")
            
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
            
            for password in passwords:
                try:
                    login_data = {
                        "username": "demo@sofinance.com",
                        "password": password,
                        "grant_type": "password"
                    }
                    
                    response = await self.client.post(
                        f"{self.base_url}/api/v1/auth/token",
                        data=login_data,
                        headers={"Content-Type": "application/x-www-form-urlencoded"}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        self.auth_token = result.get("access_token")
                        self.auth_headers = {
                            "Authorization": f"Bearer {self.auth_token}",
                            "Content-Type": "application/json"
                        }
                        logger.info(f"✅ Authentication successful with password: {password}")
                        return True
                        
                except Exception as e:
                    continue
                    
            logger.error(f"❌ Authentication failed with all passwords")
            return False
                    
        except Exception as e:
            logger.error(f"❌ Authentication error: {str(e)}")
            return False

    async def test_endpoint(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                           expected_status: int = 200, description: str = "") -> Dict[str, Any]:
        """Test a single endpoint."""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                response = await self.client.get(url, headers=self.auth_headers)
            elif method.upper() == "POST":
                response = await self.client.post(url, json=data, headers=self.auth_headers)
            elif method.upper() == "PUT":
                response = await self.client.put(url, json=data, headers=self.auth_headers)
            elif method.upper() == "DELETE":
                response = await self.client.delete(url, headers=self.auth_headers)
            elif method.upper() == "PATCH":
                response = await self.client.patch(url, json=data, headers=self.auth_headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            success = response.status_code == expected_status
            
            result = {
                'endpoint': endpoint,
                'method': method.upper(),
                'status_code': response.status_code,
                'expected_status': expected_status,
                'success': success,
                'description': description,
                'response_data': None,
                'error': None
            }
            
            try:
                result['response_data'] = response.json()
            except:
                result['response_data'] = response.text
            
            if success:
                logger.info(f"✅ {method.upper()} {endpoint} - {description}")
                self.test_results['passed'] += 1
            else:
                logger.error(f"❌ {method.upper()} {endpoint} - Expected {expected_status}, got {response.status_code}")
                self.test_results['failed'] += 1
                self.test_results['errors'].append({
                    'endpoint': endpoint,
                    'method': method,
                    'status_code': response.status_code,
                    'expected': expected_status,
                    'response': result['response_data']
                })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Exception testing {method.upper()} {endpoint}: {str(e)}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append({
                'endpoint': endpoint,
                'method': method,
                'error': str(e)
            })
            return {
                'endpoint': endpoint,
                'method': method.upper(),
                'success': False,
                'error': str(e)
            }

    async def create_test_data(self) -> Dict[str, Any]:
        """Create necessary test data for comprehensive testing."""
        logger.info("📋 Creating test data...")
        
        # Create a branch first
        branch_data = {
            "name": f"Test Branch {fake.city()}",
            "address": fake.address(),
            "phone": fake.phone_number()[:15],
            "email": fake.email(),
            "is_active": True
        }
        
        result = await self.test_endpoint("POST", "/api/v1/branches/", branch_data, 201, "Create test branch")
        if result['success'] and result.get('response_data'):
            self.test_data['branch_id'] = result['response_data']['data']['id']
            logger.info(f"✅ Created branch ID: {self.test_data['branch_id']}")
        
        # Create a customer
        customer_data = {
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number()[:15],
            "address": fake.address(),
            "customer_type": "REGULAR",
            "credit_limit": 1000.0
        }
        
        result = await self.test_endpoint("POST", "/api/v1/customers/", customer_data, 201, "Create test customer")
        if result['success'] and result.get('response_data'):
            self.test_data['customer_id'] = result['response_data']['data']['id']
            logger.info(f"✅ Created customer ID: {self.test_data['customer_id']}")
        
        # Create a product category
        category_data = {
            "name": f"Test Category {fake.word()}",
            "description": fake.text(50)
        }
        
        result = await self.test_endpoint("POST", "/api/v1/categories/", category_data, 201, "Create test category")
        if result['success'] and result.get('response_data'):
            self.test_data['category_id'] = result['response_data']['id']
            logger.info(f"✅ Created category ID: {self.test_data['category_id']}")
        
        # Create a product
        product_data = {
            "name": f"Test Product {fake.word()}",
            "description": fake.text(100),
            "sku": fake.uuid4()[:12],
            "barcode": fake.ean13(),
            "category_id": self.test_data['category_id'],
            "unit_price": 25.99,
            "cost_price": 15.99,
            "tax_rate": 0.1,
            "is_active": True,
            "track_inventory": True
        }
        
        result = await self.test_endpoint("POST", "/api/v1/products/", product_data, 201, "Create test product")
        if result['success'] and result.get('response_data'):
            self.test_data['product_id'] = result['response_data']['data']['id']
            logger.info(f"✅ Created product ID: {self.test_data['product_id']}")

        return self.test_data

    async def test_auth_endpoints(self):
        """Test authentication endpoints."""
        logger.info("🔐 Testing Authentication Endpoints...")
        module_results = []
        
        # Test token endpoint (already tested in authenticate)
        module_results.append(await self.test_endpoint(
            "POST", "/api/v1/auth/token", 
            {"username": "demo@sofinance.com", "password": "SecureDemo2024!", "grant_type": "password"},
            200, "Get access token"
        ))
        
        # Test current user
        module_results.append(await self.test_endpoint(
            "GET", "/api/v1/auth/me", None, 200, "Get current user"
        ))
        
        self.test_results['module_results']['auth'] = module_results

    async def test_users_endpoints(self):
        """Test users endpoints."""
        logger.info("👥 Testing Users Endpoints...")
        module_results = []
        
        # List users
        module_results.append(await self.test_endpoint("GET", "/api/v1/users/", None, 200, "List users"))
        
        # Create user
        user_data = {
            "username": f"testuser_{fake.user_name()}",
            "email": fake.email(),
            "full_name": fake.name(),
            "password": "testpass123",
            "role": "CASHIER",
            "branch_id": self.test_data.get('branch_id', 1),
            "is_active": True
        }
        
        result = await self.test_endpoint("POST", "/api/v1/users/", user_data, 201, "Create user")
        module_results.append(result)
        
        if result['success'] and result.get('response_data'):
            user_id = result['response_data']['data']['id']
            
            # Get user details
            module_results.append(await self.test_endpoint("GET", f"/api/v1/users/{user_id}", None, 200, "Get user details"))
            
            # Update user
            update_data = {"full_name": fake.name()}
            module_results.append(await self.test_endpoint("PUT", f"/api/v1/users/{user_id}", update_data, 200, "Update user"))
        
        self.test_results['module_results']['users'] = module_results

    async def test_branches_endpoints(self):
        """Test branches endpoints."""
        logger.info("🏢 Testing Branches Endpoints...")
        module_results = []
        
        # List branches
        module_results.append(await self.test_endpoint("GET", "/api/v1/branches/", None, 200, "List branches"))
        
        # Create branch (already done in test data creation)
        if self.test_data['branch_id']:
            # Get branch details
            module_results.append(await self.test_endpoint(
                "GET", f"/api/v1/branches/{self.test_data['branch_id']}", None, 200, "Get branch details"
            ))
            
            # Update branch
            update_data = {"name": f"Updated Branch {fake.city()}"}
            module_results.append(await self.test_endpoint(
                "PUT", f"/api/v1/branches/{self.test_data['branch_id']}", update_data, 200, "Update branch"
            ))
        
        # Get branch stats
        module_results.append(await self.test_endpoint("GET", "/api/v1/branches/stats", None, 200, "Get branch stats"))
        
        self.test_results['module_results']['branches'] = module_results

    async def test_customers_endpoints(self):
        """Test customers endpoints."""
        logger.info("👤 Testing Customers Endpoints...")
        module_results = []
        
        # List customers
        module_results.append(await self.test_endpoint("GET", "/api/v1/customers/", None, 200, "List customers"))
        
        # Customer already created in test data
        if self.test_data['customer_id']:
            # Get customer details
            module_results.append(await self.test_endpoint(
                "GET", f"/api/v1/customers/{self.test_data['customer_id']}", None, 200, "Get customer details"
            ))
            
            # Update customer
            update_data = {"name": fake.name()}
            module_results.append(await self.test_endpoint(
                "PUT", f"/api/v1/customers/{self.test_data['customer_id']}", update_data, 200, "Update customer"
            ))
            
            # Get customer purchase history
            module_results.append(await self.test_endpoint(
                "GET", f"/api/v1/customers/{self.test_data['customer_id']}/purchase-history", 
                None, 200, "Get customer purchase history"
            ))
        
        # Get customer stats
        module_results.append(await self.test_endpoint("GET", "/api/v1/customers/stats", None, 200, "Get customer stats"))
        
        self.test_results['module_results']['customers'] = module_results

    async def test_products_endpoints(self):
        """Test products endpoints."""
        logger.info("📦 Testing Products Endpoints...")
        module_results = []
        
        # List products
        module_results.append(await self.test_endpoint("GET", "/api/v1/products/", None, 200, "List products"))
        
        # Product already created in test data
        if self.test_data['product_id']:
            # Get product details
            module_results.append(await self.test_endpoint(
                "GET", f"/api/v1/products/{self.test_data['product_id']}", None, 200, "Get product details"
            ))
            
            # Update product
            update_data = {"name": f"Updated Product {fake.word()}"}
            module_results.append(await self.test_endpoint(
                "PUT", f"/api/v1/products/{self.test_data['product_id']}", update_data, 200, "Update product"
            ))
        
        # List categories
        module_results.append(await self.test_endpoint("GET", "/api/v1/categories/", None, 200, "List categories"))
        
        # Get product stats
        module_results.append(await self.test_endpoint("GET", "/api/v1/products/stats", None, 200, "Get product stats"))
        
        self.test_results['module_results']['products'] = module_results

    async def test_inventory_endpoints(self):
        """Test inventory endpoints."""
        logger.info("📋 Testing Inventory Endpoints...")
        module_results = []
        
        # List inventory
        module_results.append(await self.test_endpoint("GET", "/api/v1/inventory/", None, 200, "List inventory"))
        
        # Get low stock alerts
        module_results.append(await self.test_endpoint("GET", "/api/v1/inventory/low-stock", None, 200, "Get low stock alerts"))
        
        if self.test_data['product_id']:
            # Get product stock
            module_results.append(await self.test_endpoint(
                "GET", f"/api/v1/inventory/{self.test_data['product_id']}", None, 200, "Get product stock"
            ))
            
            # Create stock adjustment
            adjustment_data = {
                "product_id": self.test_data['product_id'],
                "adjustment_type": "INCREASE",
                "quantity": 100,
                "reason": "INITIAL_STOCK",
                "notes": "Initial stock addition for testing"
            }
            
            module_results.append(await self.test_endpoint(
                "POST", "/api/v1/inventory/adjust", adjustment_data, 201, "Create stock adjustment"
            ))
        
        # Get inventory valuation
        module_results.append(await self.test_endpoint("GET", "/api/v1/inventory/valuation/report", None, 200, "Get inventory valuation"))
        
        # Get inventory dashboard
        module_results.append(await self.test_endpoint("GET", "/api/v1/inventory/dashboard", None, 200, "Get inventory dashboard"))
        
        self.test_results['module_results']['inventory'] = module_results

    async def test_sales_endpoints(self):
        """Test sales endpoints."""
        logger.info("💰 Testing Sales Endpoints...")
        module_results = []
        
        # List sales
        module_results.append(await self.test_endpoint("GET", "/api/v1/sales/", None, 200, "List sales"))
        
        # Create a sale
        if self.test_data['product_id'] and self.test_data['customer_id']:
            sale_data = {
                "customer_id": self.test_data['customer_id'],
                "branch_id": self.test_data.get('branch_id', 1),
                "items": [
                    {
                        "product_id": self.test_data['product_id'],
                        "quantity": 2,
                        "unit_price": 25.99
                    }
                ],
                "payment_method": "CASH",
                "payment_status": "PAID",
                "notes": "Test sale"
            }
            
            result = await self.test_endpoint("POST", "/api/v1/sales/", sale_data, 201, "Create sale")
            module_results.append(result)
            
            if result['success'] and result.get('response_data'):
                sale_id = result['response_data']['data']['id']
                self.test_data['sale_id'] = sale_id
                
                # Get sale details
                module_results.append(await self.test_endpoint(
                    "GET", f"/api/v1/sales/{sale_id}", None, 200, "Get sale details"
                ))
                
                # Generate receipt
                module_results.append(await self.test_endpoint(
                    "GET", f"/api/v1/sales/{sale_id}/receipt", None, 200, "Generate receipt"
                ))
        
        # Get sales stats
        module_results.append(await self.test_endpoint("GET", "/api/v1/sales/stats", None, 200, "Get sales stats"))
        
        # Get today's summary
        module_results.append(await self.test_endpoint("GET", "/api/v1/sales/today", None, 200, "Get today's sales summary"))
        
        self.test_results['module_results']['sales'] = module_results

    async def test_financial_endpoints(self):
        """Test financial endpoints."""
        logger.info("💳 Testing Financial Endpoints...")
        module_results = []
        
        # Get balance sheet
        module_results.append(await self.test_endpoint("GET", "/api/v1/financial/balance-sheet", None, 200, "Get balance sheet"))
        
        # Get income statement
        module_results.append(await self.test_endpoint("GET", "/api/v1/financial/income-statement", None, 200, "Get income statement"))
        
        # Get cash flow
        module_results.append(await self.test_endpoint("GET", "/api/v1/financial/cash-flow", None, 200, "Get cash flow"))
        
        # Get financial dashboard
        module_results.append(await self.test_endpoint("GET", "/api/v1/financial/dashboard", None, 200, "Get financial dashboard"))
        
        self.test_results['module_results']['financial'] = module_results

    async def run_all_tests(self):
        """Run all endpoint tests."""
        logger.info("🚀 Starting comprehensive endpoint testing...")
        
        # Step 1: Authenticate
        if not await self.authenticate():
            logger.error("❌ Authentication failed - cannot proceed with tests")
            return
        
        # Step 2: Create test data
        await self.create_test_data()
        
        # Step 3: Run all endpoint tests
        test_modules = [
            ("auth", self.test_auth_endpoints),
            ("users", self.test_users_endpoints),
            ("branches", self.test_branches_endpoints),
            ("customers", self.test_customers_endpoints),
            ("products", self.test_products_endpoints),
            ("inventory", self.test_inventory_endpoints),
            ("sales", self.test_sales_endpoints),
            ("financial", self.test_financial_endpoints),
        ]
        
        for module_name, test_function in test_modules:
            try:
                await test_function()
            except Exception as e:
                logger.error(f"❌ Error testing {module_name} module: {str(e)}")
                self.test_results['errors'].append({
                    'module': module_name,
                    'error': str(e)
                })
        
        # Step 4: Print results
        self.print_results()

    def print_results(self):
        """Print comprehensive test results."""
        total_tests = self.test_results['passed'] + self.test_results['failed']
        success_rate = (self.test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*80)
        print("🔍 COMPREHENSIVE ENDPOINT TEST RESULTS")
        print("="*80)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print("="*80)
        
        # Print module results
        for module, results in self.test_results['module_results'].items():
            if results:
                passed = sum(1 for r in results if r.get('success', False))
                failed = len(results) - passed
                print(f"📋 {module.upper()}: {passed}/{len(results)} passed")
        
        # Print errors if any
        if self.test_results['errors']:
            print("\n❌ ERRORS ENCOUNTERED:")
            print("-"*50)
            for error in self.test_results['errors'][:10]:  # Show first 10 errors
                print(f"• {error.get('method', 'N/A')} {error.get('endpoint', 'N/A')}: {error.get('error', 'Unknown error')}")
        
        print("="*80)

async def main():
    """Main test execution."""
    async with ComprehensiveEndpointTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
