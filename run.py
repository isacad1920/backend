"""
Application entry point for running the SOFinance POS System.
"""
import os
import sys
from pathlib import Path

import uvicorn

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import environment variables
from dotenv import load_dotenv

load_dotenv()

def main():
    """Main entry point for the application."""
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    environment = os.getenv("ENVIRONMENT", "DEV").upper()
    debug = os.getenv("DEBUG", "true").lower() in ["true", "1", "yes"]
    
    # Determine if we should reload
    reload = environment == "DEV" and debug
    
    # Log level
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print("=" * 60)
    print("🏪 SOFinance - Point of Sale & Financial Management System")
    print("=" * 60)
    print(f"🌐 Host: {host}")
    print(f"🚪 Port: {port}")
    print(f"🔧 Environment: {environment}")
    print(f"🐛 Debug: {debug}")
    print(f"🔄 Hot Reload: {reload}")
    print(f"📝 Log Level: {log_level.upper()}")
    print("=" * 60)
    
    if environment == "DEV":
        print("📚 API Documentation:")
        print(f"   - Swagger UI: http://{host}:{port}/docs")
        print(f"   - ReDoc: http://{host}:{port}/redoc")
        print(f"   - OpenAPI Spec: http://{host}:{port}/openapi.json")
        print("=" * 60)
        if host == "0.0.0.0":
            # Helpful hint: 0.0.0.0 is not browsable; use localhost in the browser
            print(f"💡 Open in your browser: http://localhost:{port}")
            print("=" * 60)
    
    # Run the application
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=debug,
            workers=1 if reload else None,
            reload_dirs=[str(project_root)] if reload else None
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down SOFinance system...")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()