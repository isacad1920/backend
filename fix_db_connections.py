#!/usr/bin/env python3
"""
Script to fix database connections in all modules.
This updates all service initializations to include the database dependency.
"""

import os
import re

# Define modules and their service names
MODULES = [
    ("inventory", "InventoryService"),
    ("customers", "CustomerService"),
    ("products", "ProductService"), 
    ("financial", "FinancialService"),
    ("stock_requests", "StockRequestService"),
    ("notifications", "NotificationService"),
    ("permissions", "PermissionService"),
    ("system", "SystemService"),
    ("journal", "JournalService"),
]

def fix_module_routes(module_name, service_name):
    """Fix database connections in a module's routes file."""
    routes_file = f"app/modules/{module_name}/routes.py"
    
    if not os.path.exists(routes_file):
        print(f"⚠️  Routes file not found: {routes_file}")
        return
    
    print(f"🔧 Fixing {module_name} module...")
    
    with open(routes_file, 'r') as f:
        content = f.read()
    
    # Different patterns for service initialization without database
    patterns = [
        (rf'(\s+){service_name.lower()}_service = {service_name}\(\)', rf'\1{service_name.lower()}_service = {service_name}(db)'),
        (rf'(\s+){module_name}_service = {service_name}\(\)', rf'\1{module_name}_service = {service_name}(db)'),
        (rf'(\s+)service = {service_name}\(\)', rf'\1service = {service_name}(db)'),
    ]
    
    new_content = content
    changes_made = False
    
    for pattern, replacement in patterns:
        temp_content = re.sub(pattern, replacement, new_content)
        if temp_content != new_content:
            new_content = temp_content
            changes_made = True
    
    if changes_made:
        with open(routes_file, 'w') as f:
            f.write(new_content)
        print(f"✅ Fixed {module_name} module - updated service initializations")
    else:
        print(f"ℹ️  {module_name} module already updated or no changes needed")

def main():
    """Main function to fix all modules."""
    print("🚀 Starting database connection fixes...")
    print("=" * 60)
    
    for module_name, service_name in MODULES:
        try:
            fix_module_routes(module_name, service_name)
        except Exception as e:
            print(f"❌ Error fixing {module_name}: {str(e)}")
    
    print("=" * 60)
    print("✅ Database connection fixes completed!")

if __name__ == "__main__":
    main()
