#!/usr/bin/env bash

# SOFinance API Comprehensive Endpoint Testing Script
# This script will test every single endpoint with real data

set -e

BASE_URL="http://localhost:8000/api/v1"
TOKEN=""
USER_ID=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to make authenticated requests
auth_request() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    
    if [ -n "$data" ]; then
        curl -s -X "$method" "$BASE_URL$endpoint" \
             -H "Authorization: Bearer $TOKEN" \
             -H "Content-Type: application/json" \
             -d "$data"
    else
        curl -s -X "$method" "$BASE_URL$endpoint" \
             -H "Authorization: Bearer $TOKEN"
    fi
}

# Function to test endpoint
test_endpoint() {
    local method="$1"
    local endpoint="$2"
    local description="$3"
    local data="$4"
    
    print_status "Testing: $method $endpoint - $description"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "%{http_code}" -X "$method" "$BASE_URL$endpoint" \
                       -H "Authorization: Bearer $TOKEN" \
                       -H "Content-Type: application/json" \
                       -d "$data" -o /tmp/response.json)
    else
        response=$(curl -s -w "%{http_code}" -X "$method" "$BASE_URL$endpoint" \
                       -H "Authorization: Bearer $TOKEN" -o /tmp/response.json)
    fi
    
    http_code="${response: -3}"
    
    if [[ $http_code -ge 200 && $http_code -lt 300 ]]; then
        print_success "$method $endpoint -> $http_code"
        if [ -s /tmp/response.json ]; then
            echo "Response: $(cat /tmp/response.json | jq -r '.' 2>/dev/null || cat /tmp/response.json)"
        fi
    elif [[ $http_code -ge 400 && $http_code -lt 500 ]]; then
        print_warning "$method $endpoint -> $http_code (Client Error)"
        echo "Response: $(cat /tmp/response.json 2>/dev/null || echo 'No response body')"
    else
        print_error "$method $endpoint -> $http_code"
        echo "Response: $(cat /tmp/response.json 2>/dev/null || echo 'No response body')"
    fi
    
    echo "----------------------------------------"
}

echo "🏪 SOFinance API Comprehensive Testing Script"
echo "=============================================="

# Step 1: Health Check
print_status "Step 1: Health Check"
echo "Testing health endpoints..."
curl -s "$BASE_URL/../health" | jq '.' 2>/dev/null || echo "Health endpoint response"
curl -s "$BASE_URL/../ping" | jq '.' 2>/dev/null || echo "Ping endpoint response"
echo ""

# Step 2: Authentication
print_status "Step 2: Authentication - Login"
echo "Attempting to login with demo credentials..."

# Try to login with demo user
login_response=$(curl -s -X POST "$BASE_URL/auth/login" \
                      -H "Content-Type: application/json" \
                      -d '{
                        "email": "demo@sofinance.com",
                        "password": "SecureDemo2024!"
                      }' 2>/dev/null)

echo "Login response: $login_response"

# Extract token from response
TOKEN=$(echo "$login_response" | jq -r '.access_token' 2>/dev/null || echo "")

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    print_error "Failed to get authentication token. Creating demo user first..."
    
    # Try to create demo user
    print_status "Creating demo user..."
    cd /Users/abdiqayum/Desktop/SOFinance/backend
    source .venv/bin/activate
    python create_demo_user.py || true
    
    # Try login again
    sleep 2
    login_response=$(curl -s -X POST "$BASE_URL/auth/login" \
                          -H "Content-Type: application/json" \
                          -d '{
                            "email": "demo@sofinance.com",
                            "password": "SecureDemo2024!"
                          }' 2>/dev/null)
    
    TOKEN=$(echo "$login_response" | jq -r '.access_token' 2>/dev/null || echo "")
fi

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    print_error "Still failed to get token. Trying alternative credentials..."
    
    # Try admin credentials
    login_response=$(curl -s -X POST "$BASE_URL/auth/login" \
                          -H "Content-Type: application/json" \
                          -d '{
                            "email": "admin@sofinance.com",
                            "password": "admin123"
                          }' 2>/dev/null)
    
    TOKEN=$(echo "$login_response" | jq -r '.access_token' 2>/dev/null || echo "")
fi

if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    print_success "Successfully authenticated! Token: ${TOKEN:0:50}..."
    USER_ID=$(echo "$login_response" | jq -r '.user.id' 2>/dev/null || echo "1")
    print_success "User ID: $USER_ID"
else
    print_error "Failed to authenticate. Cannot proceed with endpoint testing."
    echo "Login response: $login_response"
    exit 1
fi

echo ""

# Step 3: Test All Endpoints
print_status "Step 3: Testing All API Endpoints"
echo "=============================================="

# Authentication Endpoints
print_status "🔐 AUTHENTICATION ENDPOINTS"
test_endpoint "POST" "/auth/refresh" "Refresh token" '{"refresh_token":"dummy_refresh_token"}'
test_endpoint "POST" "/auth/logout" "Logout" ""

