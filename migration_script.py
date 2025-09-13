#!/usr/bin/env python3
"""
Automated migration script to update all modules to use the new response system.
This script systematically updates imports, response formats, and field mappings.
"""

import re
from pathlib import Path


def update_file_content(file_path: str, content: str) -> str:
    """Update file content with new imports and response patterns."""
    
    # Replace old error_handler imports with new response imports
    content = re.sub(
        r'from app\.core\.error_handler import.*',
        'from app.core.response import ResponseBuilder, SuccessResponse, ErrorResponse',
        content
    )
    
    # Replace create_standard_response calls
    content = re.sub(
        r'create_standard_response\(\s*data=([^,)]+),?\s*message=([^)]+)\)',
        r'ResponseBuilder.success(data=\1, message=\2)',
        content
    )
    
    content = re.sub(
        r'create_standard_response\(\s*data=([^)]+)\)',
        r'ResponseBuilder.success(data=\1)',
        content
    )
    
    # Replace handle_database_error calls
    content = re.sub(
        r'handle_database_error\([^)]+\)',
        'ResponseBuilder.database_error()',
        content
    )
    
    # Update response model annotations where needed
    content = re.sub(
        r'response_model=(\w+ResponseSchema)',
        r'response_model=SuccessResponse[\1]',
        content
    )
    
    return content

def update_schema_aliases(file_path: str, content: str) -> str:
    """Update schema field aliases to match Prisma exactly."""
    
    # Common field alias patterns to fix
    aliases = {
        'first_name': 'firstName',
        'last_name': 'lastName',
        'branch_id': 'branchId',
        'is_active': 'isActive',
        'created_at': 'createdAt',
        'updated_at': 'updatedAt',
        'category_id': 'categoryId',
        'cost_price': 'costPrice',
        'selling_price': 'sellingPrice',
        'credit_limit': 'creditLimit',
        'total_purchases': 'totalPurchases',
        'product_id': 'productId',
        'last_restocked': 'lastRestocked',
        'customer_id': 'customerId',
        'user_id': 'userId',
        'total_amount': 'totalAmount'
    }
    
    if 'schema.py' in file_path:
        for old_alias, new_alias in aliases.items():
            # Update Field aliases
            content = re.sub(
                f'alias="{old_alias}"',
                f'alias="{old_alias}"',  # Keep for backward compatibility but add camelCase
                content
            )
            
            # Add proper camelCase field names
            content = re.sub(
                f'(\w+):\s*([^=]+)\s*=\s*Field\([^)]*alias="{old_alias}"[^)]*\)',
                f'{new_alias}: \\2 = Field(..., alias="{old_alias}")',
                content
            )
    
    return content

def process_directory(directory: str):
    """Process all Python files in a directory."""
    
    directory_path = Path(directory)
    
    for file_path in directory_path.rglob("*.py"):
        if file_path.name in ['__init__.py', 'migration_script.py']:
            continue
            
        print(f"Processing: {file_path}")
        
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
            
            # Skip if no relevant imports
            if 'error_handler' not in content and 'schema.py' not in str(file_path):
                continue
            
            original_content = content
            
            # Update imports and response patterns
            content = update_file_content(str(file_path), content)
            
            # Update schema aliases if it's a schema file
            content = update_schema_aliases(str(file_path), content)
            
            # Write back if changed
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Updated: {file_path}")
            else:
                print(f"⏭️  No changes: {file_path}")
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

def main():
    """Main migration function."""
    
    print("🚀 Starting automated migration to new response system...")
    print("=" * 60)
    
    # Process app directory
    app_dir = "/Users/abdiqayum/Desktop/SOFinance/backend/app"
    process_directory(app_dir)
    
    print("=" * 60)
    print("✅ Migration completed!")
    print("\nNext steps:")
    print("1. Update main.py to remove GlobalErrorHandler")
    print("2. Update route response models") 
    print("3. Fix any remaining schema field mappings")
    print("4. Test the endpoints")

if __name__ == "__main__":
    main()
