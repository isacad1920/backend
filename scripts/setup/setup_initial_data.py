"""
Create initial setup data for SOFinance system.
"""
import asyncio
import traceback
from app.db import connect_db, close_db
from app.db.prisma import prisma
from app.core.config import UserRole

async def setup_initial_data():
    """Create initial setup data including branch, categories, and demo user."""
    
    try:
        # Connect to database
        await connect_db()
        print("✅ Connected to database")
        
        # Create default branch
        print("📍 Creating default branch...")
        try:
            branch = await prisma.branch.create({
                'name': 'Main Branch',
                'address': '123 Main Street',
                'phone': '+1-555-0100',
                'isActive': True
            })
            print(f"✅ Created branch: {branch.name} (ID: {branch.id})")
        except Exception as e:
            if "unique constraint" in str(e).lower():
                print("ℹ️  Branch already exists, getting existing branch...")
                branch = await prisma.branch.find_first({
                    'where': {'name': 'Main Branch'}
                })
            else:
                raise e
        
        # Create default categories
        print("📋 Creating default categories...")
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and accessories'},
            {'name': 'Clothing', 'description': 'Apparel and fashion items'},
            {'name': 'Books', 'description': 'Books and educational materials'},
            {'name': 'Food & Beverage', 'description': 'Food items and drinks'},
        ]
        
        for cat_data in categories_data:
            try:
                category = await prisma.category.create(cat_data)
                print(f"✅ Created category: {category.name}")
            except Exception as e:
                if "unique constraint" in str(e).lower():
                    print(f"ℹ️  Category '{cat_data['name']}' already exists")
                else:
                    raise e
        
        # Create demo user with proper branch ID
        print("👤 Creating demo user...")
        try:
            # Check if user already exists
            existing_user = await prisma.user.find_unique({
                'where': {'email': 'demo@sofinance.com'}
            })
            
            if existing_user:
                print("ℹ️  Demo user already exists")
            else:
                from app.core.security import pwd_context
                hashed_password = pwd_context.hash("SecureDemo2024!")
                
                user = await prisma.user.create({
                    'email': 'demo@sofinance.com',
                    'password': hashed_password,
                    'firstName': 'Demo',
                    'lastName': 'User',
                    'phoneNumber': '+1-555-0123',
                    'role': UserRole.ADMIN.value,
                    'branchId': branch.id,
                    'isActive': True
                })
                print(f"✅ Created demo user: {user.email} (ID: {user.id})")
        except Exception as e:
            print(f"❌ Error creating demo user: {e}")
            traceback.print_exc()
        
        # Create some sample products
        print("📦 Creating sample products...")
        sample_products = [
            {
                'name': 'iPhone 15',
                'sku': 'IPHONE15-001',
                'description': 'Latest iPhone model',
                'costPrice': 800.00,
                'sellingPrice': 1200.00,
                'categoryId': 1,  # Electronics
                'isActive': True
            },
            {
                'name': 'Nike T-Shirt',
                'sku': 'NIKE-TSHIRT-001',
                'description': 'Cotton T-shirt',
                'costPrice': 15.00,
                'sellingPrice': 35.00,
                'categoryId': 2,  # Clothing
                'isActive': True
            },
            {
                'name': 'Python Programming Book',
                'sku': 'BOOK-PYTHON-001',
                'description': 'Learn Python programming',
                'costPrice': 25.00,
                'sellingPrice': 50.00,
                'categoryId': 3,  # Books
                'isActive': True
            }
        ]
        
        for prod_data in sample_products:
            try:
                product = await prisma.product.create(prod_data)
                print(f"✅ Created product: {product.name}")
                
                # Create stock record for the product
                await prisma.stock.create({
                    'productId': product.id,
                    'quantity': 100,  # Initial stock
                    'lastRestocked': None
                })
                print(f"✅ Created stock record for: {product.name}")
                
            except Exception as e:
                if "unique constraint" in str(e).lower():
                    print(f"ℹ️  Product '{prod_data['name']}' already exists")
                else:
                    print(f"❌ Error creating product '{prod_data['name']}': {e}")
        
        print("✅ Initial data setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        traceback.print_exc()
    finally:
        await close_db()
        print("✅ Disconnected from database")

if __name__ == "__main__":
    print("🚀 Setting up initial data for SOFinance system...")
    asyncio.run(setup_initial_data())
