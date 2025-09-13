#!/usr/bin/env python3
"""
Simple test runner that starts server and runs tests
"""
import os
import subprocess
import sys
import time
from pathlib import Path


def run_server():
    """Start the server without hot reload"""
    print("🚀 Starting server without hot reload...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path.cwd())
    
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--host", "0.0.0.0",
        "--port", "8000"
    ]
    
    process = subprocess.Popen(cmd, env=env)
    print(f"Server started with PID: {process.pid}")
    return process

def run_test():
    """Run a simple health check test"""
    print("🧪 Running health check test...")
    time.sleep(3)  # Give server time to start
    
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/api/test_misc.py::TestHealthEndpoints::test_health_check",
        "-v"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
    print(f"Return code: {result.returncode}")
    
    return result.returncode == 0

def main():
    server_process = None
    try:
        # Start server
        server_process = run_server()
        
        # Run test
        success = run_test()
        
        if success:
            print("✅ Test passed!")
        else:
            print("❌ Test failed!")
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    finally:
        if server_process:
            print(f"🛑 Stopping server (PID: {server_process.pid})")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    main()
