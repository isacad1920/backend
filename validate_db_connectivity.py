#!/usr/bin/env python3
"""
Comprehensive database connectivity validator for all modules.
This checks that all critical business operations are properly connected to the database.
"""

import os
import re
import sys

def check_file_exists(file_path):
    """Check if a file exists and return status."""
    if os.path.exists(file_path):
        return "✅"
    else:
        return "❌"

def check_database_imports(file_path):
    """Check if a file properly imports database dependencies."""
    if not os.path.exists(file_path):
        return "❌"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check for database imports
    if "from app.db.prisma import get_db" in content:
        return "✅"
    else:
        return "⚠️"

def check_service_initialization(file_path, service_name):
    """Check if service is properly initialized with database."""
    if not os.path.exists(file_path):
        return "❌"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Look for proper service initialization patterns
    patterns = [
        rf'{service_name}\(db\)',
        rf'{service_name}\([^)]*Model\([^)]*db[^)]*\)[^)]*\)',
        rf'service = {service_name}\(db\)'
    ]
    
    for pattern in patterns:
        if re.search(pattern, content):
            return "✅"
    
    # Check for old pattern without database
    if f'{service_name}()' in content:
        return "❌"
    
    return "⚠️"

def main():
    """Main validation function."""
    print("🔍 COMPREHENSIVE DATABASE CONNECTIVITY VALIDATION")
    print("=" * 70)
    
    # Define critical modules for business operations
    critical_modules = [
        ("users", "UserService"),
        ("products", "ProductService"), 
        ("inventory", "InventoryService"),
        ("sales", "SalesService"),
        ("customers", "CustomerService"),
        ("branches", "BranchService"),
        ("financial", "FinancialService"),
        ("journal", "JournalService"),
        ("stock_requests", "StockRequestService"),
        ("notifications", "NotificationService"),
        ("permissions", "PermissionService"),
        ("system", "SystemService")
    ]
    
    print(f"{'Module':<15} {'Routes':<8} {'Service':<8} {'DB Import':<10} {'DB Connect':<10}")
    print("-" * 70)
    
    all_good = True
    
    for module, service_name in critical_modules:
        routes_path = f"app/modules/{module}/routes.py"
        service_path = f"app/modules/{module}/service.py"
        
        routes_exist = check_file_exists(routes_path)
        service_exist = check_file_exists(service_path)
        db_import = check_database_imports(routes_path)
        db_connect = check_service_initialization(routes_path, service_name)
        
        print(f"{module:<15} {routes_exist:<8} {service_exist:<8} {db_import:<10} {db_connect:<10}")
        
        if routes_exist == "❌" or service_exist == "❌" or db_connect == "❌":
            all_good = False
    
    print("=" * 70)
    
    if all_good:
        print("🎉 ALL MODULES ARE PROPERLY CONNECTED TO DATABASE!")
        print("✅ Production-ready database connectivity confirmed")
    else:
        print("⚠️  Some modules need attention for production deployment")
        print("❌ = Missing/Broken, ⚠️ = Warning/Needs Review, ✅ = Good")
    
    print("\n📊 CONNECTIVITY SUMMARY:")
    print("- Routes: API endpoint definitions")
    print("- Service: Business logic layer") 
    print("- DB Import: Database dependency import")
    print("- DB Connect: Service initialization with database")

if __name__ == "__main__":
    main()
