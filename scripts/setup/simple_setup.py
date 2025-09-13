"""
Simple setup script for essential testing data.
"""
import asyncio
from app.db import connect_db, close_db
from app.db.prisma import prisma
from app.core.config import UserRole
from app.core.security import pwd_context

async def simple_setup():
    """Create minimal data for testing."""
    
    try:
        await connect_db()
        print("✅ Connected to database")
        
        # Create demo user directly without validation
        print("👤 Creating demo user...")
        try:
            hashed_password = pwd_context.hash("SecureDemo2024!")
            
            user = await prisma.user.create({
                'username': 'demo_user',
                'email': 'demo@sofinance.com',
                'firstName': 'Demo',
                'lastName': 'User',
                'hashedPassword': hashed_password,
                'role': UserRole.ADMIN.value,
                'branchId': 1,
                'isActive': True
            })
            print(f"✅ Created demo user: {user.email} (ID: {user.id})")
        except Exception as e:
            if "unique constraint" in str(e).lower():
                print("ℹ️  Demo user already exists")
            else:
                print(f"❌ Error creating demo user: {e}")
        
        print("✅ Simple setup completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(simple_setup())
