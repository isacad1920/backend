#!/usr/bin/env python3
"""
Script to fix service-model pattern in all modules.
This ensures services get proper model instances instead of raw database clients.
"""

import os
import re

def fix_customer_routes():
    """Fix customer routes to use proper model pattern."""
    routes_file = "app/modules/customers/routes.py"
    
    print(f"🔧 Fixing customers service-model pattern...")
    
    with open(routes_file, 'r') as f:
        content = f.read()
    
    # Add the import if it doesn't exist
    if "from app.modules.customers.model import CustomerModel" not in content:
        # Find the imports section and add the model import
        import_section = content.find("from app.modules.customers.service import CustomerService")
        if import_section != -1:
            new_import = "from app.modules.customers.model import CustomerModel\nfrom app.modules.customers.service import CustomerService"
            content = content.replace("from app.modules.customers.service import CustomerService", new_import)
    
    # Pattern to fix service initialization
    pattern = r'(\s+)customers_service = CustomerService\(db\)'
    replacement = r'\1customer_model = CustomerModel(db)\n\1customers_service = CustomerService(customer_model)'
    
    # Apply the replacement
    new_content = re.sub(pattern, replacement, content)
    
    # Remove redundant model imports inside functions
    new_content = re.sub(r'(\s+)from app\.modules\.customers\.model import CustomerModel\n\s+customer_model = CustomerModel\(db\)\n', r'\1customer_model = CustomerModel(db)\n', new_content)
    
    if new_content != content:
        with open(routes_file, 'w') as f:
            f.write(new_content)
        print(f"✅ Fixed customers module - updated service-model pattern")
    else:
        print(f"ℹ️  Customers module already has correct pattern")

def main():
    """Main function to fix service-model patterns."""
    print("🚀 Fixing service-model patterns...")
    print("=" * 60)
    
    try:
        fix_customer_routes()
    except Exception as e:
        print(f"❌ Error fixing customers: {str(e)}")
    
    print("=" * 60)
    print("✅ Service-model pattern fixes completed!")

if __name__ == "__main__":
    main()
