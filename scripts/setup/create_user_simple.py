#!/usr/bin/env python3
"""
Simple demo user creation using direct database connection
"""
import asyncio
import hashlib
import os
from datetime import datetime

# Simple database connection without importing the app
import asyncpg


async def create_demo_user_direct():
    """Create demo user directly in database."""
    print("🚀 Creating demo user directly in database...")
    
    # Database URL from environment or default
    database_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/sofinance_db")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database")
        
        # Check if user already exists
        existing_user = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1", 
            "demo@sofinance.com"
        )
        
        if existing_user:
            print("✅ Demo user already exists!")
            user_id = existing_user['id']
        else:
            # Hash password (simple SHA-256 for demo - not production ready)
            password = "demo123"
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Insert demo user
            user_id = await conn.fetchval("""
                INSERT INTO users (username, email, first_name, last_name, hashed_password, role, is_active, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id
            """, 
            "demo_user",
            "demo@sofinance.com", 
            "Demo", 
            "User", 
            hashed_password, 
            "ADMIN",
            True,
            datetime.utcnow(),
            datetime.utcnow()
            )
            
            print(f"✅ Demo user created with ID: {user_id}")
        
        print("\n🔑 Login credentials:")
        print("   Email: demo@sofinance.com")
        print("   Password: demo123")
        
        print("\n🌐 To test login:")
        print("1. Go to http://localhost:8000/docs")
        print("2. Use POST /api/v1/auth/login with the credentials above")
        print("3. Copy the access_token from the response")
        print("4. Click 'Authorize' button in Swagger UI")
        print("5. Enter the token (just the token, not 'Bearer')")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure PostgreSQL is running and DATABASE_URL is correct")

if __name__ == "__main__":
    asyncio.run(create_demo_user_direct())
