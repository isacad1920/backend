#!/usr/bin/env python3
"""
Create a demo user for testing the SOFinance system
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.prisma import connect_db, disconnect_db, get_db
from app.modules.users.service import create_user_service
from app.modules.users.schema import UserCreateSchema
from app.core.config import UserRole

async def create_demo_user():
    """Create a demo user for testing."""
    print("🚀 Creating demo user for SOFinance system...")
    
    try:
        # Connect to database
        await connect_db()
        print("✅ Connected to database")
        
        # Get database instance directly
        from app.db.prisma import prisma
        
        # Create user service
        user_service = create_user_service(prisma)
        
        # Demo user data
        demo_user = UserCreateSchema(
            email="demo@sofinance.com",
            password="SecureDemo2024!",
            first_name="Demo",
            last_name="User",
            phone_number="+1-555-0123",
            role=UserRole.ADMIN,  # Admin role for full access
            branch_id=1,
            is_active=True
        )
        
        print(f"📝 Creating user: {demo_user.email}")
        
        # Create the user
        result = await user_service.create_user(demo_user)
        
        print("✅ Demo user created successfully!")
        print(f"   Email: {result.email}")
        print(f"   Role: {result.role}")
        print(f"   ID: {result.id}")
        
        print("\n🔑 Login credentials:")
        print(f"   Email: demo@sofinance.com")
        print(f"   Password: demo123")
        
        print("\n🌐 To test login:")
        print("1. Go to http://localhost:8000/docs")
        print("2. Use POST /api/v1/auth/login with the credentials above")
        print("3. Copy the access_token from the response")
        print("4. Click 'Authorize' button in Swagger UI")
        print("5. Enter: Bearer YOUR_TOKEN_HERE")
        
    except Exception as e:
        print(f"❌ Error creating demo user: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Disconnect from database
        await disconnect_db()
        print("✅ Disconnected from database")

if __name__ == "__main__":
    asyncio.run(create_demo_user())
