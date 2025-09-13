"""
Pytest configuration and fixtures for SOFinance tests.
"""
import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.core.config import settings
from app.main import app
from generated.prisma import Prisma


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[Prisma, None]:
    """Create test database connection."""
    prisma = Prisma()
    await prisma.connect()
    yield prisma
    await prisma.disconnect()


@pytest.fixture(scope="session")  
def test_client() -> Generator[TestClient, None, None]:
    """Create test client."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    # Use ASGI transport to test app directly without server
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
async def authenticated_client(async_client: AsyncClient, test_db: Prisma) -> AsyncGenerator[AsyncClient, None]:
    """Create authenticated client with valid JWT token without mutating the shared client."""
    # Ensure test user exists
    test_user = await test_db.user.find_first(where={"email": "test@sofinance.com"})
    if not test_user:
        from app.modules.users.schema import UserCreateSchema
        from app.modules.users.service import create_user_service
        user_service = create_user_service(test_db)
        user_data = UserCreateSchema(
            email="test@sofinance.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="User",
            role="ADMIN"
        )
        test_user = await user_service.create_user(user_data)

    # Login using the shared client (no header mutation)
    login_response = await async_client.post(
        f"{settings.api_v1_str}/auth/login",
        json={
            "email": "test@sofinance.com",
            "password": "TestPassword123!"
        }
    )
    access_token = None
    if login_response.status_code == 200:
        token_data = login_response.json()
        # Support standardized envelope (token inside data)
        if "access_token" in token_data:
            access_token = token_data.get("access_token")
        else:
            inner = token_data.get("data") or {}
            access_token = inner.get("access_token")

    # Create an isolated client with its own headers to avoid leaking Authorization
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    headers = {}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    new_client = AsyncClient(transport=transport, base_url="http://testserver", headers=headers)
    try:
        yield new_client
    finally:
        await new_client.aclose()


@pytest.fixture
async def system_manage_client(async_client: AsyncClient, test_db: Prisma) -> AsyncGenerator[AsyncClient, None]:
    """Authenticated client guaranteed to have system:manage permission (ADMIN).

    Reuses the shared event loop and ASGI transport to avoid cross-loop issues seen in some tests.
    """
    admin = await test_db.user.find_first(where={"email": "sysadmin@sofinance.com"})
    if not admin:
        from app.modules.users.schema import UserCreateSchema
        from app.modules.users.service import create_user_service
        user_service = create_user_service(test_db)
        admin = await user_service.create_user(UserCreateSchema(
            email="sysadmin@sofinance.com",
            password="SysAdminPassword123!",
            first_name="Sys",
            last_name="Admin",
            role="ADMIN",
        ))
    login_response = await async_client.post(
        f"{settings.api_v1_str}/auth/login",
        json={"email": "sysadmin@sofinance.com", "password": "SysAdminPassword123!"}
    )
    token = None
    if login_response.status_code == 200:
        token_json = login_response.json()
        token = token_json.get("access_token") or (token_json.get("data") or {}).get("access_token")
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    client = AsyncClient(transport=transport, base_url="http://testserver", headers=headers)
    try:
        yield client
    finally:
        await client.aclose()


# Compatibility aliases expected by some test files
@pytest.fixture
async def client(async_client: AsyncClient) -> AsyncGenerator[AsyncClient, None]:
    """Alias for unauthenticated async client."""
    yield async_client


@pytest.fixture
async def auth_client(authenticated_client: AsyncClient) -> AsyncGenerator[AsyncClient, None]:
    """Alias for authenticated async client."""
    yield authenticated_client


@pytest.fixture
async def admin_user(test_db: Prisma) -> dict:
    """Create or get admin user for tests."""
    admin_user = await test_db.user.find_first(where={"email": "admin@sofinance.com"})
    
    if not admin_user:
        from app.modules.users.schema import UserCreateSchema
        from app.modules.users.service import create_user_service
        
        user_service = create_user_service(test_db)
        user_data = UserCreateSchema(
            email="admin@sofinance.com",
            password="AdminPassword123!",
            first_name="Admin",
            last_name="User",
            role="ADMIN"
        )
        admin_user = await user_service.create_user(user_data)
    
    return {
        "id": admin_user.id,
        "email": admin_user.email,
    "first_name": getattr(admin_user, "firstName", getattr(admin_user, "first_name", None)),
    "last_name": getattr(admin_user, "lastName", getattr(admin_user, "last_name", None)),
        "role": admin_user.role
    }


# Backwards-compat aliases expected by some tests
@pytest.fixture
async def test_user_admin(admin_user: dict) -> dict:
    return admin_user


@pytest.fixture
async def test_user_cashier(cashier_user: dict) -> dict:
    return cashier_user


@pytest.fixture
async def cashier_user(test_db: Prisma) -> dict:
    """Create or get cashier user for tests."""
    cashier_user = await test_db.user.find_first(where={"email": "cashier@sofinance.com"})
    
    if not cashier_user:
        from app.modules.users.schema import UserCreateSchema
        from app.modules.users.service import create_user_service
        
        user_service = create_user_service(test_db)
        user_data = UserCreateSchema(
            email="cashier@sofinance.com",
            password="CashierPassword123!",
            first_name="Cashier",
            last_name="User",
            role="CASHIER"
        )
        cashier_user = await user_service.create_user(user_data)
    
    return {
        "id": cashier_user.id,
        "email": cashier_user.email,
    "first_name": getattr(cashier_user, "firstName", getattr(cashier_user, "first_name", None)),
    "last_name": getattr(cashier_user, "lastName", getattr(cashier_user, "last_name", None)),
        "role": cashier_user.role
    }


@pytest.fixture
async def test_branch(test_db: Prisma, admin_user: dict) -> dict:
    """Create test branch."""
    branch = await test_db.branch.find_first(where={"name": "Test Branch"})
    
    if not branch:
        # Align with current Prisma schema: Branch has no email/status fields
        branch = await test_db.branch.create(
            data={
                "name": "Test Branch",
                "address": "123 Test Street",
                "phone": "+1234567890",
                # If your schema has manager/creator linkage, add appropriate fields here
            }
        )
    
    return {
        "id": branch.id,
        "name": branch.name,
        "address": branch.address,
        "phone": branch.phone,
        # Branch model doesn't have email; keep for legacy callers
        "email": getattr(branch, "email", None),
        # Derive status from isActive
        "status": "ACTIVE" if getattr(branch, "isActive", True) else "INACTIVE"
    }


@pytest.fixture
async def test_category(test_db: Prisma) -> dict:
    """Create test category."""
    category = await test_db.category.find_first(where={"name": "Test Category"})
    
    if not category:
        # Category in Prisma has status enum; if not provided, defaults to ACTIVE
        category = await test_db.category.create(
            data={
                "name": "Test Category",
                "description": "Category for testing purposes",
            }
        )
    
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
    # Some tests expect status; include if present on model
    "status": getattr(category, "status", "ACTIVE")
    }


@pytest.fixture
async def test_product(test_db: Prisma, test_category: dict) -> dict:
    """Create test product, tolerant to existing SKU or name."""
    product = await test_db.product.find_first(
        where={
            "OR": [
                {"name": "Test Product"},
                {"sku": "TEST-001"},
            ]
        }
    )
    
    if not product:
        product = await test_db.product.create(
            data={
                "name": "Test Product",
                "description": "Product for testing purposes",
                "sku": "TEST-001",
                "barcode": "1234567890123",
                "categoryId": test_category["id"],
                "sellingPrice": 10.99,
                "costPrice": 5.99,
            }
        )
    # Ensure Stock row
    stock = await test_db.stock.find_first(where={"productId": product.id})
    if not stock:
        await test_db.stock.create(data={
            "productId": product.id,
            "quantity": 100,
        })
    
    # Return an object that supports both attribute and key access
    class AttrDict(dict):
        def __getattr__(self, name):
            try:
                return self[name]
            except KeyError as e:
                raise AttributeError(name) from e

    return AttrDict({
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "sku": product.sku,
        "barcode": product.barcode,
        "categoryId": product.categoryId,
        # Provide legacy keys expected by some tests
        "price": float(product.sellingPrice),
        "cost": float(product.costPrice),
        "stockQuantity": 100,
        "minStockLevel": 10,
        "status": "ACTIVE"
    })


# --- Additional role/user/token fixtures used by inventory tests ---

async def _ensure_user_and_token(async_client: AsyncClient, test_db: Prisma, *, email: str, password: str, role: str, first_name: str, last_name: str) -> str:
    """Helper to ensure a user exists and return a fresh JWT access token."""
    user = await test_db.user.find_first(where={"email": email})
    if not user:
        from app.modules.users.schema import UserCreateSchema
        from app.modules.users.service import create_user_service
        user_service = create_user_service(test_db)
        user_data = UserCreateSchema(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        await user_service.create_user(user_data)

    # Login and return token
    login_response = await async_client.post(
        f"{settings.api_v1_str}/auth/login",
        json={"email": email, "password": password},
    )
    if login_response.status_code == 200:
        token_json = login_response.json()
        return token_json.get("access_token") or (token_json.get("data") or {}).get("access_token")
    return ""


@pytest.fixture
async def test_user_inventory_clerk(test_db: Prisma) -> dict:
    """Create or get an inventory clerk user for tests."""
    user = await test_db.user.find_first(where={"email": "inventory@sofinance.com"})
    if not user:
        from app.modules.users.schema import UserCreateSchema
        from app.modules.users.service import create_user_service
        user_service = create_user_service(test_db)
        user_data = UserCreateSchema(
            email="inventory@sofinance.com",
            password="InventoryPassword123!",
            first_name="Inventory",
            last_name="Clerk",
            role="INVENTORY_CLERK",
        )
        user = await user_service.create_user(user_data)
    return {"id": user.id, "email": user.email, "role": user.role}


@pytest.fixture
async def test_user_accountant(test_db: Prisma) -> dict:
    """Create or get an accountant user for tests."""
    user = await test_db.user.find_first(where={"email": "accountant@sofinance.com"})
    if not user:
        from app.modules.users.schema import UserCreateSchema
        from app.modules.users.service import create_user_service
        user_service = create_user_service(test_db)
        user_data = UserCreateSchema(
            email="accountant@sofinance.com",
            password="AccountantPassword123!",
            first_name="Accountant",
            last_name="User",
            role="ACCOUNTANT",
        )
        user = await user_service.create_user(user_data)
    return {"id": user.id, "email": user.email, "role": user.role}


@pytest.fixture
async def cashier_token(async_client: AsyncClient, test_db: Prisma, test_user_cashier: dict) -> str:
    return await _ensure_user_and_token(
        async_client, test_db,
        email="cashier@sofinance.com",
        password="CashierPassword123!",
        role="CASHIER",
        first_name="Cashier",
        last_name="User",
    )


@pytest.fixture
async def inventory_clerk_token(async_client: AsyncClient, test_db: Prisma, test_user_inventory_clerk: dict) -> str:
    return await _ensure_user_and_token(
        async_client, test_db,
        email="inventory@sofinance.com",
        password="InventoryPassword123!",
        role="INVENTORY_CLERK",
        first_name="Inventory",
        last_name="Clerk",
    )


@pytest.fixture
async def accountant_token(async_client: AsyncClient, test_db: Prisma, test_user_accountant: dict) -> str:
    return await _ensure_user_and_token(
        async_client, test_db,
        email="accountant@sofinance.com",
        password="AccountantPassword123!",
        role="ACCOUNTANT",
        first_name="Accountant",
        last_name="User",
    )


@pytest.fixture
async def test_customer(test_db: Prisma) -> dict:
    """Create test customer."""
    customer = await test_db.customer.find_first(where={"email": "customer@test.com"})

    if not customer:
        # Align with current Prisma schema (Customer has name/type/status fields)
        customer = await test_db.customer.create(
            data={
                "name": "Test Customer",
                "email": "customer@test.com",
                "phone": "+1234567890",
                "address": "123 Customer Street",
                "type": "INDIVIDUAL",
                "status": "ACTIVE"
            }
        )

    # Provide legacy keys expected by some tests by deriving from `name`
    full_name = getattr(customer, "name", "") or "Test Customer"
    parts = full_name.split(" ", 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ""

    return {
        "id": customer.id,
        "firstName": first_name,
        "lastName": last_name,
        "email": customer.email,
        "phone": customer.phone,
        "address": customer.address,
        "customerType": getattr(customer, "type", None),
        "status": customer.status,
        # Also include canonical fields for convenience
        "name": full_name,
        "type": getattr(customer, "type", None),
    }


# Test data constants
TEST_USER_DATA = {
    "email": "newuser@test.com",
    "password": "TestPassword123!",
    "first_name": "New",
    "last_name": "User",
    "role": "CASHIER"
}

TEST_BRANCH_DATA = {
    "name": "New Branch",
    "address": "456 New Street",
    "phone": "+0987654321",
    "email": "newbranch@sofinance.com"
}

TEST_CATEGORY_DATA = {
    "name": "New Category",
    "description": "New category for testing"
}

TEST_PRODUCT_DATA = {
    "name": "New Product",
    "description": "New product for testing",
    "sku": "NEW-001",
    "barcode": "9876543210987",
    "price": 15.99,
    "cost": 8.99,
    "stockQuantity": 50,
    "minStockLevel": 5
}

TEST_CUSTOMER_DATA = {
    "firstName": "New",
    "lastName": "Customer",
    "email": "newcustomer@test.com",
    "phone": "+1111111111",
    "address": "789 New Customer Street"
}

TEST_LOGIN_DATA = {
    "email": "test@sofinance.com",
    "password": "TestPassword123!"
}