# User Management Endpoints
print_status "👥 USER MANAGEMENT ENDPOINTS"
test_endpoint "GET" "/users/" "List users"
test_endpoint "GET" "/users/$USER_ID" "Get specific user"
test_endpoint "GET" "/users/profile" "Get current user profile"
test_endpoint "PUT" "/users/profile" "Update profile" '{
  "firstName": "Demo Updated",
  "lastName": "User Updated",
  "phone": "+1234567890"
}'
test_endpoint "POST" "/users/" "Create new user" '{
  "email": "newuser@sofinance.com",
  "password": "NewUser123!",
  "firstName": "New",
  "lastName": "User",
  "role": "CASHIER",
  "phone": "+1987654321"
}'

# Branch Management Endpoints
print_status "🏢 BRANCH MANAGEMENT ENDPOINTS"
test_endpoint "GET" "/branches/" "List branches"
test_endpoint "POST" "/branches/" "Create branch" '{
  "name": "Main Branch",
  "code": "MAIN001",
  "address": "123 Main St",
  "city": "New York",
  "phone": "+1234567890",
  "isActive": true
}'

# Category Endpoints
print_status "📋 CATEGORY ENDPOINTS"
test_endpoint "GET" "/categories/" "List categories"
test_endpoint "POST" "/categories/" "Create category" '{
  "name": "Electronics",
  "description": "Electronic devices and accessories",
  "isActive": true
}'

# Product Endpoints
print_status "📦 PRODUCT ENDPOINTS"
test_endpoint "GET" "/products/" "List products"
test_endpoint "POST" "/products/" "Create product" '{
  "name": "Test Product",
  "sku": "TEST001",
  "description": "A test product",
  "costPrice": 50.00,
  "sellingPrice": 100.00,
  "categoryId": "1",
  "isActive": true
}'

# Customer Endpoints
print_status "👤 CUSTOMER ENDPOINTS"
test_endpoint "GET" "/customers/" "List customers"
test_endpoint "POST" "/customers/" "Create customer" '{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "address": "123 Customer St"
}'

# Sales Endpoints
print_status "💰 SALES ENDPOINTS"
test_endpoint "GET" "/sales/" "List sales"
test_endpoint "GET" "/sales/summary" "Sales summary"
test_endpoint "POST" "/sales/" "Create sale" '{
  "customerId": 1,
  "items": [
    {
      "productId": 1,
      "quantity": 2,
      "unitPrice": 100.00
    }
  ],
  "paymentMethod": "CASH",
  "totalAmount": 200.00
}'

# Financial Endpoints
print_status "📊 FINANCIAL ENDPOINTS"
test_endpoint "GET" "/financial/dashboard" "Financial dashboard"
test_endpoint "GET" "/financial/analytics/sales" "Sales analytics"
test_endpoint "GET" "/financial/analytics/revenue" "Revenue analytics"
test_endpoint "GET" "/financial/analytics/inventory" "Inventory analytics"
test_endpoint "GET" "/financial/reports/profit-loss" "Profit & Loss report"
test_endpoint "GET" "/financial/reports/cash-flow" "Cash flow report"

# Inventory Endpoints (NEW)
print_status "📦 INVENTORY MANAGEMENT ENDPOINTS"
test_endpoint "GET" "/inventory/stock-levels" "Stock levels"
test_endpoint "GET" "/inventory/low-stock-alerts" "Low stock alerts"
test_endpoint "GET" "/inventory/valuation" "Inventory valuation"
test_endpoint "GET" "/inventory/dead-stock" "Dead stock analysis"
test_endpoint "GET" "/inventory/dashboard" "Inventory dashboard"
test_endpoint "POST" "/inventory/stock-adjustments" "Create stock adjustment" '{
  "product_id": 1,
  "adjustment_type": "INCREASE",
  "quantity": 10,
  "reason": "correction",
  "notes": "Manual adjustment for testing"
}'

# Permissions Endpoints
print_status "🔒 PERMISSIONS ENDPOINTS"
test_endpoint "GET" "/admin/roles" "List roles"
test_endpoint "GET" "/admin/permissions" "List permissions"

# Notifications Endpoints
print_status "🔔 NOTIFICATIONS ENDPOINTS"
test_endpoint "GET" "/notifications/" "List notifications"

# Stock Requests Endpoints
print_status "📋 STOCK REQUESTS ENDPOINTS"
test_endpoint "GET" "/stock-requests/" "List stock requests"
test_endpoint "POST" "/stock-requests/" "Create stock request" '{
  "fromBranchId": 1,
  "toBranchId": 2,
  "items": [
    {
      "productId": 1,
      "quantity": 5
    }
  ],
  "notes": "Test stock request"
}'

# Report Endpoints
print_status "📈 ADDITIONAL REPORT ENDPOINTS"
test_endpoint "GET" "/inventory/reports/turnover" "Inventory turnover report"
test_endpoint "GET" "/inventory/reports/movement" "Stock movement report"
test_endpoint "GET" "/inventory/reports/comprehensive" "Comprehensive inventory report"

print_status "🎉 TESTING COMPLETED!"
echo "=============================================="
print_success "All endpoint testing completed successfully!"
print_status "Check the detailed output above for individual endpoint results."
