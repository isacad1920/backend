# SOFinance Backend Tests

This directory contains comprehensive tests for the SOFinance backend API.

## Directory Structure

```
tests/
├── __init__.py
├── conftest.py           # Pytest configuration and fixtures
├── api/                  # API endpoint tests
│   ├── test_auth.py      # Authentication endpoints
│   ├── test_users.py     # User management endpoints
│   ├── test_branches.py  # Branch management endpoints  
│   ├── test_products.py  # Product and category endpoints
│   ├── test_sales.py     # Sales management endpoints
│   ├── test_customers.py # Customer management endpoints
│   ├── test_financial.py # Financial analytics endpoints
│   ├── test_permissions.py # Permission management endpoints
│   └── test_misc.py      # Health, notifications, stock requests
├── unit/                 # Unit tests (to be implemented)
└── integration/          # Integration tests (to be implemented)
```

## Test Coverage

The test suite covers all major API endpoints:

### Authentication (`test_auth.py`)
- ✅ Login with valid/invalid credentials
- ✅ Token refresh
- ✅ Logout
- ✅ Password reset request

### User Management (`test_users.py`)  
- ✅ List users with pagination and filters
- ✅ Get user by ID
- ✅ Create/update/delete users
- ✅ User profile management
- ✅ Password changes
- ✅ User statistics

### Branch Management (`test_branches.py`)
- ✅ List branches with filters
- ✅ Get branch by ID  
- ✅ Create/update/delete branches
- ✅ Branch statistics

### Product & Category Management (`test_products.py`)
- ✅ List products/categories with filters
- ✅ Get product/category by ID
- ✅ Create/update/delete products/categories
- ✅ Stock adjustments
- ✅ Product statistics

### Sales Management (`test_sales.py`)
- ✅ List sales with filters
- ✅ Get sale by ID
- ✅ Create sales
- ✅ Process refunds
- ✅ Sales statistics and receipts

### Customer Management (`test_customers.py`)
- ✅ List customers with filters
- ✅ Get customer by ID
- ✅ Create/update/delete customers
- ✅ Customer purchase history
- ✅ Bulk operations

### Financial Analytics (`test_financial.py`)
- ✅ Financial summary and analytics
- ✅ Income statements and balance sheets
- ✅ Cash flow and tax reports
- ✅ Performance metrics and alerts

### Permission Management (`test_permissions.py`)
- ✅ Grant/revoke permissions
- ✅ User permission management
- ✅ Audit logs

### System Endpoints (`test_misc.py`)
- ✅ Health checks and system info
- ✅ Notifications
- ✅ Stock requests

## Running Tests

### Method 1: Using the test runner script

```bash
# Run all tests
python run_tests.py

# Run only API tests
python run_tests.py --type api

# Run with coverage
python run_tests.py --coverage

# Run specific test pattern
python run_tests.py --pattern "test_login"

# Run tests with specific marker
python run_tests.py --marker "auth"

# Verbose output
python run_tests.py --verbose
```

### Method 2: Using pytest directly

First install test dependencies:
```bash
pip install -r requirements-test.txt
```

Then run tests:
```bash
# Run all tests
pytest

# Run API tests only
pytest tests/api/

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/api/test_auth.py

# Run specific test method
pytest tests/api/test_auth.py::TestAuthenticationEndpoints::test_login_valid_credentials

# Run tests with markers
pytest -m "auth"
pytest -m "not slow"
```

## Test Configuration

Tests are configured via:
- `pytest.ini` - Pytest configuration
- `conftest.py` - Shared fixtures and test data
- `requirements-test.txt` - Test dependencies

## Fixtures

The `conftest.py` file provides several useful fixtures:

- `test_db` - Database connection for tests
- `async_client` - Async HTTP client for API calls
- `authenticated_client` - Pre-authenticated client with JWT token
- `admin_user`, `cashier_user` - Test user accounts
- `test_branch`, `test_category`, `test_product`, `test_customer` - Test data

## Authentication

Most API tests use the `authenticated_client` fixture which automatically:
1. Creates a test user if needed
2. Logs in to get JWT tokens  
3. Sets Authorization header on the client

## Test Data

Test data constants are defined in `conftest.py`:
- `TEST_USER_DATA` - Sample user data
- `TEST_BRANCH_DATA` - Sample branch data  
- `TEST_PRODUCT_DATA` - Sample product data
- `TEST_CUSTOMER_DATA` - Sample customer data

## Best Practices

1. **Isolation**: Each test should be independent and not rely on other tests
2. **Cleanup**: Use fixtures to create and cleanup test data
3. **Assertions**: Use specific assertions that test the expected behavior
4. **Error Cases**: Test both success and failure scenarios
5. **Authentication**: Test both authenticated and unauthenticated access
6. **Permissions**: Test different user roles and permissions

## Adding New Tests

To add tests for a new endpoint:

1. Create a new test file in the appropriate directory
2. Import required fixtures from `conftest.py`
3. Create test class with descriptive name
4. Add test methods following the naming convention `test_*`
5. Use appropriate HTTP methods and assertions
6. Test both success and error cases

Example:
```python
import pytest
from httpx import AsyncClient
from app.core.config import settings

class TestNewEndpoints:
    @pytest.mark.asyncio
    async def test_new_endpoint(self, authenticated_client: AsyncClient):
        response = await authenticated_client.get(f"{settings.api_v1_str}/new-endpoint")
        assert response.status_code == 200
        data = response.json()
        assert "expected_field" in data
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. They use:
- Async test support for FastAPI
- HTTP client testing without starting actual server
- Configurable test database
- Proper cleanup and isolation
